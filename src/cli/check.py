"""The `lazy check` command."""

import typer

from src.cli._shared import DEFAULT_ROOT, FormatOption, RootOption, render_all
from src.generate import build


def check(root: RootOption = DEFAULT_ROOT, format: FormatOption = None) -> None:
    """Verify the generated files match src/, without writing anything."""
    rendered = render_all(root, format)
    drifted = build.stale(rendered, root)
    if drifted:
        typer.secho(
            "Generated files are out of date. Run: uv run lazy render",
            fg=typer.colors.RED,
            err=True,
        )
        for rel in drifted:
            typer.echo(f"  {rel}", err=True)
        raise typer.Exit(1)
    typer.secho(f"{len(rendered)} generated files are up to date.", fg=typer.colors.GREEN)
