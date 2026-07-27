---
name: evidence-standard
description: every claim in the README needs a citable source; the two primary ones
metadata:
  type: project
  updated: 2026-07-27
---

Claims in `README.md` and `docs/` must be traceable to a source, not asserted from
intuition. The two primary sources currently underwriting the docs:

1. **Anthropic, "Effective context engineering for AI agents"** (Sep 2025) —
   https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
   Underwrites: finite attention budget, just-in-time retrieval, grep-beats-stale-index,
   compaction / note-taking / sub-agents as long-horizon techniques.
2. **Zhou et al., "Are We Ready For An Agent-Native Memory System?"**
   arXiv:2606.24775 — 12 memory systems, 11 datasets. Underwrites the entire memory
   architecture section: the four-family taxonomy, the late filtering principle, the
   24.2 → 8.5 Exact Match drop from write-time summarization, revisability, localized
   maintenance, conservative consolidation.

**Why:** the whole value proposition of this repo is that its advice is measured rather
than vibes-based. One unsourced confident claim undermines the rest.

**How to apply:** when adding a rule to a template, name which finding supports it. If
none does, either find one or mark it explicitly as an opinion.
