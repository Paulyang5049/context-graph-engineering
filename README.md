# Context & Graph Engineering for Developers

**An orchestration shape for an agent working a bounded, citation-sensitive,
moderately-stable knowledge base.**

Not a framework. A retrieval policy you write into `CLAUDE.md`, plus the templates and a
reference implementation that make it concrete. The agent decides, turn by turn, how much
retrieval to pay for — and stops as soon as it has the answer.

---

## The shape

```
paid unconditionally  →  CLAUDE.md + MEMORY.md            ~1,050 tok
                              │
                    already answers? ──yes──→ cite → verify → done
                              │ no
                    grep / scoped read                     ~100–300 tok
                              │
                    already answers? ──yes──→ check section kind → cite → verify → done
                              │ no
                    semantic search                        ~350–750 tok
                              │
                    top hit boilerplate? ──yes──→ read ranks 2–5, not rank 1
                              │
                    full file read                         last resort, named file only
```

Every rung is a bet that checking is cheaper than skipping. The ordering is the product;
the tooling underneath is replaceable.

## The three conditions

The shape is optimized for one problem, and it's worth naming precisely, because it is
narrower than "good for knowledge work."

| Condition | Why it matters |
|---|---|
| **Bounded + queried repeatedly** | Compile-once beats pay-per-query only if ingest cost amortizes. A corpus of one-off questions never repays the compilation. |
| **Moderately stable** | Cheap-first escalation is worth its complexity when most queries resolve at rung 1–2. A corpus changing hourly goes stale faster than it compiles. |
| **Citation-sensitive** | Every rung ends in `file:line`. If nobody checks sources, the verify step is pure overhead — drop it. |

Remove any one and this stops being obviously right. That's a real constraint, not a
disclaimer: **an incorrect knowledge base is worse than none, because wrong information
arrives in the format of right information.**

## A real trace

Question put to this repo: *"What's the biggest weakness of TF-IDF here, and when should
I switch?"*

**Rung 1** — `MEMORY.md`'s index has `rag-embedding-choice.md — sandbox blocks model
downloads`. Relevant, but it answers *why chosen*, not *weakness*. Doesn't resolve.
Continue.

**Rung 2** — the memory hit named the file without answering the question, so instead of
reading it whole, narrow a grep:

```bash
$ grep -n "Scaling up\|Entities Mentioned\|weak" rag/README.md
26:  ...without the word "remember" appearing there — see "Scaling up" below.
69:  returns `Entities Mentioned` sections...
89:  ## Scaling up
```

~15 lines pulled, **~165 tokens** instead of the file's 1,394. Resolved. Rungs 3 and 4
never fire.

**Verify** — reopen at those three line numbers to confirm nothing was torn mid-sentence.
Cheap, because they're now known locations rather than a speculative read.

The move that mattered wasn't the ladder's literal order. It was using a *partial* signal
to make the next cheap step more targeted, rather than escalating to the expensive one.
That's the orchestration skill the shape is teaching.

## Don't trust rank 1

Similarity ranks vocabulary overlap, not information content. Building `rag/`, a query for
*"what did Karpathy say about using Claude with Obsidian as a second brain"* returned this
section, in full, ranked **above** the paragraph that answered it:

```
## Entities Mentioned
- [[Andrej Karpathy]] - [[Obsidian]] - [[Claude]]
```

Short, dense with the query's exact proper nouns, zero information. Vector DB libraries
hide this behind a clean API. So the policy includes: check *what kind* of thing came
back before trusting it, and if rank 1 is boilerplate, read 2–5.

---

## Using it

Take the file:

```bash
curl -o CLAUDE.md https://raw.githubusercontent.com/Paulyang5049/context-graph-engineering/main/templates/CLAUDE.md
```

Fill in the `[bracketed]` parts, set your real lint/test commands, delete the
`<!-- comments -->`. **Trim the ladder to rungs that exist** — a repo with no semantic
index gets three rungs, not five with two dead ones. [EXAMPLES.md](EXAMPLES.md) has three
filled-in versions where the ladder is trimmed differently each time.

Optional — memory, so corrections survive between sessions:

```bash
curl -o MEMORY.md https://raw.githubusercontent.com/Paulyang5049/context-graph-engineering/main/templates/MEMORY.md
mkdir -p memory
```

Cursor: `.cursor/rules/context-engineering.mdc` (in this repo, copy it over).
Copilot: same content at `.github/copilot-instructions.md`. Generic: `AGENTS.md`.

**Cost: ~850 tokens per session.** That's the budget the shape has to earn back. It does
so the first time it greps instead of reading a directory.

## The three layers

| Layer | Holds | Written by |
|---|---|---|
| `CLAUDE.md` | The rules — retrieval order, citation, conventions | Human, reviewed like code |
| Knowledge base | What the project knows | Agent, at ingest |
| `MEMORY.md` + `memory/` | What the agent learned about working with *you* | Agent, as it works |

Blurring these is the common failure. A knowledge base tells the agent what's *in the
documents*; it does not tell the agent that you rejected an approach on Tuesday. Those are
different systems with different lifecycles — see
[docs/memory-architectures.md](docs/memory-architectures.md) for the memory design options
and the benchmark evidence behind them.

## How to know it's working

- The agent greps before it starts opening files.
- Answers arrive with `file.py:42` attached, not "somewhere in the auth module."
- It says "these two sources disagree" instead of confidently picking the stale one.
- Session cost stops scaling with repo size.

If none of that changes, the file is too long or too generic — it's competing with your
code for attention instead of directing it. Cut it.

---

## Where this is incomplete

Honest limits, in the order they'll bite:

1. **Scale.** `rag/` is a flat in-memory TF-IDF matrix. That holds to roughly Karpathy's
   stated ceiling — ~100 sources, a few hundred pages. Past that, rung 3 needs a real ANN
   index and hybrid BM25 + vector search, not a bigger version of this.
2. **Freshness.** Nothing runs the lint automatically. For a domain where facts change —
   pricing, policy, anything with a "current as of" — staleness checking has to be
   continuous, not something an agent remembers to do.
3. **Multi-hop.** The trace above is single-hop. Questions like *"why did we stop using
   the deduplicated dataset?"* need three hops across linked pages, which flat retrieval
   can't do regardless of whether it's TF-IDF or embeddings. **This is what the graph
   layer is for, and it is designed but not built.**

**Agent, not served product.** What's described here is an agent choosing, per turn, how
much retrieval to buy. A support bot answering end users over an API usually can't run a
multi-rung tool loop per request — the escalation has to be decided server-side, by
classifying the query once and routing it. The ladder is still the right *policy* there;
it just has to be compiled into a router rather than left as a live decision tree.

## What's in here

```
templates/CLAUDE.md      the policy, as a droppable file. ~570 tok/session.
templates/MEMORY.md      optional memory index. ~300 tok/session.
templates/memory/        annotated example memories
EXAMPLES.md              three filled-in CLAUDE.md files
docs/                    memory architecture selection guide
rag/                     reference implementation, ~250 readable lines
.cursor/rules/           the same policy as a Cursor project rule
CLAUDE.md, MEMORY.md, memory/    live instances — this repo runs on its own templates
```

## Reading

- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — Anthropic, 2025
- [The State of Agent Wikis](https://x.com/mem0ai/status/2079585032587694582) — mem0, 2026
- [Are We Ready For An Agent-Native Memory System?](https://arxiv.org/abs/2606.24775) — Zhou et al., 2026
- [Context Rot](https://research.trychroma.com/context-rot) — Chroma Research

MIT — take these, change them, no credit needed.
