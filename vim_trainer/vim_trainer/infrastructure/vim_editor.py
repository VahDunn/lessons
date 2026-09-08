from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from vim_trainer.application.ports import EditOutcome
from vim_trainer.domain.entities import Cursor, Lesson, ObservedState


class EditorError(RuntimeError):
    pass


class EditorNotFoundError(EditorError):
    pass


class EditorExecutionError(EditorError):
    pass


class ExerciseReadError(EditorError):
    pass


class VimSessionLayout(Enum):
    """Presentation owned by a Vim session, independent from lesson content."""

    EMBEDDED_GUIDE = "embedded-guide"
    EDITOR_ONLY = "editor-only"


@dataclass(frozen=True)
class EditorInfo:
    command: tuple[str, ...]
    version: str


class PreparedVimExercise:
    """A prepared disposable workspace shared by sync and interactive editors."""

    def __init__(
        self,
        lesson: Lesson,
        temporary_directory: tempfile.TemporaryDirectory[str],
    ) -> None:
        self.lesson = lesson
        self._temporary_directory: tempfile.TemporaryDirectory[str] | None = (
            temporary_directory
        )
        self.workspace = Path(temporary_directory.name)
        self.guide_path = self.workspace / ".trainer-guide.txt"
        self.state_path = self.workspace / ".trainer-state.json"
        self.session_path = self.workspace / ".trainer-session.vim"
        self.cancel_path = self.workspace / ".trainer-cancelled"

    def outcome(self, returncode: int, *, cancelled: bool = False) -> EditOutcome:
        if cancelled or self.cancel_path.is_file():
            return EditOutcome(observed=ObservedState(files={}), cancelled=True)
        if returncode != 0:
            raise EditorExecutionError(
                f"Редактор аварийно завершился с кодом {returncode}"
            )

        state = VimEditorGateway._read_state(self.state_path)
        return EditOutcome(
            observed=ObservedState(
                files=VimEditorGateway._read_files(self.workspace, self.lesson),
                cursor=VimEditorGateway._read_cursor(state),
                registers=VimEditorGateway._read_registers(state),
            )
        )

    def mark_cancelled(self) -> None:
        try:
            self.cancel_path.write_text("cancelled", encoding="utf-8")
        except OSError as error:
            raise EditorExecutionError(
                f"Не удалось отметить упражнение отменённым: {error}"
            ) from error

    def close(self) -> None:
        temporary_directory = self._temporary_directory
        if temporary_directory is None:
            return
        self._temporary_directory = None
        temporary_directory.cleanup()

    def __enter__(self) -> PreparedVimExercise:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


class VimEditorGateway:
    def __init__(
        self,
        editor_command: str | Sequence[str] | None = None,
        *,
        clean: bool = True,
    ) -> None:
        self._editor_command = editor_command
        self._resolved_command: tuple[str, ...] | None = None
        self._clean = clean

    @property
    def command(self) -> tuple[str, ...]:
        if self._resolved_command is None:
            self._resolved_command = self._resolve_command(self._editor_command)
        return self._resolved_command

    def info(self) -> EditorInfo:
        try:
            result = subprocess.run(
                [*self.command, "--version"],
                check=False,
                capture_output=True,
                text=True,
                timeout=5,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            raise EditorNotFoundError(f"Не удалось запустить редактор: {error}") from error
        output = result.stdout or result.stderr
        if result.returncode != 0:
            raise EditorExecutionError(
                f"Редактор не прошёл проверку --version (код {result.returncode})"
            )
        version = output.splitlines()[0] if output else ""
        if "vim" not in version.lower():
            raise EditorExecutionError("Выбранная команда не похожа на Vim или Neovim")
        self._verify_capabilities()
        return EditorInfo(self.command, version)

    def _verify_capabilities(self) -> None:
        capability_check = (
            "if !(has('nvim') || v:version >= 800) "
            "|| !exists('*json_encode') || !exists('*win_getid') | cquit | endif"
        )
        try:
            result = subprocess.run(
                [
                    *self.command,
                    "-u",
                    "NONE",
                    "-n",
                    "-es",
                    "-c",
                    capability_check,
                    "-c",
                    "qa!",
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=5,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            raise EditorExecutionError(
                f"Не удалось проверить возможности редактора: {error}"
            ) from error
        if result.returncode != 0:
            raise EditorExecutionError(
                "Редактору не хватает нужных возможностей; нужен Vim 8+ или Neovim"
            )

    def edit(self, lesson: Lesson) -> EditOutcome:
        with self.prepare(lesson) as exercise:
            try:
                result = subprocess.run(
                    self.arguments(exercise),
                    cwd=exercise.workspace,
                    check=False,
                )
            except OSError as error:
                raise EditorNotFoundError(f"Не удалось запустить редактор: {error}") from error
            return exercise.outcome(result.returncode)

    def prepare(
        self,
        lesson: Lesson,
        *,
        layout: VimSessionLayout = VimSessionLayout.EMBEDDED_GUIDE,
    ) -> PreparedVimExercise:
        if not isinstance(layout, VimSessionLayout):
            raise TypeError("layout должен иметь тип VimSessionLayout")
        temporary_directory = tempfile.TemporaryDirectory(prefix="vim-trainer-")
        exercise = PreparedVimExercise(lesson, temporary_directory)
        try:
            self._prepare_files(exercise.workspace, lesson)
            if layout is VimSessionLayout.EMBEDDED_GUIDE:
                exercise.guide_path.write_text(self._build_guide(lesson), encoding="utf-8")
            exercise.session_path.write_text(
                self._build_session(
                    lesson,
                    exercise.workspace,
                    exercise.guide_path,
                    exercise.state_path,
                    layout=layout,
                ),
                encoding="utf-8",
            )
        except OSError as error:
            exercise.close()
            raise EditorExecutionError(
                f"Не удалось подготовить упражнение: {error}"
            ) from error
        except BaseException:
            exercise.close()
            raise
        return exercise

    def arguments(self, exercise: PreparedVimExercise) -> list[str]:
        arguments = [*self.command]
        if self._clean:
            arguments.extend(["-u", "NONE", "--noplugin", "-N"])
        arguments.extend(["-n", "-i", "NONE", "-S", str(exercise.session_path)])
        return arguments

    @staticmethod
    def _resolve_command(editor_command: str | Sequence[str] | None) -> tuple[str, ...]:
        configured: str | Sequence[str] | None = editor_command
        if configured is None:
            configured = os.environ.get("VIM_TRAINER_EDITOR")

        if isinstance(configured, str):
            parts = tuple(shlex.split(configured))
            if not parts:
                raise EditorNotFoundError("Пустая команда редактора")
            executable = shutil.which(parts[0])
            if executable is None:
                raise EditorNotFoundError(f"Редактор {parts[0]!r} не найден")
            return (executable, *parts[1:])

        if configured is not None:
            parts = tuple(configured)
            if not parts:
                raise EditorNotFoundError("Пустая команда редактора")
            executable = shutil.which(parts[0])
            if executable is None:
                raise EditorNotFoundError(f"Редактор {parts[0]!r} не найден")
            return (executable, *parts[1:])

        for candidate in ("nvim", "vim"):
            executable = shutil.which(candidate)
            if executable:
                return (executable,)
        raise EditorNotFoundError("Vim или Neovim не найден в PATH")

    @staticmethod
    def _prepare_files(workspace: Path, lesson: Lesson) -> None:
        for practice_file in lesson.files:
            destination = VimEditorGateway._workspace_path(workspace, practice_file.path)
            try:
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text(practice_file.initial, encoding="utf-8")
            except OSError as error:
                raise EditorExecutionError(
                    f"Не удалось создать {practice_file.path}: {error}"
                ) from error

    @staticmethod
    def _read_files(workspace: Path, lesson: Lesson) -> dict[str, str]:
        result: dict[str, str] = {}
        for practice_file in lesson.files:
            path = VimEditorGateway._workspace_path(workspace, practice_file.path)
            try:
                if path.is_file():
                    result[practice_file.path] = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError) as error:
                raise ExerciseReadError(
                    f"Не удалось прочитать {practice_file.path}: {error}"
                ) from error
        return result

    @staticmethod
    def _read_state(path: Path) -> dict[str, Any]:
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise ExerciseReadError(f"Редактор не вернул корректное состояние: {error}") from error
        if not isinstance(raw, dict):
            raise ExerciseReadError("Редактор вернул состояние неверного формата")
        return raw

    @staticmethod
    def _read_cursor(raw: Mapping[str, Any]) -> Cursor:
        line = raw.get("line")
        column = raw.get("column")
        if (
            isinstance(line, int)
            and not isinstance(line, bool)
            and isinstance(column, int)
            and not isinstance(column, bool)
            and line > 0
            and column > 0
        ):
            return Cursor(line, column)
        raise ExerciseReadError("Редактор вернул некорректную позицию курсора")

    @staticmethod
    def _read_registers(state: Mapping[str, Any]) -> dict[str, str]:
        registers = state.get("registers")
        if not isinstance(registers, dict) or not all(
            isinstance(key, str) and isinstance(value, str) for key, value in registers.items()
        ):
            raise ExerciseReadError("Редактор вернул некорректное состояние регистров")
        return {
            key: value
            for key, value in registers.items()
            if isinstance(key, str) and isinstance(value, str)
        }

    @staticmethod
    def _workspace_path(workspace: Path, relative_path: str) -> Path:
        root = workspace.resolve()
        candidate = (root / relative_path).resolve()
        if not candidate.is_relative_to(root):
            raise ExerciseReadError(f"Путь {relative_path!r} вышел за пределы упражнения")
        return candidate

    @staticmethod
    def _build_guide(lesson: Lesson) -> str:
        task = "\n".join(f"{index}. {item}" for index, item in enumerate(lesson.task, 1))
        commands = " · ".join(lesson.commands)
        return (
            f"{lesson.id} · {lesson.title}\n"
            f"ЦЕЛЬ  {lesson.goal}\n"
            f"ЗАДАЧА\n{task}\n\n"
            f"КОМАНДЫ  {commands}\n"
            f"ПОДСКАЗКА  {lesson.hint}\n\n"
            ":wqa — проверить · :TrainerCancel — отменить\n"
        )

    @classmethod
    def _build_session(
        cls,
        lesson: Lesson,
        workspace: Path,
        guide_path: Path,
        state_path: Path,
        *,
        layout: VimSessionLayout = VimSessionLayout.EMBEDDED_GUIDE,
    ) -> str:
        if not isinstance(layout, VimSessionLayout):
            raise TypeError("layout должен иметь тип VimSessionLayout")
        target_path = workspace / lesson.entrypoint
        register_names = [item.name for item in lesson.expected_registers]
        register_literal = json.dumps(register_names, ensure_ascii=True)
        cancel_path = state_path.with_name(".trainer-cancelled")
        statusline = cls._statusline(layout)
        layout_script = cls._layout_script(lesson, guide_path, layout)
        return f"""set encoding=utf-8
set nocompatible
set nomodeline
set noswapfile
set nobackup
set nowritebackup
set noundofile
set hidden
set number
set relativenumber
set cursorline
set splitbelow
set splitright
set backspace=indent,eol,start
set tabstop=4
set shiftwidth=4
set softtabstop=4
set expandtab
set incsearch
set hlsearch
set shortmess+=IF
set statusline={statusline}
silent! set t_RV=
silent! set t_u7=
silent! set t_RF=
silent! set t_RB=
silent! filetype plugin indent on
silent! syntax enable

let s:trainer_state_path = {cls._vim_quote(str(state_path))}
let s:trainer_cancel_path = {cls._vim_quote(str(cancel_path))}
let s:trainer_register_names = {register_literal}
let s:trainer_last_line = {lesson.start_cursor.line}
let s:trainer_last_column = {lesson.start_cursor.column}

silent execute 'edit ' . fnameescape({cls._vim_quote(str(target_path))})
let s:trainer_target_buffer = bufnr('%')
let s:trainer_target_window = win_getid()
let s:trainer_return_window = s:trainer_target_window
call cursor({lesson.start_cursor.line}, {lesson.start_cursor.column})
normal! zz

function! s:TrainerCaptureCursor() abort
  if bufnr('%') == s:trainer_target_buffer
    let s:trainer_last_line = line('.')
    let s:trainer_last_column = col('.')
  endif
endfunction

function! s:TrainerSaveState() abort
  call s:TrainerCaptureCursor()
  let l:registers = {{}}
  for l:name in s:trainer_register_names
    let l:registers[l:name] = getreg(l:name)
  endfor
  let l:state = {{
        \\ 'line': s:trainer_last_line,
        \\ 'column': s:trainer_last_column,
        \\ 'registers': l:registers
        \\ }}
  call writefile([json_encode(l:state)], s:trainer_state_path)
endfunction

function! s:TrainerCancel() abort
  call writefile(['cancelled'], s:trainer_cancel_path)
  cquit
endfunction

command! TrainerCancel call <SID>TrainerCancel()

augroup VimTrainer
  autocmd!
  autocmd CursorMoved,CursorMovedI,BufLeave * call <SID>TrainerCaptureCursor()
  autocmd VimLeavePre * call <SID>TrainerSaveState()
augroup END

{layout_script}
"""

    @staticmethod
    def _statusline(layout: VimSessionLayout) -> str:
        if layout is VimSessionLayout.EMBEDDED_GUIDE:
            return r"F1\ ·\ :wqa%<%=%t%m%r\ ·\ %l:%c\ [%p%%]"
        return r"%<%t%m%r%=%l:%c\ [%p%%]"

    @classmethod
    def _layout_script(
        cls,
        lesson: Lesson,
        guide_path: Path,
        layout: VimSessionLayout,
    ) -> str:
        if layout is VimSessionLayout.EDITOR_ONLY:
            return ""

        title = cls._vim_quote("F1 — задание · :wqa — готово · :TrainerCancel")
        return f"""if &columns >= 100
  let s:trainer_vertical_guide = 1
  silent execute 'botright 46vsplit ' . fnameescape({cls._vim_quote(str(guide_path))})
  setlocal winfixwidth
else
  let s:trainer_vertical_guide = 0
  silent execute 'topleft 13split ' . fnameescape({cls._vim_quote(str(guide_path))})
  setlocal winfixheight
endif
let s:trainer_guide_window = win_getid()
let s:trainer_guide_expanded = 0
setlocal readonly
setlocal nomodifiable
setlocal nobuflisted
setlocal nonumber
setlocal norelativenumber
setlocal nocursorline
setlocal wrap
setlocal linebreak
setlocal noswapfile
call matchadd('Title', '^.* · .*$')
call matchadd('Statement', '^ЗАДАЧА$')
call matchadd('Identifier', '^КОМАНДЫ')
call matchadd('Comment', '^ПОДСКАЗКА')
call matchadd('Special', '^F1 ')

function! s:TrainerToggleGuide() abort
  if s:trainer_guide_expanded
    call win_gotoid(s:trainer_guide_window)
    setlocal nowinfixwidth nowinfixheight
    if s:trainer_vertical_guide
      vertical resize 46
      setlocal winfixwidth
    else
      resize 13
      setlocal winfixheight
    endif
    if !win_gotoid(s:trainer_return_window)
      call win_gotoid(s:trainer_target_window)
    endif
    let s:trainer_guide_expanded = 0
    return
  endif
  let s:trainer_return_window = win_getid()
  call win_gotoid(s:trainer_guide_window)
  setlocal nowinfixwidth nowinfixheight
  if s:trainer_vertical_guide
    vertical resize
  else
    resize
  endif
  normal! gg
  let s:trainer_guide_expanded = 1
endfunction

nnoremap <silent> <F1> :call <SID>TrainerToggleGuide()<CR>
wincmd p
call cursor({lesson.start_cursor.line}, {lesson.start_cursor.column})
normal! zz
echohl ModeMsg
echo {title}
echohl None"""

    @staticmethod
    def _vim_quote(value: str) -> str:
        return "'" + value.replace("'", "''") + "'"
