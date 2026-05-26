#!/usr/bin/env python3
"""Generate a synthetic Markdown corpus for beta validation.

Usage:
    python3 scripts/generate-corpus.py [--out DIR] [--seed N]

Output:
    Directory tree with Markdown files covering nested dirs, Unicode,
    long sections, code-like identifiers, and repeated terms.
"""

from __future__ import annotations

import argparse
import random
import string
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Corpus configuration
# ---------------------------------------------------------------------------

DIR_STRUCTURE: list[tuple[str, int]] = [
    ("recipes", 3),
    ("recipes/italian", 2),
    ("recipes/asian", 2),
    ("dev", 4),
    ("dev/python", 3),
    ("dev/cli", 2),
    ("science", 2),
    ("personal", 3),
]

LONG_SECTION_PARAS = 30  # paragraphs per long section
MAX_WORDS_PER_PARA = 40

# Reusable content blocks make the corpus non-sensitive and deterministic
CONTENT_BLOCKS: dict[str, list[str]] = {
    "recipes": [
        "Heat the pan over medium flame before adding oil.",
        "Season generously with salt and freshly ground pepper.",
        "Let the dish rest for five minutes before serving.",
    ],
    "recipes/italian": [
        "Pasta should be cooked al dente in salted boiling water.",
        "Risotto requires constant stirring for the perfect creaminess.",
        "Parmigiano-Reggiano adds umami to any tomato-based sauce.",
    ],
    "recipes/asian": [
        "Sauté ginger and garlic until fragrant before adding protein.",
        "Soy sauce, rice vinegar, and sesame oil form a balanced dressing.",
        "Bamboo shoots and water chestnuts add texture to stir-fries.",
    ],
    "dev": [
        "Always validate user input before processing it.",
        "Write unit tests before implementing new features.",
        "Use version control for all project code.",
    ],
    "dev/python": [
        "List comprehensions are preferred over map and filter.",
        "Type hints improve code readability and tooling support.",
        "Context managers handle resource cleanup automatically.",
    ],
    "dev/cli": [
        "Use argparse for command-line argument parsing.",
        "Return non-zero exit codes on errors.",
        "Print usage information when required arguments are missing.",
    ],
    "science": [
        "The null hypothesis should be stated before data collection.",
        "Effect size matters more than p-value for practical significance.",
        "Replication studies strengthen the reliability of findings.",
    ],
    "personal": [
        "Morning routines set the tone for a productive day.",
        "Regular exercise improves both physical and mental health.",
        "Reading diverse perspectives broadens understanding.",
        "日本語のメモも検索できることを確認する。",  # Unicode
        "Les notes en français sont également prises en charge.",  # Unicode
        "Український текст також підтримується.",  # Unicode
    ],
}

CODE_IDENTIFIERS = [
    "snake_case_function", "CamelCaseClass", "dotted.path.ref",
    "HTTP_STATUS_OK", "MAX_BUFFER_SIZE", "_internal_helper",
    "process_data_v2", "ConfigParser", "XMLParserMixin",
    "thread_local_storage", "AbstractBaseClass",
]


def _paragraph(words: list[str], rng: random.Random) -> str:
    n = rng.randint(5, MAX_WORDS_PER_PARA)
    return " ".join(rng.choices(words, k=n)) + "."


def _section(
    title: str,
    body_words: list[str],
    rng: random.Random,
    num_paras: int = 3,
) -> str:
    lines = [f"## {title}", ""]
    for _ in range(num_paras):
        lines.append(_paragraph(body_words, rng))
        lines.append("")
    return "\n".join(lines)


def generate_corpus(out_dir: Path, seed: int = 42) -> None:
    rng = random.Random(seed)

    for dir_path, file_count in DIR_STRUCTURE:
        full_dir = out_dir / dir_path
        full_dir.mkdir(parents=True, exist_ok=True)

        base_words = CONTENT_BLOCKS.get(dir_path, CONTENT_BLOCKS["dev"])
        # Also include parent words for thematic overlap
        parent = str(Path(dir_path).parent)
        if parent in CONTENT_BLOCKS:
            base_words = base_words + CONTENT_BLOCKS[parent]

        # Include code identifiers thematically in dev paths
        if dir_path.startswith("dev"):
            base_words = base_words + CODE_IDENTIFIERS

        for i in range(file_count):
            title = f"Document {i + 1} — {dir_path.replace('/', ' ').title()}"
            doc_lines = [f"# {title}", ""]

            # Intro paragraph
            doc_lines.append(_paragraph(base_words, rng))
            doc_lines.append("")

            # Sections with varying length
            for si in range(rng.randint(2, 5)):
                if si == 0 and dir_path.startswith("dev"):
                    section_title = rng.choice(CODE_IDENTIFIERS)
                    num_paras = 1
                elif si == 0:
                    section_title = f"Overview"
                    num_paras = 2
                else:
                    section_title = (
                        f"{'Details'} {si}" if rng.random() < 0.5
                        else f"Section {string.ascii_uppercase[si]}"
                    )
                    num_paras = (LONG_SECTION_PARAS if si == 1 and i == 0 else 2)
                    # Force long section only once

                doc_lines.append(_section(
                    section_title, base_words, rng, num_paras
                ))

            # Tags / footer
            tags = rng.sample(CODE_IDENTIFIERS, k=min(3, len(CODE_IDENTIFIERS)))
            doc_lines.append(f"Tags: {', '.join(tags)}")
            doc_lines.append("")

            file_path = full_dir / f"doc-{i + 1}.md"
            file_path.write_text("\n".join(doc_lines), encoding="utf-8")

    # One extra file with only Unicode content to test encoding
    unicode_dir = out_dir / "unicode"
    unicode_dir.mkdir(exist_ok=True)
    unicode_file = unicode_dir / "mixed-langs.md"
    unicode_file.write_text(
        "# Mixed Languages\n\n"
        "English text with 日本語混じり.\n\n"
        "Français et русский aussi.\n\n"
        "Emoji: 🚀 ✅ 📝\n\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a synthetic Markdown corpus."
    )
    parser.add_argument("--out", default="/tmp/si-corpus", help="Output dir")
    parser.add_argument("--seed", type=int, default=42, help="RNG seed")
    args = parser.parse_args()

    out_dir = Path(args.out)
    if out_dir.exists():
        import shutil
        shutil.rmtree(out_dir)

    t0 = time.time()
    generate_corpus(out_dir, seed=args.seed)
    elapsed = time.time() - t0

    md_files = list(out_dir.rglob("*.md"))
    total_bytes = sum(f.stat().st_size for f in md_files)
    dirs = sorted({f.parent for f in md_files})

    print(f"Corpus generated in: {out_dir}")
    print(f"  Directories:  {len(dirs)}")
    print(f"  Files:        {len(md_files)}")
    print(f"  Total size:   {total_bytes:,} bytes")
    print(f"  Generation:   {elapsed:.2f}s")

    # Print directory tree
    print(f"\nDirectory tree:")
    for d in sorted(dirs):
        indent = "  " * len(d.relative_to(out_dir).parts)
        print(f"{indent}{d.name}/")
        for f in sorted(d.iterdir()):
            if f.suffix == ".md":
                print(f"{indent}  {f.name}")


if __name__ == "__main__":
    main()
