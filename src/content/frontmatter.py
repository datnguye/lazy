"""Minimal YAML frontmatter parsing and rendering."""

import yaml

DELIMITER = "---"


def parse(text: str) -> tuple[dict, str]:
    """Split a markdown document into its frontmatter mapping and body."""
    if not text.startswith(DELIMITER):
        return {}, text
    parts = text.split(f"\n{DELIMITER}", 1)
    if len(parts) != 2:
        return {}, text
    raw = parts[0][len(DELIMITER) :]
    body = parts[1].lstrip("\n")
    data = yaml.safe_load(raw) or {}
    if not isinstance(data, dict):
        raise ValueError("frontmatter must be a mapping")
    return data, body


def render(data: dict, body: str) -> str:
    """Recombine a frontmatter mapping and body into a markdown document."""
    if not data:
        return body if body.endswith("\n") else body + "\n"
    raw = yaml.safe_dump(data, sort_keys=False, allow_unicode=True, default_flow_style=False)
    body = body if body.endswith("\n") else body + "\n"
    return f"{DELIMITER}\n{raw}{DELIMITER}\n\n{body}"
