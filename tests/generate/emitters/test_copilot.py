"""Tests for the GitHub Copilot emitter."""

import json
import subprocess
import sys

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


def test_repo_wide_file_has_no_frontmatter(src):
    """Copilot reads .github/copilot-instructions.md raw; frontmatter would leak into it."""
    meta, _ = frontmatter.parse(copilot.emit(src)[".github/copilot-instructions.md"])
    assert meta == {}


def test_emits_the_paths_copilot_looks_in(src):
    out = copilot.emit(src)
    assert ".github/copilot-instructions.md" in out
    scoped = [p for p in out if p.startswith(".github/instructions/")]
    assert scoped
    for path in scoped:
        assert path.endswith(".instructions.md"), path
    for path in out:
        assert path.startswith((".github/", f"{copilot.PLUGIN_ROOT}/")), path


def test_every_instruction_declares_apply_to(src):
    for path, text in copilot.emit(src).items():
        if path.startswith(".github/instructions/"):
            assert frontmatter.parse(text)[0]["applyTo"], path


def test_plugin_tree_is_separate_from_the_claude_one(src):
    out = copilot.emit(src)
    root = f"{copilot.PLUGIN_ROOT}/lazy"
    assert f"{root}/{copilot.MANIFEST_DIR}/plugin.json" in out
    assert not any(p.startswith("plugins/") for p in out)


def test_marketplace_source_is_relative_to_the_marketplace_root(src):
    """Copilot resolves source against the marketplace dir, not the repo root."""
    raw = copilot.emit(src)[f"{copilot.PLUGIN_ROOT}/{copilot.MANIFEST_DIR}/marketplace.json"]
    assert json.loads(raw)["plugins"][0]["source"] == "./lazy"


def test_marketplace_declares_no_plugin_root(src):
    raw = copilot.emit(src)[f"{copilot.PLUGIN_ROOT}/{copilot.MANIFEST_DIR}/marketplace.json"]
    assert "pluginRoot" not in raw


def test_every_skill_reaches_the_plugin_tree(src):
    out = copilot.emit(src)
    for skill in src.skills:
        assert f"{copilot.PLUGIN_ROOT}/lazy/skills/{skill.slug}/SKILL.md" in out


def test_plugin_skill_carries_optional_license():
    assert frontmatter.parse(copilot._skill(doc(license="MIT")))[0]["license"] == "MIT"


def test_plugin_skill_omits_absent_optional_fields():
    meta, _ = frontmatter.parse(copilot._skill(doc()))
    assert "allowed-tools" not in meta
    assert "license" not in meta


def test_plugin_skill_joins_declared_tools():
    meta, _ = frontmatter.parse(copilot._skill(doc(**{"allowed-tools": ["Read", "Bash"]})))
    assert meta["allowed-tools"] == "Read, Bash"


def test_skill_extras_travel_with_the_skill(src, tmp_path):
    extra = tmp_path / "helper.py"
    extra.write_text("x = 1\n")
    src.skills[0].extras = [extra]
    out = copilot.emit(src)
    slug = src.skills[0].slug
    assert out[f"{copilot.PLUGIN_ROOT}/lazy/skills/{slug}/helper.py"] == "x = 1\n"


def test_plugin_ships_a_session_start_hook(src):
    config = json.loads(copilot.emit(src)[f"{copilot.PLUGIN_ROOT}/lazy/hooks/hooks.json"])
    assert config["version"] == 1
    assert copilot.HOOK_EVENT in config["hooks"]


def test_hook_runs_the_generated_script(src):
    config = json.loads(copilot.emit(src)[f"{copilot.PLUGIN_ROOT}/lazy/hooks/hooks.json"])
    hook = config["hooks"][copilot.HOOK_EVENT][0]
    assert hook["type"] == "command"
    assert "${PLUGIN_ROOT}/hooks/lazy.py" in hook["bash"]
    assert copilot.HOOK_EVENT in hook["bash"]


def test_hook_injects_additional_context_at_the_top_level(src, tmp_path):
    """Copilot reads additionalContext one level shallower than Claude does."""
    script = tmp_path / "lazy.py"
    script.write_text(copilot.emit(src)[f"{copilot.PLUGIN_ROOT}/lazy/hooks/lazy.py"])
    out = subprocess.run(
        [sys.executable, str(script), copilot.HOOK_EVENT],
        capture_output=True,
        text=True,
        check=True,
    )
    assert list(json.loads(out.stdout)) == ["additionalContext"]


def test_a_plugin_without_the_core_skill_ships_no_hook(src):
    src.plugin["name"] = "absent"
    assert not any(p.endswith("hooks.json") for p in copilot.emit(src))
