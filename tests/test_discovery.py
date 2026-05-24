"""Unit tests for safe Markdown file discovery."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"

# Keep tests runnable with `python -m unittest discover` before editable install.
sys.path.insert(0, str(SRC_DIR))

from semantic_index.discovery import DiscoveryError, discover_markdown_files  # noqa: E402


class MarkdownDiscoveryTests(unittest.TestCase):
    def test_discovers_single_markdown_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            note = Path(tmp) / "note.md"
            note.write_text("# Note\n", encoding="utf-8")

            self.assertEqual(discover_markdown_files(note), [note])

    def test_rejects_single_non_markdown_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            text_file = Path(tmp) / "note.txt"
            text_file.write_text("not markdown", encoding="utf-8")

            with self.assertRaisesRegex(DiscoveryError, "not a Markdown"):
                discover_markdown_files(text_file)

    def test_rejects_missing_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing"

            with self.assertRaisesRegex(DiscoveryError, "does not exist"):
                discover_markdown_files(missing)

    def test_discovers_markdown_files_recursively_in_deterministic_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "docs"
            nested = docs / "nested"
            nested.mkdir(parents=True)
            second = nested / "b.md"
            first = docs / "a.md"
            ignored = docs / "ignore.txt"
            second.write_text("# B\n", encoding="utf-8")
            first.write_text("# A\n", encoding="utf-8")
            ignored.write_text("ignore", encoding="utf-8")

            self.assertEqual(discover_markdown_files(docs), [first, second])

    def test_skips_default_excluded_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            included = root / "keep.md"
            included.write_text("# Keep\n", encoding="utf-8")

            for dirname in [".git", ".venv", ".semantic-index", ".embeddings", "__pycache__"]:
                ignored_dir = root / dirname
                ignored_dir.mkdir()
                (ignored_dir / "ignored.md").write_text("# Ignored\n", encoding="utf-8")

            self.assertEqual(discover_markdown_files(root), [included])

    @unittest.skipUnless(hasattr(os, "symlink"), "symlink support required")
    def test_does_not_follow_symlinked_files_or_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            real_dir = root / "real"
            real_dir.mkdir()
            real_note = real_dir / "real.md"
            real_note.write_text("# Real\n", encoding="utf-8")
            linked_file = root / "linked.md"
            linked_dir = root / "linked-dir"

            try:
                os.symlink(real_note, linked_file)
                os.symlink(real_dir, linked_dir)
            except OSError as exc:  # pragma: no cover - platform/permission specific
                self.skipTest(f"cannot create symlink in this environment: {exc}")

            self.assertEqual(discover_markdown_files(root), [real_note])

    @unittest.skipUnless(hasattr(os, "symlink"), "symlink support required")
    def test_rejects_symlink_input_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            real_note = root / "real.md"
            linked_note = root / "linked.md"
            real_note.write_text("# Real\n", encoding="utf-8")

            try:
                os.symlink(real_note, linked_note)
            except OSError as exc:  # pragma: no cover - platform/permission specific
                self.skipTest(f"cannot create symlink in this environment: {exc}")

            with self.assertRaisesRegex(DiscoveryError, "symlink"):
                discover_markdown_files(linked_note)

    def test_rejects_unreadable_markdown_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            note = Path(tmp) / "private.md"
            note.write_text("# Private\n", encoding="utf-8")
            note.chmod(0)
            try:
                if os.access(note, os.R_OK):
                    self.skipTest("environment can still read chmod 000 files")
                with self.assertRaisesRegex(DiscoveryError, "not readable"):
                    discover_markdown_files(note)
            finally:
                note.chmod(0o600)


if __name__ == "__main__":
    unittest.main()
