"""Module for CLONE use cases."""

from typing import Protocol

from blossy.shared.error import ConfigError
from blossy.shared.model import TomlValue

_URL_TEMPLATE = "{prefix}{user}/{repository}.git"
_PREFIX_SSH = "git@github.com:"
_PREFIX_HTTPS = "https://github.com/"


class ConfigRepository(Protocol):
    """Repository for handling configurations."""

    def get_property(self, subcommand: str, property_name: str) -> TomlValue | None:
        """Get a property value for a subcommand."""
        ...

    def set_property(self, subcommand: str, property_name: str, value: TomlValue) -> None:
        """Set a property value for a subcommand."""
        ...


class SubprocessAdapter(Protocol):
    """Adapter for subprocess operations."""

    def run(self, *args: str) -> None:
        """Run a subprocess with the given arguments."""
        ...


class CloneUseCase(Protocol):
    """Use case for cloning GitHub repositories."""

    def execute(self, repositories: list[str], use_https: bool) -> None: ...


class CloneUseCaseFactory:
    """Factory for creating CLONE use cases."""

    @staticmethod
    def get_use_case(
        config_repository: ConfigRepository, subprocess_adapter: SubprocessAdapter
    ) -> CloneUseCase:
        """Get an instance of the CLONE use case based on the flags."""
        return _CloneUseCaseOption1(config_repository, subprocess_adapter)


class _CloneUseCaseOption1:
    """Use case for cloning GitHub repositories."""

    _config_repository: ConfigRepository
    _subprocess_adapter: SubprocessAdapter

    def __init__(
        self, config_repository: ConfigRepository, subprocess_adapter: SubprocessAdapter
    ) -> None:
        self._config_repository = config_repository
        self._subprocess_adapter = subprocess_adapter

    def execute(self, repositories: list[str], use_https: bool) -> None:
        prefix = _PREFIX_HTTPS if use_https else _PREFIX_SSH
        user = self._load_configured_user()

        for repo in repositories:
            repo_url = _URL_TEMPLATE.format(
                prefix=prefix,
                user=user,
                repository=repo,
            )

            self._subprocess_adapter.run("git", "clone", repo_url)

    def _load_configured_user(self) -> str:
        user = self._config_repository.get_property("clone", "github-user")
        if not user:
            raise ConfigError(
                "GitHub user is not configured for 'clone' subcommand. "
                "Use 'blossy config clone github-user <username>' to set it."
            )
        if not isinstance(user, str):
            raise ConfigError("GitHub user configuration is not a string.")

        return user
