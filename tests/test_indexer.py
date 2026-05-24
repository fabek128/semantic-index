"""Unit tests for the embedding index module."""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from semantic_index.indexer import (
    _normalize,
    _save_index,
    build_index,
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
