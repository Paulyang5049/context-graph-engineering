# Choosing a memory architecture

Practical notes distilled from **"Are We Ready For An Agent-Native Memory System?"**
(Zhou, Zhou, Han, Xu, Li, Li, Xiong & Wu, 2026 — [arXiv:2606.24775](https://arxiv.org/abs/2606.24775)),
a systematic benchmark of 12 agent-memory systems across 11 datasets, read through the
lens of "what should I actually put in my repo on Monday morning."

The paper's framing is useful because it treats agent memory as a **data management
system** with four separable modules, rather than as one undifferentiated blob:

| Module | The question it answers |
|---|---|
| **Representation & storage** | What form is a memory stored in — raw text, summary, table row, graph node? |
| **Extraction** | What gets written down at all, and when? |
| **Retrieval & routing** | Given a query, which memories come back? |
| **Maintenance** | How do memories get updated, merged, or forgotten? |

Most memory setups people build by hand get modules 1 and 2 wrong in the same
direction — they compress too early — and then blame module 3 when recall is bad.

---

## The four architectures

The paper groups existing systems into four families. Mapped onto what a developer
would actually keep in a repo:

### 1. Stream-and-Reflection
*(paper: MemoryBank; repo equivalent: an append-only `JOURNAL.md` plus a periodically
regenerated summary)*

A timestamped log of everything, with an LLM periodically reading the log and writing
higher-level "reflections" back into it. Retrieval scores by recency × importance ×
relevance.

- **Good at:** preserving exact wording and chronology; cheap to write.
- **Bad at:** finding evidence that's far back in the log; the log grows without bound.

### 2. Hierarchical Tiered
*(paper: MemGPT, MemOS; repo equivalent: `CLAUDE.md` as always-loaded "core memory" +
`memory/` as "archival storage", with explicit promotion between them)*

Memory is split into tiers with different capacities and access costs. Small hot tier
always in context; large cold tier accessed by explicit search. Items get promoted and
evicted between tiers.

- **Good at:** bounded always-on context cost; coarse-to-fine lookup ("find the right
  session, then the right detail").
- **Bad at:** nothing much, if the promote/evict policy is sane — this is the workhorse.

### 3. Knowledge Graph
*(paper: Mem0g, Zep, Cognee; repo equivalent: the Obsidian-vault pattern — one page per
entity/concept, wikilinks between them, as in this project's
[Agentic Knowledge Graph](../rag/README.md) corpus)*

Entities, relations, and their temporal evolution stored as a graph, with entity
disambiguation and conflict resolution at write time.

- **Good at:** **revising facts.** A new fact binds to the same entity node rather than
  being appended as another undifferentiated paragraph. The paper singles this out
  (Finding 3): append-only stores return stale facts, producing what it memorably calls
  *"hallucinations of the past."*
- **Good at:** evidence scattered across many sessions — explicit links beat similarity
  search when the supporting facts are far apart (Finding 2, Finding 4).
- **Bad at:** cost. Graph-wide consolidation is the single heaviest maintenance pattern
  measured (Finding 5), and pure graph methods underperformed on *temporal* reasoning.

### 4. Composite Hybrid
*(paper: A-MEM; repo equivalent: mixing the above — e.g. graph pages for entities, a flat
journal for chronology, a vector index over both)*

Routes different memory types to different substrates, separating runtime state from
long-term storage.

- **Good at:** conversational QA benchmarks overall — it led on the broadest set.
- **Bad at:** being simple. Only worth it once you can name which substrate solves which
  of your failure modes.

**The headline result: no architecture wins everywhere.** Effectiveness depends on how
well the memory structure matches the *dominant bottleneck of your workload* (Finding 1).
Pick by bottleneck, not by sophistication.

---

## The findings that should change what you build

These are the ones with direct, non-obvious implications for a hand-rolled setup.

### Don't summarize at write time (Findings 6 & 7)

The most actionable result in the paper. Comparing storage formats for the same content:

| Storage format | LoCoMo Exact Match | LongMemEval ROUGE-L F1 |
|---|---|---|
| **Raw** (verbatim) | **24.2** | **31.4** |
| Light compression (filler removed, phrasing kept) | 23.6 | 19.1 |
| **LLM abstractive summary** | **8.5** | 17.4 |

Summarizing at write time cost **~65% of exact-match accuracy**. And a deeper hierarchy
over the summarized content did not recover it — *"hierarchy mainly improves access, but
cannot restore removed content."* Every layer of abstraction (compression, summarization,
fact extraction) irreversibly discards information.

The paper's name for the fix is the **late filtering principle**: preserve context when
writing, filter when reading. Concretely:

- Store detail; put the compression in the *retrieval* step, where it's reversible.
- Prefer coarse segmentation over fine — finer LLM-driven topic splitting scored *worse*
  because it separated cues that later needed combining.
- Keep both sides of a dialogue, not just the "important" one — clarifications and
  refined phrasings live in the replies.

This directly contradicts the intuition that a good memory file is a terse one. The
resolution is that **there are two different budgets**: disk (be generous) and context
window (be ruthless). See [`../templates/MEMORY.md`](../templates/MEMORY.md) §"Two budgets".

### Build revisability into the representation (Finding 3)

Post-update correctness is a *pipeline design* problem, not a model-capacity problem.
Systems that bind a new fact to an existing entity handled updates reliably; append-only
stores did not, and stronger LLM backbones did **not** rescue them — *"LLM scaling is most
valuable only after grounding has succeeded."*

Practically: a memory file should have a stable identity (a slug, an entity page) that
later facts overwrite or amend. `- 2026-03-01: we use Postgres` followed 200 lines later
by `- 2026-06-14: migrated to CockroachDB` is the failure mode. One `database.md` that
*says* CockroachDB, with the migration noted, is the fix.

### Localize maintenance (Finding 5)

Cost is governed by **maintenance scope**, not by how fancy the structure is. Localized
updates (path-local tree aggregation, bounded hybrid retrieval) gave the best
cost/utility balance; graph-wide consolidation and repeated whole-memory rewriting were
orders of magnitude more expensive without proportional accuracy gains.

Practically: a "re-read and rewrite all my memory files" pass is the expensive
antipattern. Update the one file that changed.

### Consolidate conservatively (Finding 9)

Of the maintenance policies tested, **strict merging** (only merge when clearly the same
topic) beat both the default and the alternatives. Two specific losers:

- **Delayed flushing** — batching writes to "save tokens" left recent evidence fragmented
  and unresolved at query time. It scored the worst of any variant tested.
- **Forcing one summary per window** — collapsing everything to a single topic obscured
  sparse-but-useful cues.

Practically: write the memory when you learn the thing, and merge two memories only when
they're genuinely the same fact.

### Retrieval: moderate hybrid, light planning, no extra reflection (Finding 8)

- A balanced dense+sparse fusion beat leaning hard either way — they fail differently, so
  the mix covers more.
- A lightweight "plan the query first" step consistently beat direct retrieval.
- Adding a *reflection* step on top of planning gave **no further gain** and added
  overhead. More deliberation is not free and not always better.

---

## Selection guide

Diagnose your bottleneck first, then pick:

| If your main failure is… | Use | Because |
|---|---|---|
| Context window blowing up on every session | **Tiered** (§2) | Bounds always-on cost; everything else loads on demand |
| Agent citing facts that changed months ago | **Graph** (§3) | Only architecture that reliably binds updates to an identity (F3) |
| Agent can't connect facts from different sessions | **Graph** (§3) | Explicit links beat similarity when evidence is scattered (F2, F4) |
| Losing exact details — names, dates, versions | **Stream** (§1), stored raw | Any summarization step destroys exact recall (F6) |
| Long inputs full of distractors | **Tiered** (§2) with multi-view filtering | Coarse-to-fine narrows attention before generation (F4) |
| Memory upkeep is slow or expensive | **Stream** or **Tiered** | Localized maintenance; avoid graph-wide consolidation (F5) |
| Several of the above | **Hybrid** (§4) | But only once you can name which substrate fixes which failure |

**Default recommendation for a normal software project:** tiered (§2), because a
repo already has the tiers — `CLAUDE.md` is core memory (always loaded, keep it small),
`memory/` and `docs/` are archival (loaded on demand). Add graph-style entity pages
(§3) for the handful of things that get *revised* often: architecture decisions,
service ownership, environment/config facts. That combination is what
[`../templates/`](../templates/) ships.

---

## Where this revised the first draft of these templates

Honest changelog, since the templates in this repo predate reading the paper:

| v1 said | The paper says | Now |
|---|---|---|
| "Memory files: prefer 5-15 lines" | Write-time compression costs ~65% exact-match accuracy (F6) | Split into two budgets: disk generous, context ruthless (late filtering, F7) |
| "Check whether an existing memory just needs updating" | Right instinct, but understated — append-only is *the* update failure mode (F3) | Promoted to a first-class rule: memories need stable identities |
| Maintenance listed as a periodic full lint pass | Global reorganization is the dominant cost driver (F5) | Prefer localized, per-file updates; full passes are rare and deliberate |
| No guidance on write timing | Delayed flushing was the worst-scoring variant tested (F9) | Write when you learn it, not in batches |
