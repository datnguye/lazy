"""Tests for `lazy render`."""

from src.cli import app
from tests.cli.conftest import runner


def test_writes_every_format(repo):
    result = runner.invoke(app, ["render", "--root", str(repo)])
    assert result.exit_code == 0
    assert "Wrote" in result.stdout
    assert (repo / "plugins/lazy/.claude-plugin/plugin.json").exists()


def test_warns_on_oversized_rule(repo):
    skill = repo / "src/skills/lazy/SKILL.md"
    skill.write_text(skill.read_text(encoding="utf-8") + "x" * 7000, encoding="utf-8")
    result = runner.invoke(app, ["render", "--root", str(repo)])
    assert result.exit_code == 0
    assert "exceeds" in result.output


def test_format_writes_only_that_format(repo):
    result = runner.invoke(app, ["render", "--root", str(repo), "--format", "claude"])
    assert result.exit_code == 0
    assert (repo / "plugins/lazy/.claude-plugin/plugin.json").exists()
    assert not (repo / ".cursor/rules/lazy.mdc").exists()


def test_format_claude_brings_its_hooks(repo):
    """plugin.json points at hooks/hooks.json, so the pair must render together."""
    runner.invoke(app, ["render", "--root", str(repo), "--format", "claude"])
    assert (repo / "plugins/lazy/hooks/hooks.json").exists()
    assert (repo / "plugins/lazy/hooks/lazy.py").exists()


def test_format_leaves_other_formats_alone(repo):
    runner.invoke(app, ["render", "--root", str(repo)])
    runner.invoke(app, ["render", "--root", str(repo), "--format", "claude"])
    assert (repo / ".cursor/rules/lazy.mdc").exists()
    assert (repo / "AGENTS.md").exists()


def test_format_is_repeatable(repo):
    result = runner.invoke(app, ["render", "--root", str(repo), "-f", "cursor", "-f", "windsurf"])
    assert result.exit_code == 0
    assert (repo / ".cursor/rules/lazy.mdc").exists()
    assert (repo / ".windsurf/rules/lazy.md").exists()
    assert not (repo / "plugins/lazy/.claude-plugin/plugin.json").exists()


def test_unknown_format_is_rejected(repo):
    result = runner.invoke(app, ["render", "--root", str(repo), "--format", "nope"])
    assert result.exit_code == 2
    assert "Unknown format" in result.output
