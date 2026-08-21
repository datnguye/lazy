"""Render the Claude Code activation hook.

Skills load when invoked or when Claude judges the description relevant. A
SessionStart hook makes lazy mode persistent instead: it prints the skill body
so every session starts with the ladder already in context, matching the
`alwaysApply` / `always_on` behaviour the rule-based formats get for free.

The hook script is generated from the same SKILL.md as everything else, so the
instructions it injects can never drift from the skill itself.
"""

import json

from src.content.sources import Sources

BANNER = "# Generated from src/ by `lazy render`. Do not edit."

# Windows lacks `python3`; try the usual names in order.
INTERPRETERS = ("python3", "python", "py")
MISSING = "lazy: no Python interpreter found on PATH (tried python3, python, py)"

# SessionStart takes raw stdout; SubagentStart drops it unless wrapped in the
# hookSpecificOutput JSON form. Both write encoded bytes: the instructions are
# UTF-8, and a Windows console defaults sys.stdout to cp1252, which raises
# UnicodeEncodeError on any character outside it.
SCRIPT = '''#!/usr/bin/env python3
{banner}
"""Inject lazy mode at the start of every Claude Code session."""

import json
import os
import sys

MODE = os.environ.get("LAZY_DEFAULT_MODE", "full").strip().lower()
INSTRUCTIONS = """\
{instructions}"""


def main() -> int:
    """Print the ruleset in the shape the firing event expects."""
    if MODE == "off":
        return 0
    event = sys.argv[1] if len(sys.argv) > 1 else "SessionStart"
    body = INSTRUCTIONS + "\\n\\nActive intensity: " + MODE + "."
    if event == "SubagentStart":
        body = json.dumps(
            {{"hookSpecificOutput": {{"hookEventName": event, "additionalContext": body}}}}
        )
    elif event == "sessionStart":
        body = json.dumps({{"additionalContext": body}})
    sys.stdout.buffer.write(body.encode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def literal(body: str) -> str:
    """Escape a skill body for embedding in a triple-quoted string literal."""
    return body.replace("\\", "\\\\").replace('"""', '\\"\\"\\"')


def command(script: str, event: str) -> str:
    """Run the script under the first Python interpreter that exists."""
    candidates = " ".join(INTERPRETERS)
    return (
        f"for py in {candidates}; do "
        f'command -v "$py" >/dev/null 2>&1 && exec "$py" {script} {event}; '
        f'done; echo "{MISSING}" >&2; exit 1'
    )


def _config(name: str) -> str:
    """Wire both start events to the generated script.

    Windows has no `python3` on PATH: python.org ships `python` plus the `py`
    launcher, and the Microsoft Store stub named `python3` opens the Store
    instead of running anything. Hook commands go through a shell, so the
    interpreter is resolved at run time and the first one that exists wins.
    """
    script = f'"${{CLAUDE_PLUGIN_ROOT}}/hooks/{name}.py"'
    hooks = {
        event: [
            {
                "hooks": [
                    {
                        "type": "command",
                        "command": command(script, event),
                        "timeout": 5,
                        "statusMessage": "Loading lazy mode...",
                    }
                ]
            }
        ]
        for event in ("SessionStart", "SubagentStart")
    }
    return json.dumps({"hooks": hooks}, indent=2) + "\n"


def emit(src: Sources) -> dict[str, str]:
    """Return the hook script and its configuration."""
    name = src.plugin["name"]
    core = next((d for d in src.skills if d.slug == name), None)
    if core is None:
        return {}
    root = f"plugins/{name}"
    script = SCRIPT.format(banner=BANNER, instructions=literal(core.body))
    return {
        f"{root}/hooks/{name}.py": script,
        f"{root}/hooks/hooks.json": _config(name),
    }
