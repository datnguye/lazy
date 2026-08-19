"""The `lazy formats` command."""

import typer

from src.cli._shared import DEFAULT_ROOT, RootOption
from src.content import sources
from src.generate.emitters import ALL as EMITTERS


def formats(root: RootOption = DEFAULT_ROOT) -> None:
    """List each output format and the files it generates."""
    src = sources.load(root / "src")
    for emitter in EMITTERS:
        paths = emitter.emit(src)
        name = emitter.__name__.rsplit(".", 1)[-1]
        typer.secho(f"{name} ({len(paths)} files)", fg=typer.colors.CYAN, bold=True)
        for path in sorted(paths):
            typer.echo(f"  {path}")
