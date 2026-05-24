"""Command-line interface for semantic-index."""

from __future__ import annotations

import argparse
import sys
from importlib.metadata import PackageNotFoundError, version as package_version
from pathlib import Path
from typing import Sequence

from semantic_index import __version__
from semantic_index.discovery import DiscoveryError, discover_markdown_files

PACKAGE_NAME = "semantic-index"


def get_version() -> str:
    """Return the installed package version, with a source-tree fallback."""

    try:
        return package_version(PACKAGE_NAME)
    except PackageNotFoundError:
        return __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=PACKAGE_NAME,
        description="CLI-first local semantic search for Markdown notes.",
    )
    subcommands = parser.add_subparsers(dest="command", metavar="command")

    build_command = subcommands.add_parser(
        "build",
        help="discover local Markdown files for a future index build",
        description=(
            "Discover Markdown files from a local file or directory. "
            "This command does not generate embeddings or write index files yet."
        ),
    )
    build_command.add_argument(
        "path",
        type=Path,
        help="local Markdown file or directory to scan",
    )
    build_command.add_argument(
        "--out",
        type=Path,
        default=Path(".semantic-index"),
        help="future index output directory (default: .semantic-index; not written yet)",
    )
    build_command.set_defaults(handler=handle_build)

    version_parser = subcommands.add_parser(
        "version",
        help="print the semantic-index version",
        description="Print the semantic-index version and exit.",
    )
    version_parser.set_defaults(handler=handle_version)

    return parser


def handle_build(args: argparse.Namespace) -> int:
    markdown_files = discover_markdown_files(args.path)

    print(f"Input path: {args.path}")
    print(f"Markdown files discovered: {len(markdown_files)}")
    print(f"Output directory (not written yet): {args.out}")
    print("Index build is not implemented yet.")
    return 0


def handle_version(_args: argparse.Namespace) -> int:
    print(f"{PACKAGE_NAME} {get_version()}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    handler = getattr(args, "handler", None)
    if handler is None:
        parser.print_help()
        return 0

    try:
        return handler(args)
    except DiscoveryError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
