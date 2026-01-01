"""Entry point for the Blossy CLI."""

from pathlib import Path
from typing import Annotated

import typer

from blossy.countc import CountCharactersUseCaseFactory
from blossy.countl import CountLinesUseCaseFactory
from blossy.perc import PercentageUseCaseFactory
from blossy.rand import RandomUseCaseFactory

from .command import (
    calculate,
    random_cmd,
    standardize,
)

app = typer.Typer(name="blossy", help="A lil' bud that helps you with stuff (it's a utility CLI).")

app.command("calc")(calculate.execute)


@app.command()
def countc(
    file: Annotated[Path, typer.Argument(show_default=False, help="Relative path to the file.")],
    ignore_unnec: Annotated[
        bool,
        typer.Option("--ignore-unnec", help="Ignore unnecessary (repeated) whitespace."),
    ] = False,
    ignore_ws: Annotated[bool, typer.Option("--ignore-ws", help="Ignore all whitespace.")] = False,
    full_msg: Annotated[bool, typer.Option(help="Show full message.")] = True,
):
    """
    COUNT CHARACTERS

    Count the amount of characters in a text file.
    """
    try:
        use_case = CountCharactersUseCaseFactory.get_use_case(ignore_unnec, ignore_ws, full_msg)
        use_case.execute(file)
    except FileNotFoundError as e:
        raise typer.BadParameter(f"'{file}' does not exist.") from e
    except IsADirectoryError as e:
        raise typer.BadParameter(f"'{file}' is not a file.") from e


@app.command()
def countl(
    file: Annotated[Path, typer.Argument(show_default=False, help="Relative path to the file.")],
    ignore_blank: Annotated[bool, typer.Option(help="Ignore all blank lines.")] = True,
    full_msg: Annotated[bool, typer.Option(help="Show full message.")] = True,
):
    """
    COUNT LINES

    Count the amount of lines in a code source file.
    """
    try:
        use_case = CountLinesUseCaseFactory.get_use_case(ignore_blank, full_msg)
        use_case.execute(file)
    except FileNotFoundError as e:
        raise typer.BadParameter(f"'{file}' does not exist.") from e
    except IsADirectoryError as e:
        raise typer.BadParameter(f"'{file}' is not a file.") from e


@app.command()
def perc(
    whole: Annotated[float | None, typer.Option("--whole", "-w", show_default=False)] = None,
    part: Annotated[float | None, typer.Option("--part", "-p", show_default=False)] = None,
    ratio: Annotated[float | None, typer.Option("--ratio", "-r", show_default=False)] = None,
    full_msg: Annotated[bool, typer.Option(help="Show full message.")] = True,
):
    """
    PERCENTAGE

    Take two of the three percentage-related options and calculate the remaining one.

    Example:\n
    $ blossy perc --whole 100 --part 25\n
    Ratio: 0.25
    """
    try:
        use_case = PercentageUseCaseFactory.get_use_case(full_msg)
        use_case.execute(whole, part, ratio)
    except typer.BadParameter as e:
        raise e


@app.command()
def rand(
    lower: Annotated[
        int,
        typer.Argument(show_default=False, help="Lower limit (inclusive)."),
    ],
    upper: Annotated[
        int,
        typer.Argument(show_default=False, help="Upper limit (inclusive)."),
    ],
    quantity: Annotated[
        int,
        typer.Option("--quantity", "-q", help="Quantity of random numbers to generate."),
    ] = 1,
):
    """
    RANDOM

    Generate a random number between 'lower' an 'upper'.
    """
    try:
        use_case = RandomUseCaseFactory.get_use_case()
        use_case.execute(lower, upper, quantity)
    except typer.BadParameter as e:
        raise e


app.command("stddz")(standardize.execute)
