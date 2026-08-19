"""Rules every emitter must satisfy, whatever format it targets."""

import pytest

from src.content import frontmatter
from src.generate.emitters import ALL as EMITTERS


@pytest.mark.parametrize("emitter", EMITTERS)
def test_every_emitter_produces_parseable_markdown(emitter, src):
    for path, text in emitter.emit(src).items():
        assert text.endswith("\n"), path
        if path.endswith((".md", ".mdc")):
            frontmatter.parse(text)


@pytest.mark.parametrize("emitter", EMITTERS)
def test_generated_files_carry_a_do_not_edit_banner(emitter, src):
    for path, text in emitter.emit(src).items():
        if path.endswith((".md", ".mdc")):
            assert "Do not edit" in text, path
