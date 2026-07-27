# CLAUDE.md

> **Template.** Copy to your repo root, delete this blockquote and the `<!-- note -->`
> lines, and fill in the `[bracketed]` parts. Works for Claude Code, Cursor
> (`.cursorrules`), Copilot (`.github/copilot-instructions.md`), and any agent that
> reads a project instruction file — rename as needed.

<!-- note: This file is loaded into context on EVERY session. It is the most expensive
     documentation in the repo per unit of length. Target under ~200 lines. If a
     section only applies to one kind of task, move it to a linked doc and reference
     it here — the agent will open the link when it needs it. -->

## Project

[One paragraph: what this is, who uses it, what the stack is. The agent uses this to
decide whether a given file is likely relevant, so name the domain concretely.]

## Retrieval order — cheapest first

Stop as soon as one of these answers the question. **Do not pre-load files "just in
case"** — every unnecessary token spent here degrades attention on the tokens that
matter.

1. **This file + `MEMORY.md`** — already in context, costs nothing extra.
2. **Index/catalog** — `[README.md / docs/index.md / your catalog file]`. A map of what
   exists, cheaper than searching for it.
3. **Structured search** — `grep`/`glob` over the actual files. Precise, cheap, and never
   stale. This resolves most "where is X defined" questions in one call.
4. **Semantic search** — `[your RAG index / vector search command, if any]`. Use only when
   the question is phrased in language that won't match a filename or grep pattern
   ("what does this project think about X" rather than "where is X defined").
5. **Full file read** — only after 1–4 point at a specific file. Read that file, not its
   neighbours.

## Citing retrieved context

- Every retrieved fact carries its source: `path/to/file.py:42` or `doc.md#heading`.
- Quote the minimum + cite; don't paste whole sections. The reader opens the link if
  they need more.
- When synthesising across sources, list them at the end rather than interleaving dumps.

## Don't trust the top result blindly

Retrieval rank measures *similarity*, not *correctness* or *information content*. Short,
keyword-dense sections (imports, tables of contents, link lists, "See also") routinely
outrank the prose that actually answers the question — they match the query's vocabulary
without containing its answer.

Before answering from a retrieved chunk:

- Check what kind of section it is. Boilerplate/index, or actual content?
- If the top hit is boilerplate, look at ranks 2–5 before answering.
- If nothing in the top results is content, re-query with different phrasing rather than
  answering from the best of a bad set.

## Verify before you finalise

<!-- note: replace with this project's real commands — an agent will run these. -->

- Re-check claims against the actual source file, not just the retrieved excerpt.
- Run `[lint command]` and `[test command]` for the files you touched.
- If two sources contradict each other, say so explicitly. Don't silently pick one.

## Conventions

<!-- note: keep this to things a linter can't enforce. If a formatter or type checker
     already catches it, deleting the rule here makes the file cheaper with no loss. -->

- [e.g. Error handling: return Result types, don't raise across module boundaries.]
- [e.g. New endpoints go in `api/routes/`, one file per resource.]
- [e.g. Never edit `generated/` by hand — regenerate with `make codegen`.]

## This file vs. `MEMORY.md`

- **`CLAUDE.md`** (this file) — human-authored, version-controlled, reviewed. States
  *requirements and conventions*: how things must be done here. Changes go through PR.
- **`MEMORY.md`** — agent-maintained. Records *observations*: decisions made, corrections
  received, current state of the world.

Don't duplicate across them. A standing rule belongs here; a fact about how things
currently are belongs there.

## Anti-patterns

- Reading a directory because it "might be relevant." One targeted `grep` beats forty
  speculative file reads, and leaves the context window intact for actual reasoning.
- Re-deriving the same summary every session instead of writing it to `MEMORY.md` once.
- Answering from a file's name or a section heading without reading the body.
- Treating a high similarity score as a correctness guarantee.
- Growing this file until it's a manual. Length here is charged on every single session —
  push situational detail into linked docs.
