# MEMORY.md

<!-- Index of what the agent has learned. Loaded every session, so it stays an index:
     one line per memory, content in memory/*.md, opened only when the topic is live.
     Why it's shaped this way: docs/memory-architectures.md -->

What I've learned about this project. Content in `memory/`; open a file when its topic
comes up.

## Project
- [Database](memory/database.md) — CockroachDB since June; Postgres patterns are stale.

## Feedback
- [Testing](memory/feedback-testing.md) — targeted tests only; full suite is 40 min.

## Reference
- [Systems](memory/reference-systems.md) — logs, tickets, dashboards, on-call.

---

**Writing memories** — one file per *thing* (`database.md`), not per event, so updates
overwrite instead of piling up. Record the *why*, not just the rule. Store detail: be
generous on disk, ruthless about what loads. Write when you learn it.

**Don't save** what the code already says, bug fixes (they're in the commit), task state,
or anything in `CLAUDE.md`. Never secrets.

**Before acting** on a memory that names a file or symbol, verify it still exists.
