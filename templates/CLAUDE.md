# CLAUDE.md

<!-- Loaded into context on EVERY session — the most expensive file in the repo per line.
     Fill in [brackets], delete these comments, keep it under ~100 lines. Anything that
     applies to only one kind of task belongs in a linked doc, not here. -->

## Project

[What this is, the stack, the domain. One paragraph. The agent uses this to judge
whether a given file is plausibly relevant, so be concrete.]

## Finding things — cheapest first, stop when answered

1. **This file + `MEMORY.md`** — already in context, free.
2. **`grep` / `glob`** — precise, cheap, never stale. Resolves most "where is X" in one call.
3. **[index or catalog file, if you have one]** — a map of what exists.
4. **[semantic search command, if you have one]** — only when the question won't match a
   filename or a grep pattern.
5. **Read the file** — after 1–4 point at a specific one. That file, not its neighbours.

**Never read a directory speculatively.** Forty exploratory reads cost more than the task
and leave less attention for the actual work.

## Answering

- Cite the source of every claim: `path/to/file.py:42`, `doc.md#heading`.
- Quote the minimum. Don't paste sections — link and let the reader open it.
- Check *what kind* of thing you retrieved before trusting it. Imports, tables of
  contents, and link lists rank high on keyword match while containing nothing. If the
  top hit is boilerplate, look at the next few.
- If two sources disagree, say so. Don't silently pick one.

## Before finishing

<!-- Replace with the real commands — an agent will run these. -->

- `[lint command]`
- `[test command]` — for the files touched. [Note here if the full suite is slow.]

## Conventions

<!-- Only what a linter can't catch. If a formatter already enforces it, deleting the
     rule here makes every future session cheaper at zero cost. -->

- [e.g. New endpoints go in `api/routes/`, one file per resource.]
- [e.g. Never hand-edit `generated/` — run `make codegen`.]
- [e.g. Errors cross module boundaries as Result types, not exceptions.]

## `CLAUDE.md` vs `MEMORY.md`

This file: standing rules, human-authored, reviewed like code.
`MEMORY.md`: what the agent has observed — decisions, corrections, current state.
Don't duplicate across them.
