"""Render sources into GitHub Copilot's .github/ layout."""

from src.content import frontmatter
from src.content.sources import Doc, Sources

BANNER = "<!-- Generated from src/ by src/build.py. Do not edit. -->"


def _instruction(doc: Doc) -> str:
    """Render a path-scoped instruction file; applyTo takes a glob string."""
    globs = doc.meta.get("globs") or "**"
    meta = {
        "name": doc.slug,
        "description": doc.description,
        "applyTo": ", ".join(globs) if isinstance(globs, list) else globs,
    }
    return frontmatter.render(meta, f"{BANNER}\n\n{doc.body}")


def emit(src: Sources) -> dict[str, str]:
    """Return Copilot repo-wide, path-scoped, and prompt files."""
    out = {".github/copilot-instructions.md": f"{BANNER}\n\n{src.guidance}"}
    for doc in src.skills:
        out[f".github/instructions/{doc.slug}.instructions.md"] = _instruction(doc)
    return out
