"""Local lexical search over chunk text and metadata.

No external dependencies.  Simple term-frequency scoring with
length normalisation.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Sequence

_WORD_RE = re.compile(r"[a-zA-Z0-9]+")


def _tokenize(text: str) -> list[str]:
    return [m.group().lower() for m in _WORD_RE.finditer(text)]


def score_query(
    query: str,
    chunks: Sequence[dict],
) -> list[float]:
    """Return a lexical similarity score in ``[0, 1]`` per chunk.

    The score is the fraction of query terms that appear in each chunk's
    text, heading, or title (case-insensitive word-boundary match).
    Heading/title matches receive a small bonus.
    """
    query_terms = _tokenize(query)
    if not query_terms:
        return [0.0] * len(chunks)

    scores: list[float] = []
    for ch in chunks:
        text_terms = set(_tokenize(ch.get("text", "")))
        heading_terms = set(_tokenize(ch.get("heading") or ""))
        title_terms = set(_tokenize(ch.get("title") or ""))

        hit_count = 0
        for qt in query_terms:
            if qt in text_terms:
                hit_count += 1
                continue
            if qt in heading_terms or qt in title_terms:
                hit_count += 0.5
                continue

        scores.append(hit_count / len(query_terms))

    return scores


def search_index(
    query: str,
    chunks: Sequence[dict],
    top_k: int = 5,
) -> list[dict]:
    """Return the top-*k* chunks ranked by lexical similarity.

    Results have the same schema as ``search_index`` from
    ``indexer.py``: ``score``, chunk metadata.
    """
    if top_k < 1:
        raise ValueError(f"top_k must be >= 1, got {top_k}")

    scores = score_query(query, chunks)
    indexed = list(enumerate(scores))
    indexed.sort(key=lambda x: x[1], reverse=True)

    results: list[dict] = []
    for idx, score in indexed[:top_k]:
        results.append({
            "score": score,
            **chunks[idx],
        })
    return results
