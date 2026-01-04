"""Module for CONFIGURATE use cases."""

from typing import Any, Protocol

from blossy.shared.error import ConfigError
from blossy.shared.repository import TomlValue


class ConfigValidator(Protocol):
    """Service for handling configuration rules."""

    def is_subcommand_supported(self, subcommand: str) -> bool:
        """Check if the subcommand is supported for configuration."""
        ...

    def is_key_supported(self, key: str) -> bool:
        """Check if the configuration key is supported."""
        ...

    def is_value_type_valid(self, key: str, value: Any) -> bool:
        """Check if the value type for the given key is valid."""
        ...


class ConfigRepository(Protocol):
    """Repository for handling configurations."""

    def set_property(self, subcommand: str, property_name: str, value: TomlValue) -> None:
        """Set a property value for a subcommand."""
        ...


class ConfigurateUseCase(Protocol):
    """Use case for setting configurations."""

    def execute(self, subcommand: str, key: str, value: TomlValue) -> None: ...


class ConfigurateUseCaseFactory:
    """Factory for creating CONFIGURATE use cases."""

    @staticmethod
    def get_use_case(
        validator: ConfigValidator, repository: ConfigRepository
    ) -> ConfigurateUseCase:
        """Get an instance of the CONFIGURATE use case based on the flags."""
        return _ConfigurateUseCaseOption1(validator, repository)


class _ConfigurateUseCaseOption1:
    """Use case for cloning GitHub repositories."""

    _validator: ConfigValidator
    _repository: ConfigRepository

    def __init__(self, validator: ConfigValidator, repository: ConfigRepository) -> None:
        self._validator = validator
        self._repository = repository

    def execute(self, subcommand: str, key: str, value: TomlValue) -> None:
        if not self._validator.is_subcommand_supported(subcommand):
            raise ConfigError(f"No configuration available for '{subcommand}' subcommand.")
        if not self._validator.is_key_supported(key):
            raise ConfigError(f"The '{key}' configuration key is not supported.")
        if not self._validator.is_value_type_valid(key, value):
            raise ConfigError(f"Invalid type for '{key}' value.")

        self._repository.set_property(subcommand, key, value)
