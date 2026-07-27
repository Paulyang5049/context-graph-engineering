# Context & Graph Engineering for Developers

**A `CLAUDE.md` that makes coding agents cheaper and more accurate.** Copy one file into
your project and the agent stops reading forty files to answer a question that one `grep`
would have resolved.

Everything else here — the memory file, the RAG pipeline — exists to serve that. They're
instructions for finding information faster and more accurately, not products of their own.

---

## The problem

| Symptom | What's actually happening |
|---|---|
| Token bills climb with no matching output | The agent reads directories speculatively. Every doc gets loaded "just in case." |
| Confidently wrong answers | It answered from a filename, a heading, or a keyword-dense index section that ranked high and said nothing. |
| Cites facts that changed months ago | Nothing bound the new fact to the old one. |
| Gets worse the longer the session runs | [Context rot](https://research.trychroma.com/context-rot) — recall from within the context window measurably degrades as it fills. |
| You re-explain the project every morning | Conventions and corrections evaporate at session end. |

One cause: **context is finite and expensive, and most setups spend it like it's free.**

## The fix

```bash
git clone https://github.com/Paulyang5049/context-graph-engineering.git
cp context-graph-engineering/templates/CLAUDE.md your-project/
```

Fill in the `[bracketed]` parts, set your real lint/test commands, delete the
`<!-- comments -->`. Next session picks it up automatically. Cursor and Copilot use the
same content under a different filename (`.cursorrules`,
`.github/copilot-instructions.md`).

Add [`templates/MEMORY.md`](templates/MEMORY.md) + [`templates/memory/`](templates/memory)
if you want the agent to remember corrections between sessions.

**The whole thing costs ~850 tokens per session.** That's the budget it has to earn back —
it does so the first time it greps instead of reading a directory.

---

## What `CLAUDE.md` actually does

### 1. A retrieval ladder, cheapest first

```
1. CLAUDE.md + MEMORY.md   already in context — free
2. grep / glob             precise, cheap, never stale
3. index / catalog file    a map of what exists
4. semantic search         only when the question won't match a filename
5. read the file           only after 1–4 point at a specific one
```

The ordering is the point. Step 2 answers most "where is X" questions in one call;
jumping straight to step 5 is where the token bills come from. Anthropic makes the same
argument about [Claude Code itself](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents):
`grep` and `glob` beat pre-computed indexes because they can't go stale.

### 2. A rule against trusting the top result

Similarity rank measures *vocabulary overlap*, not information content. We hit this
building the pipeline in `rag/` — querying *"what did Karpathy say about using Claude with
Obsidian as a second brain"* returned this section, in full:

```
## Entities Mentioned
- [[Andrej Karpathy]] - [[Obsidian]] - [[Claude]]
```

Ranked **above** the paragraph that answered the question. Short, dense with the query's
exact proper nouns, and containing zero information. Vector DB libraries hide this behind
a clean API. An agent that doesn't know to check the *kind* of thing it retrieved will
answer from it.

### 3. Citation and verification rules

Every claim carries `file.py:42`. Quote the minimum. Run the real lint/test commands
before finishing. If two sources disagree, say so instead of silently picking one.

### 4. Conventions a linter can't catch

And only those. If a formatter already enforces a rule, deleting it from `CLAUDE.md`
makes every future session cheaper at zero cost.

> **Keep it under ~100 lines.** This file is charged on every session — it's the most
> expensive documentation in the repo per line. Anything that applies to one kind of task
> belongs in a linked doc the agent opens when it needs it.

---

## `MEMORY.md` — so corrections stick

A thin index, always loaded; the actual memories in `memory/*.md`, opened only when their
topic is live. Three rules do most of the work:

- **One file per *thing*, not per event.** `database.md`, not `migration-2026-06.md`, so
  a new fact overwrites the old one instead of piling up next to it.
- **Be generous on disk, ruthless about what loads.** Store exact names, dates, versions.
  Compress at *read* time — you can't retrieve what you deleted at write time.
- **Write when you learn it.** Batching memory writes to save tokens leaves evidence
  unresolved exactly when a query needs it.

Those aren't guesses. [Zhou et al. 2026](https://arxiv.org/abs/2606.24775) benchmarked 12
memory systems across 11 datasets: storing memories as LLM summaries instead of raw text
dropped Exact Match from **24.2 → 8.5**, and no amount of indexing on top recovered it.

If your situation differs — you need a graph, or a plain journal —
[`docs/memory-architectures.md`](docs/memory-architectures.md) has the selection guide and
the evidence. Most projects don't need to read it.

---

## `rag/` — optional, and most projects don't need it

A complete RAG pipeline in ~250 readable lines: no API keys, no model downloads, no vector
database. It indexes a folder of markdown and returns cited chunks.

```bash
cd rag && pip install -r requirements.txt
python3 ingest.py /path/to/your/notes --out ./index
python3 query.py "what is loop engineering?"
```

**Reach for this only when `grep` genuinely can't answer the question** — when queries are
phrased in language that doesn't appear in the text ("what does this project think about
X"). For code, `grep` almost always wins. This is mainly here as a teaching artifact: once
you can read these files, LangChain and Chroma are just faster versions of the same six
steps. Two ideas worth stealing anyway:

- **Chunk by heading, not token count.** A fixed 500-token window cuts definitions in half.
- **Keep retrieval separate from generation.** `query.py` never calls an LLM — it prints
  the context and stops, so what the model is grounded on stays visible.

Details: [`rag/README.md`](rag/README.md).

---

## Reading

- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — Anthropic, 2025
- [Are We Ready For An Agent-Native Memory System?](https://arxiv.org/abs/2606.24775) — Zhou et al., 2026
- [Context Rot](https://research.trychroma.com/context-rot) — Chroma Research

MIT — take these, change them, no credit needed.
