# pylint: disable=missing-module-docstring,missing-function-docstring,missing-class-docstring,redefined-outer-name

from typing import Any

import pytest

from blossy.config.use_case import ConfigureUseCase, ConfigureUseCaseFactory
from blossy.shared.error import ConfigError
from blossy.shared.repository import TomlValue


class MockConfigValidator:
    is_subcommand_supported_calls: list[str]
    is_key_supported_calls: list[str]
    is_value_type_valid_calls: list[tuple[str, Any]]

    is_subcommand_supported_outputs: list[bool]
    is_key_supported_outputs: list[bool]
    is_value_type_valid_outputs: list[bool]

    def __init__(self) -> None:
        self.is_subcommand_supported_outputs = []
        self.is_key_supported_outputs = []
        self.is_value_type_valid_outputs = []

        self.is_subcommand_supported_calls = []
        self.is_key_supported_calls = []
        self.is_value_type_valid_calls = []

    def is_subcommand_supported(self, subcommand: str) -> bool:
        self.is_subcommand_supported_calls.append(subcommand)
        return self.is_subcommand_supported_outputs.pop(0)

    def is_key_supported(self, key: str) -> bool:
        self.is_key_supported_calls.append(key)
        return self.is_key_supported_outputs.pop(0)

    def is_value_type_valid(self, key: str, value: Any) -> bool:
        self.is_value_type_valid_calls.append((key, value))
        return self.is_value_type_valid_outputs.pop(0)


class MockConfigRepository:
    set_property_calls: list[tuple[str, str, TomlValue]]

    def __init__(self) -> None:
        self.set_property_calls = []

    def set_property(self, subcommand: str, property_name: str, value: TomlValue) -> None:
        self.set_property_calls.append((subcommand, property_name, value))


@pytest.fixture()
def config_validator() -> MockConfigValidator:
    return MockConfigValidator()


@pytest.fixture()
def config_repository() -> MockConfigRepository:
    return MockConfigRepository()


@pytest.fixture()
def use_case(
    config_validator: MockConfigValidator,
    config_repository: MockConfigRepository,
) -> ConfigureUseCase:
    return ConfigureUseCaseFactory.get_use_case(config_validator, config_repository)


class TestConfigureUseCase:
    def test_execute_valid_configuration(
        self,
        use_case: ConfigureUseCase,
        config_validator: MockConfigValidator,
        config_repository: MockConfigRepository,
    ) -> None:
        config_validator.is_subcommand_supported_outputs = [True]
        config_validator.is_key_supported_outputs = [True]
        config_validator.is_value_type_valid_outputs = [True]

        use_case.execute("clone", "github-user", "octocat")

        assert config_validator.is_subcommand_supported_calls == ["clone"]
        assert config_validator.is_key_supported_calls == ["github-user"]
        assert config_validator.is_value_type_valid_calls == [("github-user", "octocat")]
        assert config_repository.set_property_calls == [("clone", "github-user", "octocat")]

    def test_execute_unsupported_subcommand(
        self,
        use_case: ConfigureUseCase,
        config_validator: MockConfigValidator,
        config_repository: MockConfigRepository,
    ) -> None:
        config_validator.is_subcommand_supported_outputs = [False]

        with pytest.raises(ConfigError):
            use_case.execute("invalid", "github-user", "octocat")

        assert not config_repository.set_property_calls

    def test_execute_unsupported_key(
        self,
        use_case: ConfigureUseCase,
        config_validator: MockConfigValidator,
        config_repository: MockConfigRepository,
    ) -> None:
        config_validator.is_subcommand_supported_outputs = [True]
        config_validator.is_key_supported_outputs = [False]

        with pytest.raises(ConfigError):
            use_case.execute("clone", "invalid-key", "octocat")

        assert not config_repository.set_property_calls

    def test_execute_invalid_value_type(
        self,
        use_case: ConfigureUseCase,
        config_validator: MockConfigValidator,
        config_repository: MockConfigRepository,
    ) -> None:
        config_validator.is_subcommand_supported_outputs = [True]
        config_validator.is_key_supported_outputs = [True]
        config_validator.is_value_type_valid_outputs = [False]

        with pytest.raises(ConfigError):
            use_case.execute("clone", "github-user", 123)

        assert not config_repository.set_property_calls
