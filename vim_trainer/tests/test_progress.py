from __future__ import annotations

import json
import multiprocessing
import os
import tempfile
import threading
import unittest
from pathlib import Path

from vim_trainer.domain.entities import Progress
from vim_trainer.infrastructure.json_progress import (
    JsonProgressRepository,
    ProgressStorageError,
)


def _record_attempt_in_process(path: str, start_event) -> None:
    start_event.wait(timeout=5)
    JsonProgressRepository(Path(path)).record_attempt("01-test", passed=True)


class JsonProgressRepositoryTests(unittest.TestCase):
    def test_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "progress.json"
            repository = JsonProgressRepository(path)
            expected = Progress({"01-test"}, {"01-test": 2})

            repository.record_attempt("01-test", passed=True)
            repository.record_attempt("01-test", passed=True)

            self.assertEqual(repository.load(), expected)
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["version"], 1)

    def test_missing_file_means_empty_progress(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = JsonProgressRepository(Path(directory) / "progress.json")

            self.assertEqual(repository.load(), Progress())

    @unittest.skipIf(os.name == "nt", "POSIX directory permissions only")
    def test_load_does_not_require_directory_write_access(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = JsonProgressRepository(root / "progress.json")
            repository.record_attempt("01-test", passed=True)
            root.chmod(0o500)
            try:
                self.assertEqual(
                    repository.load(),
                    Progress({"01-test"}, {"01-test": 1}),
                )
            finally:
                root.chmod(0o700)

    def test_corrupt_file_is_not_silently_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "progress.json"
            path.write_text("not json", encoding="utf-8")

            with self.assertRaises(ProgressStorageError):
                JsonProgressRepository(path).load()

    def test_directory_creation_error_is_wrapped(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            blocking_file = Path(directory) / "not-a-directory"
            blocking_file.write_text("block", encoding="utf-8")
            repository = JsonProgressRepository(blocking_file / "progress.json")

            with self.assertRaises(ProgressStorageError):
                repository.reset()

    def test_record_attempt_is_atomic_across_repository_instances(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "progress.json"
            workers = 12
            barrier = threading.Barrier(workers)

            def record() -> None:
                barrier.wait()
                JsonProgressRepository(path).record_attempt("01-test", passed=True)

            threads = [threading.Thread(target=record) for _ in range(workers)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join(timeout=5)

            self.assertFalse(any(thread.is_alive() for thread in threads))
            self.assertEqual(
                JsonProgressRepository(path).load(),
                Progress({"01-test"}, {"01-test": workers}),
            )

    def test_record_attempt_is_atomic_across_processes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "progress.json"
            workers = 8
            context = multiprocessing.get_context("spawn")
            start_event = context.Event()
            processes = [
                context.Process(
                    target=_record_attempt_in_process,
                    args=(str(path), start_event),
                )
                for _ in range(workers)
            ]

            for process in processes:
                process.start()
            start_event.set()
            for process in processes:
                process.join(timeout=10)
            for process in processes:
                if process.is_alive():
                    process.terminate()
                    process.join(timeout=2)

            self.assertEqual([process.exitcode for process in processes], [0] * workers)
            self.assertEqual(
                JsonProgressRepository(path).load(),
                Progress({"01-test"}, {"01-test": workers}),
            )

    def test_reset_replaces_progress_under_the_same_lock(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = JsonProgressRepository(Path(directory) / "progress.json")
            repository.record_attempt("01-test", passed=True)

            snapshot = repository.reset()

            self.assertEqual(snapshot, Progress())
            self.assertEqual(repository.load(), Progress())
