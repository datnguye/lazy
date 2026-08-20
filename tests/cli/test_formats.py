"""Tests for `lazy formats`."""

from src.cli import app
from tests.cli.conftest import runner


def test_lists_each_emitter(repo):
    result = runner.invoke(app, ["formats", "--root", str(repo)])
    assert result.exit_code == 0
    assert "claude" in result.stdout
    assert "plugins/lazy/.claude-plugin/plugin.json" in result.stdout


def test_format_narrows_the_listing(repo):
    result = runner.invoke(app, ["formats", "--root", str(repo), "--format", "cursor"])
    assert result.exit_code == 0
    assert "cursor" in result.stdout
    assert "windsurf" not in result.stdout
