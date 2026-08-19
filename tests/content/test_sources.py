"""Tests for the source loader."""

import shutil

import pytest

from src.content import sources
from src.content.sources import ROOT, Doc


def test_loader_reads_every_source_kind(src):
    assert src.plugin["name"] == "lazy"
    assert [d.slug for d in src.skills] == ["lazy", "lazy-debt", "lazy-review"]
    assert "lazy senior developer" in src.guidance


def test_loader_collects_supporting_files(tmp_path, src):
    shutil.copytree(ROOT / "src", tmp_path / "src")
    (tmp_path / "src/skills/lazy/reference.md").write_text("notes\n", encoding="utf-8")
    loaded = sources.load(tmp_path / "src")
    assert [p.name for p in loaded.skills[0].extras] == ["reference.md"]


@pytest.mark.parametrize(
    ("meta", "expected"),
    [
        ({"allowed-tools": ["A", "B"]}, "A, B"),
        ({"allowed-tools": "A, B"}, "A, B"),
        ({"tools": ["A"]}, "A"),
        ({}, None),
        ({"allowed-tools": []}, None),
    ],
)
def test_tools_normalise_to_a_comma_separated_string(meta, expected):
    assert Doc(slug="s", meta=meta, body="").tools() == expected


def test_description_is_stripped():
    assert Doc(slug="s", meta={"description": "  d  "}, body="").description == "d"
    assert Doc(slug="s", meta={}, body="").description == ""


def test_expand_inlines_a_shared_block():
    assert sources.expand("a\n{{ x }}\nb\n", {"x": "BLOCK"}) == "a\nBLOCK\nb\n"


def test_expand_tolerates_missing_whitespace():
    assert sources.expand("{{x}}\n", {"x": "B"}) == "B\n"


def test_expand_replaces_every_occurrence():
    assert sources.expand("{{ x }}\n{{ x }}\n", {"x": "B"}) == "B\nB\n"


def test_expand_leaves_text_without_markers_alone():
    assert sources.expand("plain\n", {}) == "plain\n"


def test_expand_rejects_an_unknown_block():
    with pytest.raises(KeyError, match="unknown shared block: nope"):
        sources.expand("{{ nope }}\n", {})


def test_loaded_skills_have_no_unexpanded_markers(src):
    for doc in src.skills:
        assert "{{" not in doc.body, doc.slug
    assert "{{" not in src.guidance


def test_shared_blocks_are_actually_inlined(src):
    review = next(d for d in src.skills if d.slug == "lazy-review")
    assert "| `yagni:` |" in review.body


def test_expand_keeps_list_indentation():
    """A marker used as a bullet keeps its bullet."""
    assert sources.expand("- {{ x }}\n", {"x": "B"}) == "- B\n"
    assert sources.expand("* {{ x }}\n", {"x": "B"}) == "* B\n"
