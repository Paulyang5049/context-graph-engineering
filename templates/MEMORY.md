# MEMORY.md

> **Template.** Copy to your repo root, delete this blockquote and the `<!-- note -->`
> lines, replace the example entries. Companion to `CLAUDE.md` — see that file for the
> split between the two. Architecture rationale: [docs/memory-architectures.md](../docs/memory-architectures.md).

<!-- note: This file is the INDEX. It is loaded every session, so it stays short.
     Memory *content* lives in memory/*.md and loads on demand. -->

This is the index of what the agent has learned about this project. One line per memory,
content lives in `memory/`.

## Two budgets (read this before adding anything)

Memory has two separate budgets, and the common mistake is applying one rule to both:

| | Budget | Rule |
|---|---|---|
| **Disk** (`memory/*.md`) | Effectively unlimited | **Be generous.** Store detail, exact names, dates, versions, verbatim quotes. |
| **Context window** (what actually gets loaded) | Small and expensive | **Be ruthless.** Load the index; open a memory file only when the topic is live. |

Compress at *read* time, not at *write* time. This is the **late filtering principle**,
and it's the single most counterintuitive finding in the benchmark literature: rewriting
memories into tidy LLM summaries at write time cost ~65% of exact-detail recall, and no
amount of clever indexing afterward recovered it — you cannot retrieve what you deleted.
A memory file that reads like a slightly messy engineering note is doing its job. See
[docs/memory-architectures.md](../docs/memory-architectures.md) §"Don't summarize at write time".

## Index

<!-- note: format is `- [Title](memory/file.md) — hook.` Keep each line under ~150 chars.
     No memory content here. Group by topic, not by date. Cap this file around 200 lines. -->

### Project
- [Database choice](memory/database.md) — CockroachDB since the June migration; Postgres references are stale.
- [Deploy process](memory/deploy.md) — staged behind a flag, rollback is a flag flip not a revert.

### Preferences & feedback
- [Testing expectations](memory/feedback-testing.md) — targeted tests only; full suite is 40 min and not expected per-change.
- [Code review style](memory/feedback-review.md) — wants trade-offs named explicitly, not just a recommendation.

### Reference
- [Where things live](memory/reference-systems.md) — dashboards, issue tracker, on-call rota.

## Memory types

Tag every file with one. Four cover most projects:

| Type | Captures | Write trigger |
|---|---|---|
| **project** | Decisions, constraints, ongoing work — the *why* behind the code | Learning a reason, not just a fact |
| **feedback** | Corrections *and* confirmed approaches | User corrects you, or validates a non-obvious call |
| **user** | Role, expertise, what they care about | A durable fact about the person |
| **reference** | Pointers to external systems | Learning *where* to look, not the thing itself |

Add types sparingly. If a fact doesn't fit one, it's usually not worth saving.

## File format

```markdown
---
name: database
description: which database this project uses and why — supersedes older Postgres notes
metadata:
  type: project
  updated: 2026-06-14
---

We run CockroachDB (moved from Postgres in June 2026).

**Why:** needed multi-region writes for the EU rollout; the Postgres HA setup
couldn't do it without a proxy layer nobody wanted to own.
**How to apply:** connection code follows CRDB retry semantics — serializable
isolation means transactions can fail with 40001 and must be retried. Don't
copy patterns from the pre-June migration code.

Related: [[deploy]]
```

Rules that matter:

- **Stable identity.** One file per *thing* (`database.md`), not per *event*. New facts
  amend the file. Append-only logs of `2026-03: we use X` / `2026-06: now we use Y` are
  how agents end up confidently citing facts that changed months ago.
- **Always record the "why."** A rule without its reason can't be judged against a new
  edge case, and by then the conversation that produced it is gone.
- **Link related memories** with `[[slug]]`. A link to a memory that doesn't exist yet is
  fine — it marks something worth writing.

## What NOT to save

The biggest source of bloat is saving things cheaper to re-derive than to keep correct:

- Anything recoverable from the code (architecture, file layout, conventions) — the code
  is authoritative and a memory about it will silently drift out of date.
- Bug fixes — the fix is in the commit; a memory is just a stale echo.
- Ephemeral task state — that's a todo list.
- Anything already in `CLAUDE.md` — standing rules live there, observations live here.
- Secrets, credentials, tokens. Ever. Also protected personal attributes and government
  IDs unless the person explicitly asks you to remember them.

## Writing and maintenance

- **Write when you learn it, not in batches.** Deferring writes to "save tokens" scored
  worst of every maintenance policy tested — evidence sits unresolved exactly when a
  query needs it.
- **Update the one file that changed.** Periodic rewrite-everything passes are the
  dominant cost driver in every benchmarked system and rarely improve anything.
- **Merge conservatively.** Combine two memories only when they're genuinely the same
  fact. Over-eager merging loses the sparse detail that turns out to matter later.
- **Run a real lint pass rarely and deliberately** — checking for: contradictions between
  memories (flag both, don't silently pick), index entries pointing at deleted files,
  and memories that have become code-derivable and should be dropped.

## Recall discipline

A memory naming a file, function, or flag asserts that it existed *when written*. Before
**acting** on it (not merely mentioning it), verify — grep for the symbol, check the path.
"The memory says X" and "X is true now" are different claims; only the second justifies
an edit.
