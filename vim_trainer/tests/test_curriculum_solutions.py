from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from vim_trainer.curriculum import DEFAULT_COURSE
from vim_trainer.domain.entities import Lesson, ObservedState
from vim_trainer.domain.validation import validate_lesson
from vim_trainer.infrastructure.vim_editor import VimEditorGateway

VIM = shutil.which("vim")


@unittest.skipUnless(VIM, "Vim is not installed")
class ReferenceSolutionTests(unittest.TestCase):
    def test_important_techniques_work_in_real_vim(self) -> None:
        solutions = {
            "00-navigation-warmup": ("normal! lllljjhhk",),
            "03-hjkl": ("normal! jjjllllll",),
            "08-advanced-motion": ('execute "normal! %\\<C-o>\\<C-i>"',),
            "25-ex-ranges": (
                "2,5s/todo/DONE/",
                "2,5normal! I- ",
                "2,5normal! A;",
            ),
            "27-named-register": ('execute "normal! f \\"ay$j$\\"apj$\\"apj$\\"ap"',),
            "28-black-hole": ('execute "normal! yyjdd\\"_dd\\"0p"',),
            "30-macros": ('call feedkeys("qqI- \\<Esc>A;\\<Esc>jq4@q", "xt")',),
            "33-argdo": (
                "args src/a.py src/b.py src/c.py",
                "argdo %s/TODO/DONE/g | update",
            ),
            "34-quickfix": (
                "vimgrep /BROKEN/ src/*.py",
                "cfdo %s/BROKEN/FIXED/g | update",
            ),
            "35-final-python": (
                "2,5delete",
                "1put ='    return sum(values)'",
                "2put =''",
                r"%s/\<value\>/total_value/g",
                r'%s/print("total:", total_value)/print(f"total={total_value}")/',
                "7put =''",
                "args config.py tests/test_report.py",
                "argdo %s/debug/prod/ge | update",
                "vimgrep /old_total/ *.py tests/*.py",
                "cfdo %s/old_total/total/g | update",
            ),
            "36-nested-text-object": ('execute "normal! c2i(prepared, retries=3\\<Esc>"',),
            "37-tag-text-objects": (
                'execute "normal! citRelease status\\<Esc>"',
                'execute "normal! /aside\\<CR>datdd"',
            ),
            "38-search-boundaries": (r"%s/\v<key\=\zs\d+\ze;/42/g",),
            "39-cgn-rename": ('call feedkeys("*Ncgnsum_value\\<Esc>..", "xt")',),
            "40-ex-move": ("4move 1",),
            "41-sequential-numbers": ('execute "normal! V3jg\\<C-a>"',),
            "42-expression-register": (
                'call feedkeys("a \\<C-r>=7*6\\<CR>\\<Esc>", "xt")',
                "call cursor(2, 8)",
                "call feedkeys(\"a\\<C-r>=tolower(substitute('Release Candidate', ' ', '-', 'g'))\\<CR>\\<Esc>\", \"xt\")",
            ),
            "43-append-macro": ('call feedkeys("qaI\\"\\<Esc>qqAA\\",\\<Esc>jq2@a", "xt")',),
            "44-change-list": (
                'call feedkeys("ci\\"ready\\<Esc>/secondary\\<CR>ci\\"ready\\<Esc>/fallback\\<CR>ci\\"ready\\<Esc>g;g;g;", "xt")',
            ),
            "45-find-path": (
                "set path+=src/**",
                "find formatter.py",
                "%s/return value/return value.strip().title()/",
                "update",
            ),
            "46-location-list": (
                "lvimgrep /DEPRECATED/ src/*.py",
                "ldo s/DEPRECATED/SUPPORTED/ | update",
            ),
            "47-quickfix-items": (
                "vimgrep /TODO/ **/*.py",
                "cdo s/TODO/DONE/ | update",
            ),
            "48-code-navigation": (
                "normal! gf",
                "%s/0.10/0.20/",
                "update",
                'execute "normal! \\<C-o>/calculate_total\\<CR>\\<C-]>"',
                "%s/return subtotal/return subtotal * (1 + DEFAULT_TAX)/",
                "update",
            ),
            "49-make-quickfix": (
                r"set makeprg=python3\ check_project.py",
                "set errorformat=%f:%l:%m",
                "silent make",
                "copen",
                "cfirst",
                "%s/debug/prod/",
                "update",
                "buffer README.txt",
                "silent make",
            ),
            "50-final-project": (
                r"set makeprg=python3\ check_project.py",
                "set errorformat=%f:%l:%m",
                "silent make",
                "buffer main.py",
                "call cursor(1, 11)",
                "normal! gf",
                'execute "normal! /total_value\\<CR>"',
                'call feedkeys("*Ncgnsum_value\\<Esc>.", "xt")',
                'execute "normal! /format_value(sum_value\\<CR>f(l"',
                'execute "normal! c2i(sum_value, retries=SETTINGS[\\"retries\\"]\\<Esc>"',
                "update",
                "set path+=src/**",
                "find config.py",
                '%s/"debug"/"prod"/',
                '%s/"retries": 1/"retries": 3/',
                "update",
                "vimgrep /TODO/ **/*.py",
                "cdo s/TODO/DONE/ | update",
                "buffer main.py",
                r"set makeprg=python3\ check_project.py",
                "set errorformat=%f:%l:%m",
                "silent make",
            ),
        }

        for reference, commands in solutions.items():
            with self.subTest(lesson=reference):
                lesson = DEFAULT_COURSE.resolve(reference)
                observed = self._run_solution(lesson, commands)
                result = validate_lesson(lesson, observed)
                self.assertTrue(result.passed, result.issues)

    def _run_solution(self, lesson: Lesson, commands: tuple[str, ...]) -> ObservedState:
        assert VIM is not None
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            guide = workspace / ".trainer-guide.txt"
            state = workspace / ".trainer-state.json"
            session = workspace / ".trainer-session.vim"
            VimEditorGateway._prepare_files(workspace, lesson)
            guide.write_text(VimEditorGateway._build_guide(lesson), encoding="utf-8")
            script = VimEditorGateway._build_session(lesson, workspace, guide, state)
            session.write_text(
                f"{script}\n" + "\n".join(commands) + "\nwqa\n",
                encoding="utf-8",
            )

            completed = subprocess.run(
                [
                    VIM,
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
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.assertEqual(
                completed.returncode,
                0,
                completed.stderr or completed.stdout,
            )
            raw_state = VimEditorGateway._read_state(state)
            return ObservedState(
                files=VimEditorGateway._read_files(workspace, lesson),
                cursor=VimEditorGateway._read_cursor(raw_state),
                registers=VimEditorGateway._read_registers(raw_state),
            )

    def test_append_macro_accepts_equivalent_movements(self) -> None:
        lesson = DEFAULT_COURSE.resolve("43-append-macro")
        observed = self._run_solution(
            lesson,
            ('call feedkeys("qa0i\\"\\<Esc>qqA$a\\",\\<Esc>jq2@a", "xt")',),
        )

        result = validate_lesson(lesson, observed)

        self.assertTrue(result.passed, result.issues)

    def test_change_list_accepts_equivalent_file_edit(self) -> None:
        lesson = DEFAULT_COURSE.resolve("44-change-list")
        observed = self._run_solution(lesson, ("%s/old/ready/g",))

        result = validate_lesson(lesson, observed)

        self.assertTrue(result.passed, result.issues)
