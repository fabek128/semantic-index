"""Command-line interface for semantic-index."""

from __future__ import annotations

import argparse
import sys
from importlib.metadata import PackageNotFoundError, version as package_version
from pathlib import Path
from typing import Sequence

from semantic_index import __version__
from semantic_index.discovery import discover_markdown

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

    version_parser = subcommands.add_parser(
        "version",
        help="print the semantic-index version",
        description="Print the semantic-index version and exit.",
    )
    version_parser.set_defaults(handler=handle_version)

    build_parser_inst = subcommands.add_parser(
        "build",
        help="discover Markdown files and print a summary",
        description=(
            "Discover Markdown files from a local input path and print a "
            "summary. No index is built yet."
        ),
    )
    build_parser_inst.add_argument(
        "input_path",
        type=str,
        help="path to a Markdown file or directory of Markdown files",
    )
    build_parser_inst.add_argument(
        "--out",
        default=".semantic-index",
        help="output directory for future index data (default: .semantic-index)",
    )
    build_parser_inst.set_defaults(handler=handle_build)

    return parser


def handle_version(_args: argparse.Namespace) -> int:
    print(f"{PACKAGE_NAME} {get_version()}")
    return 0


def handle_build(args: argparse.Namespace) -> int:
    input_path = Path(args.input_path)

    try:
        files = discover_markdown(input_path)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except NotADirectoryError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except PermissionError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if not files:
        print(f"No Markdown files found in: {input_path}")
        return 0

    print(f"Output directory: {args.out}")
    print(f"Discovered {len(files)} Markdown file(s):")
    for f in files:
        print(f"  {f}")

    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    handler = getattr(args, "handler", None)
    if handler is None:
        parser.print_help()
        return 0

    return handler(args)
