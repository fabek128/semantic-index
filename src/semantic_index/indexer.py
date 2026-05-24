"""Local embedding index build and persistence.

Builds deterministic ``docs.jsonl`` + ``index.npz`` from chunked Markdown
content using a pluggable embedder.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

import numpy as np


class Embedder(Protocol):
    """Protocol for embedders used by ``build_index``."""

    def embed(self, texts: list[str]) -> np.ndarray:
        """Return a float32 array of shape ``(len(texts), dims)``."""
        ...


def build_index(
    chunks: list[dict],
    output_dir: Path,
    embedder: Embedder,
) -> None:
    """Embed chunks, normalize vectors, and persist to *output_dir*.

    Parameters
    ----------
    chunks:
        List of chunk dicts (as returned by ``chunk_markdown``).
    output_dir:
        Target directory for ``docs.jsonl`` and ``index.npz``.
    embedder:
        An ``Embedder`` instance.

    Raises
    ------
    ValueError
        If *chunks* is empty.
    OSError
        If the output directory cannot be created or written to.
    """
    if not chunks:
        raise ValueError("Cannot build index from an empty chunk list")

    texts = [c["text"] for c in chunks]
    embeddings = embedder.embed(texts)
    embeddings = _normalize(embeddings)
    _save_index(output_dir, chunks, embeddings)


def _normalize(vectors: np.ndarray) -> np.ndarray:
    """Normalize vectors in-place for cosine similarity via dot product."""
    vectors = vectors.astype(np.float32, copy=False)
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    vectors /= norms
    return vectors


def _save_index(
    output_dir: Path,
    chunks: list[dict],
    embeddings: np.ndarray,
) -> None:
    """Persist chunk metadata and embeddings to *output_dir*."""
    output_dir.mkdir(parents=True, exist_ok=True)

    np.savez_compressed(output_dir / "index.npz", embeddings=embeddings)

    docs_path = output_dir / "docs.jsonl"
    with docs_path.open("w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
#  Production embedder
# ---------------------------------------------------------------------------


class FastEmbedEmbedder:
    """Embedder backed by ``fastembed.TextEmbedding``.

    The model is downloaded on first use and cached locally by
    ``fastembed``.  Note content is **never** sent to external services.
    """

    DEFAULT_MODEL: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

    def __init__(self, model_name: str | None = None) -> None:
        from fastembed import TextEmbedding  # type: ignore[import-untyped]

        model = model_name or self.DEFAULT_MODEL
        self._model = TextEmbedding(model_name=model)

    def embed(self, texts: list[str]) -> np.ndarray:
        return np.array(list(self._model.embed(texts)), dtype=np.float32)
