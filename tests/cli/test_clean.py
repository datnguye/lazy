"""Tests for `lazy clean`."""

from src.cli import app
from src.generate import build
from tests.cli.conftest import runner


def test_removes_generated_files_but_keeps_the_skeleton(repo):
    runner.invoke(app, ["render", "--root", str(repo)])
    result = runner.invoke(app, ["clean", "--root", str(repo)])
    assert result.exit_code == 0
    assert "Removed" in result.stdout
    assert "Removed 0 " not in result.stdout
    for rel in build.GENERATED_DIRS:
        assert (repo / rel / build.KEEP).exists(), rel
        assert list((repo / rel).rglob("*")) == [repo / rel / build.KEEP], rel
    for rel in build.LOOSE_FILES:
        assert not (repo / rel).exists(), rel


def test_is_safe_to_run_twice(repo):
    runner.invoke(app, ["render", "--root", str(repo)])
    runner.invoke(app, ["clean", "--root", str(repo)])
    result = runner.invoke(app, ["clean", "--root", str(repo)])
    assert result.exit_code == 0
    assert "Removed 0" in result.stdout


def test_render_restores_what_clean_removed(repo):
    runner.invoke(app, ["render", "--root", str(repo)])
    runner.invoke(app, ["clean", "--root", str(repo)])
    runner.invoke(app, ["render", "--root", str(repo)])
    assert runner.invoke(app, ["check", "--root", str(repo)]).exit_code == 0


def test_format_cleans_only_that_format(repo):
    runner.invoke(app, ["render", "--root", str(repo)])
    result = runner.invoke(app, ["clean", "--root", str(repo), "--format", "claude"])
    assert result.exit_code == 0
    assert not (repo / "plugins/lazy").exists()
    assert (repo / "plugins" / build.KEEP).exists()
    assert (repo / ".cursor/rules/lazy.mdc").exists()
    assert (repo / "AGENTS.md").exists()


def test_format_cleans_the_loose_file_it_owns(repo):
    """AGENTS.md belongs to the agents format; Copilot's repo-wide file does not."""
    runner.invoke(app, ["render", "--root", str(repo)])
    runner.invoke(app, ["clean", "--root", str(repo), "--format", "agents"])
    assert not (repo / "AGENTS.md").exists()
    assert (repo / ".github/copilot-instructions.md").exists()


def test_format_clean_then_render_restores_it(repo):
    runner.invoke(app, ["render", "--root", str(repo)])
    runner.invoke(app, ["clean", "--root", str(repo), "--format", "claude"])
    runner.invoke(app, ["render", "--root", str(repo), "--format", "claude"])
    assert runner.invoke(app, ["check", "--root", str(repo)]).exit_code == 0


def test_unknown_format_is_rejected(repo):
    result = runner.invoke(app, ["clean", "--root", str(repo), "--format", "nope"])
    assert result.exit_code == 2
    assert "Unknown format" in result.output
