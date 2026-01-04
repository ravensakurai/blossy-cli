"""Module for CLONE use cases."""

from subprocess import run
from typing import Protocol

from blossy.shared.error import ConfigError
from blossy.shared.model import TomlValue

_URL_TEMPLATE = "{prefix}github.com:{user}/{repository}.git"
_PREFIX_SSH = "git@"
_PREFIX_HTTPS = "https://"


class ConfigRepository(Protocol):
    """Repository for handling configurations."""

    def get_property(self, subcommand: str, property_name: str) -> TomlValue | None:
        """Get a property value for a subcommand."""
        ...

    def set_property(self, subcommand: str, property_name: str, value: TomlValue) -> None:
        """Set a property value for a subcommand."""
        ...


class CloneUseCase(Protocol):
    """Use case for cloning GitHub repositories."""

    def execute(self, repositories: list[str], use_https: bool) -> None: ...


class CloneUseCaseFactory:
    """Factory for creating CLONE use cases."""

    @staticmethod
    def get_use_case(config_service: ConfigRepository) -> CloneUseCase:
        """Get an instance of the CLONE use case based on the flags."""
        return _CloneUseCaseOption1(config_service)


class _CloneUseCaseOption1:
    """Use case for cloning GitHub repositories."""

    _config_service: ConfigRepository

    def __init__(self, config_service: ConfigRepository) -> None:
        self._config_service = config_service

    def execute(self, repositories: list[str], use_https: bool) -> None:
        prefix = _PREFIX_HTTPS if use_https else _PREFIX_SSH
        user = self._load_configured_user()

        for repo in repositories:
            repo_url = _URL_TEMPLATE.format(
                prefix=prefix,
                user=user,
                repository=repo,
            )

            run(["git", "clone", repo_url], check=True)

    def _load_configured_user(self) -> str:
        user = self._config_service.get_property("clone", "github_user")
        if not user:
            raise ConfigError("GitHub user is not configured for 'clone' subcommand.")
        if not isinstance(user, str):
            raise ConfigError("GitHub user configuration is not a string.")

        return user
