"""Unit tests for the lexical search module."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))


from semantic_index.lexical import score_query, search_index


_CHUNKS = [
    {"id": "c0", "text": "The quick brown fox", "title": "Animals", "heading": "Mammals"},
    {"id": "c1", "text": "Python is a programming language", "title": "Programming", "heading": "Languages"},
    {"id": "c2", "text": "The fox is quick and brown", "title": "Colors", "heading": None},
    {"id": "c3", "text": "Error code 0xFF: connection refused", "title": "Networking", "heading": "Errors"},
]


class LexicalScoreTests(unittest.TestCase):
    def test_exact_term_match(self) -> None:
        scores = score_query("fox", _CHUNKS)
        self.assertGreater(scores[0], 0)
        self.assertGreater(scores[2], 0)
        # c0 and c2 both have "fox"
        self.assertEqual(scores[0], scores[2])

    def test_no_match(self) -> None:
        scores = score_query("zzzznotfound", _CHUNKS)
        for s in scores:
            self.assertEqual(s, 0.0)

    def test_multi_term_query(self) -> None:
        scores = score_query("programming language", _CHUNKS)
        # c1 has both terms
        self.assertGreater(scores[1], 0)
        # Other chunks have neither
        for i in (0, 2):
            self.assertEqual(scores[i], 0.0)

    def test_partial_term_match(self) -> None:
        scores = score_query("python error", _CHUNKS)
        # c1 has "python" in text (term 1/2 = 0.5)
        self.assertEqual(scores[1], 0.5)
        # c3 has no term match ("error" not in text, "errors" in heading but not exact)
        self.assertEqual(scores[3], 0.0)

    def test_empty_query(self) -> None:
        scores = score_query("", _CHUNKS)
        for s in scores:
            self.assertEqual(s, 0.0)

    def test_heading_match_exact(self) -> None:
        scores = score_query("errors", _CHUNKS)
        # c3 heading is "Errors" (heading match = 0.5 weight per term)
        self.assertGreater(scores[3], 0)
        self.assertAlmostEqual(scores[3], 0.5)


class LexicalSearchTests(unittest.TestCase):
    def test_search_returns_top_k(self) -> None:
        results = search_index("fox", _CHUNKS, top_k=1)
        self.assertEqual(len(results), 1)

    def test_search_returns_all_if_top_k_exceeds(self) -> None:
        results = search_index("fox", _CHUNKS, top_k=100)
        # All chunks are returned; zero-score items stay at the end
        self.assertEqual(len(results), 4)

    def test_search_sorted_by_score_desc(self) -> None:
        results = search_index("fox quick brown", _CHUNKS, top_k=4)
        scores = [r["score"] for r in results]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_search_has_metadata(self) -> None:
        results = search_index("fox", _CHUNKS, top_k=1)
        self.assertIn("id", results[0])
        self.assertIn("text", results[0])
        self.assertIn("score", results[0])

    def test_search_top_k_invalid_raises(self) -> None:
        with self.assertRaises(ValueError):
            search_index("test", _CHUNKS, top_k=0)

    def test_search_no_match_returns_empty_scores(self) -> None:
        results = search_index("zzzznotfound", _CHUNKS, top_k=2)
        self.assertEqual(len(results), 2)
        for r in results:
            self.assertEqual(r["score"], 0.0)
