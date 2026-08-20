"""Tests for the Claude Code activation hook emitter."""

import json
import subprocess
import sys

import pytest

from src.generate.emitters import hooks


@pytest.fixture
def script(src, tmp_path):
    """The generated hook script, written where it can be executed."""
    path = tmp_path / "lazy.py"
    path.write_text(hooks.emit(src)["plugins/lazy/hooks/lazy.py"], encoding="utf-8")
    return path


def run(script, event, **env):
    """Execute the hook script for one event and capture stdout."""
    result = subprocess.run(
        [sys.executable, str(script), event],
        capture_output=True,
        text=True,
        check=True,
        env={"PATH": "/usr/bin:/bin", **env},
    )
    return result.stdout


@pytest.mark.parametrize("event", ("SessionStart", "SubagentStart"))
def test_writes_utf8_under_a_legacy_console_encoding(script, event):
    """A Windows console gives sys.stdout cp1252, which cannot encode the arrow."""
    result = subprocess.run(
        [sys.executable, str(script), event],
        capture_output=True,
        check=True,
        env={"PATH": "/usr/bin:/bin", "PYTHONIOENCODING": "cp1252"},
    )
    body = result.stdout.decode("utf-8")
    if event == "SubagentStart":
        body = json.loads(body)["hookSpecificOutput"]["additionalContext"]
    assert "\u2192" in body


def test_emits_script_and_config(src):
    out = hooks.emit(src)
    assert set(out) == {"plugins/lazy/hooks/lazy.py", "plugins/lazy/hooks/hooks.json"}


def test_config_wires_both_start_events(src):
    config = json.loads(hooks.emit(src)["plugins/lazy/hooks/hooks.json"])
    assert set(config["hooks"]) == {"SessionStart", "SubagentStart"}
    for event, entries in config["hooks"].items():
        command = entries[0]["hooks"][0]["command"]
        assert "${CLAUDE_PLUGIN_ROOT}" in command
        assert f'lazy.py" {event}' in command


def test_command_falls_back_past_a_missing_python3(src, tmp_path):
    """Windows has no `python3`; the command must find `python` or `py` instead."""
    out = hooks.emit(src)
    (tmp_path / "hooks").mkdir()
    (tmp_path / "hooks/lazy.py").write_text(out["plugins/lazy/hooks/lazy.py"], encoding="utf-8")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    only = bin_dir / "python"
    only.write_text(f'#!/bin/sh\nexec "{sys.executable}" "$@"\n', encoding="utf-8")
    only.chmod(0o755)

    command = json.loads(out["plugins/lazy/hooks/hooks.json"])["hooks"]["SessionStart"][0]["hooks"][
        0
    ]["command"]
    result = subprocess.run(
        ["bash", "-c", command],
        capture_output=True,
        text=True,
        check=True,
        env={"PATH": f"{bin_dir}:/usr/bin:/bin", "CLAUDE_PLUGIN_ROOT": str(tmp_path)},
    )
    assert "# Lazy" in result.stdout


def test_command_fails_loudly_without_any_interpreter(src, tmp_path):
    command = json.loads(hooks.emit(src)["plugins/lazy/hooks/hooks.json"])["hooks"]["SessionStart"][
        0
    ]["hooks"][0]["command"]
    empty = tmp_path / "bin"
    empty.mkdir()
    result = subprocess.run(
        ["bash", "-c", f"PATH={empty}; {command}"],
        capture_output=True,
        text=True,
        env={"PATH": "/usr/bin:/bin", "CLAUDE_PLUGIN_ROOT": str(tmp_path)},
    )
    assert result.returncode == 1
    assert "no Python interpreter found" in result.stderr


def test_emits_nothing_without_a_core_skill(src):
    src.skills = [d for d in src.skills if d.slug != "lazy"]
    assert hooks.emit(src) == {}


def test_session_start_prints_the_skill_body(script):
    out = run(script, "SessionStart")
    assert "lazy senior developer" in out
    assert out.rstrip().endswith("Active intensity: full.")


def test_subagent_start_wraps_context_in_json(script):
    payload = json.loads(run(script, "SubagentStart"))["hookSpecificOutput"]
    assert payload["hookEventName"] == "SubagentStart"
    assert "lazy senior developer" in payload["additionalContext"]


def test_off_mode_emits_nothing(script):
    assert run(script, "SessionStart", LAZY_DEFAULT_MODE="off") == ""


def test_mode_is_read_from_the_environment(script):
    assert "Active intensity: ultra." in run(script, "SessionStart", LAZY_DEFAULT_MODE="ultra")


def test_defaults_to_session_start_without_an_argument(script):
    result = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
        check=True,
        env={"PATH": "/usr/bin:/bin"},
    )
    assert "lazy senior developer" in result.stdout


@pytest.mark.parametrize(
    "body", ['has """ triple quotes', "ends with a backslash \\", 'both \\ and """']
)
def test_bodies_survive_embedding_in_the_script(body, src, tmp_path):
    """Prose that collides with Python string syntax must still round-trip."""
    src.skills = [d for d in src.skills if d.slug == "lazy"]
    src.skills[0].body = body
    path = tmp_path / "lazy.py"
    path.write_text(hooks.emit(src)["plugins/lazy/hooks/lazy.py"], encoding="utf-8")
    assert body in run(path, "SessionStart")
