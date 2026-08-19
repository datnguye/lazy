"""Tests for the Claude Code plugin emitter."""

import json

from src.content import frontmatter
from src.generate.emitters import claude
from tests.conftest import doc

# Fields the Agent Skills spec allows; anything else hard-errors on upload.
SPEC_FIELDS = {"name", "description", "allowed-tools", "license", "compatibility", "metadata"}


def test_manifest_matches_plugin_yaml(src):
    manifest = json.loads(claude.emit(src)["plugins/lazy/.claude-plugin/plugin.json"])
    assert manifest["name"] == src.plugin["name"]
    assert manifest["author"] == src.plugin["author"]


def test_components_sit_outside_the_manifest_dir(src):
    for path in claude.emit(src):
        assert "/.claude-plugin/" not in path or path.endswith("plugin.json")


def test_skill_frontmatter_stays_within_agent_skills_spec(src):
    meta, _ = frontmatter.parse(claude.emit(src)["plugins/lazy/skills/lazy/SKILL.md"])
    assert set(meta) <= SPEC_FIELDS


def test_skill_carries_optional_license():
    assert frontmatter.parse(claude._skill(doc(license="MIT")))[0]["license"] == "MIT"


def test_skill_omits_allowed_tools_when_none_declared():
    meta, _ = frontmatter.parse(claude._skill(doc()))
    assert "allowed-tools" not in meta
    assert "license" not in meta


def test_skill_keeps_declared_allowed_tools():
    meta, _ = frontmatter.parse(claude._skill(doc(**{"allowed-tools": ["Read", "Bash"]})))
    assert meta["allowed-tools"] == "Read, Bash"


def test_skill_with_tools_and_license():
    meta, _ = frontmatter.parse(claude._skill(doc(license="MIT", **{"allowed-tools": ["Read"]})))
    assert meta["allowed-tools"] == "Read"
    assert meta["license"] == "MIT"


def test_skill_bundles_supporting_files(tmp_path, src):
    extra = tmp_path / "helper.py"
    extra.write_text("print('hi')\n", encoding="utf-8")
    src.skills[0].extras = [extra]
    assert claude.emit(src)["plugins/lazy/skills/lazy/helper.py"] == "print('hi')\n"
