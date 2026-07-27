# Minimal local RAG pipeline

A from-scratch, dependency-light retrieval-augmented generation pipeline, built to be
read end to end in one sitting. It indexes the `wiki/` folder of the **Agentic Knowledge
Graph** Obsidian vault and retrieves the most relevant chunks for a question — no API
keys, no downloaded models, no external services.

This exists to make the mechanics of RAG legible before reaching for a framework. Once
you understand what these ~250 lines do, LangChain/LlamaIndex/Chroma are just faster,
more scalable versions of the same six steps.

## Why TF-IDF instead of real embeddings

The obvious choice — download `all-MiniLM-L6-v2` and do dense cosine search — was tried
first. It failed here for an environment reason worth knowing about: sandboxed dev
environments frequently block arbitrary outbound traffic (Hugging Face Hub, PyPI mirrors,
etc.) via an allowlisted proxy. `fastembed`/`sentence-transformers` need to fetch the
model on first run, and that fetch hit a `403 Forbidden`.

TF-IDF has no such dependency: it's computed entirely from the corpus itself
(`rag_lib.py`'s `TfidfIndex`), so it runs anywhere Python + numpy run. It's also a fair
match for a notes vault — this corpus has a small, distinctive vocabulary (*"loop
engineering," "context rot," "second brain"*) where exact lexical overlap already goes
a long way. **Swap it for dense embeddings once you have network access and need to
match paraphrases** (e.g. "how does the agent remember things" → *agent-memory.md*
without the word "remember" appearing there) — see "Scaling up" below.

## Pipeline

```
markdown files ──► parse frontmatter ──► chunk by heading ──► TF-IDF vectorize ──► save
                                                                                      │
                                                                                      ▼
question ──────────────────────────────► TF-IDF vectorize ──► cosine sim ──► top-k chunks
```

| File | Role |
|---|---|
| `rag_lib.py` | All the logic: frontmatter parsing, heading-based chunking, TF-IDF index, save/load. |
| `ingest.py` | CLI: walk a folder, chunk it, fit the index, write `index/vectors.npz` + `index/chunks.json`. |
| `query.py` | CLI: load the index, retrieve top-k chunks for a question, print them + a ready-to-paste context block. |

## Usage

```bash
pip install -r requirements.txt

# Build the index (point at any folder of markdown; here, the vault's wiki/)
python3 ingest.py "/path/to/Agentic Knowledge Graph/wiki" --out ./index

# Ask questions
python3 query.py "what is loop engineering?"
python3 query.py "how does agent memory work across sessions?" --k 3
```

Re-run `ingest.py` whenever the source files change — there is no incremental update;
it rebuilds the whole index (fine at this scale: 106 docs → 428 chunks → sub-second).

## Design decisions, and what they taught us

**Chunk by heading, not by fixed token count.** This vault's own `CLAUDE.md` already
defines the unit of meaning — a concept page's `## Definition` section is a complete,
citable claim. A sliding 500-token window would routinely cut that section in half.
Chunking along a document's own structure is the cheapest context-engineering win
available, and it's free when your source documents already have one (most do).

**A documented failure mode: metadata sections outscore content sections.**
Querying `"what did Karpathy say about using Claude with Obsidian as a second brain"`
returns `Entities Mentioned` sections (literally: `- [[Andrej Karpathy]] - [[Obsidian]]
- [[Claude]]`) ranked *above* the `One-Paragraph Summary` section that actually answers
the question. TF-IDF scores these list-of-links sections highly because they're short
and dense with the exact proper nouns in the query — but they carry almost no
information. Two fixes, left as an exercise rather than baked in (so the failure stays
visible):
1. Skip or downweight boilerplate headings (`Entities Mentioned`, `Sources`,
   `Relationships`) at chunk time.
2. Add a length/informativeness prior — e.g. divide score by `1 / log(len(chunk.text))`
   to penalize very short chunks.

This is the kind of thing that's easy to miss when a vector DB library hides the
scoring from you, and exactly the kind of thing worth putting in a CLAUDE.md so an
agent building on top of this index doesn't trust top-1 blindly. See `../CLAUDE.md`.

**Retrieval and generation are kept separate.** `query.py` never calls an LLM. It prints
a context block and stops. Bolting on generation is one line (pipe the context block +
question into `claude -p` or the Messages API) — but keeping the boundary explicit makes
it obvious exactly what the model is grounded on, which is the entire point of RAG.

## Scaling up

| At this scale (~100s of docs) | Reach for this when it stops being enough |
|---|---|
| TF-IDF, in-memory numpy matrix | Dense embeddings (`sentence-transformers`, OpenAI/Voyage/Claude embeddings) for paraphrase matching |
| Flat `.npz` file, reload on every query | A real vector store (Chroma, FAISS, pgvector, LanceDB) once the corpus doesn't fit in memory or you need filters/updates |
| Full re-index on every run | Incremental ingest keyed by file mtime/hash |
| Single retrieval pass | Hybrid search (BM25/TF-IDF + dense, reciprocal rank fusion) — sparse and dense catch different failure modes |
| No reranking | A cross-encoder reranker over the top ~20 candidates before returning top-k |
