"""Render sources into GitHub Copilot's .github/ layout and its own plugin tree."""

import json

from src.content import frontmatter
from src.content.sources import Doc, Sources

BANNER = "<!-- Generated from src/ by src/build.py. Do not edit. -->"

# Copilot's own plugin root. It resolves a marketplace entry's source relative
# to pluginRoot, where Claude resolves it from the repo root, so the two cannot
# share one marketplace.json. A separate tree keeps both installable.
PLUGIN_ROOT = "plugins-copilot"

# Copilot searches .plugin/, ./, .github/plugin/, and .claude-plugin/ for both
# manifests. This tree is Copilot's alone, so it uses the vendor-neutral one.
MANIFEST_DIR = ".plugin"


def _instruction(doc: Doc) -> str:
    """Render a path-scoped instruction file; applyTo takes a glob string."""
    globs = doc.meta.get("globs") or "**"
    meta = {
        "name": doc.slug,
        "description": doc.description,
        "applyTo": ", ".join(globs) if isinstance(globs, list) else globs,
    }
    return frontmatter.render(meta, f"{BANNER}\n\n{doc.body}")


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
    """Render the marketplace manifest.

    Copilot resolves each entry's source against the marketplace root, so the
    plugin sits one level down as ./<name>; no pluginRoot is declared.
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
                "source": f"./{p['name']}",
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


def emit(src: Sources) -> dict[str, str]:
    """Return Copilot's instruction files plus its own installable plugin tree."""
    out = {".github/copilot-instructions.md": f"{BANNER}\n\n{src.guidance}"}
    for doc in src.skills:
        out[f".github/instructions/{doc.slug}.instructions.md"] = _instruction(doc)

    root = f"{PLUGIN_ROOT}/{src.plugin['name']}"
    out[f"{PLUGIN_ROOT}/{MANIFEST_DIR}/marketplace.json"] = _marketplace_json(src)
    out[f"{root}/{MANIFEST_DIR}/plugin.json"] = _plugin_json(src)
    for doc in src.skills:
        out[f"{root}/skills/{doc.slug}/SKILL.md"] = _skill(doc)
        for extra in doc.extras:
            out[f"{root}/skills/{doc.slug}/{extra.name}"] = extra.read_text(encoding="utf-8")
    out[f"{root}/README.md"] = (
        f"{BANNER}\n\n# {src.plugin['name']}\n\n{src.plugin['description']}\n"
    )
    return out
