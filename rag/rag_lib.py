"""
rag_lib.py — shared building blocks for the minimal local RAG pipeline.

Design goal: teach the mechanics of retrieval-augmented generation with zero
external services and zero downloaded models. Everything here runs offline,
in milliseconds, using only numpy + PyYAML (both already in most Python
environments). This is a *reference implementation* meant to be read, not a
production vector database — swap `TfidfIndex` for Chroma/FAISS/pgvector +
a real embedding model once you outgrow it (see README.md "Scaling up").

Pipeline stages, mirrored in ingest.py / query.py:
  1. Load  — read markdown files from a directory tree.
  2. Parse — split YAML frontmatter from body (Obsidian/Jekyll convention).
  3. Chunk — split body into sections by heading, not by fixed token count.
  4. Embed — TF-IDF vectorize each chunk (sparse, lexical "embedding").
  5. Store — persist vectors + metadata to disk (the "vector store").
  6. Query — vectorize the question the same way, rank chunks by cosine sim.
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import yaml

# ---------------------------------------------------------------------------
# 2. Parse — YAML frontmatter + body
# ---------------------------------------------------------------------------

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Split '---\\nyaml\\n---\\nbody' into (metadata, body). Tolerates no frontmatter."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    raw_yaml, body = m.group(1), m.group(2)
    try:
        meta = yaml.safe_load(raw_yaml) or {}
    except yaml.YAMLError:
        meta = {}
    return meta, body


# ---------------------------------------------------------------------------
# 3. Chunk — split by markdown heading (semantic, not fixed-size)
# ---------------------------------------------------------------------------

HEADING_RE = re.compile(r"^(#{1,3})\s+(.*)$", re.MULTILINE)


@dataclass
class Chunk:
    doc_path: str          # relative path, used as the citation
    doc_title: str         # from frontmatter `name`/`title`, or filename
    doc_type: str          # frontmatter `type`: entity | concept | summary | comparison
    heading: str           # nearest heading above this text, e.g. "Definition"
    text: str              # the chunk's raw text (heading stripped)
    chunk_id: str = field(init=False)

    def __post_init__(self):
        self.chunk_id = f"{self.doc_path}#{self.heading}"


def chunk_markdown(doc_path: str, meta: dict, body: str, min_chars: int = 40) -> list[Chunk]:
    """Split a markdown body into one chunk per heading section.

    Rationale: this vault's own schema (see CLAUDE.md) already defines the
    unit of meaning — a concept page's "## Definition" section is a coherent,
    citable claim; splitting by a fixed token window would cut it mid-thought.
    Chunking along the document's own structure is the cheapest form of
    context engineering available at ingest time.
    """
    title = meta.get("name") or meta.get("title") or Path(doc_path).stem
    doc_type = meta.get("type", "unknown")

    headings = list(HEADING_RE.finditer(body))
    chunks: list[Chunk] = []

    if not headings:
        text = body.strip()
        if len(text) >= min_chars:
            chunks.append(Chunk(doc_path, title, doc_type, "(full document)", text))
        return chunks

    # Text before the first heading (e.g. a lede paragraph) becomes its own chunk.
    lede = body[: headings[0].start()].strip()
    if len(lede) >= min_chars:
        chunks.append(Chunk(doc_path, title, doc_type, "(intro)", lede))

    for i, h in enumerate(headings):
        heading_text = h.group(2).strip()
        start = h.end()
        end = headings[i + 1].start() if i + 1 < len(headings) else len(body)
        section_text = body[start:end].strip()
        if len(section_text) >= min_chars:
            chunks.append(Chunk(doc_path, title, doc_type, heading_text, section_text))

    return chunks


# ---------------------------------------------------------------------------
# 4/5/6. Embed + Store + Query — a from-scratch TF-IDF vector store
# ---------------------------------------------------------------------------

TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9\-]+")
STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "of", "to", "in", "on", "for",
    "is", "are", "was", "were", "be", "been", "being", "with", "as", "by",
    "at", "from", "that", "this", "these", "those", "it", "its", "into",
    "than", "then", "so", "not", "no", "if", "when", "while", "which",
    "what", "who", "how", "you", "your", "we", "our", "they", "their",
}


def tokenize(text: str) -> list[str]:
    return [t for t in TOKEN_RE.findall(text.lower()) if t not in STOPWORDS]


class TfidfIndex:
    """A tiny, dependency-free stand-in for a dense vector store.

    Why TF-IDF instead of a downloaded embedding model: it needs no network
    access, no GPU, and no multi-hundred-MB model file, while still capturing
    the thing that matters most for a terminology-heavy notes vault — exact
    and near-exact matches on the vault's own vocabulary (e.g. "loop
    engineering", "context rot"). Swap this class for real embeddings when
    you need to match on *meaning* across paraphrases; see README.md.
    """

    def __init__(self):
        self.vocab: dict[str, int] = {}
        self.idf: np.ndarray | None = None
        self.matrix: np.ndarray | None = None  # (n_chunks, vocab_size), L2-normalized
        self.chunks: list[Chunk] = []

    def fit(self, chunks: list[Chunk]) -> "TfidfIndex":
        self.chunks = chunks
        tokenized = [tokenize(c.text) for c in chunks]

        # Build vocabulary.
        vocab_counter = Counter(tok for doc in tokenized for tok in set(doc))
        self.vocab = {tok: i for i, tok in enumerate(sorted(vocab_counter))}
        n_docs, n_vocab = len(chunks), len(self.vocab)

        # Document frequency -> IDF (smoothed, like sklearn's default).
        df = np.array([vocab_counter[tok] for tok in self.vocab], dtype=np.float64)
        self.idf = np.log((1 + n_docs) / (1 + df)) + 1.0

        # Term frequency matrix.
        tf = np.zeros((n_docs, n_vocab), dtype=np.float64)
        for row, doc in enumerate(tokenized):
            counts = Counter(doc)
            total = sum(counts.values()) or 1
            for tok, cnt in counts.items():
                col = self.vocab.get(tok)
                if col is not None:
                    tf[row, col] = cnt / total

        matrix = tf * self.idf
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self.matrix = matrix / norms
        return self

    def embed_query(self, query: str) -> np.ndarray:
        counts = Counter(tokenize(query))
        vec = np.zeros(len(self.vocab), dtype=np.float64)
        total = sum(counts.values()) or 1
        for tok, cnt in counts.items():
            col = self.vocab.get(tok)
            if col is not None:
                vec[col] = (cnt / total) * self.idf[col]
        norm = np.linalg.norm(vec)
        return vec / norm if norm > 0 else vec

    def search(self, query: str, k: int = 5) -> list[tuple[Chunk, float]]:
        if self.matrix is None or len(self.chunks) == 0:
            return []
        qvec = self.embed_query(query)
        scores = self.matrix @ qvec
        top_idx = np.argsort(-scores)[:k]
        return [(self.chunks[i], float(scores[i])) for i in top_idx if scores[i] > 0]

    # -- persistence: this is the entire "vector store" on disk ------------

    def save(self, out_dir: Path) -> None:
        out_dir.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            out_dir / "vectors.npz",
            matrix=self.matrix,
            idf=self.idf,
            vocab_tokens=np.array(list(self.vocab.keys())),
        )
        meta = [
            {
                "doc_path": c.doc_path,
                "doc_title": c.doc_title,
                "doc_type": c.doc_type,
                "heading": c.heading,
                "text": c.text,
            }
            for c in self.chunks
        ]
        (out_dir / "chunks.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, out_dir: Path) -> "TfidfIndex":
        data = np.load(out_dir / "vectors.npz", allow_pickle=False)
        idx = cls()
        idx.matrix = data["matrix"]
        idx.idf = data["idf"]
        idx.vocab = {tok: i for i, tok in enumerate(data["vocab_tokens"].tolist())}
        meta = json.loads((out_dir / "chunks.json").read_text(encoding="utf-8"))
        idx.chunks = [
            Chunk(m["doc_path"], m["doc_title"], m["doc_type"], m["heading"], m["text"])
            for m in meta
        ]
        return idx


# ---------------------------------------------------------------------------
# 1. Load — walk a directory of markdown files
# ---------------------------------------------------------------------------

def load_and_chunk_vault(root: Path) -> list[Chunk]:
    all_chunks: list[Chunk] = []
    for path in sorted(root.rglob("*.md")):
        rel = str(path.relative_to(root))
        text = path.read_text(encoding="utf-8", errors="ignore")
        meta, body = parse_frontmatter(text)
        all_chunks.extend(chunk_markdown(rel, meta, body))
    return all_chunks
