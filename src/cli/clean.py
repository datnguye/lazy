"""The `lazy clean` command."""

import typer

from src.cli._shared import DEFAULT_ROOT, FormatOption, RootOption, render_all
from src.generate import build


def clean(root: RootOption = DEFAULT_ROOT, format: FormatOption = None) -> None:
    """Remove generated files, or just one format's with --format."""
    rendered = render_all(root, format) if format else None
    removed = build.clean(root, rendered)
    typer.secho(
        f"Removed {removed} generated files; directory skeleton kept.",
        fg=typer.colors.GREEN,
    )
