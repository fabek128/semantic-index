"""Markdown chunking by ATX headings and approximate size."""

from __future__ import annotations

import hashlib
from pathlib import Path

ATX_HEADING_RE = "#"  # simple prefix check for speed


def chunk_markdown(
    path: Path,
    max_chars: int = 1800,
) -> list[dict]:
    """Split a Markdown file into metadata-rich chunks.

    Parameters
    ----------
    path:
        Path to the Markdown file.
    max_chars:
        Maximum approximate characters per chunk.

    Returns
    -------
    List of chunk dicts with keys:
        id, path, title, heading, chunk_index, text

    Raises
    ------
    FileNotFoundError
        If *path* does not exist.
    UnicodeDecodeError
        If the file is not valid UTF-8.
    """
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    title: str = _resolve_title(lines, path)
    file_id = hashlib.md5(str(path.resolve()).encode()).hexdigest()[:12]

    chunks: list[dict] = []
    sections = _split_by_headings(lines)

    for heading, section_lines in sections:
        heading = _clean_heading(heading) if heading is not None else None
        sub_chunks = _split_section(section_lines, max_chars)
        for idx, chunk_lines in enumerate(sub_chunks):
            chunk_text = "\n".join(chunk_lines).strip()
            if not chunk_text:
                continue
            chunk_index = len(chunks)
            chunks.append({
                "id": f"{file_id}_{chunk_index}",
                "path": str(path),
                "title": title,
                "heading": heading,
                "chunk_index": chunk_index,
                "text": chunk_text,
            })

    return chunks


def _resolve_title(lines: list[str], path: Path) -> str:
    """Extract the document title from the first H1 or fall back to the filename stem."""
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# ") and not stripped.startswith("##"):
            return stripped.lstrip("# ").strip()
    return path.stem


def _clean_heading(line: str) -> str:
    """Strip leading '#' markers and return the heading text."""
    return line.lstrip("# ").strip()


def _split_by_headings(
    lines: list[str],
) -> list[tuple[str | None, list[str]]]:
    """Split lines into (heading, content_lines) sections by ATX headings.

    Content before the first heading is assigned heading=None.
    """
    sections: list[tuple[str | None, list[str]]] = []
    current_heading: str | None = None
    current_lines: list[str] = []

    for line in lines:
        if line.strip().startswith("#") and _is_atx_heading(line):
            if current_lines or current_heading is not None:
                sections.append((current_heading, current_lines))
            current_heading = line.strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines or current_heading is not None:
        sections.append((current_heading, current_lines))

    return sections


def _is_atx_heading(line: str) -> bool:
    """Check if line is an ATX heading (starts with # and space)."""
    stripped = line.strip()
    # Must start with 1-6 # followed by a space
    if not stripped:
        return False
    idx = 0
    while idx < len(stripped) and stripped[idx] == "#":
        idx += 1
    if idx == 0 or idx > 6:
        return False
    if idx < len(stripped) and stripped[idx] == " ":
        return True
    return False


def _split_section(lines: list[str], max_chars: int) -> list[list[str]]:
    """Split a section's lines into chunks respecting *max_chars*.

    Handles paragraphs (double-newline separated blocks) and overlong
    paragraphs by line-level splitting.
    """
    if not lines:
        return []

    # Build paragraph blocks
    paragraphs = _split_paragraphs(lines)

    chunks: list[list[str]] = []
    buffer: list[str] = []
    buffer_len = 0

    def _flush() -> None:
        nonlocal buffer, buffer_len
        if buffer:
            chunks.append(buffer)
            buffer = []
            buffer_len = 0

    for para_lines in paragraphs:
        para_text = "\n".join(para_lines)
        para_len = len(para_text) + 1  # +1 for the trailing newline separator

        if not buffer:
            # Fresh buffer
            if para_len <= max_chars:
                buffer = para_lines
                buffer_len = para_len
            else:
                # Overlong paragraph: split by lines
                chunks.extend(_split_lines(para_lines, max_chars))
        else:
            if buffer_len + para_len <= max_chars:
                buffer.append("")
                buffer.extend(para_lines)
                buffer_len += para_len
            else:
                _flush()
                # Put the paragraph into a new buffer
                if para_len <= max_chars:
                    buffer = para_lines
                    buffer_len = para_len
                else:
                    chunks.extend(_split_lines(para_lines, max_chars))

    _flush()
    return chunks


def _split_paragraphs(lines: list[str]) -> list[list[str]]:
    """Group lines into paragraphs separated by blank lines."""
    paragraphs: list[list[str]] = []
    current: list[str] = []

    for line in lines:
        if line.strip() == "":
            if current:
                paragraphs.append(current)
                current = []
        else:
            current.append(line)

    if current:
        paragraphs.append(current)

    return paragraphs


def _split_lines(lines: list[str], max_chars: int) -> list[list[str]]:
    """Split a single paragraph (list of lines) into max_chars-sized chunks."""
    chunks: list[list[str]] = []
    buffer: list[str] = []
    buffer_len = 0

    for line in lines:
        line_len = len(line) + 1  # +1 for newline

        if line_len > max_chars:
            if buffer:
                chunks.append(buffer)
                buffer = []
                buffer_len = 0
            chunks.append([line])
            continue

        if not buffer:
            buffer = [line]
            buffer_len = line_len
        elif buffer_len + line_len <= max_chars:
            buffer.append(line)
            buffer_len += line_len
        else:
            chunks.append(buffer)
            buffer = [line]
            buffer_len = line_len

    if buffer:
        chunks.append(buffer)

    return chunks
