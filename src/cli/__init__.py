"""The `lazy` command line interface, one module per command."""

import typer

from src.cli.check import check
from src.cli.clean import clean
from src.cli.formats import formats
from src.cli.render import render
from src.cli.skills import skills

app = typer.Typer(
    help="Author agent skills once in src/, render them into every agent format.",
    no_args_is_help=True,
    add_completion=False,
)

for command in (render, check, clean, formats, skills):
    app.command()(command)
