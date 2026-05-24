"""Local embedding index build, persistence, and search.

Builds and searches deterministic ``docs.jsonl`` + ``index.npz`` from
chunked Markdown content using a pluggable embedder.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

import numpy as np


DEFAULT_QUERY_PREFIX = "query: "


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
#  Search
# ---------------------------------------------------------------------------


def load_index(index_dir: Path) -> tuple[list[dict], np.ndarray]:
    """Load ``docs.jsonl`` and ``index.npz`` from *index_dir*.

    Returns
    -------
    Tuple of (chunks, embeddings) where *chunks* is the list of metadata
    dicts and *embeddings* is the normalized float32 array.

    Raises
    ------
    FileNotFoundError
        If the index directory or required files are missing.
    ValueError
        If files are malformed.
    """
    docs_path = index_dir / "docs.jsonl"
    npz_path = index_dir / "index.npz"

    if not docs_path.exists():
        raise FileNotFoundError(f"Index file not found: {docs_path}")
    if not npz_path.exists():
        raise FileNotFoundError(f"Index file not found: {npz_path}")

    chunks: list[dict] = []
    with docs_path.open("r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped:
                continue
            try:
                chunks.append(json.loads(stripped))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Malformed docs.jsonl: {exc}") from exc

    if not chunks:
        raise ValueError("docs.jsonl is empty")

    data = np.load(npz_path)
    if "embeddings" not in data:
        raise ValueError("index.npz missing 'embeddings' key")
    embeddings = data["embeddings"]

    if embeddings.shape[0] != len(chunks):
        raise ValueError(
            f"Chunk/embedding mismatch: {len(chunks)} chunks vs "
            f"{embeddings.shape[0]} embeddings"
        )

    return chunks, embeddings


def search_index(
    index_dir: Path,
    query: str,
    embedder: Embedder,
    top_k: int = 5,
    query_prefix: str = DEFAULT_QUERY_PREFIX,
) -> list[dict]:
    """Search an existing index and return the top-*k* results.

    Parameters
    ----------
    index_dir:
        Directory containing ``docs.jsonl`` and ``index.npz``.
    query:
        Free-text search query.
    embedder:
        An ``Embedder`` instance (must use the same model as the index).
    top_k:
        Maximum number of results to return.
    query_prefix:
        Prefix prepended to the query before embedding
        (e.g. the E5 ``query: `` prefix).

    Returns
    -------
    List of result dicts sorted by descending score, each containing:
        score, id, path, title, heading, chunk_index, text
    """
    if top_k < 1:
        raise ValueError(f"top_k must be >= 1, got {top_k}")

    chunks, embeddings = load_index(index_dir)

    texts = [f"{query_prefix}{query}"]
    q_vec = embedder.embed(texts)
    q_vec = _normalize(q_vec)

    scores = (q_vec @ embeddings.T)[0]
    top_indices = np.argsort(scores)[-top_k:][::-1]

    results: list[dict] = []
    for idx in top_indices:
        results.append({
            "score": float(scores[idx]),
            **chunks[idx],
        })

    return results


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
