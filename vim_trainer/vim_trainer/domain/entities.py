from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import PurePosixPath, PureWindowsPath


@dataclass(frozen=True)
class Cursor:
    line: int
    column: int

    def __post_init__(self) -> None:
        if self.line < 1 or self.column < 1:
            raise ValueError("Cursor coordinates are one-based positive integers")


@dataclass(frozen=True)
class PracticeFile:
    path: str
    initial: str
    expected: str

    def __post_init__(self) -> None:
        candidate = PurePosixPath(self.path)
        if candidate.is_absolute() or ".." in candidate.parts or candidate.name == "":
            raise ValueError(f"Unsafe practice file path: {self.path!r}")
        if "\\" in self.path:
            raise ValueError("Practice file paths must use forward slashes")
        if PureWindowsPath(self.path).drive:
            raise ValueError(f"Drive-qualified practice file path: {self.path!r}")
        if candidate.parts[0].startswith(".trainer-"):
            raise ValueError(f"Reserved practice file path: {self.path!r}")


@dataclass(frozen=True)
class RegisterExpectation:
    name: str
    value: str

    def __post_init__(self) -> None:
        if len(self.name) != 1:
            raise ValueError("A Vim register name must be one character")


@dataclass(frozen=True)
class Lesson:
    id: str
    chapter: str
    title: str
    goal: str
    task: tuple[str, ...]
    commands: tuple[str, ...]
    hint: str
    files: tuple[PracticeFile, ...]
    entrypoint: str
    start_cursor: Cursor = Cursor(1, 1)
    expected_cursor: Cursor | None = None
    expected_registers: tuple[RegisterExpectation, ...] = ()

    def __post_init__(self) -> None:
        if not self.id or not self.id[0:2].isdigit():
            raise ValueError(f"Lesson id must start with a number: {self.id!r}")
        if not self.task or not self.commands or not self.files:
            raise ValueError(f"Lesson {self.id!r} is incomplete")
        paths = [item.path for item in self.files]
        if len(paths) != len(set(paths)):
            raise ValueError(f"Lesson {self.id!r} contains duplicate paths")
        if self.entrypoint not in paths:
            raise ValueError(f"Entrypoint {self.entrypoint!r} is not a practice file")
        register_names = [item.name for item in self.expected_registers]
        if len(register_names) != len(set(register_names)):
            raise ValueError(f"Lesson {self.id!r} contains duplicate register goals")

        entry_file = next(item for item in self.files if item.path == self.entrypoint)
        self._ensure_cursor_fits(self.start_cursor, entry_file.initial, "start")
        if self.expected_cursor is not None:
            self._ensure_cursor_fits(self.expected_cursor, entry_file.expected, "expected")

        file_changes = any(item.initial != item.expected for item in self.files)
        cursor_changes = (
            self.expected_cursor is not None and self.expected_cursor != self.start_cursor
        )
        if not file_changes and not cursor_changes and not self.expected_registers:
            raise ValueError(f"Lesson {self.id!r} has no observable goal")

    def _ensure_cursor_fits(self, cursor: Cursor, text: str, label: str) -> None:
        lines = text.splitlines() or [""]
        if cursor.line > len(lines):
            raise ValueError(f"Lesson {self.id!r} {label} cursor is below the file")
        maximum_column = max(1, len(lines[cursor.line - 1]))
        if cursor.column > maximum_column:
            raise ValueError(f"Lesson {self.id!r} {label} cursor is past end of line")


@dataclass(frozen=True)
class ObservedState:
    files: Mapping[str, str]
    cursor: Cursor | None = None
    registers: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ValidationIssue:
    message: str
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ValidationResult:
    issues: tuple[ValidationIssue, ...] = ()

    @property
    def passed(self) -> bool:
        return not self.issues


@dataclass
class Progress:
    completed: set[str] = field(default_factory=set)
    attempts: dict[str, int] = field(default_factory=dict)

    def record_attempt(self, lesson_id: str, passed: bool) -> None:
        self.attempts[lesson_id] = self.attempts.get(lesson_id, 0) + 1
        if passed:
            self.completed.add(lesson_id)

    def reset(self) -> None:
        self.completed.clear()
        self.attempts.clear()
