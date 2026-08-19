# Contributing

## The one rule

Edit the content under `src/`. Never edit generated output. If you find yourself fixing a typo in
`.cursor/rules/` you are patching a shadow, and the next build will cheerfully
undo your work.

## Setup

```bash
uv sync
```

## Workflow

1. Add or edit content under `src/` (`plugin.yaml`, `AGENTS.md`, or a skill).
2. Regenerate every format:
   ```bash
   uv run lazy render
   ```
3. Commit the sources and the regenerated output together.

## Generated output

The generated directories ship empty, each holding only a `.gitkeep` so the
structure survives a clone. Fill them with `uv run lazy render`, and empty them
again with `uv run lazy clean` — both preserve the placeholders, so the
skeleton is never lost.

## Checks

```bash
uv run lazy check   # outputs match src/
uv run ruff format
uv run ruff check .
uv run pytest
```

CI runs all of the above. The `check` step catches the most common mistake:
editing a source and forgetting to rebuild.
