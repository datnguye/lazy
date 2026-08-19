"""Tests for the GitHub Copilot emitter."""

from src.content import frontmatter
from src.generate.emitters import copilot
from tests.conftest import doc


def test_instruction_scopes_with_apply_to(src):
    meta, _ = frontmatter.parse(copilot.emit(src)[".github/instructions/lazy.instructions.md"])
    assert meta["applyTo"] == "**"


def test_instruction_defaults_apply_to_everything():
    assert frontmatter.parse(copilot._instruction(doc()))[0]["applyTo"] == "**"


def test_instruction_joins_glob_lists():
    assert frontmatter.parse(copilot._instruction(doc(globs=["a", "b"])))[0]["applyTo"] == "a, b"
