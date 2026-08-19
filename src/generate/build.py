"""Render the authored content in src/ into every supported agent format.

Pure rendering: no printing, no exit codes. The CLI in src/cli.py wraps these.
"""

import shutil
from pathlib import Path

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


def render(src: Sources) -> dict[str, str]:
    """Run every emitter and merge their output."""
    out: dict[str, str] = {}
    for emitter in EMITTERS:
        for path, text in emitter.emit(src).items():
            if path in out:
                raise ValueError(f"two emitters both claim {path}")
            out[path] = text
    return out


def write(rendered: dict[str, str], root: Path) -> None:
    """Replace the generated tree with freshly rendered content.

    Each generated directory keeps a .gitkeep so the structure survives a clone
    even before anything is rendered into it; wiping the tree must not take
    those with it.
    """
    for rel in GENERATED_DIRS:
        target = root / rel
        shutil.rmtree(target, ignore_errors=True)
        target.mkdir(parents=True, exist_ok=True)
        (target / KEEP).touch()
    for rel, text in rendered.items():
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")


def clean(root: Path) -> int:
    """Delete generated output, leaving each directory and its .gitkeep behind.

    Files an emitter writes outside a generated directory (AGENTS.md and the
    Copilot repo-wide file) have no skeleton to preserve, so they go too.
    """
    removed = 0
    for rel in GENERATED_DIRS:
        target = root / rel
        removed += sum(1 for p in target.rglob("*") if p.is_file() and p.name != KEEP)
        shutil.rmtree(target, ignore_errors=True)
        target.mkdir(parents=True, exist_ok=True)
        (target / KEEP).touch()
    for rel in LOOSE_FILES:
        path = root / rel
        if path.exists():
            path.unlink()
            removed += 1
    return removed


def stale(rendered: dict[str, str], root: Path) -> list[str]:
    """Return generated paths whose on-disk content differs from the render."""
    drifted = [
        rel
        for rel, text in rendered.items()
        if not (root / rel).exists() or (root / rel).read_text(encoding="utf-8") != text
    ]
    expected = set(rendered)
    for rel in GENERATED_DIRS:
        base = root / rel
        if not base.exists():
            continue
        drifted += [
            str(p.relative_to(root))
            for p in base.rglob("*")
            if p.is_file() and p.name != KEEP and str(p.relative_to(root)) not in expected
        ]
    return sorted(set(drifted))
