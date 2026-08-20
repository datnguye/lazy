"""Render the authored content in src/ into every supported agent format.

Pure rendering: no printing, no exit codes. The CLI in src/cli.py wraps these.
"""

import shutil
from collections.abc import Sequence
from pathlib import Path
from types import ModuleType

from src.content.sources import Sources
from src.generate.emitters import ALL as EMITTERS

# Generated files that live outside any generated directory.
LOOSE_FILES = ("AGENTS.md", ".github/copilot-instructions.md")

# Placeholder that keeps an otherwise-empty generated directory in git.
KEEP = ".gitkeep"

# Directories owned entirely by the generator; cleared before each write so a
# renamed source never leaves an orphan behind.
GENERATED_DIRS = (
    "plugins",
    ".agents/skills",
    ".cursor/rules",
    ".windsurf/rules",
    ".github/instructions",
    ".kiro/steering",
    ".qoder/rules",
    ".clinerules",
    ".roo/rules",
)


def render(src: Sources, emitters: Sequence[ModuleType] = EMITTERS) -> dict[str, str]:
    """Run each emitter and merge their output."""
    out: dict[str, str] = {}
    for emitter in emitters:
        for path, text in emitter.emit(src).items():
            if path in out:
                raise ValueError(f"two emitters both claim {path}")
            out[path] = text
    return out


def owned_dirs(rendered: dict[str, str]) -> tuple[str, ...]:
    """Return the generated dirs a render actually writes into.

    A partial render must not wipe a format it was not asked to write, so the
    dirs to clear come from the render itself rather than from GENERATED_DIRS.
    """
    return tuple(
        rel for rel in GENERATED_DIRS if any(path.startswith(f"{rel}/") for path in rendered)
    )


def write(rendered: dict[str, str], root: Path) -> None:
    """Replace the rendered part of the generated tree with fresh content.

    A .gitkeep only earns its place in an empty directory, so a dir that gets
    real output loses it; `lazy clean` puts it back when the output goes away.
    """
    for rel in owned_dirs(rendered):
        target = root / rel
        shutil.rmtree(target, ignore_errors=True)
        target.mkdir(parents=True, exist_ok=True)
    for rel, text in rendered.items():
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")


def clean(root: Path, rendered: dict[str, str] | None = None) -> int:
    """Delete generated output, leaving each directory and its .gitkeep behind.

    Files an emitter writes outside a generated directory (AGENTS.md and the
    Copilot repo-wide file) have no skeleton to preserve, so they go too.

    Pass `rendered` to scope the wipe to one format's output; the paths it owns
    come from the render itself, so cleaning one format never touches another.
    """
    dirs = GENERATED_DIRS if rendered is None else owned_dirs(rendered)
    loose = LOOSE_FILES if rendered is None else tuple(r for r in LOOSE_FILES if r in rendered)
    removed = 0
    for rel in dirs:
        target = root / rel
        removed += sum(1 for p in target.rglob("*") if p.is_file() and p.name != KEEP)
        shutil.rmtree(target, ignore_errors=True)
        target.mkdir(parents=True, exist_ok=True)
        (target / KEEP).touch()
    for rel in loose:
        path = root / rel
        if path.exists():
            path.unlink()
            removed += 1
    return removed


def stale(rendered: dict[str, str], root: Path) -> list[str]:
    """Return generated paths whose on-disk content differs from the render.

    Orphans are only hunted in the dirs this render owns, so checking one
    format never reports another format's files as strays.
    """
    drifted = [
        rel
        for rel, text in rendered.items()
        if not (root / rel).exists() or (root / rel).read_text(encoding="utf-8") != text
    ]
    expected = set(rendered)
    for rel in owned_dirs(rendered):
        base = root / rel
        if not base.exists():
            continue
        drifted += [
            str(p.relative_to(root))
            for p in base.rglob("*")
            if p.is_file() and p.name != KEEP and str(p.relative_to(root)) not in expected
        ]
    return sorted(set(drifted))
