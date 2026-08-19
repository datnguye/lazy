"""Load the authored content: skills, plugin.yaml, and the shared guidance."""

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from src.content import frontmatter

ROOT = Path(__file__).resolve().parent.parent.parent
SRC = ROOT / "src"

INCLUDE = re.compile(r"^(?P<indent>[-*]\s+)?\{\{\s*(?P<name>[\w-]+)\s*\}\}$", re.MULTILINE)


@dataclass
class Doc:
    """One authored markdown document plus its parsed frontmatter."""

    slug: str
    meta: dict
    body: str
    extras: list[Path] = field(default_factory=list)

    @property
    def description(self) -> str:
        return str(self.meta.get("description", "")).strip()

    def tools(self) -> str | None:
        """Return declared tools as a comma-separated string, if any."""
        raw = self.meta.get("allowed-tools") or self.meta.get("tools")
        if not raw:
            return None
        if isinstance(raw, str):
            return raw
        return ", ".join(raw)


@dataclass
class Sources:
    """Everything authored under src/."""

    plugin: dict
    skills: list[Doc]
    guidance: str


def expand(body: str, shared: dict[str, str]) -> str:
    """Replace every {{ name }} marker with the shared block it names.

    Formats like Cursor and Kiro flatten a skill to one standalone file, so a
    cross-file reference would dangle there. Authoring stays DRY by inlining
    the shared text at render time instead.
    """

    def replace(match: re.Match) -> str:
        name = match.group("name")
        if name not in shared:
            raise KeyError(f"unknown shared block: {name}")
        return (match.group("indent") or "") + shared[name]

    return INCLUDE.sub(replace, body)


def _load_doc(path: Path, slug: str, shared: dict[str, str] | None = None) -> Doc:
    meta, body = frontmatter.parse(path.read_text(encoding="utf-8"))
    body = expand(body, shared or {})
    extras = sorted(p for p in path.parent.rglob("*") if p.is_file() and p != path)
    return Doc(slug=slug, meta=meta, body=body, extras=extras)


def load(src: Path = SRC) -> Sources:
    """Read every source document from the src/ tree."""
    plugin = yaml.safe_load((src / "plugin.yaml").read_text(encoding="utf-8"))
    shared = {p.stem: p.read_text(encoding="utf-8").strip() for p in (src / "shared").glob("*.md")}
    skills = [
        _load_doc(d / "SKILL.md", d.name, shared)
        for d in sorted(p for p in (src / "skills").iterdir() if p.is_dir())
    ]
    guidance = expand((src / "AGENTS.md").read_text(encoding="utf-8"), shared)
    return Sources(plugin=plugin, skills=skills, guidance=guidance)
