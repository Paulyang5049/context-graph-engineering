---
name: reference-corpus
description: the Obsidian vault used to test retrieval, and its measured numbers
metadata:
  type: reference
  updated: 2026-07-27
---

Retrieval is tested against the **Agentic Knowledge Graph** Obsidian vault (a personal
vault, not committed to this repo). Its `wiki/` folder is the corpus.

Measured 2026-07-27:

- 106 markdown documents → **428 chunks**, vocabulary 1356 terms
- Corpus: 135,733 chars raw; **87,945 chars of indexed chunk text** (~22K tokens)
- Top-5 retrieval returns: 2,952 chars (~738 tokens, **3.36%**) for
  "what is loop engineering"; 1,422 chars (~355 tokens, **1.62%**) for
  "how does agent memory work across sessions"

These are the numbers quoted in `README.md` §"The principle". Re-measure before
changing them — the vault grows.

**How to apply:** to reproduce, run `rag/ingest.py` against the vault's `wiki/`
directory. The vault is not redistributable, so anyone else should substitute their
own markdown folder; the pipeline is corpus-agnostic.

Related: [[rag-embedding-choice]]
