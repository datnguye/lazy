"""Render sources into a Claude Code plugin."""

import json

from src.content import frontmatter
from src.content.sources import Doc, Sources

BANNER = "<!-- Generated from src/ by src/build.py. Do not edit. -->"


def _plugin_json(src: Sources) -> str:
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


def _skill(doc: Doc) -> str:
    """Render a plugin skill.

    Kept to the six fields of the Agent Skills spec (name, description,
    allowed-tools, license, compatibility, metadata) so the same file also
    survives a claude.ai upload or the Skills API, both of which hard-error on
    any other key.
    """
    meta = {"name": doc.slug, "description": doc.description}
    tools = doc.tools()
    if tools:
        meta["allowed-tools"] = tools
    if doc.meta.get("license"):
        meta["license"] = doc.meta["license"]
    return frontmatter.render(meta, f"{BANNER}\n\n{doc.body}")


def emit(src: Sources) -> dict[str, str]:
    """Return a mapping of repo-relative path -> file contents."""
    root = f"plugins/{src.plugin['name']}"
    out = {f"{root}/.claude-plugin/plugin.json": _plugin_json(src)}
    for doc in src.skills:
        out[f"{root}/skills/{doc.slug}/SKILL.md"] = _skill(doc)
        for extra in doc.extras:
            out[f"{root}/skills/{doc.slug}/{extra.name}"] = extra.read_text(encoding="utf-8")
    out[f"{root}/README.md"] = (
        f"{BANNER}\n\n# {src.plugin['name']}\n\n{src.plugin['description']}\n"
    )
    return out
