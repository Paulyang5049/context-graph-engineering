# Templates

The drop-in files. Copy these into a project **before** you start working with an agent.

```bash
cp templates/CLAUDE.md   your-project/
cp templates/MEMORY.md   your-project/
cp -r templates/memory   your-project/
```

| File | Loaded | Purpose |
|---|---|---|
| `CLAUDE.md` | Every session | Standing rules: retrieval order, citation, conventions. Human-authored, reviewed. |
| `MEMORY.md` | Every session | Index of what the agent has learned. Thin by design. |
| `memory/*.md` | On demand | The actual memories. Detailed — this is the cheap tier. |

## After copying

1. **`CLAUDE.md`** — fill in the `[bracketed]` sections, set your real lint/test commands,
   delete the `<!-- note -->` comments. Keep it under ~200 lines; it's charged every session.
2. **`MEMORY.md`** — replace the example index entries with nothing. It starts empty.
3. **`memory/`** — delete the three example files. They exist to show the shape; each has
   a trailing comment explaining what it demonstrates.
4. Commit all of it. `CLAUDE.md` changes should go through review like any other
   requirement; `MEMORY.md` will be edited by the agent as it works.

## Other agents

Same content, different filename:

| Tool | File |
|---|---|
| Claude Code | `CLAUDE.md` |
| Cursor | `.cursorrules` |
| GitHub Copilot | `.github/copilot-instructions.md` |
| Generic / multi-tool | `AGENTS.md` |

`MEMORY.md` has no tool-specific convention — reference it from the instruction file so
the agent knows to read and maintain it.

## Why they're shaped this way

- Retrieval-order reasoning: [`../README.md`](../README.md)
- Memory architecture choice and the benchmark evidence: [`../docs/memory-architectures.md`](../docs/memory-architectures.md)
