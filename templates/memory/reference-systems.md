---
name: reference-systems
description: where to look for logs, tickets, dashboards, and who's on call
metadata:
  type: reference
  updated: 2026-04-18
---

- **Issue tracker:** Linear, team `PLT`. Bug convention: title starts with the
  affected service name.
- **Logs:** Datadog, `service:api-gateway env:prod`. Retention is 15 days — anything
  older needs the S3 archive.
- **Dashboards:** "API Golden Signals" is the one used in incident review.
- **On-call:** PagerDuty schedule `platform-primary`. Escalation is 15 min.

**How to apply:** when asked to investigate an incident, check the golden-signals
dashboard before reading code — most reports turn out to be a dependency, not us.

<!-- EXAMPLE FILE — replace with a real memory.
     Note what this demonstrates:
     - Stores *pointers*, not content. It doesn't cache what the dashboard says
       (that changes hourly and would be stale before it was useful); it records
       where to look. This is the cheapest kind of memory to keep correct.
     - Exact query strings are preserved verbatim — they're only useful precisely. -->
