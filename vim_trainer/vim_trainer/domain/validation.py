from __future__ import annotations

from difflib import unified_diff

from .entities import Lesson, ObservedState, ValidationIssue, ValidationResult


def validate_lesson(lesson: Lesson, observed: ObservedState) -> ValidationResult:
    issues: list[ValidationIssue] = []

    for practice_file in lesson.files:
        actual = observed.files.get(practice_file.path)
        if actual is None:
            issues.append(ValidationIssue(f"Файл {practice_file.path} удалён"))
            continue
        if actual != practice_file.expected:
            diff = unified_diff(
                practice_file.expected.splitlines(),
                actual.splitlines(),
                fromfile=f"ожидалось/{practice_file.path}",
                tofile=f"получилось/{practice_file.path}",
                lineterm="",
            )
            issues.append(
                ValidationIssue(
                    f"Содержимое {practice_file.path} пока не совпало",
                    tuple(diff),
                )
            )

    if lesson.expected_cursor is not None:
        if observed.cursor is None:
            issues.append(ValidationIssue("Не удалось получить позицию курсора"))
        elif observed.cursor != lesson.expected_cursor:
            expected = lesson.expected_cursor
            actual = observed.cursor
            issues.append(
                ValidationIssue(
                    "Курсор стоит не там",
                    (
                        f"ожидалось: строка {expected.line}, колонка {expected.column}",
                        f"сейчас:      строка {actual.line}, колонка {actual.column}",
                    ),
                )
            )

    for register in lesson.expected_registers:
        actual = observed.registers.get(register.name)
        if actual != register.value:
            issues.append(
                ValidationIssue(
                    f"Регистр {register.name!r} содержит другое значение",
                    (
                        f"ожидалось: {register.value!r}",
                        f"сейчас:      {actual!r}",
                    ),
                )
            )

    return ValidationResult(tuple(issues))
