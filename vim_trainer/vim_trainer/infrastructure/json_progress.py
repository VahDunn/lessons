from __future__ import annotations

import json
import os
import tempfile
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any, BinaryIO

from vim_trainer.domain.entities import Progress

SCHEMA_VERSION = 1
_PATH_LOCKS: dict[Path, threading.RLock] = {}
_PATH_LOCKS_GUARD = threading.Lock()


class ProgressStorageError(RuntimeError):
    pass


def default_progress_path() -> Path:
    custom_dir = os.environ.get("VIM_TRAINER_DATA_DIR")
    if custom_dir:
        return Path(custom_dir).expanduser() / "progress.json"
    data_home = os.environ.get("XDG_DATA_HOME")
    root = Path(data_home).expanduser() if data_home else Path.home() / ".local" / "share"
    return root / "vim-trainer" / "progress.json"


class JsonProgressRepository:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or default_progress_path()

    def load(self) -> Progress:
        if not self.path.exists():
            return Progress()
        with self._locked(create_lock=False):
            return self._load_unlocked()

    def record_attempt(self, lesson_id: str, passed: bool) -> Progress:
        with self._locked():
            progress = self._load_unlocked()
            progress.record_attempt(lesson_id, passed)
            self._save_unlocked(progress)
            return progress

    def reset(self) -> Progress:
        with self._locked():
            progress = Progress()
            self._save_unlocked(progress)
            return progress

    def _load_unlocked(self) -> Progress:
        if not self.path.exists():
            return Progress()
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            return self._decode(raw)
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as error:
            raise ProgressStorageError(
                f"Не удалось прочитать прогресс из {self.path}: {error}"
            ) from error

    def _save_unlocked(self, progress: Progress) -> None:
        payload = {
            "version": SCHEMA_VERSION,
            "completed": sorted(progress.completed),
            "attempts": dict(sorted(progress.attempts.items())),
        }
        temporary_path: Path | None = None
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.path.parent,
                prefix=".progress-",
                suffix=".tmp",
                delete=False,
            ) as stream:
                json.dump(payload, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
                temporary_path = Path(stream.name)
            os.replace(temporary_path, self.path)
        except OSError as error:
            if temporary_path is not None:
                try:
                    temporary_path.unlink(missing_ok=True)
                except OSError:
                    pass
            raise ProgressStorageError(
                f"Не удалось сохранить прогресс в {self.path}: {error}"
            ) from error

    @contextmanager
    def _locked(self, *, create_lock: bool = True) -> Iterator[None]:
        lock_key = self.path.resolve(strict=False)
        with _PATH_LOCKS_GUARD:
            thread_lock = _PATH_LOCKS.setdefault(lock_key, threading.RLock())

        with thread_lock:
            lock_path = Path(f"{self.path}.lock")
            if create_lock:
                try:
                    self.path.parent.mkdir(parents=True, exist_ok=True)
                    lock_stream = lock_path.open("a+b")
                except OSError as error:
                    raise ProgressStorageError(
                        f"Не удалось заблокировать прогресс в {self.path}: {error}"
                    ) from error
            else:
                try:
                    lock_stream = lock_path.open("rb")
                except FileNotFoundError:
                    yield
                    return
                except OSError as error:
                    raise ProgressStorageError(
                        f"Не удалось прочитать прогресс из {self.path}: {error}"
                    ) from error

            try:
                with lock_stream:
                    _lock_file(lock_stream)
                    try:
                        yield
                    finally:
                        try:
                            _unlock_file(lock_stream)
                        except OSError:
                            pass
            except OSError as error:
                action = "обновить" if create_lock else "прочитать"
                raise ProgressStorageError(
                    f"Не удалось {action} прогресс в {self.path}: {error}"
                ) from error

    @staticmethod
    def _decode(raw: Any) -> Progress:
        if not isinstance(raw, dict) or raw.get("version") != SCHEMA_VERSION:
            raise ValueError("неподдерживаемый формат файла")
        completed = raw.get("completed")
        attempts = raw.get("attempts")
        if not isinstance(completed, list) or not all(isinstance(item, str) for item in completed):
            raise ValueError("поле completed повреждено")
        if not isinstance(attempts, dict) or not all(
            isinstance(key, str)
            and isinstance(value, int)
            and not isinstance(value, bool)
            and value >= 0
            for key, value in attempts.items()
        ):
            raise ValueError("поле attempts повреждено")
        return Progress(completed=set(completed), attempts=dict(attempts))


def _lock_file(stream: BinaryIO) -> None:
    if os.name == "posix":
        import fcntl

        fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        return
    if os.name == "nt":
        import msvcrt

        if os.fstat(stream.fileno()).st_size == 0:
            stream.write(b"\0")
            stream.flush()
        stream.seek(0)
        msvcrt.locking(stream.fileno(), msvcrt.LK_LOCK, 1)


def _unlock_file(stream: BinaryIO) -> None:
    if os.name == "posix":
        import fcntl

        fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
        return
    if os.name == "nt":
        import msvcrt

        stream.seek(0)
        msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
