from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from vim_trainer.domain.course import Course
from vim_trainer.domain.entities import Lesson, ObservedState, Progress, ValidationResult
from vim_trainer.domain.validation import validate_lesson

from .ports import EditOutcome, EditorGateway, ProgressRepository


class AttemptStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class AttemptResult:
    lesson: Lesson
    status: AttemptStatus
    validation: ValidationResult
    completed_count: int
    total_count: int


class TrainingService:
    def __init__(
        self,
        course: Course,
        editor: EditorGateway,
        progress_repository: ProgressRepository,
    ) -> None:
        self.course = course
        self._editor = editor
        self._progress_repository = progress_repository

    def progress(self) -> Progress:
        return self._progress_repository.load()

    def select_lesson(self, reference: str | None = None) -> Lesson:
        progress = self.progress()
        if reference is None:
            return self.course.next_lesson(progress.completed)
        return self.course.resolve(reference)

    def train(self, lesson: Lesson) -> AttemptResult:
        outcome = self._editor.edit(lesson)
        return self.complete_attempt(lesson, outcome)

    def complete_attempt(
        self,
        lesson: Lesson,
        outcome: EditOutcome | ObservedState,
    ) -> AttemptResult:
        """Validate an editor result and atomically persist exactly one attempt.

        Interactive adapters use this method after their editor session ends, so
        validation and progress persistence do not require opening another editor.
        """
        if isinstance(outcome, ObservedState):
            outcome = EditOutcome(outcome)
        if outcome.cancelled:
            progress = self.progress()
            return AttemptResult(
                lesson=lesson,
                status=AttemptStatus.CANCELLED,
                validation=ValidationResult(),
                completed_count=self._completed_count(progress),
                total_count=len(self.course),
            )

        validation = validate_lesson(lesson, outcome.observed)
        progress = self._progress_repository.record_attempt(lesson.id, validation.passed)
        return AttemptResult(
            lesson=lesson,
            status=AttemptStatus.PASSED if validation.passed else AttemptStatus.FAILED,
            validation=validation,
            completed_count=self._completed_count(progress),
            total_count=len(self.course),
        )

    def reset_progress(self) -> None:
        self._progress_repository.reset()

    def _completed_count(self, progress: Progress) -> int:
        course_ids = {lesson.id for lesson in self.course}
        return len(progress.completed.intersection(course_ids))
