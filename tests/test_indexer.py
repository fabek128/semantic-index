"""Unit tests for the embedding index module."""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))


from semantic_index.indexer import (  # noqa: E402
    DEFAULT_QUERY_PREFIX,
    _normalize,
    _save_index,
    build_index,
    load_index,
    search_index,
)


class FakeEmbedder:
    """Deterministic embedder for tests — no model download needed."""

    def __init__(self, dims: int = 4) -> None:
        self.dims = dims
        self.called_with: list[list[str]] = []

    def embed(self, texts: list[str]) -> np.ndarray:
        self.called_with.append(texts)
        result = np.zeros((len(texts), self.dims), dtype=np.float32)
        for i, text in enumerate(texts):
            digest = hashlib.sha256(text.encode()).digest()
            for d in range(self.dims):
                chunk = digest[d * 4 : (d + 1) * 4]
                val = int.from_bytes(chunk, "big", signed=True)
                result[i, d] = val / 2**31  # normalize to [-1, 1]
        return result


class BuildIndexTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp_dir = tempfile.TemporaryDirectory()
        self.output = Path(self._tmp_dir.name)
        self.embedder = FakeEmbedder(dims=4)
        self.chunks = [
            {"id": "chunk_0", "path": "/a.md", "title": "A", "heading": "H1", "chunk_index": 0, "text": "Hello."},
            {"id": "chunk_1", "path": "/a.md", "title": "A", "heading": "H2", "chunk_index": 1, "text": "World."},
            {"id": "chunk_2", "path": "/b.md", "title": "B", "heading": None, "chunk_index": 0, "text": "Foo bar."},
        ]

    def tearDown(self) -> None:
        self._tmp_dir.cleanup()

    def test_build_index_creates_both_files(self) -> None:
        build_index(self.chunks, self.output, self.embedder)

        self.assertTrue((self.output / "docs.jsonl").exists())
        self.assertTrue((self.output / "index.npz").exists())

    def test_build_index_docs_jsonl_format(self) -> None:
        build_index(self.chunks, self.output, self.embedder)

        with (self.output / "docs.jsonl").open("r", encoding="utf-8") as f:
            lines = f.readlines()

        self.assertEqual(len(lines), 3)
        for i, line in enumerate(lines):
            obj = json.loads(line)
            # Each line is a full chunk dict
            self.assertEqual(obj["id"], self.chunks[i]["id"])
            self.assertEqual(obj["text"], self.chunks[i]["text"])

    def test_build_index_index_npz_format(self) -> None:
        build_index(self.chunks, self.output, self.embedder)

        data = np.load(self.output / "index.npz")
        self.assertIn("embeddings", data)
        embeddings = data["embeddings"]
        self.assertEqual(embeddings.shape, (3, 4))
        self.assertEqual(embeddings.dtype, np.float32)

    def test_build_index_embeddings_normalized(self) -> None:
        build_index(self.chunks, self.output, self.embedder)

        data = np.load(self.output / "index.npz")
        embeddings = data["embeddings"]
        norms = np.linalg.norm(embeddings, axis=1)
        for norm in norms:
            self.assertAlmostEqual(norm, 1.0, places=5)

    def test_build_index_empty_chunks_raises(self) -> None:
        with self.assertRaises(ValueError):
            build_index([], self.output, self.embedder)

    def test_build_index_texts_passed_directly(self) -> None:
        build_index(self.chunks, self.output, self.embedder)

        self.assertEqual(len(self.embedder.called_with), 1)
        texts = self.embedder.called_with[0]
        self.assertEqual(len(texts), 3)
        for i, text in enumerate(texts):
            self.assertEqual(text, self.chunks[i]["text"])

    def test_build_index_output_dir_created(self) -> None:
        nested = self.output / "sub" / "dir"
        build_index(self.chunks, nested, self.embedder)

        self.assertTrue(nested.is_dir())
        self.assertTrue((nested / "docs.jsonl").exists())
        self.assertTrue((nested / "index.npz").exists())

    def test_build_index_chunk_order_preserved(self) -> None:
        build_index(self.chunks, self.output, self.embedder)

        with (self.output / "docs.jsonl").open("r", encoding="utf-8") as f:
            ids = [json.loads(line)["id"] for line in f]

        self.assertEqual(ids, ["chunk_0", "chunk_1", "chunk_2"])


class NormalizeTests(unittest.TestCase):
    def test_normalize_unit_length(self) -> None:
        vec = np.array([[3.0, 0.0], [1.0, 2.0]], dtype=np.float32)
        result = _normalize(vec)

        self.assertEqual(result.shape, (2, 2))
        # First vector: (3,0) -> (1,0)
        self.assertAlmostEqual(result[0, 0], 1.0, places=5)
        self.assertAlmostEqual(result[0, 1], 0.0, places=5)
        # All non-zero vectors should be unit length
        for r in result:
            self.assertAlmostEqual(np.linalg.norm(r), 1.0, places=5)

    def test_normalize_zero_vector_preserved(self) -> None:
        vec = np.array([[0.0, 0.0]], dtype=np.float32)
        result = _normalize(vec)

        # Zero vector should not crash; result stays zero (no NaN)
        self.assertEqual(result[0, 0], 0.0)
        self.assertEqual(result[0, 1], 0.0)

    def test_normalize_dtype_float32(self) -> None:
        vec = np.array([[1.0, 2.0]], dtype=np.float64)
        result = _normalize(vec)

        self.assertEqual(result.dtype, np.float32)


class SaveIndexTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp_dir = tempfile.TemporaryDirectory()
        self.output = Path(self._tmp_dir.name)
        self.chunks = [
            {"id": "c0", "text": "A", "path": "/a.md", "title": "A", "heading": None, "chunk_index": 0},
        ]
        self.embeddings = np.array([[1.0, 0.0]], dtype=np.float32)

    def tearDown(self) -> None:
        self._tmp_dir.cleanup()

    def test_save_index_overwrites_existing(self) -> None:
        old_dir = self.output / "existing"
        old_dir.mkdir()
        (old_dir / "docs.jsonl").write_text("old", encoding="utf-8")
        (old_dir / "index.npz").write_text("old", encoding="utf-8")

        _save_index(old_dir, self.chunks, self.embeddings)

        # Should have overwritten
        with (old_dir / "docs.jsonl").open("r", encoding="utf-8") as f:
            self.assertEqual(json.loads(f.readline())["id"], "c0")


# ---------------------------------------------------------------------------
#  Search tests
# ---------------------------------------------------------------------------


class LoadIndexTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp_dir = tempfile.TemporaryDirectory()
        self.index_dir = Path(self._tmp_dir.name)
        self.chunks = [
            {"id": "c0", "text": "Hello", "path": "/a.md", "title": "A", "heading": "H1", "chunk_index": 0},
            {"id": "c1", "text": "World", "path": "/a.md", "title": "A", "heading": "H2", "chunk_index": 1},
        ]
        self.embeddings = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
        _save_index(self.index_dir, self.chunks, self.embeddings)

    def tearDown(self) -> None:
        self._tmp_dir.cleanup()

    def test_load_index_returns_chunks_and_embeddings(self) -> None:
        chunks, embeddings = load_index(self.index_dir)

        self.assertEqual(len(chunks), 2)
        self.assertEqual(embeddings.shape, (2, 2))
        self.assertEqual(chunks[0]["id"], "c0")
        self.assertEqual(chunks[1]["id"], "c1")

    def test_load_index_missing_directory(self) -> None:
        missing = self.index_dir / "nonexistent"
        with self.assertRaises(FileNotFoundError):
            load_index(missing)

    def test_load_index_missing_docs_jsonl(self) -> None:
        (self.index_dir / "docs.jsonl").unlink()
        with self.assertRaises(FileNotFoundError):
            load_index(self.index_dir)

    def test_load_index_missing_index_npz(self) -> None:
        (self.index_dir / "index.npz").unlink()
        with self.assertRaises(FileNotFoundError):
            load_index(self.index_dir)

    def test_load_index_empty_docs_jsonl(self) -> None:
        with (self.index_dir / "docs.jsonl").open("w", encoding="utf-8") as f:
            f.write("")
        with self.assertRaises(ValueError):
            load_index(self.index_dir)

    def test_load_index_mismatch_lengths(self) -> None:
        extra = {"id": "c2", "text": "Extra", "path": "/a.md", "title": "A", "heading": None, "chunk_index": 2}
        with (self.index_dir / "docs.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(extra) + "\n")
        with self.assertRaises(ValueError):
            load_index(self.index_dir)


class SearchIndexTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp_dir = tempfile.TemporaryDirectory()
        self.index_dir = Path(self._tmp_dir.name)
        self.chunks = [
            {"id": "c0", "text": "Hello world", "path": "/a.md", "title": "A", "heading": "H1", "chunk_index": 0},
            {"id": "c1", "text": "Foo bar baz", "path": "/a.md", "title": "A", "heading": "H2", "chunk_index": 1},
            {"id": "c2", "text": "More content here", "path": "/b.md", "title": "B", "heading": None, "chunk_index": 0},
        ]
        self.embedder = FakeEmbedder(dims=4)
        build_index(self.chunks, self.index_dir, self.embedder)

    def tearDown(self) -> None:
        self._tmp_dir.cleanup()

    def test_search_returns_top_k(self) -> None:
        results = search_index(self.index_dir, "test query", self.embedder, top_k=2)

        self.assertEqual(len(results), 2)
        for r in results:
            self.assertIn("score", r)

    def test_search_results_sorted_by_score_desc(self) -> None:
        results = search_index(self.index_dir, "test query", self.embedder, top_k=3)

        scores = [r["score"] for r in results]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_search_includes_metadata(self) -> None:
        results = search_index(self.index_dir, "test query", self.embedder, top_k=1)

        self.assertIn("id", results[0])
        self.assertIn("path", results[0])
        self.assertIn("title", results[0])
        self.assertIn("heading", results[0])
        self.assertIn("chunk_index", results[0])
        self.assertIn("text", results[0])
        self.assertIn("score", results[0])

    def test_search_top_k_exceeds_chunks(self) -> None:
        results = search_index(self.index_dir, "query", self.embedder, top_k=100)

        self.assertEqual(len(results), 3)

    def test_search_top_k_invalid_raises(self) -> None:
        with self.assertRaises(ValueError):
            search_index(self.index_dir, "query", self.embedder, top_k=0)

    def test_search_missing_index(self) -> None:
        missing = self.index_dir / "nonexistent"
        with self.assertRaises(FileNotFoundError):
            search_index(missing, "query", self.embedder)

    def test_search_query_prefix_applied(self) -> None:
        class PrefixCapture(FakeEmbedder):
            def __init__(self) -> None:
                super().__init__(dims=4)
                self.last_texts: list[str] | None = None

            def embed(self, texts: list[str]) -> np.ndarray:
                self.last_texts = texts
                return super().embed(texts)

        capture = PrefixCapture()
        search_index(self.index_dir, "my query", capture, top_k=1)

        self.assertIsNotNone(capture.last_texts)
        text = capture.last_texts[0]
        self.assertTrue(text.startswith(DEFAULT_QUERY_PREFIX))
        self.assertIn("my query", text)

    def test_search_read_only_does_not_modify(self) -> None:
        before_mtime = (self.index_dir / "docs.jsonl").stat().st_mtime
        search_index(self.index_dir, "query", self.embedder, top_k=1)
        after_mtime = (self.index_dir / "docs.jsonl").stat().st_mtime

        self.assertEqual(before_mtime, after_mtime)
