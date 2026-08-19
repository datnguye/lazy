"""The `lazy clean` command."""

import typer

from src.cli._shared import DEFAULT_ROOT, RootOption
from src.generate import build


def clean(root: RootOption = DEFAULT_ROOT) -> None:
    """Remove every generated file, keeping the directory skeleton."""
    removed = build.clean(root)
    typer.secho(
        f"Removed {removed} generated files; directory skeleton kept.",
        fg=typer.colors.GREEN,
    )
