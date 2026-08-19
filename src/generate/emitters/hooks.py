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

# SessionStart takes raw stdout; SubagentStart drops it unless wrapped in the
# hookSpecificOutput JSON form.
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
        json.dump(
            {{"hookSpecificOutput": {{"hookEventName": event, "additionalContext": body}}}},
            sys.stdout,
        )
    else:
        sys.stdout.write(body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def _literal(body: str) -> str:
    """Escape a skill body for embedding in a triple-quoted string literal."""
    return body.replace("\\", "\\\\").replace('"""', '\\"\\"\\"')


def _config(name: str) -> str:
    """Wire both start events to the generated script."""
    command = f'python3 "${{CLAUDE_PLUGIN_ROOT}}/hooks/{name}.py"'
    hooks = {
        event: [
            {
                "hooks": [
                    {
                        "type": "command",
                        "command": f"{command} {event}",
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
    script = SCRIPT.format(banner=BANNER, instructions=_literal(core.body))
    return {
        f"{root}/hooks/{name}.py": script,
        f"{root}/hooks/hooks.json": _config(name),
    }
