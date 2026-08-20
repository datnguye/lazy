"""The `lazy render` command."""

import typer

from src.cli._shared import DEFAULT_ROOT, FormatOption, RootOption, render_all, select
from src.generate import build


def render(root: RootOption = DEFAULT_ROOT, format: FormatOption = None) -> None:
    """Write generated formats from src/, or just the ones named with --format."""
    rendered = render_all(root, format)
    build.write(rendered, root)
    typer.secho(
        f"Wrote {len(rendered)} files across {len(select(format))} formats.",
        fg=typer.colors.GREEN,
    )
