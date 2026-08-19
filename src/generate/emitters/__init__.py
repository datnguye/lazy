"""Every output format, one module each.

An emitter is any module here exposing `emit(sources) -> {path: contents}`.
Adding a format means adding a module and listing it in ALL; nothing else in
the build has to know about it.
"""

from src.generate.emitters import (
    agents,
    claude,
    copilot,
    cursor,
    hooks,
    rules,
    windsurf,
)

ALL = (claude, agents, cursor, windsurf, copilot, rules, hooks)
