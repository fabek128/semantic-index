"""Local embedding index build, persistence, and search.

Builds and searches deterministic ``docs.jsonl`` + ``index.npz`` from
chunked Markdown content using a pluggable embedder.
"""

from __future__ import annotations

import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

import numpy as np

from semantic_index import __version__


DEFAULT_QUERY_PREFIX = ""
"""Default prefix prepended to search queries before embedding.

``""`` (no prefix) for the default model
``sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2``.
Set to ``"query: "`` when using E5-family models, which require
separate prefixes for queries and passages.
"""
MANIFEST_SCHEMA_VERSION = 1


class Embedder(Protocol):
    """Protocol for embedders used by ``build_index``."""

    def embed(self, texts: list[str]) -> np.ndarray:
        """Return a float32 array of shape ``(len(texts), dims)``."""
        ...


def build_index(
    chunks: list[dict],
    output_dir: Path,
    embedder: Embedder,
    *,
    model_name: str | None = None,
    file_count: int | None = None,
    source_dirs: list[str] | None = None,
    max_chars: int = 1800,
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
    model_name:
        Optional name of the embedding model (stored in manifest).
    file_count:
        Optional number of source files discovered.
    source_dirs:
        Optional list of source directories.
    max_chars:
        Maximum chunk size used during chunking (stored in manifest).

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
    _save_index(output_dir, chunks, embeddings, model_name=model_name, file_count=file_count, source_dirs=source_dirs, max_chars=max_chars)


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
    *,
    model_name: str | None = None,
    file_count: int | None = None,
    source_dirs: list[str] | None = None,
    max_chars: int = 1800,
) -> None:
    """Persist chunk metadata and embeddings to *output_dir*.

    Files are written to a temporary subdirectory first and then renamed
    into place.  If any write fails, the temporary directory is removed
    and the original index (if any) is left untouched.

    .. warning::

       This protects against write failures but is **not** a fully
       transactional multi-file commit.  A crash between consecutive
       ``replace()`` calls can leave ``index.npz``, ``docs.jsonl``, and
       ``manifest.json`` out of sync.  ``load_index`` detects these
       inconsistent states and raises a clear error.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    tmp_tag = f".tmp_{os.urandom(4).hex()}"
    tmp_dir = output_dir / tmp_tag
    tmp_dir.mkdir()

    try:
        np.savez_compressed(tmp_dir / "index.npz", embeddings=embeddings)

        with (tmp_dir / "docs.jsonl").open("w", encoding="utf-8") as f:
            for chunk in chunks:
                f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

        _save_manifest(
            tmp_dir,
            model_name=model_name,
            model_dimensions=embeddings.shape[1],
            chunk_count=len(chunks),
            file_count=file_count,
            source_dirs=source_dirs,
            max_chars=max_chars,
        )

        # Atomic rename into place
        for name in ("index.npz", "docs.jsonl", "manifest.json"):
            (tmp_dir / name).replace(output_dir / name)
    except BaseException:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise

    shutil.rmtree(tmp_dir, ignore_errors=True)


def _save_manifest(
    output_dir: Path,
    *,
    model_name: str | None = None,
    model_dimensions: int | None = None,
    chunk_count: int = 0,
    file_count: int | None = None,
    source_dirs: list[str] | None = None,
    max_chars: int = 1800,
) -> dict:
    """Write ``manifest.json`` to *output_dir* and return the manifest."""
    manifest: dict = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "package_version": __version__,
        "model_name": model_name,
        "embedding_dimensions": model_dimensions,
        "chunk_count": chunk_count,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "chunking": {"max_chars": max_chars},
        "source": {
            "file_count": file_count,
            "directories": sorted(source_dirs) if source_dirs else None,
        },
    }
    manifest_path = output_dir / "manifest.json"
    with manifest_path.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return manifest


def load_manifest(index_dir: Path) -> dict:
    """Load and validate ``manifest.json`` from *index_dir*.

    Returns
    -------
    Manifest dict.

    Raises
    ------
    FileNotFoundError
        If the manifest file is missing.
    ValueError
        If the manifest is malformed or has an unsupported schema version.
    """
    manifest_path = index_dir / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(
            f"Index metadata not found: {manifest_path}. "
            f"This index was built with an older version of semantic-index. "
            f"Rebuild with `semantic-index build` to add metadata."
        )

    with manifest_path.open("r", encoding="utf-8") as f:
        try:
            manifest = json.load(f)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Malformed manifest.json: {exc}"
            ) from exc

    if manifest.get("schema_version") != MANIFEST_SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported manifest schema version {manifest.get('schema_version')} "
            f"(expected {MANIFEST_SCHEMA_VERSION}). "
            f"Rebuild the index with a newer version of semantic-index."
        )

    return manifest


# ---------------------------------------------------------------------------
#  Search
# ---------------------------------------------------------------------------


def load_index(index_dir: Path) -> tuple[list[dict], np.ndarray]:
    """Load manifest, ``docs.jsonl`` and ``index.npz`` from *index_dir*.

    Returns
    -------
    Tuple of (chunks, embeddings) where *chunks* is the list of metadata
    dicts and *embeddings* is the normalized float32 array.

    Raises
    ------
    FileNotFoundError
        If the index directory, manifest, or required files are missing.
    ValueError
        If files are malformed, corrupt, or inconsistent.
    """
    manifest = load_manifest(index_dir)

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

    try:
        data = np.load(npz_path, allow_pickle=False)
    except (OSError, ValueError) as exc:
        raise ValueError(f"Failed to load index file {npz_path}: {exc}") from exc

    if "embeddings" not in data:
        raise ValueError("index.npz missing 'embeddings' key")
    embeddings = data["embeddings"]

    if embeddings.ndim != 2:
        raise ValueError(
            f"Expected a 2D embedding matrix, but index.npz contains "
            f"a {embeddings.ndim}D array. The index may be corrupted. "
            f"Rebuild with `semantic-index build`."
        )

    if embeddings.dtype.kind not in ("f",):
        raise ValueError(
            f"Expected float embeddings, but index.npz has dtype "
            f"{embeddings.dtype}. The index may be corrupted. "
            f"Rebuild with `semantic-index build`."
        )

    manifest_dims = manifest.get("embedding_dimensions")
    if manifest_dims is not None and embeddings.shape[1] != manifest_dims:
        raise ValueError(
            f"Embedding dimension mismatch: loaded embeddings have "
            f"{embeddings.shape[1]} dimensions, but manifest reports "
            f"{manifest_dims}. The index may be corrupted. "
            f"Rebuild with `semantic-index build`."
        )

    manifest_chunk_count = manifest.get("chunk_count")
    if manifest_chunk_count is not None and embeddings.shape[0] != manifest_chunk_count:
        raise ValueError(
            f"chunk_count mismatch: manifest reports {manifest_chunk_count} "
            f"chunks, but index.npz has {embeddings.shape[0]} embeddings. "
            f"The index may be inconsistent. Rebuild with `semantic-index build`."
        )

    if manifest_chunk_count is not None and len(chunks) != manifest_chunk_count:
        raise ValueError(
            f"chunk_count mismatch: manifest reports {manifest_chunk_count} "
            f"chunks, but docs.jsonl has {len(chunks)} entries. "
            f"The index may be inconsistent. Rebuild with `semantic-index build`."
        )

    if embeddings.shape[0] != len(chunks):
        raise ValueError(
            f"Chunk/embedding count mismatch: {len(chunks)} chunks vs "
            f"{embeddings.shape[0]} embeddings. "
            f"The index may be inconsistent. Rebuild with `semantic-index build`."
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
        Prefix prepended to the query before embedding.
        The default (``""``) is correct for the built-in default model.
        Set to ``"query: "`` for E5-family models, which require a
        separate ``"query: "`` prefix.

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
    if q_vec.shape[1] != embeddings.shape[1]:
        raise ValueError(
            f"Embedder produces {q_vec.shape[1]}-dimensional vectors, "
            f"but the index has {embeddings.shape[1]} dimensions. "
            f"The search model differs from the one used during indexing."
        )
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


def hybrid_search(
    index_dir: Path,
    query: str,
    embedder: Embedder,
    top_k: int = 5,
    query_prefix: str = DEFAULT_QUERY_PREFIX,
    semantic_weight: float = 0.5,
) -> list[dict]:
    """Hybrid search combining semantic (cosine) and lexical scores.

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
        Prefix prepended to the query before embedding.
    semantic_weight:
        Weight for the semantic (cosine) score.  Lexical weight is
        ``1 - semantic_weight``.  Default 0.5 (equal weight).
    """
    from semantic_index.lexical import score_query as lexical_score_query

    if top_k < 1:
        raise ValueError(f"top_k must be >= 1, got {top_k}")
    if not 0 <= semantic_weight <= 1:
        raise ValueError(f"semantic_weight must be 0-1, got {semantic_weight}")

    chunks, embeddings = load_index(index_dir)

    # Semantic scores
    texts = [f"{query_prefix}{query}"]
    q_vec = embedder.embed(texts)
    if q_vec.shape[1] != embeddings.shape[1]:
        raise ValueError(
            f"Embedder produces {q_vec.shape[1]}-dimensional vectors, "
            f"but the index has {embeddings.shape[1]} dimensions. "
            f"The search model differs from the one used during indexing."
        )
    q_vec = _normalize(q_vec)
    semantic_scores = (q_vec @ embeddings.T)[0].tolist()
    semantic_scores = [float(s) for s in semantic_scores]

    # Lexical scores
    lexical_scores = lexical_score_query(query, chunks)
    max_lex = max(lexical_scores) if lexical_scores else 1.0
    if max_lex > 0:
        lexical_scores = [s / max_lex for s in lexical_scores]
    lexical_weight = 1.0 - semantic_weight

    # Combine
    combined = [
        semantic_weight * sem + lexical_weight * lex
        for sem, lex in zip(semantic_scores, lexical_scores)
    ]
    top_indices = np.argsort(combined)[-top_k:][::-1]

    results: list[dict] = []
    for idx in top_indices:
        results.append({
            "score": float(combined[idx]),
            "semantic_score": float(semantic_scores[idx]),
            "lexical_score": float(lexical_scores[idx] * max_lex),
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
    """Default embedding model (384 dims, multilingual, no prefix needed)."""

    def __init__(self, model_name: str | None = None) -> None:
        from fastembed import TextEmbedding  # type: ignore[import-untyped]

        model = model_name or self.DEFAULT_MODEL
        self.model_name: str = model
        self._model = TextEmbedding(model_name=model)

    def embed(self, texts: list[str]) -> np.ndarray:
        return np.array(list(self._model.embed(texts)), dtype=np.float32)
