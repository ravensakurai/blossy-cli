"""Module for COUNT LINES use cases."""

import os
from pathlib import Path
from typing import Protocol


class CountLinesUseCase(Protocol):
    """Protocol for a COUNT LINES use case."""

    def execute(self, file: Path) -> None:
        """Execute the use case."""
        ...


class CountLinesUseCaseFactory:
    """Factory for creating COUNT LINES use cases."""

    @staticmethod
    def get_use_case(
        ignore_blank: bool,
        full_msg: bool,
    ) -> CountLinesUseCase:
        """Get an instance of the COUNT LINES use case based on the flags."""
        if ignore_blank:
            return CountLinesUseCaseOption1(full_msg)
        else:
            return CountLinesUseCaseOption2(full_msg)


class CountLinesUseCaseOption1:
    """Use case for counting lines while ignoring blank ones."""

    def __init__(self, full_msg: bool) -> None:
        self._full_msg = full_msg

    def execute(self, file: Path):
        current_dir = os.getcwd()
        file_abs_path = os.path.join(current_dir, file)

        with open(file_abs_path, "r", encoding="utf-8") as f:
            line_count = 0
            for line in f:
                if line.isspace() or len(line) == 0:
                    continue
                line_count += 1

            print(f"Line count: {line_count}" if self._full_msg else line_count)


class CountLinesUseCaseOption2:
    """Use case for counting lines while ignoring nothing."""

    def __init__(self, full_msg: bool) -> None:
        self._full_msg = full_msg

    def execute(self, file: Path):
        current_dir = os.getcwd()
        file_abs_path = os.path.join(current_dir, file)

        with open(file_abs_path, "r", encoding="utf-8") as f:
            line_count = 0
            for line in f:
                line_count += 1

            print(f"Line count: {line_count}" if self._full_msg else line_count)
