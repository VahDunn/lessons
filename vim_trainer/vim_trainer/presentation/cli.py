from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from vim_trainer import __version__
from vim_trainer.application.catalog import CourseCatalogService
from vim_trainer.application.training import AttemptStatus, TrainingService
from vim_trainer.curriculum import DEFAULT_COURSE
from vim_trainer.domain.course import CourseCompletedError, LessonNotFoundError
from vim_trainer.infrastructure.json_progress import (
    JsonProgressRepository,
    ProgressStorageError,
)
from vim_trainer.infrastructure.vim_editor import EditorError, VimEditorGateway
from vim_trainer.infrastructure.vim_pty import VimPtyGateway

from .console import Console
from .web import WebServerError, serve_web

DEFAULT_WEB_PORT = 8765


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vim-trainer",
        description="Практический курс по Vim в настоящем редакторе.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--editor",
        help="команда Vim/Neovim (также VIM_TRAINER_EDITOR)",
    )
    parser.add_argument(
        "--user-config",
        action="store_true",
        help="загрузить пользовательский vimrc и плагины",
    )
    subparsers = parser.add_subparsers(dest="command")

    start = subparsers.add_parser("start", help="начать или продолжить курс")
    start.add_argument("lesson", nargs="?", help="номер или id урока")
    start.add_argument(
        "--once",
        action="store_true",
        help="завершить CLI после одной попытки",
    )

    subparsers.add_parser("list", help="показать карту курса")
    subparsers.add_parser("status", help="показать прогресс")

    reset = subparsers.add_parser("reset", help="сбросить прогресс")
    reset.add_argument("--yes", action="store_true", help="не запрашивать подтверждение")

    subparsers.add_parser("doctor", help="проверить окружение")

    web = subparsers.add_parser("web", help="открыть web-интерфейс")
    web.add_argument(
        "--port",
        type=_port,
        default=DEFAULT_WEB_PORT,
        help=f"локальный порт (по умолчанию {DEFAULT_WEB_PORT})",
    )
    web.add_argument(
        "--no-open",
        action="store_true",
        help="не открывать браузер автоматически",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    arguments = parser.parse_args(argv)
    console = Console()

    try:
        editor = VimEditorGateway(arguments.editor, clean=not arguments.user_config)
        repository = JsonProgressRepository()
        service = TrainingService(DEFAULT_COURSE, editor, repository)
        catalog = CourseCatalogService(DEFAULT_COURSE, repository)

        command = arguments.command or "web"
        if command == "start":
            return _run_training(
                service,
                console,
                getattr(arguments, "lesson", None),
                once=getattr(arguments, "once", False),
            )
        if command == "list":
            return _show_course(catalog, console)
        if command == "status":
            return _show_status(catalog, console)
        if command == "reset":
            return _reset_progress(service, console, arguments.yes)
        if command == "doctor":
            return _doctor(service, editor, repository.path, console, arguments.user_config)
        if command == "web":
            terminal_editor = VimPtyGateway(
                arguments.editor,
                clean=not arguments.user_config,
            )
            serve_web(
                service,
                catalog,
                terminal_editor,
                editor_probe=lambda: terminal_editor.info().version,
                host="127.0.0.1",
                port=getattr(arguments, "port", DEFAULT_WEB_PORT),
                open_browser=not getattr(arguments, "no_open", False),
            )
            return 0
        parser.error(f"неизвестная команда: {command}")
    except (EditorError, ProgressStorageError, LessonNotFoundError, WebServerError) as error:
        console.failure(str(error))
        return 2
    except CourseCompletedError:
        console.success(f"Курс завершён: {len(DEFAULT_COURSE)}/{len(DEFAULT_COURSE)}")
        return 0
    except (KeyboardInterrupt, EOFError):
        console.write()
        console.muted("Остановлено.")
        return 130
    return 0


def _port(value: str) -> int:
    try:
        port = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("порт должен быть целым числом") from error
    if not 0 <= port <= 65535:
        raise argparse.ArgumentTypeError("порт должен быть от 0 до 65535")
    return port


def _run_training(
    service: TrainingService,
    console: Console,
    reference: str | None,
    *,
    once: bool,
) -> int:
    while True:
        lesson = service.select_lesson(reference)
        position = service.course.position(lesson)
        console.heading(f"VIM TRAINER  {position:02d}/{len(service.course):02d}  ·  {lesson.title}")
        console.write(lesson.goal)
        console.muted("Открываю одноразовую копию упражнения. Репозиторий не изменится.")

        result = service.train(lesson)
        if result.status is AttemptStatus.CANCELLED:
            console.muted("Попытка отменена. Прогресс не изменён.")
            return 0

        if result.status is AttemptStatus.PASSED:
            meter = _format_progress(result.completed_count, result.total_count, width=18)
            console.success(f"Урок пройден  {meter}")
            if result.completed_count < result.total_count:
                next_lesson = service.course.next_lesson(service.progress().completed)
                console.muted(f"> Дальше: {next_lesson.id} · {next_lesson.title}")
            if once or not console.interactive:
                return 0
            if result.completed_count == result.total_count:
                console.success("Курс завершён.")
                return 0
            answer = console.prompt("Enter — дальше · r — повторить · q — выйти > ").strip().lower()
            if answer == "q":
                return 0
            reference = lesson.id if answer == "r" else None
            console.write()
            continue

        console.failure("Результат пока не совпал")
        _show_validation(result.validation.issues, console)
        if once or not console.interactive:
            return 1
        answer = console.prompt("Enter — повторить · q — выйти > ").strip().lower()
        if answer == "q":
            return 1
        reference = lesson.id
        console.write()


def _show_validation(issues: tuple, console: Console) -> None:
    for issue in issues:
        console.write(f"  {issue.message}")
        detail_limit = 14
        for line in issue.details[:detail_limit]:
            console.muted(f"    {line}")
        if len(issue.details) > detail_limit:
            console.muted(f"    … ещё {len(issue.details) - detail_limit} строк")


def _show_course(catalog: CourseCatalogService, console: Console) -> int:
    overview = catalog.overview()
    console.heading("VIM TRAINER · КАРТА КУРСА")
    for chapter in overview.chapters:
        console.write()
        bar = _progress_bar(chapter.completed, chapter.total, width=10)
        console.write(f"{chapter.name:<24} [{bar}] {chapter.completed}/{chapter.total}")
        for lesson in chapter.lessons:
            marker = "✓" if lesson.completed else ">" if lesson.current else "·"
            suffix = f"  ({lesson.attempts} попыт.)" if lesson.attempts else ""
            console.write(
                f"  {marker} {lesson.position:02d}  " f"{lesson.id:<24} {lesson.title}{suffix}"
            )
    return 0


def _show_status(catalog: CourseCatalogService, console: Console) -> int:
    overview = catalog.overview()
    console.heading("VIM TRAINER · ПРОГРЕСС")
    console.write(_format_progress(overview.completed, overview.total, width=24))
    console.write(f"Попыток: {overview.attempts}")

    console.write()
    console.muted("ПО ГЛАВАМ")
    for chapter in overview.chapters:
        bar = _progress_bar(chapter.completed, chapter.total, width=10)
        console.write(f"  {chapter.name:<22} [{bar}] {chapter.completed:>2}/{chapter.total}")

    next_lesson = next(
        (lesson for chapter in overview.chapters for lesson in chapter.lessons if lesson.current),
        None,
    )
    if next_lesson is not None:
        console.write()
        console.write(f"> Дальше: {next_lesson.id} · {next_lesson.title}")
    else:
        console.success("Курс завершён")
    return 0


def _progress_bar(completed: int, total: int, *, width: int) -> str:
    if total <= 0 or width <= 0:
        raise ValueError("Progress dimensions must be positive")
    bounded = min(max(completed, 0), total)
    filled = round(width * bounded / total)
    return "█" * filled + "·" * (width - filled)


def _format_progress(completed: int, total: int, *, width: int) -> str:
    bar = _progress_bar(completed, total, width=width)
    bounded = min(max(completed, 0), total)
    percentage = round(100 * bounded / total)
    return f"[{bar}] {bounded}/{total} · {percentage}%"


def _reset_progress(service: TrainingService, console: Console, confirmed: bool) -> int:
    if not confirmed:
        if not console.interactive:
            console.failure("Для сброса без TTY добавьте --yes")
            return 2
        answer = console.prompt("Удалить весь прогресс? [y/N] ").strip().lower()
        if answer not in {"y", "yes", "д", "да"}:
            console.muted("Без изменений.")
            return 0
    service.reset_progress()
    console.success("Прогресс сброшен")
    return 0


def _doctor(
    service: TrainingService,
    editor: VimEditorGateway,
    progress_path: Path,
    console: Console,
    user_config: bool,
) -> int:
    info = editor.info()
    progress = service.progress()
    completed = len(progress.completed.intersection({item.id for item in service.course}))
    console.heading("VIM TRAINER · DOCTOR")
    console.success(f"Python {sys.version.split()[0]}")
    console.success(info.version)
    console.write(f"Команда: {' '.join(info.command)}")
    console.write(f"Режим: {'пользовательский vimrc' if user_config else 'чистая конфигурация'}")
    console.write(f"Курс: {len(service.course)} уроков, пройдено {completed}")
    console.write(f"Прогресс: {progress_path}")
    return 0
