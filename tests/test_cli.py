"""Unit tests for the semantic-index CLI."""

from __future__ import annotations

import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"

# Keep tests runnable with `python -m unittest discover` before editable install.
sys.path.insert(0, str(SRC_DIR))

from semantic_index import __version__  # noqa: E402
from semantic_index import cli  # noqa: E402


class FakeEmbedder:
    """Deterministic embedder for CLI tests — no model download needed."""

    def __init__(self, dims: int = 4) -> None:
        self.dims = dims

    def embed(self, texts: list[str]) -> np.ndarray:
        result = np.zeros((len(texts), self.dims), dtype=np.float32)
        for i, text in enumerate(texts):
            digest = hashlib.sha256(text.encode()).digest()
            for d in range(self.dims):
                chunk = digest[d * 4 : (d + 1) * 4]
                val = int.from_bytes(chunk, "big", signed=True)
                result[i, d] = val / 2**31
        return result


def _make_build_args(
    input_path: str,
    out: str = ".semantic-index",
) -> argparse.Namespace:
    """Build a Namespace object for handle_build."""
    import argparse
    args = argparse.Namespace()
    args.input_path = input_path
    args.out = out
    return args


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
        self.embedder = FakeEmbedder(dims=4)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _touch(self, *parts: str) -> Path:
        path = self.root.joinpath(*parts)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# Test\n\nSome content here.\n\n## Section\n\nMore text.", encoding="utf-8")
        return path

    def _run(
        self,
        input_path: str,
        out: str = ".semantic-index",
        stderr: io.StringIO | None = None,
    ) -> tuple[int, str, str]:
        """Call handle_build with injected FakeEmbedder and capture output."""
        buf_stdout = io.StringIO()
        buf_stderr = io.StringIO() if stderr is None else stderr
        old_stdout, old_stderr = sys.stdout, sys.stderr
        sys.stdout = buf_stdout
        sys.stderr = buf_stderr
        try:
            args = _make_build_args(input_path, out)
            exit_code = cli.handle_build(args, embedder=self.embedder)
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
        return exit_code, buf_stdout.getvalue(), buf_stderr.getvalue()

    def test_build_single_file_creates_index(self) -> None:
        md = self._touch("note.md")
        out_dir = self.root / "out"
        exit_code, out, err = self._run(str(md), str(out_dir))

        self.assertEqual(exit_code, 0)
        self.assertIn("Index built in:", out)
        self.assertTrue((out_dir / "docs.jsonl").exists())
        self.assertTrue((out_dir / "index.npz").exists())

    def test_build_directory_creates_index(self) -> None:
        self._touch("a.md")
        self._touch("b.md")
        out_dir = self.root / "out"
        exit_code, out, err = self._run(str(self.root), str(out_dir))

        self.assertEqual(exit_code, 0)
        self.assertIn("Index built in:", out)
        self.assertIn("Files discovered: 2", out)
        self.assertIn("Chunks indexed:", out)

    def test_build_missing_path(self) -> None:
        missing = self.root / "nonexistent"
        exit_code, out, err = self._run(str(missing))

        self.assertEqual(exit_code, 1)
        self.assertIn("Error:", err)
        self.assertIn("does not exist", err)

    def test_build_non_md_file(self) -> None:
        txt = self._touch("note.txt")
        exit_code, out, err = self._run(str(txt))

        self.assertEqual(exit_code, 1)
        self.assertIn("Error:", err)
        self.assertIn("not a Markdown file", err)

    def test_build_empty_directory(self) -> None:
        exit_code, out, err = self._run(str(self.root))

        self.assertEqual(exit_code, 0)
        self.assertIn("No Markdown files found", out)

    def test_build_default_out_default_dir(self) -> None:
        md = self._touch("note.md")
        out_dir = self.root / ".semantic-index"
        exit_code, out, err = self._run(str(md), str(out_dir))

        self.assertEqual(exit_code, 0)
        self.assertIn("Index built in:", out)
        self.assertTrue((out_dir / "docs.jsonl").exists())

    def test_build_chunks_metadata_preserved(self) -> None:
        self._touch("note.md")
        out_dir = self.root / "out"
        self._run(str(self.root), str(out_dir))

        with (out_dir / "docs.jsonl").open("r", encoding="utf-8") as f:
            chunks = [json.loads(line) for line in f]

        self.assertGreater(len(chunks), 0)
        for c in chunks:
            self.assertIn("id", c)
            self.assertIn("path", c)
            self.assertIn("title", c)
            self.assertIn("heading", c)
            self.assertIn("chunk_index", c)
            self.assertIn("text", c)

    def test_build_index_npz_content(self) -> None:
        self._touch("note.md")
        out_dir = self.root / "out"
        self._run(str(self.root), str(out_dir))

        data = np.load(out_dir / "index.npz")
        self.assertIn("embeddings", data)
        embeddings = data["embeddings"]
        self.assertEqual(embeddings.dtype, np.float32)
        # One embedding per chunk
        with (out_dir / "docs.jsonl").open("r", encoding="utf-8") as f:
            n_chunks = sum(1 for _ in f)
        self.assertEqual(embeddings.shape[0], n_chunks)


if __name__ == "__main__":
    unittest.main()
