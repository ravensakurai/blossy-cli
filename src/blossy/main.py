"""Entry point for the Blossy CLI."""

from pathlib import Path
from typing import Annotated

import typer

from blossy.countc.use_case import CountCharactersUseCaseFactory

from .command import (
    calculate,
    count_lines,
    percentage,
    random_cmd,
    standardize,
)

app = typer.Typer(name="blossy", help="A lil' bud that helps you with stuff (it's a utility CLI).")

app.command("calc")(calculate.execute)


@app.command("countc")
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


app.command("countl")(count_lines.execute)
app.command("perc")(percentage.execute)
app.command("rand")(random_cmd.execute)
app.command("stddz")(standardize.execute)
