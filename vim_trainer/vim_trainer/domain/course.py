from __future__ import annotations

from collections.abc import Collection, Iterator
from dataclasses import dataclass

from .entities import Lesson


class LessonNotFoundError(LookupError):
    pass


class CourseCompletedError(LookupError):
    pass


@dataclass(frozen=True)
class Course:
    lessons: tuple[Lesson, ...]

    def __post_init__(self) -> None:
        if not self.lessons:
            raise ValueError("A course must contain at least one lesson")
        identifiers = [lesson.id for lesson in self.lessons]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("Lesson ids must be unique")

    def __iter__(self) -> Iterator[Lesson]:
        return iter(self.lessons)

    def __len__(self) -> int:
        return len(self.lessons)

    def resolve(self, reference: str) -> Lesson:
        normalized = reference.strip().lower()
        if normalized.isdigit():
            index = int(normalized) - 1
            if 0 <= index < len(self.lessons):
                return self.lessons[index]

        exact = [lesson for lesson in self.lessons if lesson.id.lower() == normalized]
        if exact:
            return exact[0]

        prefix = [lesson for lesson in self.lessons if lesson.id.lower().startswith(normalized)]
        if len(prefix) == 1:
            return prefix[0]
        raise LessonNotFoundError(f"Урок {reference!r} не найден")

    def next_lesson(self, completed: Collection[str]) -> Lesson:
        for lesson in self.lessons:
            if lesson.id not in completed:
                return lesson
        raise CourseCompletedError("Курс уже завершён")

    def position(self, lesson: Lesson) -> int:
        return self.lessons.index(lesson) + 1

    def chapters(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(lesson.chapter for lesson in self.lessons))
