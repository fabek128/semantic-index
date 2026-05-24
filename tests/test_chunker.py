"""Unit tests for the Markdown chunker module."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from semantic_index.chunker import chunk_markdown


class ChunkerTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        )
        self.path = Path(self._tmp.name)

    def tearDown(self) -> None:
        self.path.unlink(missing_ok=True)

    def _write(self, content: str) -> None:
        self.path.write_text(content, encoding="utf-8")

    # -- Basic heading splitting --

    def test_single_h1(self) -> None:
        self._write("# Title\n\nSome content.")
        chunks = chunk_markdown(self.path)

        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0]["heading"], "Title")
        self.assertEqual(chunks[0]["title"], "Title")
        self.assertEqual(chunks[0]["text"], "Some content.")

    def test_multiple_headings(self) -> None:
        self._write("# Title\n\nIntro.\n\n## Section 1\n\nBody A.\n\n### Sub\n\nBody B.")
        chunks = chunk_markdown(self.path)

        self.assertEqual(len(chunks), 3)
        self.assertEqual(chunks[0]["heading"], "Title")
        self.assertEqual(chunks[0]["text"], "Intro.")
        self.assertEqual(chunks[1]["heading"], "Section 1")
        self.assertEqual(chunks[1]["text"], "Body A.")
        self.assertEqual(chunks[2]["heading"], "Sub")
        self.assertEqual(chunks[2]["text"], "Body B.")

    def test_no_heading(self) -> None:
        self._write("Just a paragraph.\n\nAnother paragraph.")
        chunks = chunk_markdown(self.path)

        self.assertEqual(len(chunks), 1)
        self.assertIsNone(chunks[0]["heading"])
        self.assertEqual(chunks[0]["title"], self.path.stem)
        self.assertIn("Just a paragraph.", chunks[0]["text"])

    def test_no_h1_title_falls_back_to_stem(self) -> None:
        self._write("## Section\n\nContent.")
        chunks = chunk_markdown(self.path)

        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0]["title"], self.path.stem)
        self.assertEqual(chunks[0]["heading"], "Section")

    def test_empty_file(self) -> None:
        self._write("")
        chunks = chunk_markdown(self.path)

        self.assertEqual(chunks, [])

    def test_only_headings(self) -> None:
        self._write("# A\n\n## B\n\n### C")
        chunks = chunk_markdown(self.path)

        # Each heading creates an empty-content section -> no chunks
        self.assertEqual(chunks, [])

    # -- Chunk id --

    def test_chunk_ids_are_deterministic(self) -> None:
        self._write("# Title\n\nA\n\n## S\n\nB")
        chunks_a = chunk_markdown(self.path)
        chunks_b = chunk_markdown(self.path)

        for ca, cb in zip(chunks_a, chunks_b):
            self.assertEqual(ca["id"], cb["id"])

    def test_chunk_ids_unique(self) -> None:
        self._write("# Title\n\nA\n\n## S\n\nB")
        chunks = chunk_markdown(self.path)

        ids = [c["id"] for c in chunks]
        self.assertEqual(len(ids), len(set(ids)))

    # -- Metadata --

    def test_metadata_fields_present(self) -> None:
        self._write("# Title\n\nContent.")
        chunks = chunk_markdown(self.path)

        self.assertEqual(len(chunks), 1)
        chunk = chunks[0]
        self.assertIn("id", chunk)
        self.assertIn("path", chunk)
        self.assertIn("title", chunk)
        self.assertIn("heading", chunk)
        self.assertIn("chunk_index", chunk)
        self.assertIn("text", chunk)

    def test_path_in_metadata(self) -> None:
        self._write("# Title\n\nContent.")
        chunks = chunk_markdown(self.path)

        self.assertEqual(chunks[0]["path"], str(self.path))

    def test_chunk_index_sequential(self) -> None:
        self._write("# A\n\nX\n\n## B\n\nY\n\n### C\n\nZ")
        chunks = chunk_markdown(self.path)

        for i, c in enumerate(chunks):
            self.assertEqual(c["chunk_index"], i)

    # -- Long sections / splitting --

    def test_section_exceeds_max_chars_paragraph_split(self) -> None:
        para_a = "A" * 1000
        para_b = "B" * 1000
        self._write(f"# Title\n\n{para_a}\n\n{para_b}")
        chunks = chunk_markdown(self.path, max_chars=1200)

        self.assertGreaterEqual(len(chunks), 2)
        # First chunk should contain para_a, second should contain para_b
        self.assertIn("A" * 1000, chunks[0]["text"])
        self.assertIn("B" * 1000, chunks[-1]["text"])

    def test_overlong_paragraph_split_by_lines(self) -> None:
        lines = "\n".join([f"Line {i} " + "-" * 200 for i in range(10)])
        self._write(f"# Title\n\n{lines}")
        chunks = chunk_markdown(self.path, max_chars=500)

        self.assertGreaterEqual(len(chunks), 2)

    def test_no_empty_chunks(self) -> None:
        self._write("# A\n\n\n\n## B\n\n\n\n### C\n\n")
        chunks = chunk_markdown(self.path)

        for c in chunks:
            self.assertNotEqual(c["text"].strip(), "")

    def test_many_short_paragraphs_under_one_heading(self) -> None:
        paragraphs = "\n\n".join([f"Para {i}." for i in range(20)])
        self._write(f"# Title\n\n{paragraphs}")
        chunks = chunk_markdown(self.path, max_chars=50)

        self.assertGreaterEqual(len(chunks), 2)
        total_text = " ".join(c["text"] for c in chunks)
        for i in range(20):
            self.assertIn(f"Para {i}.", total_text)

    # -- Edge cases --

    def test_unicode_content(self) -> None:
        self._write("# Título\n\nContenido con ñandú y café.")
        chunks = chunk_markdown(self.path)

        self.assertEqual(len(chunks), 1)
        self.assertIn("ñandú", chunks[0]["text"])

    def test_heading_levels_preserved(self) -> None:
        self._write("# H1\n\n## H2\n\n### H3")
        chunks = chunk_markdown(self.path)

        # No content => no chunks
        self.assertEqual(chunks, [])

    def test_heading_with_content_before_first_heading(self) -> None:
        self._write("Preamble.\n\n# Title\n\nBody.")
        chunks = chunk_markdown(self.path)

        self.assertEqual(len(chunks), 2)
        self.assertIsNone(chunks[0]["heading"])
        self.assertIn("Preamble.", chunks[0]["text"])
        self.assertEqual(chunks[1]["heading"], "Title")
        self.assertIn("Body.", chunks[1]["text"])

    def test_heading_is_not_h1_because_no_space(self) -> None:
        # "#NoSpace" is not a valid ATX heading per our parser
        self._write("#NoSpace\n\nContent.")
        chunks = chunk_markdown(self.path)

        self.assertEqual(len(chunks), 1)
        self.assertIsNone(chunks[0]["heading"])
        self.assertIn("#NoSpace", chunks[0]["text"])

    def test_non_md_suffix_raises(self) -> None:
        # chunk_markdown itself doesn't validate suffix, but reading should work
        self._write("# Title\n\nContent.")
        chunks = chunk_markdown(self.path)
        self.assertEqual(len(chunks), 1)

    def test_nonexistent_path_raises(self) -> None:
        missing = Path("/nonexistent/file.md")
        with self.assertRaises(FileNotFoundError):
            chunk_markdown(missing)
