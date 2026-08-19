"""Fixtures for CLI command tests."""

import shutil

import pytest
from typer.testing import CliRunner

from src.content.sources import ROOT

runner = CliRunner()


@pytest.fixture
def repo(tmp_path):
    """A throwaway copy of src/ so CLI runs never touch the real tree."""
    shutil.copytree(ROOT / "src", tmp_path / "src")
    return tmp_path
