"""Entry point for the Blossy CLI."""

from pathlib import Path
from typing import Annotated

import tomlkit
import typer

from blossy.calc.service import ExpressionLexer, ExpressionParser
from blossy.calc.use_case import CalculateUseCaseFactory, PostfixedExpressionParser
from blossy.config.service import ConfigGatekeeper
from blossy.config.use_case import ConfigurateUseCaseFactory
from blossy.countc.use_case import CountCharactersUseCaseFactory
from blossy.countl.use_case import CountLinesUseCaseFactory
from blossy.perc.use_case import PercentageUseCaseFactory
from blossy.rand.use_case import RandomUseCaseFactory
from blossy.shared.adapter import FileAdapter
from blossy.shared.error import ConfigError
from blossy.shared.model import SUPPORTED_CONFIG_TYPES, TomlValue
from blossy.shared.repository import ConfigRepository
from blossy.stddz.use_case import StandardizeUseCaseFactory

# pylint: disable=broad-exception-caught

app = typer.Typer(name="blossy", help="A lil' bud that helps you with stuff (it's a utility CLI).")


@app.command()
def calc(
    expression: Annotated[
        str, typer.Argument(show_default=False, help="Expression to be calculated.")
    ],
    visualize: Annotated[
        bool,
        typer.Option(
            "--visualize",
            "-v",
            help="Show a visualization using postfix notation and a stack.",
        ),
    ] = False,
):
    """
    CALCULATE

    Calculate the value of a mathematical expression involving numbers and time.

    Number syntax:\n
    • Integers: 123\n
    • Decimals: 12.34\n

    Time syntax:\n
    • 43:21 (43 minutes, 21 seconds)\n
    • 65:43:21 (65 hours, 43 minutes, 21 seconds)\n

    Available operations:\n
    • (expr) - Grouping\n
    • +expr - Unary plus\n
    • -expr - Unary minus\n
    • expr ^ expr - Exponentiation\n
    • expr * expr - Multiplication\n
    • expr / expr - Division\n
    • expr + expr - Addition\n
    • expr - expr - Subtraction\n

    Operation rules for time:\n
    • Time + Time = Time\n
    • Time - Time = Time\n
    • Time * Number = Time\n
    • Number * Time = Time\n
    • Time / Number = Time\n
    """
    try:
        lexer = ExpressionLexer()
        regular_parser = ExpressionParser()
        postfixed_parser = PostfixedExpressionParser()
        use_case = CalculateUseCaseFactory.get_use_case(
            lexer, regular_parser, postfixed_parser, visualize
        )
        use_case.execute(expression)
    except Exception as e:
        raise typer.BadParameter(str(e)) from e
    typer.echo()


@app.command()
def config(
    subcommand: Annotated[str, typer.Argument(help="Subcommand to configure.")],
    key: Annotated[
        str,
        typer.Argument(help="Configuration key to set."),
    ],
    value: Annotated[
        str,
        typer.Argument(help="Value to assign to the configuration key."),
    ],
):
    """
    CONFIGURATE

    Set a configuration value for a specific subcommand.
    """

    try:
        file_adapter = FileAdapter()
        gatekeeper = ConfigGatekeeper()
        repository = ConfigRepository(file_adapter)
        use_case = ConfigurateUseCaseFactory.get_use_case(gatekeeper, repository)

        parsed_value = _parse_value(value)
        use_case.execute(subcommand, key, parsed_value)
    except ConfigError as e:
        raise typer.BadParameter(str(e)) from e


def _parse_value(value: str) -> TomlValue:
    try:
        parsed = tomlkit.parse(f"value = {value}")
        toml_item = parsed["value"]
        unwrapped = toml_item.unwrap()
        return unwrapped if isinstance(unwrapped, tuple(SUPPORTED_CONFIG_TYPES)) else value
    except Exception:  # pylint: disable=broad-exception-caught
        return value


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

    Generate a random number between 'lower' and 'upper'.
    """
    try:
        use_case = RandomUseCaseFactory.get_use_case()
        use_case.execute(lower, upper, quantity)
    except typer.BadParameter as e:
        raise e


@app.command()
def stddz(
    prefix: Annotated[str, typer.Argument(show_default=False, help="Prefix of the files.")],
    directory: Annotated[
        Path, typer.Argument(show_default=False, help="Relative path to the directory.")
    ],
    start_idx: Annotated[
        int, typer.Option("--start", "-s", help="Starting number for the IDs.")
    ] = 0,
    qt_digits: Annotated[
        int,
        typer.Option("--digits", "-d", help="Quantity of digits used to represent the ID."),
    ] = 3,
) -> None:
    """
    STANDARDIZE

    Rename all files in a DIRECTORY to '{PREFIX}-{ID}', in which the ID is
    calculated incrementally.
    """
    try:
        use_case = StandardizeUseCaseFactory.get_use_case()
        use_case.execute(prefix, directory, start_idx, qt_digits)
    except FileNotFoundError as e:
        raise typer.BadParameter(f"'{directory}' does not exist.") from e
    except NotADirectoryError as e:
        raise typer.BadParameter(f"'{directory}' is not a directory.") from e
