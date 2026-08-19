"""Tests for the plain-markdown rule emitter (Kiro, Qoder, Cline, Zoo Code)."""

from src.content import frontmatter
from src.generate.emitters import rules
from tests.conftest import doc


def test_kiro_inclusion_mapping():
    assert frontmatter.parse(rules._kiro(doc(alwaysApply=True)))[0]["inclusion"] == "always"
    assert frontmatter.parse(rules._kiro(doc()))[0]["inclusion"] == "manual"


def test_plain_formats_carry_no_frontmatter(src):
    out = rules.emit(src)
    for path in (".qoder/rules/lazy.md", ".clinerules/lazy.md", ".roo/rules/lazy.md"):
        assert frontmatter.parse(out[path])[0] == {}


def test_every_plain_target_is_generated(src):
    out = rules.emit(src)
    assert ".kiro/steering/lazy.md" in out
    assert ".qoder/rules/lazy.md" in out
    assert ".clinerules/lazy.md" in out
    assert ".roo/rules/lazy.md" in out
