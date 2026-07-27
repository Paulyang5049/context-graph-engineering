---
name: feedback-testing
description: run targeted tests, not the full suite, unless explicitly asked
metadata:
  type: feedback
  updated: 2026-05-02
---

Run the tests for the files touched. Do not run the full suite by default.

**Why:** the full suite takes ~40 minutes and mostly exercises code paths unrelated
to any given change. Asked for this after three consecutive sessions ended with a
long test run that found nothing.

**How to apply:** `pytest path/to/test_file.py` for the changed module, plus anything
that imports it. Run the full suite only before a release, or when explicitly asked.
If a targeted run can't be determined (e.g. a change to shared config), say so and
ask rather than defaulting to everything.

<!-- EXAMPLE FILE — replace with a real memory.
     Note what this demonstrates:
     - Records the *reason* (40 min, three wasted sessions), so the rule can be
       overridden intelligently — a config change genuinely might need the full suite,
       and an agent that only knows "don't run the full suite" can't work that out.
     - Captures a correction the user made once, so they never have to make it again.
       This is where most of the compounding value in a memory system comes from. -->
