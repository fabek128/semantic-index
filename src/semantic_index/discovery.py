"""Local Markdown discovery helpers for semantic-index."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable


DEFAULT_EXCLUDED_DIRS = frozenset(
    {
        ".git",
        ".venv",
        ".semantic-index",
        ".embeddings",
        "__pycache__",
    }
)


class DiscoveryError(ValueError):
    """Raised when Markdown discovery cannot safely proceed."""


def is_markdown_file(path: Path) -> bool:
    """Return True when *path* looks like a Markdown note supported by v0.2."""

    return path.suffix.lower() == ".md"


def discover_markdown_files(
    input_path: Path,
    *,
    exclude_dirs: Iterable[str] = DEFAULT_EXCLUDED_DIRS,
) -> list[Path]:
    """Discover Markdown files below *input_path* without following symlinks.

    The function supports a single Markdown file or a directory. Directory
    discovery is recursive, deterministic, and excludes generated or unsafe
    directories by default.
    """

    path = Path(input_path)
    excluded = set(exclude_dirs)

    if path.is_symlink():
        raise DiscoveryError(f"symlink input paths are not supported: {path}")

    if not path.exists():
        raise DiscoveryError(f"input path does not exist: {path}")

    if path.is_file():
        if not is_markdown_file(path):
            raise DiscoveryError(f"input file is not a Markdown .md file: {path}")
        _ensure_readable(path, "input file")
        return [path]

    if not path.is_dir():
        raise DiscoveryError(f"input path is not a file or directory: {path}")

    _ensure_readable(path, "input directory")

    discovered: list[Path] = []

    def on_walk_error(error: OSError) -> None:
        filename = error.filename or str(path)
        raise DiscoveryError(f"cannot read directory during discovery: {filename}") from error

    for root, dirnames, filenames in os.walk(path, topdown=True, onerror=on_walk_error, followlinks=False):
        root_path = Path(root)

        safe_dirnames = []
        for dirname in sorted(dirnames):
            directory = root_path / dirname
            if dirname in excluded or directory.is_symlink():
                continue
            safe_dirnames.append(dirname)
        dirnames[:] = safe_dirnames

        for filename in sorted(filenames):
            candidate = root_path / filename
            if candidate.is_symlink() or not is_markdown_file(candidate):
                continue
            _ensure_readable(candidate, "Markdown file")
            discovered.append(candidate)

    return sorted(discovered, key=lambda file_path: str(file_path))


def _ensure_readable(path: Path, label: str) -> None:
    if not os.access(path, os.R_OK):
        raise DiscoveryError(f"{label} is not readable: {path}")
