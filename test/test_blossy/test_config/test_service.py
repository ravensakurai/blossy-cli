# pylint: disable=missing-module-docstring,missing-function-docstring,missing-class-docstring,redefined-outer-name

from typing import Any

import pytest

from blossy.config.service import ConfigGatekeeer


@pytest.fixture()
def gatekeeper() -> ConfigGatekeeer:
    return ConfigGatekeeer()


class TestConfigGatekeeerIsSubcommandSupported:
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
        self, gatekeeper: ConfigGatekeeer, subcommand: str, expected: bool
    ) -> None:
        assert gatekeeper.is_subcommand_supported(subcommand) == expected


class TestConfigGatekeeerIsKeySupported:
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
    def test_is_key_supported(self, gatekeeper: ConfigGatekeeer, key: str, expected: bool) -> None:
        assert gatekeeper.is_key_supported(key) == expected


class TestConfigGatekeeerIsValueTypeValid:
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
        self, gatekeeper: ConfigGatekeeer, key: str, value: Any, expected: bool
    ) -> None:
        assert gatekeeper.is_value_type_valid(key, value) == expected


class TestConfigGatekeeerGetInternalPropertyName:
    @pytest.mark.parametrize(
        "external_name,expected",
        [
            ("github-user", "github_user"),
            ("GITHUB-USER", "github_user"),
            ("Github-User", "github_user"),
        ],
    )
    def test_get_internal_property_name_success(
        self, gatekeeper: ConfigGatekeeer, external_name: str, expected: str | None
    ) -> None:
        assert gatekeeper.get_internal_property_name(external_name) == expected

    @pytest.mark.parametrize(
        "external_name",
        [
            "invalid-key",
            "",
        ],
    )
    def test_get_internal_property_name_not_found(
        self, gatekeeper: ConfigGatekeeer, external_name: str
    ) -> None:
        assert gatekeeper.get_internal_property_name(external_name) is None
