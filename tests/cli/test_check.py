"""Tests for `lazy check`."""

from src.cli import app
from tests.cli.conftest import runner


def test_passes_after_render(repo):
    runner.invoke(app, ["render", "--root", str(repo)])
    result = runner.invoke(app, ["check", "--root", str(repo)])
    assert result.exit_code == 0
    assert "up to date" in result.stdout


def test_fails_on_drift(repo):
    runner.invoke(app, ["render", "--root", str(repo)])
    (repo / ".cursor/rules/lazy.mdc").write_text("tampered\n", encoding="utf-8")
    result = runner.invoke(app, ["check", "--root", str(repo)])
    assert result.exit_code == 1
    assert "out of date" in result.output


def test_format_checks_only_that_format(repo):
    """A claude-only tree is up to date when only claude is checked."""
    runner.invoke(app, ["render", "--root", str(repo), "--format", "claude"])
    assert runner.invoke(app, ["check", "--root", str(repo), "--format", "claude"]).exit_code == 0
    assert runner.invoke(app, ["check", "--root", str(repo)]).exit_code == 1
