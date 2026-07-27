# CLAUDE.md

Instructions for agents working **on this repo**. This is a live instance of
[`templates/CLAUDE.md`](templates/CLAUDE.md) — if you're here to grab the template, take
that file, not this one. Keeping a real one at the root is deliberate: a template nobody
runs against a real project drifts.

## Project

`context-graph-engineering` — drop-in `CLAUDE.md` / `MEMORY.md` templates plus a readable
reference RAG implementation, aimed at developers who want coding agents to spend fewer
tokens and make fewer retrieval mistakes. Mostly markdown; the only code is `rag/`
(Python 3.10+, numpy + PyYAML only, deliberately dependency-light).

The claims in the docs are evidence-backed. Two primary sources:
[Anthropic on context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
and [arXiv:2606.24775](https://arxiv.org/abs/2606.24775) on agent memory. Don't add a
claim to the README without one.

## Retrieval order — cheapest first

Stop as soon as one answers the question. Don't pre-load files "just in case."

1. **This file + `MEMORY.md`** — already in context.
2. **`README.md`** — the map of what exists here and why.
3. **`grep` / `glob`** — resolves most "where is X" questions in one call.
4. **`rag/query.py`** — this repo's own pipeline, for questions phrased in language that
   won't match a filename.
5. **Full file read** — only after 1–4 point at a specific file.

## Citing

Every claim carries its source: `path/to/file.py:42`, `doc.md#heading`, or a URL for
external evidence. Quote the minimum and cite; don't paste sections.

## Don't trust the top retrieval result blindly

Similarity rank measures vocabulary overlap, not information content. Short keyword-dense
sections (link lists, tables of contents, "Entities Mentioned") outrank real prose.
Check the section type before answering; if the top hit is boilerplate, read ranks 2–5.
This repo documents the exact failure case in `rag/README.md`.

## Verify before finalising

```bash
cd rag
python3 ingest.py "/path/to/markdown/corpus" --out /tmp/verify_index   # must succeed
python3 query.py "what is loop engineering" --index /tmp/verify_index  # must return hits
python3 -m py_compile rag_lib.py ingest.py query.py
```

Re-check claims against the source, not the excerpt. If two sources disagree, say so —
don't silently pick one.

## Conventions

- **No new runtime dependencies in `rag/`.** numpy + PyYAML is the whole budget. The
  point is that it runs anywhere, offline, including in sandboxes that block model
  downloads (which is why it's TF-IDF and not sentence-transformers — see `rag/README.md`).
- **Templates carry `<!-- note -->` comments** explaining *why* each section exists, and
  `[bracketed]` placeholders for the user to fill. Keep both when editing.
- **Documented failure modes stay documented.** The `Entities Mentioned` retrieval bug in
  `rag/README.md` is not a bug to fix — it's the evidence for a rule. Don't "clean it up."
- **`templates/CLAUDE.md` stays under ~200 lines.** It's charged on every session of
  every project that adopts it.

## This file vs. `MEMORY.md`

`CLAUDE.md` = standing rules, human-authored, reviewed. `MEMORY.md` = observations the
agent recorded. Don't duplicate across them.

## Anti-patterns

- Reading a directory because it "might be relevant."
- Adding a claim to the README without a source.
- Growing this file into a manual — push situational detail into `docs/`.
