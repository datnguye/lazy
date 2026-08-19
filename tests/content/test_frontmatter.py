"""Tests for the frontmatter helper."""

import pytest

from src.content import frontmatter


def test_parse_returns_mapping_and_body():
    data, body = frontmatter.parse("---\nname: x\n---\n\nhello\n")
    assert data == {"name": "x"}
    assert body == "hello\n"


def test_parse_without_frontmatter():
    assert frontmatter.parse("hello\n") == ({}, "hello\n")


def test_parse_unterminated_frontmatter():
    assert frontmatter.parse("---\nname: x\n") == ({}, "---\nname: x\n")


def test_parse_rejects_non_mapping():
    with pytest.raises(ValueError, match="must be a mapping"):
        frontmatter.parse("---\n- a\n---\n\nbody\n")


def test_parse_empty_frontmatter():
    assert frontmatter.parse("---\n\n---\n\nbody\n") == ({}, "body\n")


def test_render_roundtrip():
    text = frontmatter.render({"name": "x"}, "hello")
    assert frontmatter.parse(text) == ({"name": "x"}, "hello\n")


def test_render_without_frontmatter():
    assert frontmatter.render({}, "hello") == "hello\n"
    assert frontmatter.render({}, "hello\n") == "hello\n"
