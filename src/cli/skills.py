"""The `lazy skills` command."""

import typer

from src.cli._shared import DEFAULT_ROOT, RootOption
from src.content import sources


def skills(root: RootOption = DEFAULT_ROOT) -> None:
    """List the authored skills and their descriptions."""
    for doc in sources.load(root / "src").skills:
        typer.secho(doc.slug, fg=typer.colors.CYAN, bold=True)
        typer.echo(f"  {doc.description}")
