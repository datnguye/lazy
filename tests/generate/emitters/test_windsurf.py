"""Tests for the Devin Desktop / Windsurf emitter."""

import pytest

from src.content import frontmatter
from src.generate.emitters import windsurf
from tests.conftest import doc


@pytest.mark.parametrize(
    ("meta", "trigger"),
    [
        ({"alwaysApply": True}, "always_on"),
        ({"globs": ["*.py"]}, "glob"),
        ({"globs": "*.py"}, "glob"),
        ({}, "model_decision"),
    ],
)
def test_trigger_mapping(meta, trigger):
    assert frontmatter.parse(windsurf._rule(doc(**meta)))[0]["trigger"] == trigger


def test_flags_oversized_rules():
    assert windsurf.over_limit({".windsurf/rules/a.md": "x" * 6001}) == [".windsurf/rules/a.md"]
    assert windsurf.over_limit({".windsurf/rules/a.md": "x"}) == []
    assert windsurf.over_limit({".windsurf/workflows/a.md": "x" * 6001}) == []


def test_budget_applies_only_to_windsurf():
    """Cursor, Qoder, Roo and Cline document no per-rule character cap."""
    oversized = "x" * 6001
    assert windsurf.over_limit({".cursor/rules/a.mdc": oversized}) == []
    assert windsurf.over_limit({".qoder/rules/a.md": oversized}) == []
    assert windsurf.over_limit({".roo/rules/a.md": oversized}) == []
