"""Render the portable formats: AGENTS.md and .agents/skills/."""

from src.content import frontmatter
from src.content.sources import Doc, Sources

BANNER = "<!-- Generated from src/ by src/build.py. Do not edit. -->"


def _skill(doc: Doc) -> str:
    """Render a skill using only the two fields every tool agrees on."""
    meta = {"name": doc.slug, "description": doc.description}
    return frontmatter.render(meta, f"{BANNER}\n\n{doc.body}")


def emit(src: Sources) -> dict[str, str]:
    """AGENTS.md is read by Codex, Cursor, Copilot and Devin alike.

    `.agents/skills/` is the emerging cross-tool skill convention: canonical
    for Codex, and read by Cursor too.
    """
    out = {"AGENTS.md": f"{BANNER}\n\n{src.guidance}"}
    for doc in src.skills:
        out[f".agents/skills/{doc.slug}/SKILL.md"] = _skill(doc)
        for extra in doc.extras:
            out[f".agents/skills/{doc.slug}/{extra.name}"] = extra.read_text(encoding="utf-8")
    return out
