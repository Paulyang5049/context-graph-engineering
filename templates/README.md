# Templates

The retrieval policy as droppable files.

```bash
curl -o CLAUDE.md https://raw.githubusercontent.com/Paulyang5049/context-graph-engineering/main/templates/CLAUDE.md
curl -o MEMORY.md https://raw.githubusercontent.com/Paulyang5049/context-graph-engineering/main/templates/MEMORY.md
mkdir -p memory
```

Or, from a clone:

```bash
cp templates/CLAUDE.md your-project/          # the policy
cp templates/MEMORY.md your-project/          # optional: corrections that stick
cp -r templates/memory  your-project/         # optional: the memory content
```

| File | Loaded | Cost | Purpose |
|---|---|---|---|
| `CLAUDE.md` | every session | ~570 tok | Standing rules: retrieval order, citation, conventions |
| `MEMORY.md` | every session | ~300 tok | Index of what the agent learned. An index, not an essay. |
| `memory/*.md` | on demand | free until opened | The actual memories. Detailed — this is the cheap tier. |

## After copying

1. **`CLAUDE.md`** — fill in `[brackets]`, set your real lint/test commands, delete the
   `<!-- comments -->`. Keep it under ~100 lines.
2. **`MEMORY.md`** — delete the example index entries. It starts empty.
3. **`memory/`** — delete the three examples. Each has a trailing comment explaining what
   it demonstrates; read them once, then remove.
4. Commit all of it. `CLAUDE.md` changes go through review like any other requirement;
   `MEMORY.md` gets edited by the agent as it works.

## Other agents

Same content, different filename: `.cursorrules` (Cursor),
`.github/copilot-instructions.md` (Copilot), `AGENTS.md` (generic). `MEMORY.md` has no
standard name — just reference it from the instruction file so the agent maintains it.

## Why these are shaped this way

[`../README.md`](../README.md) — the retrieval ladder and what it saves.
[`../docs/memory-architectures.md`](../docs/memory-architectures.md) — memory design
options, if the default doesn't fit.
