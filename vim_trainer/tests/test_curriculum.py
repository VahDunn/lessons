from __future__ import annotations

import unittest

from vim_trainer.curriculum import DEFAULT_COURSE
from vim_trainer.domain.entities import ObservedState
from vim_trainer.domain.validation import validate_lesson


class CurriculumTests(unittest.TestCase):
    def test_course_is_comprehensive_and_ordered(self) -> None:
        self.assertEqual(len(DEFAULT_COURSE), 51)
        self.assertGreaterEqual(len(DEFAULT_COURSE.chapters()), 6)
        numbers = [int(lesson.id[:2]) for lesson in DEFAULT_COURSE]
        self.assertEqual(numbers, list(range(len(DEFAULT_COURSE))))

    def test_advanced_tracks_end_with_the_final_project(self) -> None:
        advanced = tuple(DEFAULT_COURSE)[36:]
        self.assertEqual(
            [lesson.chapter for lesson in advanced],
            [
                "Объекты текста и поиск",
                "Объекты текста и поиск",
                "Объекты текста и поиск",
                "Рефакторинг кода",
                "Рефакторинг кода",
                "Рефакторинг кода",
                "Состояние и автоматизация",
                "Состояние и автоматизация",
                "Состояние и автоматизация",
                "Работа с проектом",
                "Работа с проектом",
                "Работа с проектом",
                "Работа с проектом",
                "Работа с проектом",
                "Итог",
            ],
        )
        self.assertEqual(advanced[-1].id, "50-final-project")
        self.assertEqual(DEFAULT_COURSE.resolve("35-final-python").chapter, "Проектная практика")

    def test_every_exercise_starts_unsolved(self) -> None:
        for lesson in DEFAULT_COURSE:
            with self.subTest(lesson=lesson.id):
                initial = {item.path: item.initial for item in lesson.files}
                observed = ObservedState(
                    files=initial,
                    cursor=lesson.start_cursor,
                    registers={item.name: "" for item in lesson.expected_registers},
                )
                self.assertFalse(validate_lesson(lesson, observed).passed)

    def test_declared_solution_always_passes(self) -> None:
        for lesson in DEFAULT_COURSE:
            with self.subTest(lesson=lesson.id):
                expected = {item.path: item.expected for item in lesson.files}
                registers = {item.name: item.value for item in lesson.expected_registers}
                observed = ObservedState(
                    files=expected,
                    cursor=lesson.expected_cursor or lesson.start_cursor,
                    registers=registers,
                )
                self.assertTrue(validate_lesson(lesson, observed).passed)

    def test_all_fixtures_are_text_files_with_final_newline(self) -> None:
        for lesson in DEFAULT_COURSE:
            for practice_file in lesson.files:
                with self.subTest(lesson=lesson.id, path=practice_file.path):
                    self.assertTrue(practice_file.initial.endswith("\n"))
                    self.assertTrue(practice_file.expected.endswith("\n"))

    def test_final_project_python_files_are_syntactically_valid(self) -> None:
        lesson = DEFAULT_COURSE.resolve("50-final-project")
        for practice_file in lesson.files:
            if not practice_file.path.endswith(".py"):
                continue
            with self.subTest(path=practice_file.path):
                compile(practice_file.expected, practice_file.path, "exec")
