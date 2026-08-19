# lazy

> Lazy is not lack of awareness, it is full context awareness.

Too lazy to write the pitch, so here is the important part: your agent stops
over-engineering. YAGNI, stdlib first, native over dependencies, the shortest
diff that works.

Authored once, rendered into nine agent formats. Writing the same prompt nine
times would be, of all things, not lazy.

## The ladder

Stop at the first rung that holds:

1. **Needs to exist at all?** Skip it (YAGNI)
2. **Already in this codebase?** Reuse it
3. **Stdlib does it?** Use it
4. **Native feature covers it?** CSS over JS, a DB constraint over app code
5. **Installed dependency solves it?** Never add one for what a few lines can do
6. **One line?** One line
7. **Only then**: the minimum code that works

Climb only after you understand the problem.

## Skills

| Skill | What it does |
| --- | --- |
| `/lazy` | The ladder, always on. `lite` / `full` / `ultra` |
| `/lazy-review` | Finds what to delete, on a diff or the whole repo |
| `/lazy-debt` | Harvests `lazy:` comments into a ledger |

## Install

```bash
/plugin marketplace add datnguye/lazy
/plugin install lazy@datnguye
```

Other tools: clone, `uv run lazy render`, copy the directory yours reads.

| Tool | Output |
| --- | --- |
| Claude Code | `plugins/lazy/` + `SessionStart` hook |
| Codex, Cursor, Copilot, Devin | `AGENTS.md`, `.agents/skills/` |
| Cursor | `.cursor/rules/*.mdc` |
| Devin Desktop (Windsurf) | `.windsurf/rules/` |
| GitHub Copilot | `.github/copilot-instructions.md`, `.github/instructions/` |
| Kiro | `.kiro/steering/` |
| Qoder | `.qoder/rules/` |
| Cline | `.clinerules/` |
| Zoo Code | `.roo/rules/` |

Nine formats, because the industry agreed agent instructions belong in a
markdown file and then stopped agreeing immediately afterwards.

## Authoring

Edit `src/`, nothing else. Repeated text lives once in `src/shared/` and is
inlined at render time, since most formats flatten a skill to one file.

```bash
uv run lazy render   # write every format
uv run lazy check    # fail if stale (CI runs this)
uv run lazy clean    # remove them, keep the skeleton
uv run pytest        # 100% coverage enforced
```

## License

MIT, see [LICENSE](LICENSE).
