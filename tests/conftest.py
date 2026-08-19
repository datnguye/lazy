"""Shared fixtures and helpers."""

import pytest

from src.content import sources
from src.content.sources import Doc


@pytest.fixture
def src():
    """The repository's own src/ tree, loaded once per test."""
    return sources.load()


def doc(**meta) -> Doc:
    """Build a Doc with sensible defaults for frontmatter-mapping tests."""
    meta.setdefault("description", "d")
    return Doc(slug="s", meta=meta, body="body\n")
