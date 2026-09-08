from __future__ import annotations

import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import PropertyMock, patch

from vim_trainer.infrastructure.json_progress import JsonProgressRepository
from vim_trainer.presentation.cli import _format_progress, _progress_bar, build_parser, main
from vim_trainer.presentation.console import Console


class CliTests(unittest.TestCase):
    @patch("vim_trainer.presentation.cli.serve_web")
    @patch("vim_trainer.presentation.cli.VimPtyGateway")
    def test_no_command_launches_browser_first_web_mode(
        self,
        pty_gateway: object,
        serve_web: object,
    ) -> None:
        exit_code = main([])

        self.assertEqual(exit_code, 0)
        pty_gateway.assert_called_once_with(None, clean=True)
        call = serve_web.call_args
        self.assertEqual(call.args[2], pty_gateway.return_value)
        self.assertEqual(call.kwargs["host"], "127.0.0.1")
        self.assertEqual(call.kwargs["port"], 8765)
        self.assertTrue(call.kwargs["open_browser"])

    @patch("vim_trainer.presentation.cli._run_training", return_value=0)
    def test_explicit_start_keeps_terminal_training_mode(self, run_training: object) -> None:
        exit_code = main(["start", "07", "--once"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(run_training.call_args.args[2], "07")
        self.assertTrue(run_training.call_args.kwargs["once"])

    def test_web_command_parses_local_port_without_starting_server(self) -> None:
        arguments = build_parser().parse_args(["web", "--port", "9010", "--no-open"])

        self.assertEqual(arguments.command, "web")
        self.assertEqual(arguments.port, 9010)
        self.assertTrue(arguments.no_open)

    def test_course_map_does_not_require_an_installed_editor(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            environment = {
                "VIM_TRAINER_DATA_DIR": directory,
                "VIM_TRAINER_EDITOR": "definitely-not-an-editor",
                "NO_COLOR": "1",
            }
            output = io.StringIO()
            with patch.dict(os.environ, environment, clear=False), redirect_stdout(output):
                exit_code = main(["list"])

        self.assertEqual(exit_code, 0)
        self.assertIn("КАРТА КУРСА", output.getvalue())
        self.assertIn("Основы", output.getvalue())
        self.assertIn("[··········] 0/10", output.getvalue())
        self.assertIn("> 01  00-navigation-warmup", output.getvalue())
        self.assertIn("00-navigation-warmup", output.getvalue())
        self.assertIn("35-final-python", output.getvalue())

    def test_progress_graphics_cover_empty_partial_and_complete(self) -> None:
        self.assertEqual(_progress_bar(0, 4, width=4), "····")
        self.assertEqual(_progress_bar(2, 4, width=4), "██··")
        self.assertEqual(_format_progress(4, 4, width=4), "[████] 4/4 · 100%")

    def test_status_shows_chapter_graphs_and_next_lesson(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = JsonProgressRepository(path=Path(directory) / "progress.json")
            repository.record_attempt("00-navigation-warmup", passed=True)
            repository.record_attempt("01-modes", passed=False)
            repository.record_attempt("01-modes", passed=True)
            repository.record_attempt("removed-lesson", passed=True)
            environment = {
                "VIM_TRAINER_DATA_DIR": directory,
                "VIM_TRAINER_EDITOR": "definitely-not-an-editor",
                "NO_COLOR": "1",
            }
            output = io.StringIO()
            with patch.dict(os.environ, environment, clear=False), redirect_stdout(output):
                exit_code = main(["status"])

        rendered = output.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn("ПО ГЛАВАМ", rendered)
        self.assertIn("Основы", rendered)
        self.assertIn("2/10", rendered)
        self.assertIn("Попыток: 3", rendered)
        self.assertIn("> Дальше: 02-command-line", rendered)

    def test_doctor_reports_missing_editor(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            environment = {
                "VIM_TRAINER_DATA_DIR": directory,
                "VIM_TRAINER_EDITOR": "definitely-not-an-editor",
                "NO_COLOR": "1",
            }
            output = io.StringIO()
            with patch.dict(os.environ, environment, clear=False), redirect_stdout(output):
                exit_code = main(["doctor"])

        self.assertEqual(exit_code, 2)
        self.assertIn("не найден", output.getvalue())

    def test_eof_at_confirmation_is_a_safe_exit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = io.StringIO()
            with (
                patch.dict(os.environ, {"VIM_TRAINER_DATA_DIR": directory}, clear=False),
                patch.object(
                    Console,
                    "interactive",
                    new_callable=PropertyMock,
                    return_value=True,
                ),
                patch.object(Console, "prompt", side_effect=EOFError),
                redirect_stdout(output),
            ):
                exit_code = main(["reset"])

        self.assertEqual(exit_code, 130)
        self.assertIn("Остановлено", output.getvalue())
