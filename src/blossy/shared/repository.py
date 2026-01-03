"""Shared repositories for Blossy."""

from pathlib import Path
from typing import Protocol

import platformdirs
import tomlkit

from blossy.shared.model import TomlValue


class FileAdapter(Protocol):
    """Adapter for file operations."""

    def create_if_not_exists(self, path: Path) -> None:
        """Create an empty file at the given path."""
        ...

    def read_text(self, path: Path) -> str:
        """Read text from a file at the given path."""
        ...

    def write_text(self, path: Path, content: str) -> None:
        """Write text to a file at the given path."""
        ...


class ConfigRepository:
    """Repository for handling configurations."""

    _file_adapter: FileAdapter
    _config_file: Path

    def __init__(self, file_adapter: FileAdapter) -> None:
        self._file_adapter = file_adapter

        config_dir_str = platformdirs.user_config_dir(
            appname="blossy", appauthor="ravensakurai", ensure_exists=True
        )
        config_file = Path(config_dir_str) / "config.toml"
        self._file_adapter.create_if_not_exists(config_file)

        self._config_file = config_file

    def get_property(self, subcommand: str, property_name: str) -> TomlValue | None:
        """Get a property value for a subcommand."""
        config_str = self._file_adapter.read_text(self._config_file)
        config = tomlkit.loads(config_str)
        return config.get(subcommand, {}).get(property_name)

    def set_property(self, subcommand: str, property_name: str, value: TomlValue) -> None:
        """Set a property value for a subcommand."""
        config_str = self._file_adapter.read_text(self._config_file)
        document = tomlkit.loads(config_str)

        subcommand_table = document.get(subcommand)
        if subcommand_table is None:
            new_table = tomlkit.table()
            document.add(subcommand, new_table)
            subcommand_table = new_table

        subcommand_table.update({property_name: value})

        document_str = tomlkit.dumps(document)
        self._file_adapter.write_text(self._config_file, document_str)
