"""Tests for the Cursor emitter."""

import pytest

from src.content import frontmatter
from src.generate.emitters import cursor
from tests.conftest import doc


def test_rules_use_the_mdc_extension(src):
    assert any(p.endswith(".mdc") for p in cursor.emit(src))


@pytest.mark.parametrize(
    ("meta", "expected"),
    [
        ({"alwaysApply": True, "globs": ["*.py"]}, {"alwaysApply": True}),
        ({"globs": ["*.py"]}, {"alwaysApply": False, "globs": "*.py"}),
        ({"globs": "*.py"}, {"alwaysApply": False, "globs": "*.py"}),
        ({}, {"alwaysApply": False}),
    ],
)
def test_rule_type_mapping(meta, expected):
    result, _ = frontmatter.parse(cursor._rule(doc(**meta)))
    for key, value in expected.items():
        assert result[key] == value
    if "globs" not in expected:
        assert "globs" not in result
