"""Render sources into Cursor's .cursor/ layout."""

from src.content import frontmatter
from src.content.sources import Doc, Sources

BANNER = "<!-- Generated from src/ by src/build.py. Do not edit. -->"


def _rule(doc: Doc) -> str:
    """Render a project rule.

    Cursor picks the rule type from the frontmatter combination: alwaysApply
    true is Always; a description alone is Agent Requested; globs alone is Auto
    Attached. Rules must use the .mdc extension — plain .md is ignored.
    """
    always = bool(doc.meta.get("alwaysApply", False))
    meta: dict = {"description": doc.description}
    globs = doc.meta.get("globs")
    if globs and not always:
        meta["globs"] = ", ".join(globs) if isinstance(globs, list) else globs
    meta["alwaysApply"] = always
    return frontmatter.render(meta, f"{BANNER}\n\n{doc.body}")


def emit(src: Sources) -> dict[str, str]:
    """Return Cursor rule and skill files."""
    out: dict[str, str] = {}
    for doc in src.skills:
        out[f".cursor/rules/{doc.slug}.mdc"] = _rule(doc)
    return out
