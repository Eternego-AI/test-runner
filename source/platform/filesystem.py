"""Filesystem — file discovery."""

from pathlib import Path


def glob_recursive(directory: Path, pattern: str) -> list[Path]:
    """Return all files matching the glob pattern, sorted."""
    return sorted(directory.rglob(pattern))


def read_text(path: Path) -> str:
    """Read text content from a file."""
    return path.read_text()
