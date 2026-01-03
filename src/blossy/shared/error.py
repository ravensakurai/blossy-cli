"""Shared errors for Blossy."""


class ConfigError(Exception):
    """Error for configuration issues."""

    def __init__(self, message: str) -> None:
        super().__init__(f"Configuration error: {message}")


class InternalError(Exception):
    """Error for unexpected runtime conditions that should never occur."""

    def __init__(self, message: str) -> None:
        super().__init__(f"Internal error: {message}")
