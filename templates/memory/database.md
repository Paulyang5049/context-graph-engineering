---
name: database
description: which database this project uses and why — supersedes older Postgres notes
metadata:
  type: project
  updated: 2026-06-14
---

We run CockroachDB. Moved from Postgres in June 2026.

**Why:** the EU rollout needed multi-region writes. The existing Postgres HA setup
couldn't do it without adding a proxy layer nobody on the team wanted to own.

**How to apply:** CRDB uses serializable isolation, so transactions can fail with
error `40001` and *must* be retried with backoff — this is normal operation, not a
bug. Connection/retry code written before the migration follows Postgres semantics
and is not a safe pattern to copy.

Related: [[deploy]]

<!-- EXAMPLE FILE — replace with a real memory.
     Note what this demonstrates:
     - Named for the *thing* (database), not the *event* (the migration). Next time
       the database changes, this file is edited; a new one isn't appended. That
       stable identity is what stops an agent citing the Postgres answer in 2027.
     - Detail is preserved verbatim (the literal error code 40001). Summarizing this
       to "handle retries" would lose exactly the token that makes it actionable.
     - The "why" is here, so a future edge case can be judged against it. -->
