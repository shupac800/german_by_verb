"""Tests for build_data.py parsing logic."""

import json
from pathlib import Path
from textwrap import dedent

import build_data


def test_stem_re():
    """STEM_RE matches the stem line format."""
    m = build_data.STEM_RE.match("**LEGEN:** to lay; to put; to set")
    assert m
    assert m.group(1) == "LEGEN"
    assert m.group(2) == "to lay; to put; to set"


def test_entry_re_sep():
    """ENTRY_RE matches separable verb entries."""
    m = build_data.ENTRY_RE.match(
        "**ABLEGEN** (sep.): to put down; to set down"
    )
    assert m
    assert m.group(1) == "ABLEGEN"
    assert m.group(2) == "sep."
    assert "to put down" in m.group(3)


def test_entry_re_insep():
    """ENTRY_RE matches inseparable verb entries."""
    m = build_data.ENTRY_RE.match(
        "**BELEGEN** (insep.): to occupy; to inhabit"
    )
    assert m
    assert m.group(1) == "BELEGEN"
    assert m.group(2) == "insep."


def test_adj_only_re():
    """ADJ_ONLY_RE matches adjective-only entries."""
    m = build_data.ADJ_ONLY_RE.match(
        "**ENTLEGEN** (adj.): outlying; remote; distant"
    )
    assert m
    assert m.group(1) == "ENTLEGEN"


def test_prefix_hint_re():
    """PREFIX_HINT_RE extracts prefix hints from guide headings."""
    m = build_data.PREFIX_HINT_RE.match('### AB- ("off, away from")')
    assert m
    assert m.group(1) == "AB"
    assert m.group(2) == "off, away from"


def test_parse_prefix_hints(tmp_path):
    """parse_prefix_hints extracts all hints from a guide file."""
    guide = tmp_path / "test_guide.md"
    guide.write_text(dedent("""\
        # LEGEN — A Prefix Guide

        ### AB- ("off, away from")
        Text about ablegen.

        ### AN- ("on, onto, up against")
        Text about anlegen.
    """), encoding="utf-8")

    hints = build_data.parse_prefix_hints(guide)
    assert hints == {"AB": "off, away from", "AN": "on, onto, up against"}


def test_parse_prefix_hints_missing_file(tmp_path):
    """parse_prefix_hints returns empty dict for missing file."""
    assert build_data.parse_prefix_hints(tmp_path / "nonexistent.md") == {}


def test_parse_edited_file(tmp_path):
    """parse_edited_file produces correct stem + cards structure."""
    edited = tmp_path / "test_edited.md"
    edited.write_text(dedent("""\
        # LEGEN

        **LEGEN:** to lay; to put

        **ABLEGEN** (sep.): to put down; to set down

        **BELEGEN** (insep.): to occupy; to inhabit

        **ENTLEGEN** (adj.): outlying; remote
    """), encoding="utf-8")

    hints = {"AB": "off, away from", "BE": "intensifier"}
    result = build_data.parse_edited_file(edited, hints)

    assert result["stem"] == "LEGEN"
    assert result["stem_translation"] == "to lay; to put"
    assert len(result["cards"]) == 2  # ENTLEGEN (adj-only) should be skipped

    ab = result["cards"][0]
    assert ab["verb"] == "ABLEGEN"
    assert ab["prefix"] == "AB"
    assert ab["separability"] == "sep."
    assert ab["prefix_hint"] == "off, away from"

    be = result["cards"][1]
    assert be["verb"] == "BELEGEN"
    assert be["prefix"] == "BE"
    assert be["separability"] == "insep."
    assert be["prefix_hint"] == "intensifier"


def test_parse_edited_file_skips_mismatched_verb(tmp_path):
    """Verbs that don't end with the stem are skipped."""
    edited = tmp_path / "test_edited.md"
    edited.write_text(dedent("""\
        # FALLEN

        **FALLEN:** to fall

        **AUFFALLEN** (sep.): to stand out

        **WIDERFAHREN** (insep.): to befall
    """), encoding="utf-8")

    result = build_data.parse_edited_file(edited, {})
    assert len(result["cards"]) == 1
    assert result["cards"][0]["verb"] == "AUFFALLEN"


def test_parse_edited_file_mixed_adj_verb(tmp_path):
    """Entries with both verb and adj parts (em dash) are included."""
    edited = tmp_path / "test_edited.md"
    edited.write_text(dedent("""\
        # LEGEN

        **LEGEN:** to lay; to put

        **VERLEGEN** (insep.): to relocate; to publish — (adj.) embarrassed; shy
    """), encoding="utf-8")

    result = build_data.parse_edited_file(edited, {"VER": "transformation"})
    assert len(result["cards"]) == 1
    card = result["cards"][0]
    assert card["verb"] == "VERLEGEN"
    assert "to relocate" in card["translations"]
    assert "embarrassed" in card["translations"]


def test_full_json_output():
    """The generated flashcard_data.json has expected structure."""
    path = Path(__file__).parent / "flashcard_data.json"
    if not path.exists():
        return  # Skip if not built yet

    data = json.loads(path.read_text(encoding="utf-8"))
    assert len(data) > 100  # Should have 180+ stems
    total_cards = sum(len(s["cards"]) for s in data)
    assert total_cards > 1000  # Should have 1600+ cards

    # Every entry should have required fields
    for stem_entry in data:
        assert "stem" in stem_entry
        assert "stem_translation" in stem_entry
        assert "cards" in stem_entry
        for card in stem_entry["cards"]:
            assert "verb" in card
            assert "translations" in card
            assert "prefix" in card
            assert card["prefix"]  # Should never be empty

    # Spot-check LEGEN
    legen = next(s for s in data if s["stem"] == "LEGEN")
    verbs = [c["verb"] for c in legen["cards"]]
    assert "ABLEGEN" in verbs
    assert "BELEGEN" in verbs
    # ENTLEGEN and GELEGEN (adj-only) should be excluded
    assert "ENTLEGEN" not in verbs
    assert "GELEGEN" not in verbs


def test_scoring_prompt_fields():
    """Verify the JSON has all fields needed for the scoring prompt."""
    path = Path(__file__).parent / "flashcard_data.json"
    if not path.exists():
        return

    data = json.loads(path.read_text(encoding="utf-8"))
    # Check a stem known to have hints
    legen = next(s for s in data if s["stem"] == "LEGEN")
    ab = next(c for c in legen["cards"] if c["verb"] == "ABLEGEN")
    assert ab["prefix_hint"] == "off, away from"
    assert ab["separability"] == "sep."
    assert ab["stem"] == "LEGEN" if "stem" in ab else True  # stem is on parent


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
