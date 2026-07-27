---
name: context-engineering
description: Draft a personalized CLAUDE.md (and optional MEMORY.md) for a project so the coding agent retrieves information cheaply and accurately. Use at the start of a project, or when the user asks to set up CLAUDE.md, cut token usage, stop the agent reading too many files, add agent memory, or fix an agent that keeps making retrieval mistakes.
license: MIT
---

# Context Engineering — draft a project's CLAUDE.md

Produce a `CLAUDE.md` tailored to **this** repo: one that makes the agent find things in
the cheapest way that works, cite what it found, and verify before finishing.

**The output is a file, not advice.** Write it to the repo. Keep it under ~100 lines —
it's charged on every session, so every line must earn its place.

## Step 1 — Look before you ask

Inspect the repo first. Most of what goes in `CLAUDE.md` is discoverable, and asking the
user for something you could have read is a waste of their time.

Detect and note:

| What | Where to look |
|---|---|
| Language / stack | `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `Gemfile` |
| Test command | `scripts.test`, `pytest.ini`, `Makefile`, CI workflow files |
| Lint / format | `.eslintrc*`, `ruff.toml`, `.pre-commit-config.yaml`, `biome.json` |
| Repo size | count files and directories — it decides how much retrieval guidance is needed |
| Existing agent files | `CLAUDE.md`, `AGENTS.md`, `.cursorrules`, `.github/copilot-instructions.md` |
| Generated / vendored dirs | `.gitignore`, `generated/`, `dist/`, `migrations/`, protobuf output |
| Docs entry point | `README.md`, `docs/`, an index or catalog file |

If a `CLAUDE.md` already exists, **read it and improve it in place**. Don't overwrite the
user's work — merge, and say what you changed.

## Step 2 — Ask only what you couldn't detect

Ask at most 3–4 questions, in one batch. Skip any you already answered in Step 1. The
ones that actually change the output:

1. **What does the agent keep getting wrong here?** (reads too many files / invents APIs /
   breaks conventions / edits things it shouldn't / forgets past decisions) — this decides
   which sections earn their place.
2. **Anything expensive or destructive to warn it about?** (a 40-minute test suite, a
   migration command, a deploy script, a prod-connected config)
3. **Any convention a linter can't catch?** (error-handling style, where new modules go,
   files that must never be hand-edited)
4. **Want `MEMORY.md` too?** — only if they work with this repo repeatedly and are tired
   of re-explaining things.

Don't ask about things with an obvious default. Don't ask permission to write the file —
that's the whole point of invoking this.

## Step 3 — Write `CLAUDE.md`

Start from [`templates/CLAUDE.md`](../../templates/CLAUDE.md) in this plugin, then
**fill it in with real values** — no `[brackets]` may survive into the output.

Sections, in order:

**Project** — one paragraph. Stack, domain, what it does. Concrete enough that the agent
can judge whether a given file is plausibly relevant.

**Finding things — cheapest first.** The core of the file. Ladder:

```
1. CLAUDE.md + MEMORY.md   already in context — free
2. grep / glob             precise, cheap, never stale
3. <this repo's index or catalog, if one exists>
4. <semantic search, only if the repo has one>
5. Read the file           only after 1–4 point at a specific one
```

Cut steps that don't apply — a repo with no index or RAG index gets a 3-step ladder, not
a 5-step one with two dead rungs. Add the repo's own navigation facts here: where the
entry points are, which directories are generated and shouldn't be read or edited.

**Answering** — cite sources as `path:line`; quote the minimum; check *what kind* of thing
was retrieved before trusting it (imports, tables of contents, and link lists rank high on
keyword match while containing nothing); if two sources disagree, say so.

**Before finishing** — the real lint and test commands found in Step 1. If the full suite
is slow, say so and give the targeted form.

**Conventions** — only what a linter can't enforce. If a formatter already catches it,
leaving it out makes every future session cheaper at zero cost.

Then delete every explanatory comment. The user's `CLAUDE.md` should read like it was
written for their repo, because it was.

## Step 4 — Offer the optional pieces

Only if they fit — say so briefly and let the user decline:

- **`MEMORY.md` + `memory/`** — if they asked in Step 2, or if the repo shows signs of
  repeated agent work. Copy [`templates/MEMORY.md`](../../templates/MEMORY.md) as an
  *empty index* plus a `memory/` directory. Do not ship the example memories into their
  repo. Rules: one file per *thing* not per event, so updates overwrite instead of piling
  up; record the *why*; write when you learn it.
- **`rag/`** — only when the repo has a large prose corpus (docs, notes, a wiki) and
  questions get phrased in language that doesn't appear in the text. **For code, `grep`
  almost always wins.** Don't push this.
- **Other agents** — same content at `.cursor/rules/*.mdc`, `.github/copilot-instructions.md`,
  or `AGENTS.md` if they use those tools.

## Budget

The file you produce is loaded into context on every session, forever. Hold it to:

- **Under ~100 lines / ~600 tokens.** If it's longer, the retrieval guidance is competing
  with the code for attention.
- **No filler.** No "be helpful", no "write good code", no restating what the model
  already does. Every line should change behaviour.
- **Situational detail goes in linked docs**, not inline — the agent opens them when the
  topic comes up. That's the same principle the file is teaching.

## Before you finish

- Report the line count and rough token cost of what you wrote.
- Confirm no `[bracketed]` placeholders or template comments survived.
- Confirm the lint/test commands you wrote are the ones that actually exist — run them
  once if that's cheap.
- Name what you deliberately left out and why. A short file is the deliverable, not a
  compromise.
