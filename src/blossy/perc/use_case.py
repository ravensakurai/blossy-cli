"""Module for PERCENTAGE use cases."""

from typing import Protocol

import typer


class PercentageUseCase(Protocol):
    """Use case for calculating percentages."""

    def execute(self, whole: float | None, part: float | None, ratio: float | None) -> None:
        """Execute the use case."""
        ...


class PercentageUseCaseFactory:
    """Factory for creating PERCENTAGE use cases."""

    @staticmethod
    def get_use_case(
        full_msg: bool,
    ) -> PercentageUseCase:
        """Get an instance of the PERCENTAGE use case based on the flags."""
        return PercentageUseCaseOption1(full_msg)


class PercentageUseCaseOption1:
    """Use case for calculating percentages."""

    def __init__(self, full_msg: bool) -> None:
        self._full_msg = full_msg

    def execute(self, whole: float | None, part: float | None, ratio: float | None) -> None:
        if whole is not None and part is not None:
            if whole == 0:
                raise typer.BadParameter("Result does not exist.")
            ratio = part / whole
            print(f"Ratio: {ratio}" if self._full_msg else ratio)

        elif whole is not None and ratio is not None:
            part = whole * ratio
            print(f"Part: {part}" if self._full_msg else part)

        elif part is not None and ratio is not None:
            if ratio == 0:
                raise typer.BadParameter("Result does not exist.")
            whole = part / ratio
            print(f"Whole: {whole}" if self._full_msg else whole)

        else:
            raise typer.BadParameter("Less than two parameters passed.")
