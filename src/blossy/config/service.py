"""Module for CONFIGURATE services."""

from dataclasses import dataclass
from typing import Any

from blossy.shared.error import InternalError


@dataclass(frozen=True)
class _Property:
    name: str
    value_type: type


class ConfigValidator:
    """Service for validating configuration rules."""

    _COMMANDS = frozenset({"clone"})
    _PROPERTIES = frozenset(
        {
            _Property(
                name="github-user",
                value_type=str,
            ),
        }
    )

    def is_subcommand_supported(self, subcommand: str) -> bool:
        """Check if the subcommand is supported for configuration."""
        return subcommand.lower() in (cmd.lower() for cmd in self._COMMANDS)

    def is_key_supported(self, key: str) -> bool:
        """Check if the configuration key is supported."""
        return key.lower() in (prop.name.lower() for prop in self._PROPERTIES)

    def is_value_type_valid(self, key: str, value: Any) -> bool:
        """Check if the value type for the given key is valid."""
        matching_props = [prop for prop in self._PROPERTIES if prop.name.lower() == key.lower()]
        if len(matching_props) > 1:
            raise InternalError("Multiple properties found for the same key.")

        return isinstance(value, matching_props[0].value_type) if matching_props else False
