---
name: rag-embedding-choice
description: why rag/ uses TF-IDF instead of a downloaded embedding model
metadata:
  type: project
  updated: 2026-07-27
---

`rag/` uses a hand-rolled TF-IDF index (`rag_lib.py::TfidfIndex`), not dense embeddings.

**Why:** dense embeddings were tried first. `fastembed` with
`sentence-transformers/all-MiniLM-L6-v2` failed at model-download time with
`httpx.ProxyError: 403 Forbidden` — the sandbox routes egress through an allowlisted
proxy that blocks Hugging Face Hub. Rather than work around it, TF-IDF became the
choice, because it also happens to be a reasonable fit: this corpus has a small,
distinctive vocabulary ("loop engineering", "context rot") where lexical overlap
carries most of the signal.

**How to apply:** don't "upgrade" this to sentence-transformers as a drive-by
improvement — it would break the repo's stated promise of running offline with only
numpy + PyYAML. The migration path is documented in `rag/README.md` §"Scaling up" as
something the *user* opts into.

Related: [[reference-corpus]]
