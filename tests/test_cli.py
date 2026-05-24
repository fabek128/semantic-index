"""Unit tests for the semantic-index CLI."""

from __future__ import annotations

import io
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"

# Keep tests runnable with `python -m unittest discover` before editable install.
sys.path.insert(0, str(SRC_DIR))

from semantic_index import __version__  # noqa: E402
from semantic_index import cli  # noqa: E402


class CliEntrypointTests(unittest.TestCase):
    def run_main(self, *args: str) -> tuple[int | str | None, str]:
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            try:
                exit_code = cli.main(args)
            except SystemExit as exc:
                exit_code = exc.code
        return exit_code, stdout.getvalue()

    def test_console_entrypoint_help_succeeds(self) -> None:
        exit_code, output = self.run_main("--help")

        self.assertEqual(exit_code, 0)
        self.assertIn("usage: semantic-index", output)
        self.assertIn("version", output)
        self.assertIn("build", output)

    def test_console_entrypoint_version_succeeds(self) -> None:
        exit_code, output = self.run_main("version")

        self.assertEqual(exit_code, 0)
        self.assertEqual(output.strip(), f"semantic-index {__version__}")

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


class CliBuildTests(unittest.TestCase):
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

    def run_main(self, *args: str) -> tuple[int | str | None, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with (
            redirect_stdout(stdout),
            self.assertRaises(SystemExit) if False else context_redirect_stderr(stderr),
        ):
            try:
                exit_code = cli.main(args)
            except SystemExit as exc:
                exit_code = exc.code
        return exit_code, stdout.getvalue()

    def run_main_simple(self, *args: str) -> tuple[int | str | None, str, str]:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        stdout = io.StringIO()
        stderr = io.StringIO()
        sys.stdout = stdout
        sys.stderr = stderr
        try:
            exit_code = cli.main(args)
        except SystemExit as exc:
            exit_code = exc.code
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
        return exit_code, stdout.getvalue(), stderr.getvalue()

    def test_build_single_file(self) -> None:
        md = self._touch("note.md")
        exit_code, out, err = self.run_main_simple("build", str(md))

        self.assertEqual(exit_code, 0)
        self.assertIn("Discovered 1 Markdown file(s)", out)
        self.assertIn(str(md.resolve()), out)

    def test_build_directory(self) -> None:
        self._touch("a.md")
        self._touch("b.md")
        exit_code, out, err = self.run_main_simple("build", str(self.root))

        self.assertEqual(exit_code, 0)
        self.assertIn("Discovered 2 Markdown file(s)", out)
        self.assertIn(str((self.root / "a.md").resolve()), out)
        self.assertIn(str((self.root / "b.md").resolve()), out)

    def test_build_missing_path(self) -> None:
        missing = self.root / "nonexistent"
        exit_code, out, err = self.run_main_simple("build", str(missing))

        self.assertEqual(exit_code, 1)
        self.assertIn("Error:", err)
        self.assertIn("does not exist", err)

    def test_build_non_md_file(self) -> None:
        txt = self._touch("note.txt")
        exit_code, out, err = self.run_main_simple("build", str(txt))

        self.assertEqual(exit_code, 1)
        self.assertIn("Error:", err)
        self.assertIn("not a Markdown file", err)

    def test_build_empty_directory(self) -> None:
        exit_code, out, err = self.run_main_simple("build", str(self.root))

        self.assertEqual(exit_code, 0)
        self.assertIn("No Markdown files found", out)

    def test_build_default_out(self) -> None:
        md = self._touch("note.md")
        exit_code, out, err = self.run_main_simple("build", str(md))

        self.assertEqual(exit_code, 0)
        self.assertIn("Output directory: .semantic-index", out)

    def test_build_custom_out(self) -> None:
        md = self._touch("note.md")
        exit_code, out, err = self.run_main_simple("build", str(md), "--out", "custom-out")

        self.assertEqual(exit_code, 0)
        self.assertIn("Output directory: custom-out", out)


def context_redirect_stderr(stream: io.StringIO):
    """A trivial context manager that redirects stderr (for type-checker compatibility)."""

    class _Redirect:
        def __enter__(self):
            self._old = sys.stderr
            sys.stderr = stream
            return stream

        def __exit__(self, *exc_info):
            sys.stderr = self._old

    return _Redirect()


if __name__ == "__main__":
    unittest.main()
