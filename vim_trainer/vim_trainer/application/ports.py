from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from vim_trainer.domain.entities import Lesson, ObservedState, Progress


@dataclass(frozen=True)
class EditOutcome:
    observed: ObservedState
    cancelled: bool = False


class EditorGateway(Protocol):
    def edit(self, lesson: Lesson) -> EditOutcome:
        """Open a disposable exercise and return its final observable state."""


class InteractiveEditorSession(Protocol):
    """A running editor whose terminal can be transported by any presentation layer.

    The session owns the editor process and its disposable workspace. ``wait``
    returns the final exercise state and releases those resources. ``close`` is
    idempotent and must be called when a consumer stops before ``wait`` finishes.
    """

    @property
    def running(self) -> bool:
        """Whether the editor process is still running."""

    def read(self, max_bytes: int = 65536, timeout: float | None = 0.0) -> bytes:
        """Read terminal output, waiting at most ``timeout`` seconds.

        An empty byte string means that no output is available. Consumers can
        distinguish a quiet terminal from EOF using ``running``.
        """

    def write(self, data: bytes) -> None:
        """Send raw terminal input to the editor."""

    def resize(self, rows: int, columns: int) -> None:
        """Resize the terminal using positive row and column counts."""

    def wait(self, timeout: float | None = None) -> EditOutcome:
        """Wait for completion and return its cached outcome.

        Raises ``TimeoutError`` when the process is still running after a finite
        timeout. Calling it again after completion returns the same outcome.
        """

    def cancel(self) -> None:
        """Cancel the exercise, terminate the editor, and release resources."""

    def close(self) -> None:
        """Release resources, cancelling a running exercise if necessary."""


class InteractiveEditorGateway(Protocol):
    def open(
        self,
        lesson: Lesson,
        *,
        rows: int = 24,
        columns: int = 80,
    ) -> InteractiveEditorSession:
        """Start a disposable exercise in an interactive terminal."""


class ProgressRepository(Protocol):
    def load(self) -> Progress:
        """Load the current course progress."""

    def record_attempt(self, lesson_id: str, passed: bool) -> Progress:
        """Atomically record one attempt and return the persisted snapshot."""

    def reset(self) -> Progress:
        """Atomically replace progress with an empty snapshot."""
