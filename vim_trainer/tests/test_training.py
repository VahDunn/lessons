from __future__ import annotations

import unittest

from vim_trainer.application.ports import EditOutcome
from vim_trainer.application.training import AttemptStatus, TrainingService
from vim_trainer.domain.course import Course
from vim_trainer.domain.entities import Lesson, ObservedState, PracticeFile, Progress

LESSON = Lesson(
    id="01-app",
    chapter="Тест",
    title="Use case",
    goal="Проверить сценарий",
    task=("Исправь",),
    commands=("cw",),
    hint="Исправь слово",
    files=(PracticeFile("task.txt", "bad\n", "good\n"),),
    entrypoint="task.txt",
)


class MemoryProgressRepository:
    def __init__(self) -> None:
        self.value = Progress()
        self.saved = 0

    def load(self) -> Progress:
        return Progress(set(self.value.completed), dict(self.value.attempts))

    def record_attempt(self, lesson_id: str, passed: bool) -> Progress:
        self.value.record_attempt(lesson_id, passed)
        self.saved += 1
        return self.load()

    def reset(self) -> Progress:
        self.value = Progress()
        self.saved += 1
        return self.load()


class FakeEditor:
    def __init__(self, outcome: EditOutcome) -> None:
        self.outcome = outcome
        self.calls = 0

    def edit(self, lesson: Lesson) -> EditOutcome:
        self.calls += 1
        return self.outcome


class TrainingServiceTests(unittest.TestCase):
    def test_success_marks_lesson_completed(self) -> None:
        repository = MemoryProgressRepository()
        editor = FakeEditor(EditOutcome(ObservedState({"task.txt": "good\n"})))
        service = TrainingService(Course((LESSON,)), editor, repository)

        result = service.train(LESSON)

        self.assertIs(result.status, AttemptStatus.PASSED)
        self.assertEqual(repository.value.completed, {LESSON.id})
        self.assertEqual(repository.value.attempts, {LESSON.id: 1})

    def test_failure_counts_attempt_without_completing(self) -> None:
        repository = MemoryProgressRepository()
        editor = FakeEditor(EditOutcome(ObservedState({"task.txt": "bad\n"})))
        service = TrainingService(Course((LESSON,)), editor, repository)

        result = service.train(LESSON)

        self.assertIs(result.status, AttemptStatus.FAILED)
        self.assertEqual(repository.value.completed, set())
        self.assertEqual(repository.value.attempts, {LESSON.id: 1})

    def test_cancel_does_not_touch_progress(self) -> None:
        repository = MemoryProgressRepository()
        editor = FakeEditor(EditOutcome(ObservedState({"task.txt": "bad\n"}), cancelled=True))
        service = TrainingService(Course((LESSON,)), editor, repository)

        result = service.train(LESSON)

        self.assertIs(result.status, AttemptStatus.CANCELLED)
        self.assertEqual(repository.saved, 0)

    def test_complete_attempt_accepts_observed_state_without_opening_editor(self) -> None:
        repository = MemoryProgressRepository()
        editor = FakeEditor(EditOutcome(ObservedState({"task.txt": "bad\n"})))
        service = TrainingService(Course((LESSON,)), editor, repository)

        result = service.complete_attempt(
            LESSON,
            ObservedState({"task.txt": "good\n"}),
        )

        self.assertIs(result.status, AttemptStatus.PASSED)
        self.assertEqual(repository.value.completed, {LESSON.id})
        self.assertEqual(repository.saved, 1)
        self.assertEqual(editor.calls, 0)
