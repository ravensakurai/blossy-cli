"""Module for RANDOM use cases."""

import random
from typing import Protocol

import typer


class RandomUseCase(Protocol):
    """Use case for generating random numbers."""

    def execute(self, lower: int, upper: int, quantity: int = 1) -> None:
        """Execute the use case."""
        ...


class RandomUseCaseFactory:
    """Factory for creating RANDOM use cases."""

    @staticmethod
    def get_use_case() -> RandomUseCase:
        """Get an instance of the RANDOM use case based on the flags."""
        return RandomUseCaseOption1()


class RandomUseCaseOption1:
    """Use case for generating random numbers."""

    def execute(self, lower: int, upper: int, quantity: int = 1) -> None:
        if lower > upper:
            raise typer.BadParameter("Invalid range.")

        for i in range(quantity):
            number = random.randint(lower, upper)
            end_char = " " if i < (quantity - 1) else "\n"
            print(number, end=end_char)
