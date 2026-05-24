"""Unit tests for the Markdown discovery module."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from semantic_index.discovery import DEFAULT_EXCLUDE_DIRS, discover_markdown


class DiscoverMarkdownTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _touch(self, *parts: str) -> Path:
        path = self.root.joinpath(*parts)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# test", encoding="utf-8")
        return path

    def _mkdir(self, *parts: str) -> Path:
        path = self.root.joinpath(*parts)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def test_discover_single_file(self) -> None:
        md = self._touch("note.md")
        result = discover_markdown(md)

        self.assertEqual(result, [md.resolve()])

    def test_discover_single_file_non_md_raises(self) -> None:
        txt = self._touch("note.txt")

        with self.assertRaises(NotADirectoryError):
            discover_markdown(txt)

    def test_discover_nonexistent_path_raises(self) -> None:
        missing = self.root / "does-not-exist"

        with self.assertRaises(FileNotFoundError):
            discover_markdown(missing)

    def test_discover_nonexistent_file_raises(self) -> None:
        missing = self.root / "no.md"

        with self.assertRaises(FileNotFoundError):
            discover_markdown(missing)

    def test_discover_empty_directory(self) -> None:
        result = discover_markdown(self.root)

        self.assertEqual(result, [])

    def test_discover_directory_with_md_files(self) -> None:
        self._touch("a.md")
        self._touch("b.md")
        self._touch("sub", "c.md")

        result = discover_markdown(self.root)

        self.assertEqual(len(result), 3)
        self.assertIn((self.root / "a.md").resolve(), result)
        self.assertIn((self.root / "b.md").resolve(), result)
        self.assertIn((self.root / "sub" / "c.md").resolve(), result)

    def test_discover_excludes_default_dirs(self) -> None:
        self._touch("keep.md")
        for excluded in DEFAULT_EXCLUDE_DIRS:
            self._touch(excluded, "ignored.md")

        result = discover_markdown(self.root)

        self.assertEqual(len(result), 1)
        self.assertIn((self.root / "keep.md").resolve(), result)

    def test_discover_skips_symlinks(self) -> None:
        real = self._touch("real.md")
        link = self.root / "link.md"
        os.symlink(real, link)

        result = discover_markdown(self.root)

        self.assertEqual(result, [real.resolve()])

    def test_discover_skips_symlink_dirs(self) -> None:
        real_dir = Path(tempfile.mkdtemp())
        try:
            (real_dir / "in_symlink.md").write_text("# test", encoding="utf-8")
            link = self.root / "link_dir"
            os.symlink(real_dir, link, target_is_directory=True)
            self._touch("top.md")

            result = discover_markdown(self.root)

            self.assertEqual(len(result), 1)
            self.assertIn((self.root / "top.md").resolve(), result)
        finally:
            import shutil
            shutil.rmtree(real_dir, ignore_errors=True)

    def test_discover_non_md_files_ignored(self) -> None:
        self._touch("note.md")
        self._touch("data.json")
        self._touch("script.py")

        result = discover_markdown(self.root)

        self.assertEqual(len(result), 1)
        self.assertIn((self.root / "note.md").resolve(), result)

    def test_discover_custom_exclude_dirs(self) -> None:
        self._touch("keep.md")
        self._touch("custom_exclude", "ignored.md")
        self._touch("sub", "also_keep.md")

        result = discover_markdown(self.root, exclude_dirs=["custom_exclude"])

        self.assertEqual(len(result), 2)
        self.assertIn((self.root / "keep.md").resolve(), result)
        self.assertIn((self.root / "sub" / "also_keep.md").resolve(), result)

    def test_discover_results_sorted(self) -> None:
        self._touch("z.md")
        self._touch("a.md")
        self._touch("m.md")

        result = discover_markdown(self.root)
        paths = [str(p) for p in result]

        self.assertEqual(paths, sorted(paths))
        self.assertEqual(len(result), 3)

    def test_discover_directory_not_readable_raises(self) -> None:
        unreadable = self._mkdir("unreadable")
        unreadable.chmod(0o000)
        try:
            with self.assertRaises(PermissionError):
                discover_markdown(unreadable)
        finally:
            unreadable.chmod(0o755)
