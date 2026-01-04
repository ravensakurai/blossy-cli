# pylint: disable=missing-module-docstring,missing-function-docstring,missing-class-docstring,redefined-outer-name

from typing import Any

import pytest

from blossy.config.service import ConfigValidator


@pytest.fixture()
def validator() -> ConfigValidator:
    return ConfigValidator()


class TestConfigValidatorIsSubcommandSupported:
    @pytest.mark.parametrize(
        "subcommand,expected",
        [
            ("clone", True),
            ("CLONE", True),
            ("Clone", True),
            ("invalid", False),
            ("", False),
        ],
    )
    def test_is_subcommand_supported(
        self, validator: ConfigValidator, subcommand: str, expected: bool
    ) -> None:
        assert validator.is_subcommand_supported(subcommand) == expected


class TestConfigValidatorIsKeySupported:
    @pytest.mark.parametrize(
        "key,expected",
        [
            ("github-user", True),
            ("GITHUB-USER", True),
            ("Github-User", True),
            ("invalid-key", False),
            ("", False),
        ],
    )
    def test_is_key_supported(self, validator: ConfigValidator, key: str, expected: bool) -> None:
        assert validator.is_key_supported(key) == expected


class TestConfigValidatorIsValueTypeValid:
    @pytest.mark.parametrize(
        "key,value,expected",
        [
            ("github-user", "ravensakurai", True),
            ("GITHUB-USER", "ravensakurai", True),
            ("github-user", 123, False),
            ("github-user", True, False),
            ("github-user", 1.5, False),
            ("invalid-key", "value", False),
            ("", "value", False),
        ],
    )
    def test_is_value_type_valid(
        self, validator: ConfigValidator, key: str, value: Any, expected: bool
    ) -> None:
        assert validator.is_value_type_valid(key, value) == expected
