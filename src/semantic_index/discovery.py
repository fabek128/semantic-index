"""Markdown file discovery with path validation and safe defaults."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

DEFAULT_EXCLUDE_DIRS: frozenset[str] = frozenset({
    ".git",
    ".venv",
    ".semantic-index",
    ".embeddings",
    "__pycache__",
    "node_modules",
})


def discover_markdown(
    path: Path,
    exclude_dirs: Sequence[str] | None = None,
) -> list[Path]:
    """Discover Markdown files under *path*.

    Parameters
    ----------
    path:
        A single Markdown file or directory to search.
    exclude_dirs:
        Directory names to skip during recursive walk.
        Defaults to ``DEFAULT_EXCLUDE_DIRS``.

    Returns
    -------
    Sorted list of resolved Markdown file paths.

    Raises
    ------
    FileNotFoundError
        If *path* does not exist.
    NotADirectoryError
        If *path* is a file without a ``.md`` extension.
    PermissionError
        If the top-level *path* is not readable.
    """
    excludes = frozenset(exclude_dirs) if exclude_dirs is not None else DEFAULT_EXCLUDE_DIRS

    if not path.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")

    if path.is_file():
        if path.suffix.lower() != ".md":
            raise NotADirectoryError(
                f"Input is a single file but not a Markdown file: {path} "
                f"(expected .md extension)"
            )
        return [path.resolve()]

    if not path.is_dir():
        raise NotADirectoryError(f"Path is not a file or directory: {path}")

    result: list[Path] = []
    try:
        for entry in path.iterdir():
            if entry.is_symlink():
                continue

            if entry.is_dir():
                if entry.name in excludes:
                    continue
                result.extend(_walk_dir(entry, excludes))
            elif entry.is_file() and entry.suffix.lower() == ".md":
                result.append(entry.resolve())
    except PermissionError as exc:
        raise PermissionError(f"Cannot read directory: {exc}") from exc

    result.sort(key=str)
    return result


def _walk_dir(path: Path, exclude_dirs: frozenset[str]) -> list[Path]:
    """Recursively walk a directory, skipping excluded dirs and symlinks."""
    found: list[Path] = []
    try:
        for entry in path.iterdir():
            if entry.is_symlink():
                continue

            if entry.is_dir():
                if entry.name in exclude_dirs:
                    continue
                found.extend(_walk_dir(entry, exclude_dirs))
            elif entry.is_file() and entry.suffix.lower() == ".md":
                found.append(entry.resolve())
    except PermissionError:
        pass

    return found
