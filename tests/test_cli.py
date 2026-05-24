"""Unit tests for the minimal semantic-index CLI."""

from __future__ import annotations

import io
import os
import tempfile
import subprocess
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"

# Keep tests runnable with `python -m unittest discover` before editable install.
sys.path.insert(0, str(SRC_DIR))

from semantic_index import __version__  # noqa: E402
from semantic_index import cli  # noqa: E402


class CliEntrypointTests(unittest.TestCase):
    def run_main(self, *args: str) -> tuple[int | str | None, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            try:
                exit_code = cli.main(args)
            except SystemExit as exc:
                exit_code = exc.code
        return exit_code, stdout.getvalue(), stderr.getvalue()

    def test_console_entrypoint_help_succeeds(self) -> None:
        exit_code, output, error = self.run_main("--help")

        self.assertEqual(exit_code, 0)
        self.assertIn("usage: semantic-index", output)
        self.assertIn("version", output)
        self.assertEqual(error, "")

    def test_console_entrypoint_version_succeeds(self) -> None:
        exit_code, output, error = self.run_main("version")

        self.assertEqual(exit_code, 0)
        self.assertEqual(output.strip(), f"semantic-index {__version__}")
        self.assertEqual(error, "")

    def test_console_entrypoint_build_discovers_markdown_without_writing_index(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            notes = root / "notes"
            notes.mkdir()
            (notes / "one.md").write_text("# One\n", encoding="utf-8")
            (notes / "two.txt").write_text("ignore", encoding="utf-8")
            out_dir = root / ".semantic-index"

            exit_code, output, error = self.run_main("build", str(notes), "--out", str(out_dir))

            self.assertEqual(exit_code, 0)
            self.assertIn("Markdown files discovered: 1", output)
            self.assertIn("Index build is not implemented yet.", output)
            self.assertEqual(error, "")
            self.assertFalse(out_dir.exists())

    def test_console_entrypoint_build_reports_discovery_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing"

            exit_code, output, error = self.run_main("build", str(missing))

            self.assertEqual(exit_code, 1)
            self.assertEqual(output, "")
            self.assertIn("error: input path does not exist", error)
            self.assertNotIn("Traceback", error)

    def run_module(self, *args: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        existing_pythonpath = env.get("PYTHONPATH")
        env["PYTHONPATH"] = (
            str(SRC_DIR)
            if not existing_pythonpath
            else f"{SRC_DIR}{os.pathsep}{existing_pythonpath}"
        )

        return subprocess.run(
            [sys.executable, "-m", "semantic_index", *args],
            cwd=REPO_ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_python_module_help_succeeds(self) -> None:
        result = self.run_module("--help")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("usage: semantic-index", result.stdout)
        self.assertIn("version", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_python_module_version_succeeds(self) -> None:
        result = self.run_module("version")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), f"semantic-index {__version__}")
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
