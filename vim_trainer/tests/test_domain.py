from __future__ import annotations

import unittest

from vim_trainer.domain.course import Course, LessonNotFoundError
from vim_trainer.domain.entities import (
    Cursor,
    Lesson,
    ObservedState,
    PracticeFile,
    RegisterExpectation,
)
from vim_trainer.domain.validation import validate_lesson


def make_lesson(**overrides: object) -> Lesson:
    values = {
        "id": "01-test",
        "chapter": "Тест",
        "title": "Проверка",
        "goal": "Проверить модель",
        "task": ("Измени файл",),
        "commands": ("i — вставка",),
        "hint": "Короткая подсказка",
        "files": (PracticeFile("task.txt", "bad\n", "good\n"),),
        "entrypoint": "task.txt",
    }
    values.update(overrides)
    return Lesson(**values)  # type: ignore[arg-type]


class PracticeFileTests(unittest.TestCase):
    def test_rejects_paths_outside_workspace(self) -> None:
        for path in (
            "../secret",
            "/etc/passwd",
            "nested\\file.txt",
            "C:/outside.txt",
            ".trainer-state.json",
        ):
            with self.subTest(path=path), self.assertRaises(ValueError):
                PracticeFile(path, "", "")


class LessonTests(unittest.TestCase):
    def test_rejects_cursor_outside_entry_file(self) -> None:
        with self.assertRaises(ValueError):
            make_lesson(start_cursor=Cursor(20, 1))

    def test_rejects_exercise_without_observable_goal(self) -> None:
        unchanged = PracticeFile("task.txt", "same\n", "same\n")
        with self.assertRaises(ValueError):
            make_lesson(files=(unchanged,))


class CourseTests(unittest.TestCase):
    def test_resolves_by_position_id_and_unique_prefix(self) -> None:
        first = make_lesson()
        second = make_lesson(id="02-other", title="Второй")
        course = Course((first, second))

        self.assertIs(course.resolve("1"), first)
        self.assertIs(course.resolve("02-other"), second)
        self.assertIs(course.resolve("02-o"), second)

    def test_unknown_reference_is_rejected(self) -> None:
        with self.assertRaises(LessonNotFoundError):
            Course((make_lesson(),)).resolve("missing")


class ValidationTests(unittest.TestCase):
    def test_checks_files_cursor_and_registers_together(self) -> None:
        lesson = make_lesson(
            expected_cursor=Cursor(1, 3),
            expected_registers=(RegisterExpectation("a", "saved\n"),),
        )
        observed = ObservedState(
            files={"task.txt": "good\n"},
            cursor=Cursor(1, 3),
            registers={"a": "saved\n"},
        )

        self.assertTrue(validate_lesson(lesson, observed).passed)

    def test_returns_readable_diff_for_wrong_text(self) -> None:
        lesson = make_lesson()

        result = validate_lesson(
            lesson,
            ObservedState(files={"task.txt": "almost\n"}),
        )

        self.assertFalse(result.passed)
        self.assertIn("task.txt", result.issues[0].message)
        self.assertTrue(any("-good" in line for line in result.issues[0].details))
