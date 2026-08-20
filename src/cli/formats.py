"""The `lazy formats` command."""

import typer

from src.cli._shared import DEFAULT_ROOT, FormatOption, RootOption, select
from src.content import sources


def formats(root: RootOption = DEFAULT_ROOT, format: FormatOption = None) -> None:
    """List each output format and the files it generates."""
    src = sources.load(root / "src")
    for emitter in select(format):
        paths = emitter.emit(src)
        name = emitter.__name__.rsplit(".", 1)[-1]
        typer.secho(f"{name} ({len(paths)} files)", fg=typer.colors.CYAN, bold=True)
        for path in sorted(paths):
            typer.echo(f"  {path}")
