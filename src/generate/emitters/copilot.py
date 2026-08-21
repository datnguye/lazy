"""Render sources into an installable GitHub Copilot plugin."""

import json

from src.content import frontmatter
from src.content.sources import Doc, Sources
from src.generate.emitters import hooks

BANNER = "<!-- Generated from src/ by src/build.py. Do not edit. -->"

# Copilot's own plugin tree, kept apart from Claude's so neither manifest has
# to satisfy both CLIs' source resolution.
PLUGIN_ROOT = "plugins-copilot"

# `copilot plugin marketplace add` reads a manifest only from the repo root --
# it has no subdirectory syntax -- so the marketplace lives there. Copilot
# searches .plugin/ before .claude-plugin/, which leaves Claude's untouched.
MANIFEST_DIR = ".plugin"

# Copilot's sessionStart reads a JSON object from stdout and injects its
# additionalContext, one level shallower than the shape Claude's events take.
HOOK_EVENT = "sessionStart"


def _plugin_json(src: Sources) -> str:
    """Render the plugin manifest Copilot reads from .plugin/."""
    p = src.plugin
    manifest = {
        "name": p["name"],
        "version": p["version"],
        "description": p["description"],
        "author": p["author"],
        "homepage": p["homepage"],
        "repository": p["repository"],
        "license": p["license"],
        "keywords": p["keywords"],
    }
    return json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"


def _marketplace_json(src: Sources) -> str:
    """Render the root marketplace manifest.

    Copilot resolves each entry's source against the marketplace root, which is
    the repository root here; no pluginRoot is declared.
    """
    p = src.plugin
    manifest = {
        "name": "datnguye",
        "owner": p["author"],
        "description": p["description"],
        "version": p["version"],
        "plugins": [
            {
                "name": p["name"],
                "source": f"./{PLUGIN_ROOT}/{p['name']}",
                "description": p["description"],
                "version": p["version"],
                "author": p["author"],
                "homepage": p["homepage"],
                "repository": p["repository"],
                "license": p["license"],
                "keywords": p["keywords"],
            }
        ],
    }
    return json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"


def _skill(doc: Doc) -> str:
    """Render a plugin skill, keeping to the Agent Skills spec fields."""
    meta = {"name": doc.slug, "description": doc.description}
    tools = doc.tools()
    if tools:
        meta["allowed-tools"] = tools
    if doc.meta.get("license"):
        meta["license"] = doc.meta["license"]
    return frontmatter.render(meta, f"{BANNER}\n\n{doc.body}")


def _hooks_json(name: str) -> str:
    """Wire sessionStart to the shared activation script."""
    script = f'"${{PLUGIN_ROOT}}/hooks/{name}.py"'
    config = {
        "version": 1,
        "hooks": {
            HOOK_EVENT: [
                {
                    "type": "command",
                    "bash": hooks.command(script, HOOK_EVENT),
                    "timeoutSec": 5,
                }
            ]
        },
    }
    return json.dumps(config, indent=2) + "\n"


def emit(src: Sources) -> dict[str, str]:
    """Return the installable plugin tree.

    Copilot reaches this plugin only through `copilot plugin install`, so no
    repo-level instruction files are rendered: nobody clones this repository to
    pick up the rules.
    """
    name = src.plugin["name"]
    root = f"{PLUGIN_ROOT}/{name}"
    out = {
        f"{MANIFEST_DIR}/marketplace.json": _marketplace_json(src),
        f"{root}/{MANIFEST_DIR}/plugin.json": _plugin_json(src),
        f"{root}/README.md": f"{BANNER}\n\n# {name}\n\n{src.plugin['description']}\n",
    }
    for doc in src.skills:
        out[f"{root}/skills/{doc.slug}/SKILL.md"] = _skill(doc)
        for extra in doc.extras:
            out[f"{root}/skills/{doc.slug}/{extra.name}"] = extra.read_text(encoding="utf-8")

    core = next((d for d in src.skills if d.slug == name), None)
    if core is not None:
        out[f"{root}/hooks/{name}.py"] = hooks.SCRIPT.format(
            banner=hooks.BANNER, instructions=hooks.literal(core.body)
        )
        out[f"{root}/hooks/hooks.json"] = _hooks_json(name)
    return out
