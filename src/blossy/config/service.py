"""Module for CONFIGURATE services."""

from dataclasses import dataclass
from typing import Any

from blossy.shared.error import InternalError


@dataclass(frozen=True)
class _Property:
    external_name: str
    internal_name: str
    value_type: type


class ConfigGatekeeer:
    """Service for handling configuration rules."""

    _COMMANDS = frozenset({"clone"})
    _PROPERTIES = frozenset(
        {
            _Property(
                external_name="github-user",
                internal_name="github_user",
                value_type=str,
            ),
        }
    )

    def is_subcommand_supported(self, subcommand: str) -> bool:
        """Check if the subcommand is supported for configuration."""
        return subcommand.lower() in (cmd.lower() for cmd in self._COMMANDS)

    def is_key_supported(self, key: str) -> bool:
        """Check if the configuration key is supported."""
        return key.lower() in (prop.external_name.lower() for prop in self._PROPERTIES)

    def is_value_type_valid(self, key: str, value: Any) -> bool:
        """Check if the value type for the given key is valid."""
        matching_props = [
            prop for prop in self._PROPERTIES if prop.external_name.lower() == key.lower()
        ]
        if len(matching_props) > 1:
            raise InternalError("Multiple properties found for the same key.")

        return isinstance(value, matching_props[0].value_type) if matching_props else False

    def get_internal_property_name(self, external_property_name: str) -> str | None:
        """Get the internal property name for the given external key."""
        matching_props = [
            prop
            for prop in self._PROPERTIES
            if prop.external_name.lower() == external_property_name.lower()
        ]
        if len(matching_props) > 1:
            raise InternalError("Multiple properties found for the same key.")

        return matching_props[0].internal_name if matching_props else None
