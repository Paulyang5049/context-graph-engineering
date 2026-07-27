# Examples

What a filled-in `CLAUDE.md` looks like for real projects. Copy the one closest to yours
and edit.

Note what varies: **the ladder is trimmed to rungs that actually exist.** Two of the three
below drop semantic search entirely, because `grep` wins for code. Only the docs repo — a
bounded, citation-sensitive, repeatedly-queried corpus — earns the extra rung.

---

## A Python API service

```markdown
# CLAUDE.md

## Project

FastAPI service backing the billing dashboard. Python 3.11, SQLAlchemy 2.0 + Postgres,
Alembic migrations. Deployed to ECS. Business logic lives in `app/services/`; `app/api/`
is routing and validation only.

## Finding things — cheapest first, stop when answered

1. This file + `MEMORY.md` — already in context.
2. `grep` / `glob` — resolves most "where is X" in one call.
3. `docs/architecture.md` — service boundaries and data flow.
4. Read the file — only after 2–3 point at a specific one.

`app/db/models_generated.py` and `alembic/versions/` are generated. Read them if you must,
never hand-edit them.

## Answering

- Cite sources as `app/services/billing.py:88`.
- Quote the minimum; don't paste sections.
- Check what kind of thing you retrieved — an `__init__.py` re-export block matches
  keywords while containing nothing. If the top hit is boilerplate, look at the next few.
- If two sources disagree, say so rather than picking one.

## Before finishing

- `ruff check app/ && ruff format --check app/`
- `pytest tests/ -k <relevant>` — the full suite takes ~12 min, don't run it per-change.

## Conventions

- Services raise `BillingError` subclasses; routes translate them to HTTP. Never raise
  `HTTPException` below `app/api/`.
- Every schema change needs an Alembic migration in the same PR.
- Money is `Decimal`, never `float`. No exceptions.
```

**~35 lines.** Notice what's absent: no "write clean code", no restating Python
conventions the model already knows, no four-level ladder when three rungs are real.

---

## A TypeScript monorepo

```markdown
# CLAUDE.md

## Project

pnpm monorepo. `apps/web` (Next.js 15, App Router), `apps/api` (Hono on Cloudflare
Workers), `packages/ui` (shared components), `packages/db` (Drizzle schema + queries).
Anything imported across app boundaries must live in `packages/`.

## Finding things — cheapest first, stop when answered

1. This file — already in context.
2. `grep` / `glob` — scope to the relevant workspace first; the repo is ~4k files and
   unscoped searches return noise.
3. Read the file — only after 2 points at a specific one.

`packages/db/src/schema.generated.ts` and `.next/` are generated. Never edit.

## Answering

- Cite sources as `apps/api/src/routes/user.ts:24`.
- Barrel files (`index.ts` re-exports) match keywords and contain nothing — if one is the
  top hit, follow it to the real definition before answering.
- If two sources disagree, say so.

## Before finishing

- `pnpm lint && pnpm typecheck`
- `pnpm test --filter <workspace>` — scope to the workspace you touched.

## Conventions

- Server Components by default; add `"use client"` only when a hook or handler needs it.
- Database access only through `packages/db` — no Drizzle imports in `apps/`.
- No barrel files in new code. Import from the source module.
```

**~32 lines.** The monorepo-specific fact that earns its place: *scope your grep*. That
one line prevents a lot of wasted retrieval.

---

## A docs / knowledge repo

The case where semantic search actually earns a rung on the ladder.

```markdown
# CLAUDE.md

## Project

Internal engineering handbook. ~400 markdown files under `handbook/`, no code. Readers
ask questions in their own words, so filenames rarely match queries.

## Finding things — cheapest first, stop when answered

1. This file — already in context.
2. `handbook/index.md` — the catalog. Most questions resolve here.
3. `grep` — when you know the term being used.
4. `python3 rag/query.py "<question>"` — when the question is phrased in language that
   won't appear verbatim in the text.
5. Read the file — after 2–4 point at one.

## Answering

- Cite as `handbook/security/access.md#requesting-access`.
- Retrieval ranks "See also" and link-list sections above prose that answers the question.
  Check the section type before answering; if the top hit is a list of links, read the
  next few results.
- Handbook pages carry a `last_reviewed` date. If it's over a year old, say so.

## Before finishing

- `markdownlint handbook/`
- Verify links you cite actually resolve.
```

**~28 lines.**

---

## What these have in common

- **No placeholders.** Every command is real and runnable.
- **The ladder is trimmed to rungs that exist.** Two of the three drop semantic search
  entirely, because `grep` wins for code.
- **One repo-specific retrieval fact each** — scope your grep, skip generated dirs, watch
  for barrel files. That's the part a generic template can't give you.
- **Conventions a linter can't catch**, and nothing a linter already handles.
- **Under 40 lines.** This file is billed every session.
