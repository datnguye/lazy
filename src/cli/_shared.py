"""Options and helpers shared by every command."""

from pathlib import Path
from typing import Annotated

import typer

from src.content import sources
from src.content.sources import ROOT
from src.generate import build
from src.generate.emitters import windsurf

RootOption = Annotated[
    Path,
    typer.Option("--root", "-r", help="Repository root to read from and write into."),
]

DEFAULT_ROOT = ROOT


def render_all(root: Path) -> dict[str, str]:
    """Load sources and render them, warning about any oversized rule."""
    rendered = build.render(sources.load(root / "src"))
    for path in windsurf.over_limit(rendered):
        typer.secho(
            f"warning: {path} exceeds Devin/Windsurf's per-rule character budget",
            fg=typer.colors.YELLOW,
            err=True,
        )
    return rendered
