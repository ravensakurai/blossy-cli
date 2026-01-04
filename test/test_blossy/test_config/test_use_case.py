# pylint: disable=missing-module-docstring,missing-function-docstring,missing-class-docstring,redefined-outer-name

from typing import Any

import pytest

from blossy.config.use_case import ConfigurateUseCase, ConfigurateUseCaseFactory
from blossy.shared.error import ConfigError, InternalError
from blossy.shared.repository import TomlValue


class MockConfigGatekeeer:
    is_subcommand_supported_calls: list[str]
    is_key_supported_calls: list[str]
    is_value_type_valid_calls: list[tuple[str, Any]]
    get_internal_property_name_calls: list[str]

    _is_subcommand_supported_outputs: list[bool]
    _is_key_supported_outputs: list[bool]
    _is_value_type_valid_outputs: list[bool]
    _get_internal_property_name_outputs: list[str | None]

    def __init__(
        self,
        is_subcommand_supported_calls: list[str],
        is_key_supported_calls: list[str],
        is_value_type_valid_calls: list[tuple[str, Any]],
        get_internal_property_name_calls: list[str],
    ) -> None:
        self.is_subcommand_supported_calls = is_subcommand_supported_calls
        self.is_key_supported_calls = is_key_supported_calls
        self.is_value_type_valid_calls = is_value_type_valid_calls
        self.get_internal_property_name_calls = get_internal_property_name_calls

        self._is_subcommand_supported_outputs = []
        self._is_key_supported_outputs = []
        self._is_value_type_valid_outputs = []
        self._get_internal_property_name_outputs = []

    def is_subcommand_supported(self, subcommand: str) -> bool:
        self.is_subcommand_supported_calls.append(subcommand)
        return self._is_subcommand_supported_outputs.pop(0)

    def is_key_supported(self, key: str) -> bool:
        self.is_key_supported_calls.append(key)
        return self._is_key_supported_outputs.pop(0)

    def is_value_type_valid(self, key: str, value: Any) -> bool:
        self.is_value_type_valid_calls.append((key, value))
        return self._is_value_type_valid_outputs.pop(0)

    def get_internal_property_name(self, external_property_name: str) -> str | None:
        self.get_internal_property_name_calls.append(external_property_name)
        return self._get_internal_property_name_outputs.pop(0)


class MockConfigRepository:
    set_property_calls: list[tuple[str, str, TomlValue]]

    def __init__(self, set_property_calls: list[tuple[str, str, TomlValue]]) -> None:
        self.set_property_calls = set_property_calls

    def set_property(self, subcommand: str, property_name: str, value: TomlValue) -> None:
        self.set_property_calls.append((subcommand, property_name, value))


@pytest.fixture()
def config_gatekeeer() -> MockConfigGatekeeer:
    return MockConfigGatekeeer(
        is_subcommand_supported_calls=[],
        is_key_supported_calls=[],
        is_value_type_valid_calls=[],
        get_internal_property_name_calls=[],
    )


@pytest.fixture()
def config_repository() -> MockConfigRepository:
    return MockConfigRepository(set_property_calls=[])


@pytest.fixture()
def use_case(
    config_gatekeeer: MockConfigGatekeeer,
    config_repository: MockConfigRepository,
) -> ConfigurateUseCase:
    return ConfigurateUseCaseFactory.get_use_case(config_gatekeeer, config_repository)


class TestConfigurateUseCase:
    def test_execute_valid_configuration(
        self,
        monkeypatch,
        use_case: ConfigurateUseCase,
        config_gatekeeer: MockConfigGatekeeer,
        config_repository: MockConfigRepository,
    ) -> None:
        monkeypatch.setattr(config_gatekeeer, "_is_subcommand_supported_outputs", [True])
        monkeypatch.setattr(config_gatekeeer, "_is_key_supported_outputs", [True])
        monkeypatch.setattr(config_gatekeeer, "_is_value_type_valid_outputs", [True])
        monkeypatch.setattr(
            config_gatekeeer, "_get_internal_property_name_outputs", ["github_user"]
        )

        use_case.execute("clone", "github-user", "octocat")

        assert config_gatekeeer.is_subcommand_supported_calls == ["clone"]
        assert config_gatekeeer.is_key_supported_calls == ["github-user"]
        assert config_gatekeeer.is_value_type_valid_calls == [("github-user", "octocat")]
        assert config_gatekeeer.get_internal_property_name_calls == ["github-user"]
        assert config_repository.set_property_calls == [("clone", "github_user", "octocat")]

    def test_execute_unsupported_subcommand(
        self,
        monkeypatch,
        use_case: ConfigurateUseCase,
        config_gatekeeer: MockConfigGatekeeer,
        config_repository: MockConfigRepository,
    ) -> None:
        monkeypatch.setattr(config_gatekeeer, "_is_subcommand_supported_outputs", [False])

        with pytest.raises(ConfigError):
            use_case.execute("invalid", "github-user", "octocat")

        assert not config_repository.set_property_calls

    def test_execute_unsupported_key(
        self,
        monkeypatch,
        use_case: ConfigurateUseCase,
        config_gatekeeer: MockConfigGatekeeer,
        config_repository: MockConfigRepository,
    ) -> None:
        monkeypatch.setattr(config_gatekeeer, "_is_subcommand_supported_outputs", [True])
        monkeypatch.setattr(config_gatekeeer, "_is_key_supported_outputs", [False])

        with pytest.raises(ConfigError):
            use_case.execute("clone", "invalid-key", "octocat")

        assert not config_repository.set_property_calls

    def test_execute_invalid_value_type(
        self,
        monkeypatch,
        use_case: ConfigurateUseCase,
        config_gatekeeer: MockConfigGatekeeer,
        config_repository: MockConfigRepository,
    ) -> None:
        monkeypatch.setattr(config_gatekeeer, "_is_subcommand_supported_outputs", [True])
        monkeypatch.setattr(config_gatekeeer, "_is_key_supported_outputs", [True])
        monkeypatch.setattr(config_gatekeeer, "_is_value_type_valid_outputs", [False])

        with pytest.raises(ConfigError):
            use_case.execute("clone", "github-user", 123)

        assert not config_repository.set_property_calls

    def test_execute_internal_name_not_found(
        self,
        monkeypatch,
        use_case: ConfigurateUseCase,
        config_gatekeeer: MockConfigGatekeeer,
        config_repository: MockConfigRepository,
    ) -> None:
        monkeypatch.setattr(config_gatekeeer, "_is_subcommand_supported_outputs", [True])
        monkeypatch.setattr(config_gatekeeer, "_is_key_supported_outputs", [True])
        monkeypatch.setattr(config_gatekeeer, "_is_value_type_valid_outputs", [True])
        monkeypatch.setattr(config_gatekeeer, "_get_internal_property_name_outputs", [None])

        with pytest.raises(InternalError):
            use_case.execute("clone", "github-user", "octocat")

        assert not config_repository.set_property_calls
