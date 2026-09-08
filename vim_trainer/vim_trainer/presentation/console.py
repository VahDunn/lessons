from __future__ import annotations

import os
import sys
from typing import TextIO


class Console:
    def __init__(self, output: TextIO | None = None) -> None:
        self.output = output or sys.stdout
        self.color = self.output.isatty() and "NO_COLOR" not in os.environ

    @property
    def interactive(self) -> bool:
        return sys.stdin.isatty() and self.output.isatty()

    def write(self, text: str = "") -> None:
        print(text, file=self.output)

    def heading(self, text: str) -> None:
        self.write(self._paint(text, "1;36"))

    def success(self, text: str) -> None:
        self.write(self._paint(f"✓ {text}", "1;32"))

    def failure(self, text: str) -> None:
        self.write(self._paint(f"✗ {text}", "1;31"))

    def muted(self, text: str) -> None:
        self.write(self._paint(text, "2"))

    def prompt(self, text: str) -> str:
        return input(self._paint(text, "1"))

    def _paint(self, text: str, code: str) -> str:
        return f"\033[{code}m{text}\033[0m" if self.color else text
