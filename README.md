# Context & Graph Engineering for Developers

**Drop-in `CLAUDE.md` and `MEMORY.md` templates, plus a readable reference RAG
implementation, for cutting the token cost of coding agents while making their answers
more accurate.**

Every session with a coding agent starts by paying for context. Most projects pay far
too much for it, and get worse answers in return. This repo is a small, opinionated set
of files you put in a project *before* you start working, plus the reasoning for why
they're shaped the way they are.

---

## The problem

You point an agent at a real codebase and one of these happens:

| Symptom | What's actually going on |
|---|---|
| **Burning tokens on every session** | The agent reads 40 files to answer a question one `grep` would have resolved. Every project doc is loaded "just in case." |
| **Confidently wrong answers** | It answered from a file's *name*, or from a heading, or from a keyword-dense index section that ranked high but contained nothing. |
| **Citing facts that changed months ago** | Memory was append-only. The old fact is still sitting there, and nothing binds the new fact to it. |
| **Degrades as the session gets longer** | [Context rot](https://research.trychroma.com/context-rot) — retrieval accuracy from within the context window measurably drops as it fills. This is not a metaphor; it's benchmarked. |
| **Re-explaining the project every morning** | Nothing persists. Conventions, corrections, and decisions evaporate at the end of each session. |

These aren't separate problems. They're all the same one: **context is a finite,
expensive resource, and most setups treat it as free.**

## The principle

> Retrieve the smallest set of high-signal tokens that answers the question — not
> everything that might be relevant.

This is Anthropic's framing in [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents),
and every rule in this repo is an application of it to a specific situation.

**Concretely, on the corpus in this repo's example:** a 136 KB knowledge base (~22K
tokens of indexed content) answers a typical question from **355–740 tokens** of
retrieved context — **1.6–3.4% of the corpus**. The other 96%+ never enters the context
window, never competes for attention, and never gets billed.

## What's here

```
templates/          ← the drop-in files. Start here.
  CLAUDE.md           project instructions: retrieval order, citation rules, conventions
  MEMORY.md           the memory index (thin, always loaded)
  memory/             example typed memory files (loaded on demand)
docs/
  memory-architectures.md   how to pick a memory design, with benchmark evidence
rag/                ← reference implementation: a readable RAG pipeline in ~250 lines
```

## Quick start

```bash
git clone https://github.com/Paulyang5049/context-graph-engineering.git

# Copy the templates into your project
cp context-graph-engineering/templates/CLAUDE.md   your-project/
cp context-graph-engineering/templates/MEMORY.md   your-project/
cp -r context-graph-engineering/templates/memory   your-project/
```

Then edit `CLAUDE.md`: fill in the `[bracketed]` sections, set your real lint/test
commands, delete the `<!-- note -->` comments. Empty out the example memory files. That's
it — the next agent session picks them up automatically.

Using Cursor or Copilot instead? Same content, different filename
(`.cursorrules`, `.github/copilot-instructions.md`).

---

## What the templates actually do

### `CLAUDE.md` — spend context deliberately

The core of it is a **retrieval ladder**, cheapest first, stop when answered:

```
1. CLAUDE.md + MEMORY.md   already in context — free
2. index / catalog file    a map of what exists
3. grep / glob             precise, cheap, never stale
4. semantic search (RAG)   only when the question won't match a filename
5. full file read          only after 1–4 point at a specific file
```

The ordering matters more than any individual step. Step 3 resolves most "where is X"
questions in a single call; jumping straight to step 5 is where the token bills come
from. Anthropic makes the same point about Claude Code itself — `grep` and `glob` beat
pre-computed indexes because they're never stale.

It also encodes a rule learned from actually building the pipeline in `rag/`:

> **Don't trust the top retrieval result blindly.** Similarity rank measures vocabulary
> overlap, not information content.

We hit this empirically. Querying *"what did Karpathy say about using Claude with
Obsidian as a second brain"* returned a section that reads, in its entirety:

```
## Entities Mentioned
- [[Andrej Karpathy]] - [[Obsidian]] - [[Claude]]
```

Ranked **above** the paragraph that actually answered the question. It's short and dense
with the query's exact proper nouns — a perfect similarity match containing zero
information. Vector DB libraries hide this behind a clean API; an agent that doesn't know
to check will answer from it. (Full write-up: [`rag/README.md`](rag/README.md).)

### `MEMORY.md` — persist without re-inflating

Two layers: a **thin index** loaded every session, and **typed memory files** loaded only
when their topic is live. Four types cover most projects — `project` (decisions and their
reasons), `feedback` (corrections you shouldn't have to repeat), `user`, `reference`.

The counterintuitive part is covered next.

---

## Choosing a memory architecture

The memory design in `templates/` is one of several defensible choices. This section
exists so you can pick deliberately rather than inherit ours.

The evidence base is **"Are We Ready For An Agent-Native Memory System?"**
([arXiv:2606.24775](https://arxiv.org/abs/2606.24775)) — a systematic benchmark of 12
agent-memory systems across 11 datasets, which decomposes memory into four separable
modules (representation, extraction, retrieval, maintenance) and measures each. Its
headline: **no architecture wins everywhere.** Effectiveness depends on matching the
structure to your workload's dominant bottleneck.

### The four options

| Architecture | Repo shape | Strongest at | Weakest at |
|---|---|---|---|
| **1. Stream + reflection** | Append-only `JOURNAL.md` + periodic distilled summary | Preserving exact wording and chronology; cheap writes | Finding anything far back in the log; unbounded growth |
| **2. Tiered** ⭐ | `CLAUDE.md` = hot tier, `memory/` = cold tier, explicit promotion | Bounded always-on cost; coarse-to-fine lookup | Needs a sane promote/evict policy |
| **3. Graph** | One page per entity/concept, wikilinks between them | **Revising facts**; connecting evidence across sessions | Maintenance cost; weaker on temporal reasoning |
| **4. Hybrid** | Mix of the above, routed by type | Broadest benchmark coverage | Complexity — only worth it when you can name why |

⭐ **The templates here ship #2, with a dash of #3** — because a repo already *has* tiers
(`CLAUDE.md` is always loaded; `memory/` and `docs/` are not), and because the handful of
facts that get *revised* often — architecture decisions, service ownership, config — need
graph-style stable identities.

### Pick by your failure mode

| If your main problem is… | Use | Why |
|---|---|---|
| Context blowing up every session | **Tiered** | Bounds the always-on cost; everything else loads on demand |
| Agent citing facts that changed | **Graph** | The only design that reliably binds an update to an existing identity |
| Can't connect facts across sessions | **Graph** | Explicit links beat similarity when evidence is scattered |
| Losing exact names, dates, versions | **Stream**, stored raw | Any summarization step destroys exact recall |
| Long inputs full of distractors | **Tiered** | Coarse-to-fine narrows attention before generation |
| Memory upkeep is slow/expensive | **Stream** or **Tiered** | Localized maintenance; avoid graph-wide consolidation |

Full reasoning and the benchmark numbers: [`docs/memory-architectures.md`](docs/memory-architectures.md).

### The finding that changed our template

The first draft of `MEMORY.md` in this repo said *"prefer 5–15 lines per memory; compress
aggressively."* That was wrong, and the paper says so with numbers. Storing the same
content three ways:

| Storage format | Exact Match |
|---|---|
| **Raw** (verbatim) | **24.2** |
| Light compression (filler removed, phrasing kept) | 23.6 |
| **LLM abstractive summary** | **8.5** |

Summarizing at write time cost **~65% of exact-match accuracy** — and adding a deeper
hierarchy on top did *not* recover it. You cannot retrieve what you deleted.

The resolution is that **there are two budgets, not one**:

| | Budget | Rule |
|---|---|---|
| **Disk** (`memory/*.md`) | Effectively unlimited | **Be generous.** Exact names, dates, versions, verbatim quotes. |
| **Context window** (what loads) | Small and expensive | **Be ruthless.** Index only; open a file when its topic is live. |

Compress at **read** time, not write time. The paper calls this the *late filtering
principle*, and it's the thing most hand-rolled memory setups get backwards — including
ours, until we measured it.

Three more findings that shaped the templates:

- **Build revisability in.** Name a memory file after the *thing* (`database.md`), not
  the *event* (`migration-2026-06.md`). Append-only stores produce what the paper calls
  *"hallucinations of the past"* — and a stronger model does not fix it.
- **Write when you learn it.** Batching memory writes to "save tokens" scored *worst* of
  every maintenance policy tested. Evidence sits unresolved exactly when a query needs it.
- **Update one file, not all of them.** Global reorganization is the dominant cost driver
  in every system measured, with no proportional accuracy gain.

---

## The reference implementation (`rag/`)

A complete RAG pipeline in ~250 readable lines — no API keys, no model downloads, no
vector database. It indexes a folder of markdown and retrieves cited chunks.

```bash
cd rag
pip install -r requirements.txt
python3 ingest.py /path/to/your/notes --out ./index
python3 query.py "what is loop engineering?"
```

It exists to make the mechanics legible before you reach for a framework. Once you
understand what these files do, LangChain and Chroma are just faster versions of the same
six steps. Two design choices worth stealing:

- **Chunk by heading, not by token count.** A fixed 500-token window cuts definitions in
  half. If your documents have structure, that structure already marks the unit of
  meaning — use it. (`rag_lib.py::chunk_markdown`)
- **Keep retrieval and generation separate.** `query.py` never calls an LLM; it prints a
  context block and stops. Bolting on generation is one line, but keeping the boundary
  visible makes it obvious exactly what the model is grounded on.

Details and the scaling path (dense embeddings, hybrid search, reranking):
[`rag/README.md`](rag/README.md).

---

## Reading

- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — Anthropic Engineering, 2025
- [Are We Ready For An Agent-Native Memory System?](https://arxiv.org/abs/2606.24775) — Zhou et al., 2026 ([code](https://github.com/OpenDataBox/MemoryData))
- [Context Rot](https://research.trychroma.com/context-rot) — Chroma Research

## License

MIT — see [LICENSE](LICENSE). Take these, change them, don't credit us.
