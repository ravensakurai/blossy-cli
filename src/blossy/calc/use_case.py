"""Module for CALCULATE use cases."""

import os
from collections.abc import Generator, Iterable
from typing import Protocol

from blossy.calc.model import Time, VisualCalcStep
from blossy.calc.service import ExpressionLexer, ExpressionParser, PostfixedExpressionParser


class CalculateUseCase(Protocol):
    """Use case for evaluate an expression."""

    def execute(self, expression: str) -> None:
        """Execute the use case."""
        ...


class CalculateUseCaseFactory:
    """Factory for creating CALCULATE use cases."""

    @staticmethod
    def get_use_case(
        lexer: ExpressionLexer,
        regular_parser: ExpressionParser,
        postfixed_parser: PostfixedExpressionParser,
        visualize: bool,
    ) -> CalculateUseCase:
        """Get an instance of the CALCULATE use case based on the flags."""
        if visualize:
            return _CalculateUseCaseOption1(lexer, postfixed_parser)
        return _CalculateUseCaseOption2(lexer, regular_parser)


class _CalculateUseCaseOption1:
    """Use case for evaluate an expression with visualization."""

    _lexer: ExpressionLexer
    _parser: PostfixedExpressionParser

    def __init__(self, lexer: ExpressionLexer, parser: PostfixedExpressionParser) -> None:
        self._lexer = lexer
        self._parser = parser

    def execute(self, expression: str) -> None:
        """Execute the use case."""
        token_generator = self._lexer.tokenize(expression)
        parser_response = self._parser.parse(token_generator)
        if not isinstance(parser_response, list):
            raise RuntimeError("Expected parser response to be a list of strings.")

        postfixed_expr = [str(token) for token in parser_response]

        for step in self._visualize_calc(postfixed_expr):
            if step.operation:
                print(f"> {step.operation}")
            if step.stack and step.input:
                print()
                self._print_with_padding(step.stack, step.input)
            input()

    def _visualize_calc(self, postfixed_expr: list[str]) -> Generator[VisualCalcStep, None, None]:
        ops = {
            "unary": ("+₁", "-₁"),
            "binary": ("+₂", "-₂", "*", "/", "^"),
        }
        state = {
            "stack": ["$"],
            "input": list(postfixed_expr) + ["$"],
        }

        yield VisualCalcStep(
            None, self._iter_to_str(state["stack"]), self._iter_to_str(state["input"])
        )

        while len(state["input"]) > 1:
            value = state["input"].pop(0)

            if value in ops["unary"]:
                operand = state["stack"].pop()
                operator = value
                result, operation = self._handle_unary(operator, operand)
                state["stack"].append(result)
            elif value in ops["binary"]:
                operand_2 = state["stack"].pop()
                operand_1 = state["stack"].pop()
                operator = value
                result, operation = self._handle_binary(operator, operand_1, operand_2)
                state["stack"].append(result)
            else:
                state["stack"].append(value)
                operation = f"Stack {value}"

            stack_str = self._iter_to_str(state["stack"])
            input_str = self._iter_to_str(state["input"])
            yield VisualCalcStep(operation, stack_str, input_str)

        final_result = state["stack"].pop()
        final_result = (
            self._to_time(final_result)
            if self._is_time(final_result)
            else self._to_num(final_result)
        )
        yield VisualCalcStep(f"The result is {final_result}", None, None)

    def _iter_to_str(self, iterable: Iterable[str]) -> str:
        return " ".join(iterable)

    def _is_time(self, value: str) -> bool:
        return ":" in value

    def _to_time(self, value: str) -> Time:
        parts = tuple(map(int, value.split(":")))
        if len(parts) == 3:
            return Time(hours=parts[-3], minutes=parts[-2], seconds=parts[-1])
        return Time(minutes=parts[-2], seconds=parts[-1])

    def _to_num(self, value: str) -> int | float:
        return float(value) if "." in value else int(value)

    def _handle_unary(self, operator: str, operand: str) -> tuple[str, str]:
        match operator:
            case "+₁":
                result = self._to_time(operand) if self._is_time(operand) else self._to_num(operand)
                operation = f"+{operand} = {result}"
            case "-₁":
                if self._is_time(operand):
                    result = Time() - self._to_time(operand)
                else:
                    result = 0 - self._to_num(operand)
                operation = f"-{operand} = {result}"
            case _:
                raise ValueError(f"unknown operator '{operator}'")

        return str(result), operation

    def _handle_binary(self, operator: str, operand_1: str, operand_2: str) -> tuple[str, str]:
        match operator:
            case "+₂":
                if self._is_time(operand_1) and self._is_time(operand_2):
                    result = self._to_time(operand_1) + self._to_time(operand_2)
                else:
                    result = self._to_num(operand_1) + self._to_num(operand_2)

                operation = f"{operand_1} + {operand_2} = {result}"
            case "-₂":
                if self._is_time(operand_1) and self._is_time(operand_2):
                    result = self._to_time(operand_1) - self._to_time(operand_2)
                else:
                    result = self._to_num(operand_1) - self._to_num(operand_2)

                operation = f"{operand_1} - {operand_2} = {result}"
            case "*":
                parsed_operand_1 = (
                    self._to_time(operand_1)
                    if self._is_time(operand_1)
                    else self._to_num(operand_1)
                )
                parsed_operand_2 = (
                    self._to_time(operand_2)
                    if self._is_time(operand_2)
                    else self._to_num(operand_2)
                )

                result = parsed_operand_1 * parsed_operand_2
                result = self._trim_time_or_num(result)
                operation = f"{operand_1} * {operand_2} = {result}"
            case "/":
                parsed_operand_1 = (
                    self._to_time(operand_1)
                    if self._is_time(operand_1)
                    else self._to_num(operand_1)
                )
                parsed_operand_2 = self._to_num(operand_2)

                result = parsed_operand_1 / parsed_operand_2
                result = self._trim_time_or_num(result)
                operation = f"{operand_1} / {operand_2} = {result}"
            case "^":
                result = self._to_num(operand_1) ** self._to_num(operand_2)
                result = self._trim_time_or_num(result)
                operation = f"{operand_1}^{operand_2} = {result}"
            case _:
                raise ValueError(f"unknown operator '{operator}'")

        return str(result), operation

    def _trim_time_or_num(self, value: Time | int | float) -> Time | int | float:
        if isinstance(value, Time):
            return value
        if isinstance(value, int):
            return value
        return int(value) if value.is_integer() else value

    def _print_with_padding(self, left_side: str, right_side: str) -> None:
        terminal_width = os.get_terminal_size().columns
        padding = terminal_width - len(left_side) - len(right_side)
        if padding > 0:
            print(left_side + " " * padding + right_side)
        else:
            print(left_side + " " * 2 + right_side)


class _CalculateUseCaseOption2:
    """Use case for evaluate an expression without visualization."""

    _lexer: ExpressionLexer
    _parser: ExpressionParser

    def __init__(self, lexer: ExpressionLexer, parser: ExpressionParser) -> None:
        self._lexer = lexer
        self._parser = parser

    def execute(self, expression: str) -> None:
        """Execute the use case."""
        token_generator = self._lexer.tokenize(expression)
        result = self._parser.parse(token_generator)
        if not isinstance(result, int) and not isinstance(result, float):
            raise RuntimeError("Expected parser response to be a number.")

        print(result)
