"""Tests for the pure render/write/stale logic."""

import shutil

import pytest

from src.content import sources
from src.content.sources import ROOT
from src.generate import build
from src.generate.emitters import agents


@pytest.fixture
def repo(tmp_path):
    """A throwaway copy of src/ so builds never touch the real tree."""
    shutil.copytree(ROOT / "src", tmp_path / "src")
    return tmp_path


def rendered(repo):
    """Render the throwaway repo's sources."""
    return build.render(sources.load(repo / "src"))


def test_write_emits_every_format(repo):
    build.write(rendered(repo), repo)
    for rel in (
        "plugins/lazy/.claude-plugin/plugin.json",
        "AGENTS.md",
        ".cursor/rules/lazy.mdc",
        ".windsurf/rules/lazy.md",
        ".github/copilot-instructions.md",
        ".kiro/steering/lazy.md",
        ".qoder/rules/lazy.md",
        ".clinerules/lazy.md",
        ".roo/rules/lazy.md",
    ):
        assert (repo / rel).exists(), rel


def test_nothing_is_stale_after_a_write(repo):
    out = rendered(repo)
    build.write(out, repo)
    assert build.stale(out, repo) == []


def test_stale_detects_modified_output(repo):
    out = rendered(repo)
    build.write(out, repo)
    (repo / ".cursor/rules/lazy.mdc").write_text("tampered\n", encoding="utf-8")
    assert ".cursor/rules/lazy.mdc" in build.stale(out, repo)


def test_stale_detects_missing_output(repo):
    out = rendered(repo)
    build.write(out, repo)
    (repo / "AGENTS.md").unlink()
    assert "AGENTS.md" in build.stale(out, repo)


def test_stale_detects_orphaned_output(repo):
    out = rendered(repo)
    build.write(out, repo)
    (repo / ".cursor/rules/orphan.mdc").write_text("orphan\n", encoding="utf-8")
    assert ".cursor/rules/orphan.mdc" in build.stale(out, repo)


def test_stale_ignores_absent_generated_dirs(repo):
    out = rendered(repo)
    build.write(out, repo)
    shutil.rmtree(repo / ".qoder/rules")
    assert all(p.startswith(".qoder/rules") for p in build.stale(out, repo))


def test_write_removes_renamed_sources(repo):
    build.write(rendered(repo), repo)
    (repo / "src/skills/lazy").rename(repo / "src/skills/renamed")
    build.write(rendered(repo), repo)
    assert not (repo / ".cursor/rules/lazy.mdc").exists()
    assert (repo / ".cursor/rules/renamed.mdc").exists()


def test_render_rejects_colliding_emitters(monkeypatch, src):
    monkeypatch.setattr(build, "EMITTERS", (agents, agents))
    with pytest.raises(ValueError, match="both claim"):
        build.render(src)


def test_write_keeps_the_directory_skeleton(repo):
    """Generated dirs keep a .gitkeep so the structure survives a clone."""
    build.write(rendered(repo), repo)
    for rel in build.GENERATED_DIRS:
        assert (repo / rel / build.KEEP).exists(), rel


def test_gitkeep_is_not_reported_as_an_orphan(repo):
    out = rendered(repo)
    build.write(out, repo)
    assert not any(p.endswith(build.KEEP) for p in build.stale(out, repo))


def test_write_recreates_the_skeleton_when_dirs_are_missing(repo):
    shutil.rmtree(repo / ".cursor", ignore_errors=True)
    build.write(rendered(repo), repo)
    assert (repo / ".cursor/rules" / build.KEEP).exists()
