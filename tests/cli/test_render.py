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
