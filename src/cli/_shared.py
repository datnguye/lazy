"""Options and helpers shared by every command."""

from pathlib import Path
from types import ModuleType
from typing import Annotated

import typer

from src.content import sources
from src.content.sources import ROOT
from src.generate import build
from src.generate.emitters import ALL as EMITTERS
from src.generate.emitters import BY_NAME, windsurf

# Formats that share an output tree, where rendering one without the other
# leaves a broken result: the Claude plugin.json points at hooks/hooks.json.
COUPLED = {"claude": ("hooks",), "hooks": ("claude",)}

RootOption = Annotated[
    Path,
    typer.Option("--root", "-r", help="Repository root to read from and write into."),
]

FormatOption = Annotated[
    list[str] | None,
    typer.Option(
        "--format",
        "-f",
        help="Only this format; repeatable. Defaults to every format.",
    ),
]

DEFAULT_ROOT = ROOT


def select(names: list[str] | None) -> tuple[ModuleType, ...]:
    """Resolve format names to emitters, keeping ALL's order for stable output."""
    if not names:
        return EMITTERS
    unknown = sorted(set(names) - set(BY_NAME))
    if unknown:
        typer.secho(
            f"Unknown format: {', '.join(unknown)}. Choose from: {', '.join(BY_NAME)}.",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(2)
    chosen = set(names)
    for name in list(chosen):
        chosen.update(COUPLED.get(name, ()))
    return tuple(e for e in EMITTERS if e.__name__.rsplit(".", 1)[-1] in chosen)


def render_all(root: Path, formats: list[str] | None = None) -> dict[str, str]:
    """Load sources and render them, warning about any oversized rule."""
    rendered = build.render(sources.load(root / "src"), select(formats))
    for path in windsurf.over_limit(rendered):
        typer.secho(
            f"warning: {path} exceeds Devin/Windsurf's per-rule character budget",
            fg=typer.colors.YELLOW,
            err=True,
        )
    return rendered
