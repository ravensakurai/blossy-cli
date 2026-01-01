"""Module for STANDARDIZE use cases."""

from collections.abc import Iterable
from pathlib import Path
from random import choices
from string import ascii_letters
from typing import Protocol

import typer


class StandardizeUseCase(Protocol):
    """Use case for standardizing file names."""

    def execute(
        self,
        prefix: str,
        directory: Path,
        start_idx: int = 0,
        qt_digits: int = 3,
    ) -> None:
        """Execute the use case."""
        ...


class StandardizeUseCaseFactory:
    """Factory for creating STANDARDIZE use cases."""

    @staticmethod
    def get_use_case() -> StandardizeUseCase:
        """Get an instance of the STANDARDIZE use case."""
        return StandardizeUseCaseOption1()


class StandardizeUseCaseOption1:
    """Use case for standardizing file names."""

    def execute(
        self,
        prefix: str,
        directory: Path,
        start_idx: int = 0,
        qt_digits: int = 3,
    ) -> None:
        if start_idx < 0:
            raise typer.BadParameter("Negative starting number.")

        dir_abs_path = directory.expanduser().resolve()

        try:
            files = self._get_files(dir_abs_path)

            last_id = start_idx + len(files) - 1
            min_qt_digits = len(str(last_id))
            if min_qt_digits > qt_digits:
                qt_digits = min_qt_digits
                qt_reajusted = True
            else:
                qt_reajusted = False

            # to prevent overriding previous files
            temp_prefix = "".join(choices(ascii_letters, k=10))
            self._rename(dir_abs_path, files, temp_prefix, qt_digits, start_idx)

            files = self._get_files(dir_abs_path)
            self._rename(dir_abs_path, files, prefix, qt_digits, start_idx)

            if qt_reajusted:
                print("Quantity of digits had to be reajusted.")
        except FileNotFoundError as e:
            raise typer.BadParameter(f"'{dir_abs_path}' does not exist.") from e
        except NotADirectoryError as e:
            raise typer.BadParameter(f"'{dir_abs_path}' is not a directory.") from e

    def _get_files(self, directory_path: Path) -> tuple[Path, ...]:
        files = []
        for item in directory_path.iterdir():
            if item.is_file():
                files.append(item)
        return tuple(files)

    def _rename(
        self, dir_path: Path, files: Iterable[Path], prefix: str, qt_digits: int, start_idx: int
    ) -> None:
        idx = start_idx
        for file_path in files:
            ext = file_path.suffix
            new_file = self._build_file_name(prefix, idx, qt_digits) + ext
            file_path.rename(dir_path / new_file)

            idx += 1

    def _build_file_name(self, prefix: str, index: int, qt_digits: int) -> str:
        num_str = f"{index:0{qt_digits}}"
        return f"{prefix}-{num_str}"
