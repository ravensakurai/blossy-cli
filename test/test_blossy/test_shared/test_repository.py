# pylint: disable=missing-module-docstring,missing-function-docstring,missing-class-docstring,redefined-outer-name

from pathlib import Path

import pytest

from blossy.shared.model import TomlValue
from blossy.shared.repository import ConfigRepository

FILE_1 = """[clone]
github-user = "ravensakurai"
"""

FILE_2 = """[clone]
github-user = "ravensakurai"
new-key = "value"
"""

FILE_3 = """[clone]
github-user = "monkeydluffy"
"""


class MockFileAdapter:
    create_if_not_exists_calls: list[Path]
    read_text_calls: list[Path]
    write_text_calls: list[tuple[Path, str]]

    _read_text_outputs: list[str]

    def __init__(
        self,
        create_if_not_exists_calls: list[Path],
        read_text_calls: list[Path],
        write_text_calls: list[tuple[Path, str]],
    ) -> None:
        self.create_if_not_exists_calls = create_if_not_exists_calls
        self.read_text_calls = read_text_calls
        self.write_text_calls = write_text_calls

        self._read_text_outputs = []

    def create_if_not_exists(self, path: Path) -> None:
        self.create_if_not_exists_calls.append(path)

    def read_text(self, path: Path) -> str:
        self.read_text_calls.append(path)
        return self._read_text_outputs.pop(0)

    def write_text(self, path: Path, content: str) -> None:
        self.write_text_calls.append((path, content))


@pytest.fixture()
def file_adapter() -> MockFileAdapter:
    return MockFileAdapter(
        create_if_not_exists_calls=[],
        read_text_calls=[],
        write_text_calls=[],
    )


@pytest.fixture()
def repository(file_adapter: MockFileAdapter) -> ConfigRepository:
    return ConfigRepository(file_adapter)


class TestGetProperty:
    def test_get_property_existing_key(
        self, monkeypatch, repository: ConfigRepository, file_adapter: MockFileAdapter
    ) -> None:
        monkeypatch.setattr(
            file_adapter,
            "_read_text_outputs",
            [FILE_1],
        )

        result = repository.get_property("clone", "github-user")

        assert result == "ravensakurai"
        assert len(file_adapter.read_text_calls) == 1

    def test_get_property_missing_subcommand(
        self, monkeypatch, repository: ConfigRepository, file_adapter: MockFileAdapter
    ) -> None:
        monkeypatch.setattr(
            file_adapter,
            "_read_text_outputs",
            [FILE_1],
        )

        result = repository.get_property("invalid", "github-user")

        assert result is None
        assert len(file_adapter.read_text_calls) == 1

    def test_get_property_missing_key(
        self, monkeypatch, repository: ConfigRepository, file_adapter: MockFileAdapter
    ) -> None:
        monkeypatch.setattr(
            file_adapter,
            "_read_text_outputs",
            [FILE_1],
        )

        result = repository.get_property("clone", "invalid_key")

        assert result is None
        assert len(file_adapter.read_text_calls) == 1

    def test_get_property_empty_config(
        self, monkeypatch, repository: ConfigRepository, file_adapter: MockFileAdapter
    ) -> None:
        monkeypatch.setattr(file_adapter, "_read_text_outputs", [""])

        result = repository.get_property("clone", "github-user")

        assert result is None
        assert len(file_adapter.read_text_calls) == 1


class TestSetProperty:
    def test_set_property_new_subcommand_and_key(
        self, monkeypatch, repository: ConfigRepository, file_adapter: MockFileAdapter
    ) -> None:
        monkeypatch.setattr(file_adapter, "_read_text_outputs", [""])

        repository.set_property("clone", "github-user", "ravensakurai")

        assert len(file_adapter.read_text_calls) == 1
        assert len(file_adapter.write_text_calls) == 1

        _, written_content = file_adapter.write_text_calls[0]
        assert written_content == FILE_1

    def test_set_property_existing_subcommand_new_key(
        self, monkeypatch, repository: ConfigRepository, file_adapter: MockFileAdapter
    ) -> None:
        monkeypatch.setattr(
            file_adapter,
            "_read_text_outputs",
            [FILE_1],
        )

        repository.set_property("clone", "new-key", "value")

        assert len(file_adapter.read_text_calls) == 1
        assert len(file_adapter.write_text_calls) == 1

        _, written_content = file_adapter.write_text_calls[0]
        assert written_content == FILE_2

    def test_set_property_update_existing_key(
        self, monkeypatch, repository: ConfigRepository, file_adapter: MockFileAdapter
    ) -> None:
        monkeypatch.setattr(
            file_adapter,
            "_read_text_outputs",
            [FILE_1],
        )

        repository.set_property("clone", "github-user", "monkeydluffy")

        assert len(file_adapter.read_text_calls) == 1
        assert len(file_adapter.write_text_calls) == 1

        _, written_content = file_adapter.write_text_calls[0]
        assert written_content == FILE_3

    @pytest.mark.parametrize(
        "value,expected_repr",
        [
            ("string_value", '"string_value"'),
            (123, "123"),
            (1.5, "1.5"),
            (True, "true"),
            (False, "false"),
        ],
    )
    def test_set_property_different_types(
        self,
        monkeypatch,
        repository: ConfigRepository,
        file_adapter: MockFileAdapter,
        value: TomlValue,
        expected_repr: str,
    ) -> None:
        monkeypatch.setattr(file_adapter, "_read_text_outputs", [""])

        repository.set_property("clone", "test_key", value)

        assert len(file_adapter.write_text_calls) == 1
        _, written_content = file_adapter.write_text_calls[0]
        assert f"test_key = {expected_repr}" in written_content
