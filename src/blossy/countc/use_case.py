"""Module for COUNT CHARACTERS use cases."""

from pathlib import Path
from typing import Protocol


class CountCharactersUseCase(Protocol):
    """Protocol for a COUNT CHARACTERS use case."""

    def execute(self, file: Path) -> None:
        """Execute the use case."""
        ...


class CountCharactersUseCaseFactory:
    """Factory for creating COUNT CHARACTERS use cases."""

    @staticmethod
    def get_use_case(
        ignore_unnec: bool,
        ignore_ws: bool,
        full_msg: bool,
    ) -> CountCharactersUseCase:
        """Get an instance of the COUNT CHARACTERS use case based on the flags."""
        if ignore_unnec:
            return _CountCharactersUseCaseOption1(full_msg)
        if ignore_ws:
            return _CountCharactersUseCaseOption2(full_msg)

        return _CountCharactersUseCaseOption3(full_msg)


class _CountCharactersUseCaseOption1:
    """Use case for counting characters while ignoring unnecessary whitespace."""

    _full_msg: bool

    def __init__(self, full_msg: bool) -> None:
        self._full_msg = full_msg

    def execute(self, file: Path):
        """Execute the use case."""
        current_dir = Path.cwd()
        file_abs_path = current_dir / file

        with open(file_abs_path, "r", encoding="utf-8") as f:
            char_count = 0
            first_char = ""
            prev_char = ""
            while True:
                char = f.read(1)
                if not char:
                    break

                if not (char.isspace() and prev_char.isspace()):
                    char_count += 1

                if prev_char == "":
                    first_char = char
                prev_char = char

            last_char = prev_char
            if first_char.isspace():
                char_count -= 1
            if last_char.isspace():
                char_count -= 1

            print(f"Character count: {char_count}" if self._full_msg else char_count)


class _CountCharactersUseCaseOption2:
    """Use case for counting characters while ignoring all whitespace."""

    _full_msg: bool

    def __init__(self, full_msg: bool) -> None:
        self._full_msg = full_msg

    def execute(self, file: Path):
        """Execute the use case."""
        current_dir = Path.cwd()
        file_abs_path = current_dir / file

        with open(file_abs_path, "r", encoding="utf-8") as f:
            char_count = 0
            while True:
                char = f.read(1)
                if not char:
                    break

                if not char.isspace():
                    char_count += 1

            print(f"Character count: {char_count}" if self._full_msg else char_count)


class _CountCharactersUseCaseOption3:
    """Use case for counting characters while ignoring nothing."""

    _full_msg: bool

    def __init__(self, full_msg: bool) -> None:
        self._full_msg = full_msg

    def execute(self, file: Path):
        """Execute the use case."""
        current_dir = Path.cwd()
        file_abs_path = current_dir / file

        with open(file_abs_path, "r", encoding="utf-8") as f:
            char_count = 0
            while True:
                char = f.read(1)
                if not char:
                    break

                char_count += 1

            print(f"Character count: {char_count}" if self._full_msg else char_count)
