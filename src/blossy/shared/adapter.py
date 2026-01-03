"""Shared adapters for Blossy."""

from pathlib import Path


class FileAdapter:
    """Adapter for file operations."""

    def create_if_not_exists(self, path: Path) -> None:
        """Create an empty file at the given path."""
        if not path.exists():
            path.touch()

    def read_text(self, path: Path) -> str:
        """Read text from a file at the given path."""
        return path.read_text()

    def write_text(self, path: Path, content: str) -> None:
        """Write text to a file at the given path."""
        path.write_text(content)
