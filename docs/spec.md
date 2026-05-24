# Embeddings in Python — Fast and lightweight pipeline

> A practical recipe for building an embeddings pipeline with similarity search, optimized to be fast, simple, and memory efficient.

## Quick recommendation

If you want something **easy to implement, database-free, and fully in memory**, use:

```text
fastembed + numpy + npz/jsonl
```

Recommended default for Spanish/multilingual notes:

```text
intfloat/multilingual-e5-small
```

Flow:

1. Split documents into chunks.
2. Embed documents with the `passage: ` prefix.
3. Normalize embeddings.
4. Search with dot product using `numpy`.
5. Optionally save to `index.npz` + `docs.jsonl`.

Do not add ChromaDB, LanceDB, or FAISS at the beginning. Add them only if volume or requirements justify them.

---

## ⚠️ Do not use large LLMs for embeddings

An earlier version of this document proposed `Qwen/Qwen-7B` through `transformers`. **That is overkill:** 14 GB of RAM for a task that an 80 MB-500 MB model can solve.

General-purpose LLMs (Qwen, Llama, GPT) are designed to generate text, not to produce embeddings. Small, specialized models exist for that, and they perform as well or better.

---

## 1. Generate embeddings — Lightweight models

### Option A — fastembed + multilingual E5 (recommended for simple/local use)

```bash
pip install fastembed numpy
```

```python
from fastembed import TextEmbedding

# Good default for Spanish / mixed-language content
model = TextEmbedding(model_name="intfloat/multilingual-e5-small")

# E5 uses prefixes for retrieval
emb = list(model.embed(["passage: text to embed"]))[0]
```

Advantages:

- uses ONNX Runtime;
- runs well on CPU;
- avoids installing `torch` and most of the `transformers` stack;
- is a good option for small scripts and local tools.

For queries:

```python
query_emb = list(model.embed(["query: color of the sky"]))[0]
```

### Option B — sentence-transformers (standard and flexible)

```bash
pip install sentence-transformers
```

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("intfloat/multilingual-e5-small")
embedding = model.encode("passage: text to embed")
```

Use this option if you already have `torch` installed, want more control, or plan to experiment with many Hugging Face models.

### Models by need

| Model | Dims | Best for | Note |
|-------|------|----------|------|
| `intfloat/multilingual-e5-small` | 384 | Spanish and multilingual | Recommended default; use `query:` / `passage:` |
| `paraphrase-multilingual-MiniLM-L12-v2` | 384 | Simple multilingual use | Easy with sentence-transformers |
| `BAAI/bge-small-en-v1.5` | 384 | English, good quality/size | Very good retrieval in English |
| `all-MiniLM-L6-v2` | 384 | English, very lightweight | Widely used, but not ideal as a Spanish default |
| `all-MiniLM-L12-v2` | 384 | English, better quality than L6 | Slightly heavier |

### Option C — local GGUF models

Not recommended for this case. GGUF LLMs are designed for text generation, not embeddings. Use specialized models such as E5, BGE, or MiniLM.

---

## 2. Chunking before embedding

Do not embed a long note as a single string. Models have token limits and may truncate or lose signal.

For Obsidian or Markdown, use a simple strategy:

- split by headings (`#`, `##`, `###`);
- if a section is long, split it into blocks of roughly 300-800 tokens;
- store metadata: path, title, heading, chunk index.

Simple example by paragraphs/approximate length:

```python
from pathlib import Path


def chunk_markdown(path: Path, max_chars: int = 1800):
    text = path.read_text(encoding="utf-8")
    chunks = []
    current = []
    current_len = 0
    heading = ""

    for line in text.splitlines():
        if line.startswith("#"):
            heading = line.strip("# ").strip()

        line_len = len(line) + 1
        if current and current_len + line_len > max_chars:
            chunks.append({
                "path": str(path),
                "heading": heading,
                "text": "\n".join(current).strip(),
            })
            current = []
            current_len = 0

        current.append(line)
        current_len += line_len

    if current:
        chunks.append({
            "path": str(path),
            "heading": heading,
            "text": "\n".join(current).strip(),
        })

    return [c for c in chunks if c["text"]]
```

---

## 3. Store embeddings without a database

Avoid `pickle` as the main format: it is practical, but it is unsafe if you load files from untrusted sources.

Use:

- `index.npz` for `numpy` vectors;
- `docs.jsonl` for texts and metadata.

```python
import json
import numpy as np
from pathlib import Path


def save_index(out_dir: Path, docs: list[dict], embeddings: np.ndarray):
    out_dir.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out_dir / "index.npz", embeddings=embeddings.astype("float32"))

    with (out_dir / "docs.jsonl").open("w", encoding="utf-8") as f:
        for doc in docs:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")


def load_index(out_dir: Path):
    embeddings = np.load(out_dir / "index.npz")["embeddings"]
    docs = []
    with (out_dir / "docs.jsonl").open("r", encoding="utf-8") as f:
        for line in f:
            docs.append(json.loads(line))
    return docs, embeddings
```

Normalize once when building the index:

```python
def normalize(vectors: np.ndarray) -> np.ndarray:
    vectors = vectors.astype("float32")
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return vectors / norms
```

---

## 4. In-memory similarity search

### With pure numpy (enough for < 50k-100k chunks)

```python
import numpy as np


def search(query: str, model, docs: list[dict], embeddings_norm: np.ndarray, k: int = 5):
    q = np.array(list(model.embed([f"query: {query}"])), dtype=np.float32)
    q = q / np.linalg.norm(q, axis=1, keepdims=True)

    scores = (q @ embeddings_norm.T)[0]
    idxs = np.argsort(scores)[-k:][::-1]

    return [
        {"score": float(scores[i]), **docs[i]}
        for i in idxs
    ]
```

**Why it works:** with normalized vectors, dot product is cosine similarity.

### For larger volume — FAISS

If you go beyond ~50k-100k chunks or need more speed, add FAISS:

```bash
pip install faiss-cpu
```

```python
import faiss

index = faiss.IndexFlatIP(embeddings_norm.shape[1])
index.add(embeddings_norm.astype("float32"))

scores, indices = index.search(q.astype("float32"), k=5)
```

FAISS with `IndexFlatIP` + normalized vectors = cosine similarity.

---

## Full recommended pipeline

```python
import json
from pathlib import Path

import numpy as np
from fastembed import TextEmbedding


MODEL_NAME = "intfloat/multilingual-e5-small"
INDEX_DIR = Path(".embeddings")


def normalize(vectors: np.ndarray) -> np.ndarray:
    vectors = vectors.astype("float32")
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return vectors / norms


def build_index(raw_docs: list[dict]):
    model = TextEmbedding(model_name=MODEL_NAME)

    # E5: documents as passage
    texts = ["passage: " + d["text"] for d in raw_docs]
    embeddings = np.array(list(model.embed(texts)), dtype=np.float32)
    embeddings_norm = normalize(embeddings)

    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(INDEX_DIR / "index.npz", embeddings=embeddings_norm)

    with (INDEX_DIR / "docs.jsonl").open("w", encoding="utf-8") as f:
        for doc in raw_docs:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")


def load_index():
    embeddings = np.load(INDEX_DIR / "index.npz")["embeddings"]
    docs = []
    with (INDEX_DIR / "docs.jsonl").open("r", encoding="utf-8") as f:
        for line in f:
            docs.append(json.loads(line))
    return docs, embeddings


def search(query: str, k: int = 5):
    model = TextEmbedding(model_name=MODEL_NAME)
    docs, embeddings_norm = load_index()

    q = np.array(list(model.embed(["query: " + query])), dtype=np.float32)
    q = normalize(q)

    scores = (q @ embeddings_norm.T)[0]
    idxs = np.argsort(scores)[-k:][::-1]

    return [(float(scores[i]), docs[i]) for i in idxs]


if __name__ == "__main__":
    docs = [
        {"id": "1", "path": "demo.md", "heading": "Sky", "text": "The sky is blue."},
        {"id": "2", "path": "demo.md", "heading": "Dogs", "text": "Dogs like going for walks."},
        {"id": "3", "path": "demo.md", "heading": "Code", "text": "Programming is fun."},
    ]

    build_index(docs)

    for score, doc in search("color of the sky", k=2):
        print(f"{score:.4f} {doc['path']}#{doc['heading']} -> {doc['text']}")
```

---

## More complete alternatives

Use them only if you really need queryable persistence, complex filters, or many documents.

- **FAISS** — standard for vector indexes in memory/on disk. Very fast, less of an “app framework”.
- **sqlite-vec** — good option if you want something standard on top of SQLite without a server, but it does introduce a DB.
- **ChromaDB** — practical for RAG prototypes, but more of a framework/vector database.
- **LanceDB** — good for local columnar/vector datasets, also conceptually heavier.
- **USearch** — lightweight and fast, an alternative to FAISS.

For the initial case: **I would not use a DB**.

---

## Resource comparison

| Approach | RAM | Disk | CPU latency | Worth it? |
|----------|-----|------|-------------|-----------|
| ~~Qwen-7B + transformers~~ | ~14 GB | ~14 GB | seconds | ❌ Wasteful |
| `fastembed` + E5 small + numpy | ~250-600 MB | ~500 MB + `.npz` | ms per text/search | ✅ Recommended for Spanish/local use |
| `sentence-transformers` + MiniLM + numpy | ~200-800 MB | ~80-500 MB | ms per text/search | ✅ Standard, more dependencies |
| numpy exact search | depends on the index | `.npz` | good up to ~50k-100k chunks | ✅ Simple |
| FAISS | slightly more | FAISS index | very fast | ✅ When volume grows |
| ChromaDB/LanceDB | more overhead | own storage | good | ⚠️ If you want a local DB |

---

## Pitfalls

- Do not compare embeddings without normalizing if you will use cosine/dot product.
- Do not embed very long documents as a single string.
- Do not mix embeddings from different models in the same index.
- Do not store indexes with `pickle` if they may come from another machine/person.
- For E5, keep prefix usage consistent: `passage:` for documents and `query:` for searches.
- For exact word searches, embeddings do not replace BM25/FTS. If you need precision for identifiers, combine lexical + vector search.

---

## References

- [sentence-transformers docs](https://www.sbert.net/)
- [fastembed (Qdrant)](https://github.com/qdrant/fastembed)
- [FastEmbed docs](https://qdrant.tech/documentation/fastembed/)
- [intfloat/multilingual-e5-small](https://huggingface.co/intfloat/multilingual-e5-small)
- [FAISS — Meta](https://github.com/facebookresearch/faiss)
- [[ChromaDB]] — if there are more detailed notes
