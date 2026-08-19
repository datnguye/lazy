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
