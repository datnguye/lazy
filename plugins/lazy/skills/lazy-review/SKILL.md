---
name: lazy-review
description: 'Review a diff or a whole repo for over-engineering. Finds what to delete:
  reinvented stdlib, needless deps, speculative abstractions, comments restating code.
  One line per finding.'
license: MIT
---

<!-- Generated from src/ by src/build.py. Do not edit. -->

# Lazy Review

Find unnecessary complexity. One line per finding: location, what to cut, what
replaces it.

Default scope is the current diff. Given a path, or asked for a repo-wide pass,
scan the whole tree instead and rank biggest cut first.

# Format

`L<line>: <tag> <what>. <replacement>.`, or `<file>:L<line>:` outside a single-file diff.

| Tag | Means | Replacement |
|-----|-------|-------------|
| `delete:` | Dead code, unused flexibility, speculative feature | Nothing |
| `stdlib:` | Hand-rolled thing the standard library ships | Name the function |
| `native:` | Dependency or code doing what the platform already does | Name the feature |
| `yagni:` | Abstraction with one implementation, config nobody sets, layer with one caller | Inline it |
| `shrink:` | Same logic, fewer lines | Show the shorter form |
| `comment:` | Inline comment restating the code it sits on, or narrating the diff | Delete it, or rename so the code says it |

# What to Hunt

- Dependencies the stdlib or platform already ships
- Single-implementation interfaces, factories with one product, wrappers that only delegate
- Files exporting one thing, dead flags and config, hand-rolled stdlib
- Comments restating the line below them, and commented-out code

# Examples

- ✅ `L12-38: stdlib: 27-line validator class. "@" in email, 1 line.`
- ✅ `L4: native: moment.js for one format call. Intl.DateTimeFormat, 0 deps.`
- ✅ `repo.py:L88: yagni: AbstractRepository, one implementation. Inline it.`
- ✅ `L52-71: delete: retry wrapper around an idempotent local call.`
- ✅ `L30-44: shrink: manual loop builds dict. dict(zip(keys, values)), 1 line.`
- ✅ `L17: comment: "# increment counter" above counter += 1. Delete.`
- ❌ "This EmailValidator class might be more complex than necessary, have you considered whether all these rules are needed at this stage?"

# Scoring

End with `net: -<N> lines possible.`, adding `-<M> deps` on a repo-wide pass.
Nothing to cut: `Lean already. Ship.`

# Boundaries

- Scope is over-engineering only. Correctness bugs, security holes, and performance go to a normal review pass
- **Never** flag a smoke test, an `assert`-based self-check, a `lazy:` marker, a docstring, or a comment explaining a genuine *why*
- Lists findings, applies nothing
Say "stop lazy" or "normal mode" to revert. Resume anytime with `/lazy`.
