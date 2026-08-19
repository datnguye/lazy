"""Render sources into Devin Desktop (formerly Windsurf) rules and workflows."""

from src.content import frontmatter
from src.content.sources import Doc, Sources

BANNER = "<!-- Generated from src/ by src/build.py. Do not edit. -->"
PREFIX = ".windsurf/rules/"
CHAR_LIMIT = 6000


def _rule(doc: Doc) -> str:
    """Render a workspace rule.

    `trigger` selects activation: always_on, glob (with globs), model_decision
    (with description), or manual.
    """
    globs = doc.meta.get("globs")
    if doc.meta.get("alwaysApply"):
        meta: dict = {"trigger": "always_on"}
    elif globs:
        meta = {
            "trigger": "glob",
            "globs": ", ".join(globs) if isinstance(globs, list) else globs,
            "description": doc.description,
        }
    else:
        meta = {"trigger": "model_decision", "description": doc.description}
    return frontmatter.render(meta, f"{BANNER}\n\n{doc.body}")


def over_limit(rendered: dict[str, str]) -> list[str]:
    """Return rule paths that exceed the documented per-rule character budget."""
    return sorted(p for p, t in rendered.items() if p.startswith(PREFIX) and len(t) > CHAR_LIMIT)


def emit(src: Sources) -> dict[str, str]:
    """Emit to .windsurf/, which both Devin Desktop and Windsurf still read."""
    out: dict[str, str] = {}
    for doc in src.skills:
        out[f".windsurf/rules/{doc.slug}.md"] = _rule(doc)
    return out
