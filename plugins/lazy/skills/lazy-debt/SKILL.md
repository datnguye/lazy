---
name: lazy-debt
description: 'Harvest every lazy: shortcut comment into one debt ledger, so deferrals
  get tracked instead of forgotten. One-shot report.'
license: MIT
---

<!-- Generated from src/ by src/build.py. Do not edit. -->

# Lazy Debt

Collect every `lazy:` shortcut comment into one ledger so a deferral cannot
quietly become permanent.

# Scan

```bash
grep -rnE '(#|//) ?lazy:' .
```

Skip `node_modules`, `.git`, and build output. Add other comment prefixes if
your stack uses them.

# Output

One row per marker, grouped by file:

`<file>:<line>, <what was simplified>. ceiling: <the limit>. upgrade: <the trigger>.`

- The convention is `lazy: <ceiling>, <upgrade path>`, so pull both from the comment
- **CRITICAL**: Any marker naming no upgrade path gets a `no-trigger` tag. Those are the ones that rot
- End with `<N> markers, <M> with no trigger.` Nothing found: `No lazy: debt. Clean ledger.`

# Boundaries

- Reads and reports only. To persist it, ask first, then write `LAZY-DEBT.md`
- Say "stop lazy" or "normal mode" to revert. Resume anytime with `/lazy`.
