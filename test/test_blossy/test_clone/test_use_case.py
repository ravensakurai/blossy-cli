# pylint: disable=missing-module-docstring,missing-function-docstring,missing-class-docstring,redefined-outer-name

import pytest

from blossy.clone.use_case import CloneUseCase, CloneUseCaseFactory
from blossy.shared.error import ConfigError
from blossy.shared.repository import TomlValue


class MockConfigRepository:
    get_property_calls: list[tuple[str, str]]

    get_property_outputs: list[TomlValue | None]

    def __init__(self) -> None:
        self.get_property_calls = []
        self.get_property_outputs = []

    def get_property(self, subcommand: str, property_name: str) -> TomlValue | None:
        self.get_property_calls.append((subcommand, property_name))
        return self.get_property_outputs.pop(0)

    def set_property(self, subcommand: str, property_name: str, value: TomlValue) -> None:
        """Set a property value for a subcommand."""
        raise NotImplementedError()


class MockSubprocessAdapter:
    calls: list[tuple[str, ...]]

    def __init__(self) -> None:
        self.calls = []

    def run(self, *args: str) -> None:
        self.calls.append(args)


@pytest.fixture()
def config_repository() -> MockConfigRepository:
    return MockConfigRepository()


@pytest.fixture()
def subprocess_adapter() -> MockSubprocessAdapter:
    return MockSubprocessAdapter()


@pytest.fixture()
def use_case(
    config_repository: MockConfigRepository, subprocess_adapter: MockSubprocessAdapter
) -> CloneUseCase:
    return CloneUseCaseFactory.get_use_case(config_repository, subprocess_adapter)


class TestCloneUseCase:
    def test_execute_uses_ssh_prefix(
        self,
        use_case: CloneUseCase,
        config_repository: MockConfigRepository,
        subprocess_adapter: MockSubprocessAdapter,
    ) -> None:
        config_repository.get_property_outputs = ["ravensakurai"]

        use_case.execute(["blossy-cli", "harmonics-api"], use_https=False)

        assert config_repository.get_property_calls == [("clone", "github-user")]
        assert subprocess_adapter.calls == [
            ("git", "clone", "git@github.com:ravensakurai/blossy-cli.git"),
            ("git", "clone", "git@github.com:ravensakurai/harmonics-api.git"),
        ]

    def test_execute_uses_https_prefix(
        self,
        use_case: CloneUseCase,
        config_repository: MockConfigRepository,
        subprocess_adapter: MockSubprocessAdapter,
    ) -> None:
        config_repository.get_property_outputs = ["ravensakurai"]

        use_case.execute(["blossy-cli"], use_https=True)

        assert subprocess_adapter.calls == [
            ("git", "clone", "https://github.com:ravensakurai/blossy-cli.git"),
        ]

    def test_execute_missing_user_raises(
        self,
        use_case: CloneUseCase,
        config_repository: MockConfigRepository,
        subprocess_adapter: MockSubprocessAdapter,
    ) -> None:
        config_repository.get_property_outputs = [None]

        with pytest.raises(ConfigError):
            use_case.execute(["blossy-cli"], use_https=False)

        assert not subprocess_adapter.calls

    def test_execute_non_string_user_raises(
        self,
        use_case: CloneUseCase,
        config_repository: MockConfigRepository,
        subprocess_adapter: MockSubprocessAdapter,
    ) -> None:
        config_repository.get_property_outputs = [123]

        with pytest.raises(ConfigError):
            use_case.execute(["blossy-cli"], use_https=False)

        assert not subprocess_adapter.calls
