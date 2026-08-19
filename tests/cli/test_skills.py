"""Tests for `lazy skills`."""

from src.cli import app
from tests.cli.conftest import runner


def test_lists_authored_skills(repo):
    result = runner.invoke(app, ["skills", "--root", str(repo)])
    assert result.exit_code == 0
    assert "lazy-review" in result.stdout
