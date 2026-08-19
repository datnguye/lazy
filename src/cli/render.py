"""The `lazy render` command."""

import typer

from src.cli._shared import DEFAULT_ROOT, RootOption, render_all
from src.generate import build
from src.generate.emitters import ALL as EMITTERS


def render(root: RootOption = DEFAULT_ROOT) -> None:
    """Write every generated format from src/."""
    rendered = render_all(root)
    build.write(rendered, root)
    typer.secho(
        f"Wrote {len(rendered)} files across {len(EMITTERS)} formats.",
        fg=typer.colors.GREEN,
    )
