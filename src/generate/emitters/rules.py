"""Render sources into the plain-markdown rule formats.

Kiro, Qoder, Cline, and Zoo Code each read a directory of markdown rules. Only
Kiro takes frontmatter (`title` plus an `inclusion` mode); the rest read the
body alone, so the rule text has to stand on its own without it.

Zoo Code keeps the `.roo/` directory it inherited from the Roo Code fork, and
prefers `.roo/rules/` over the legacy single-file `.roorules`.
"""

from src.content import frontmatter
from src.content.sources import Doc, Sources

BANNER = "<!-- Generated from src/ by src/build.py. Do not edit. -->"


def _kiro(doc: Doc) -> str:
    """Kiro steering docs: `inclusion` is always, fileMatch, or manual."""
    meta = {
        "title": doc.slug,
        "inclusion": "always" if doc.meta.get("alwaysApply") else "manual",
    }
    return frontmatter.render(meta, f"{BANNER}\n\n{doc.body}")


def _plain(doc: Doc) -> str:
    """Qoder, Cline, and Zoo Code read the markdown body with no frontmatter."""
    return f"{BANNER}\n\n{doc.body}"


def emit(src: Sources) -> dict[str, str]:
    """Return Kiro, Qoder, Cline, and Zoo Code rule files."""
    out: dict[str, str] = {}
    for doc in src.skills:
        out[f".kiro/steering/{doc.slug}.md"] = _kiro(doc)
        out[f".qoder/rules/{doc.slug}.md"] = _plain(doc)
        out[f".clinerules/{doc.slug}.md"] = _plain(doc)
        out[f".roo/rules/{doc.slug}.md"] = _plain(doc)
    return out
