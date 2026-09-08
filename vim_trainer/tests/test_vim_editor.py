from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from vim_trainer.curriculum import DEFAULT_COURSE
from vim_trainer.domain.entities import Cursor, Lesson, PracticeFile, RegisterExpectation
from vim_trainer.infrastructure.vim_editor import (
    EditorExecutionError,
    ExerciseReadError,
    VimEditorGateway,
    VimSessionLayout,
)

LESSON = Lesson(
    id="01-vim",
    chapter="Тест",
    title="Vim adapter",
    goal="Проверить адаптер",
    task=("Перейди на строку 2",),
    commands=("j",),
    hint="Нажми j",
    files=(PracticeFile("task.txt", "one\ntwo\n", "one\ntwo\n"),),
    entrypoint="task.txt",
    expected_cursor=Cursor(2, 3),
    expected_registers=(RegisterExpectation("a", ""),),
)


class VimEditorGatewayTests(unittest.TestCase):
    def test_default_prepared_exercise_keeps_embedded_guide(self) -> None:
        gateway = VimEditorGateway([sys.executable])
        exercise = gateway.prepare(LESSON)
        workspace = exercise.workspace

        self.assertEqual((workspace / "task.txt").read_text(encoding="utf-8"), "one\ntwo\n")
        self.assertTrue(exercise.guide_path.is_file())
        self.assertTrue(exercise.session_path.is_file())
        self.assertIn(str(exercise.session_path), gateway.arguments(exercise))
        session = exercise.session_path.read_text(encoding="utf-8")
        self.assertIn("46vsplit", session)
        self.assertIn("13split", session)
        self.assertIn("<F1>", session)

        exercise.close()
        exercise.close()
        self.assertFalse(workspace.exists())

    def test_editor_only_prepared_exercise_omits_embedded_guide(self) -> None:
        gateway = VimEditorGateway([sys.executable])
        with gateway.prepare(LESSON, layout=VimSessionLayout.EDITOR_ONLY) as exercise:
            session = exercise.session_path.read_text(encoding="utf-8")

            self.assertTrue((exercise.workspace / "task.txt").is_file())
            self.assertFalse(exercise.guide_path.exists())
            self.assertNotIn(str(exercise.guide_path), session)
            self.assertNotIn("vsplit", session)
            self.assertNotIn("13split", session)
            self.assertNotIn("F1", session)
            self.assertNotIn("trainer_guide", session)
            for task_item in LESSON.task:
                self.assertNotIn(task_item, session)

    def test_quotes_vim_single_quoted_strings(self) -> None:
        self.assertEqual(VimEditorGateway._vim_quote("it's"), "'it''s'")

    def test_guide_is_short_and_contains_exit_commands(self) -> None:
        guide = VimEditorGateway._build_guide(LESSON)
        session = VimEditorGateway._build_session(
            LESSON,
            Path("/tmp/workspace"),
            Path("/tmp/guide"),
            Path("/tmp/state"),
        )

        self.assertIn("01-vim · Vim adapter", guide)
        self.assertIn("ЗАДАЧА\n1.", guide)
        self.assertIn("КОМАНДЫ", guide)
        self.assertIn(":wqa", guide)
        self.assertIn(":TrainerCancel", guide)
        self.assertIn(r"statusline=F1\ ·\ :wqa%<", session)

    def test_guide_fits_the_training_pane(self) -> None:
        for width, maximum_rows in ((80, 14), (46, 18)):
            for lesson in DEFAULT_COURSE:
                with self.subTest(width=width, lesson=lesson.id):
                    rows = sum(
                        max(1, (len(line) + width - 1) // width)
                        for line in VimEditorGateway._build_guide(lesson).splitlines()
                    )
                    self.assertLessEqual(rows, maximum_rows)

    @patch("vim_trainer.infrastructure.vim_editor.subprocess.run")
    def test_edit_reads_successful_editor_result(self, run: object) -> None:
        def complete(arguments: object, *, cwd: Path, check: bool) -> subprocess.CompletedProcess:
            del arguments, check
            Path(cwd, ".trainer-state.json").write_text(
                json.dumps({"line": 2, "column": 3, "registers": {"a": ""}}),
                encoding="utf-8",
            )
            return subprocess.CompletedProcess([], 0)

        run.side_effect = complete  # type: ignore[attr-defined]

        outcome = VimEditorGateway([sys.executable]).edit(LESSON)

        self.assertFalse(outcome.cancelled)
        self.assertEqual(outcome.observed.cursor, Cursor(2, 3))

    @patch("vim_trainer.infrastructure.vim_editor.subprocess.run")
    def test_only_explicit_cancel_is_treated_as_cancel(self, run: object) -> None:
        def cancel(arguments: object, *, cwd: Path, check: bool) -> subprocess.CompletedProcess:
            del arguments, check
            Path(cwd, ".trainer-cancelled").write_text("cancelled", encoding="utf-8")
            return subprocess.CompletedProcess([], 1)

        run.side_effect = cancel  # type: ignore[attr-defined]

        outcome = VimEditorGateway([sys.executable]).edit(LESSON)

        self.assertTrue(outcome.cancelled)

    @patch("vim_trainer.infrastructure.vim_editor.subprocess.run")
    def test_unexpected_nonzero_exit_is_an_error(self, run: object) -> None:
        run.return_value = subprocess.CompletedProcess([], 2)  # type: ignore[attr-defined]

        with self.assertRaises(EditorExecutionError):
            VimEditorGateway([sys.executable]).edit(LESSON)

    @patch("vim_trainer.infrastructure.vim_editor.subprocess.run")
    def test_info_rejects_non_vim_executable(self, run: object) -> None:
        run.return_value = subprocess.CompletedProcess(  # type: ignore[attr-defined]
            [], 0, stdout="GNU nano 8.0\n", stderr=""
        )

        with self.assertRaises(EditorExecutionError):
            VimEditorGateway([sys.executable]).info()

    @patch("vim_trainer.infrastructure.vim_editor.subprocess.run")
    def test_info_rejects_vim_without_required_capabilities(self, run: object) -> None:
        run.side_effect = [  # type: ignore[attr-defined]
            subprocess.CompletedProcess([], 0, stdout="VIM - Vi IMproved 7.4\n", stderr=""),
            subprocess.CompletedProcess([], 1, stdout="", stderr=""),
        ]

        with self.assertRaisesRegex(EditorExecutionError, r"Vim 8\+"):
            VimEditorGateway([sys.executable]).info()

    @patch("vim_trainer.infrastructure.vim_editor.subprocess.run")
    def test_invalid_utf8_exercise_is_reported(self, run: object) -> None:
        def corrupt(arguments: object, *, cwd: Path, check: bool) -> subprocess.CompletedProcess:
            del arguments, check
            Path(cwd, ".trainer-state.json").write_text(
                json.dumps({"line": 1, "column": 1, "registers": {"a": ""}}),
                encoding="utf-8",
            )
            Path(cwd, "task.txt").write_bytes(b"\xff")
            return subprocess.CompletedProcess([], 0)

        run.side_effect = corrupt  # type: ignore[attr-defined]

        with self.assertRaises(ExerciseReadError):
            VimEditorGateway([sys.executable]).edit(LESSON)

    @unittest.skipUnless(shutil.which("vim"), "Vim is not installed")
    def test_generated_session_captures_cursor_and_registers(self) -> None:
        vim = shutil.which("vim")
        assert vim is not None
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            guide = workspace / ".guide.txt"
            state = workspace / ".state.json"
            session = workspace / ".session.vim"
            VimEditorGateway._prepare_files(workspace, LESSON)
            guide.write_text(VimEditorGateway._build_guide(LESSON), encoding="utf-8")
            script = (
                VimEditorGateway._build_session(LESSON, workspace, guide, state)
                + "\nvsplit\n"
                + "let g:trainer_expected_window = win_getid()\n"
                + 'call feedkeys("\\<F1>\\<F1>", "xt")\n'
                + "if win_getid() != g:trainer_expected_window | cquit | endif\n"
                + "call cursor(2, 3)\nwqa\n"
            )
            session.write_text(script, encoding="utf-8")

            result = subprocess.run(
                [
                    vim,
                    "-u",
                    "NONE",
                    "--noplugin",
                    "-N",
                    "-n",
                    "-i",
                    "NONE",
                    "-es",
                    "-S",
                    str(session),
                ],
                cwd=workspace,
                check=False,
                timeout=10,
            )

            self.assertEqual(result.returncode, 0)
            payload = json.loads(state.read_text(encoding="utf-8"))
            self.assertEqual((payload["line"], payload["column"]), (2, 3))
            self.assertEqual(payload["registers"], {"a": ""})
