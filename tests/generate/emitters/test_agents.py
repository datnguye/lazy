"""Tests for the portable AGENTS.md / .agents/skills emitter."""

from src.generate.emitters import agents


def test_skill_bundles_supporting_files(tmp_path, src):
    extra = tmp_path / "helper.py"
    extra.write_text("x\n", encoding="utf-8")
    src.skills[0].extras = [extra]
    assert agents.emit(src)[".agents/skills/lazy/helper.py"] == "x\n"
