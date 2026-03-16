"""Parse _edited.md and _guide.md files into flashcard_data.json."""

import json
import re
from pathlib import Path

REPO = Path(__file__).parent

# Regex for edited file entries
# Matches: **VERB** (sep./insep.): translations
# Also matches adjective-only and mixed entries like:
# **VERB** (sep.): translations — (adj.) adjective translations
ENTRY_RE = re.compile(
    r"^\*\*([A-ZÄÖÜß]+)\*\*"          # verb name
    r"(?:\s*\((sep\.|insep\.)\))?"       # optional separability
    r"(?:\s*\(adj\.\))?"                 # optional adj-only marker
    r":\s*(.+)$"                         # translations
)

# Matches adj-only entries: **WORD** (adj.): ...
ADJ_ONLY_RE = re.compile(
    r"^\*\*([A-ZÄÖÜß]+)\*\*\s*\(adj\.\):\s*(.+)$"
)

# Guide prefix heading: ### PREFIX- ("hint text")
PREFIX_HINT_RE = re.compile(
    r'^###\s+([A-ZÄÖÜß]+)-\s*\("([^"]+)"\)')

# Stem line: **STEM:** translations
STEM_RE = re.compile(
    r"^\*\*([A-ZÄÖÜß]+):\*\*\s*(.+)$"
)


def parse_prefix_hints(guide_path: Path) -> dict[str, str]:
    """Extract prefix -> hint mapping from a guide file."""
    hints = {}
    if not guide_path.exists():
        return hints
    for line in guide_path.read_text(encoding="utf-8").splitlines():
        m = PREFIX_HINT_RE.match(line)
        if m:
            hints[m.group(1)] = m.group(2)
    return hints


def parse_edited_file(edited_path: Path, hints: dict[str, str]) -> dict | None:
    """Parse an _edited.md file into a stem entry with cards."""
    text = edited_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    stem = None
    stem_translation = None
    cards = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check for stem line (first bold entry with colon inside)
        sm = STEM_RE.match(line)
        if sm and stem is None:
            stem = sm.group(1)
            stem_translation = sm.group(2)
            continue

        # Check for adj-only entry (no verb component) — skip these
        am = ADJ_ONLY_RE.match(line)
        if am and not re.search(r"\(sep\.\)|\(insep\.\)", line):
            # Pure adjective entry, but check if it also has verb translations
            # Lines like **UNTERLEGEN** (sep.): ... — (adj.) ... have sep/insep
            # and are caught by ENTRY_RE, not here
            continue

        # Check for verb entry
        em = ENTRY_RE.match(line)
        if em and stem:
            verb = em.group(1)
            separability = em.group(2) or ""
            translations = em.group(3)

            # Skip if this is just the stem repeated
            if verb == stem:
                continue

            # Derive prefix by stripping stem from verb
            stem_upper = stem.upper()
            verb_upper = verb.upper()
            if verb_upper.endswith(stem_upper):
                prefix = verb_upper[: len(verb_upper) - len(stem_upper)]
            else:
                # Verb doesn't match this stem — likely a misplaced entry
                continue

            prefix_hint = hints.get(prefix, "")

            cards.append(
                {
                    "verb": verb,
                    "separability": separability,
                    "translations": translations,
                    "prefix": prefix,
                    "prefix_hint": prefix_hint,
                }
            )

    if stem is None:
        return None

    return {
        "stem": stem,
        "stem_translation": stem_translation,
        "cards": cards,
    }


def build_data():
    edited_files = sorted(REPO.glob("*_edited.md"))
    data = []

    for edited_path in edited_files:
        stem_name = edited_path.name.replace("_edited.md", "")
        guide_path = REPO / f"{stem_name}_guide.md"

        hints = parse_prefix_hints(guide_path)
        entry = parse_edited_file(edited_path, hints)

        if entry and entry["cards"]:
            data.append(entry)

    out_path = REPO / "flashcard_data.json"
    out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    total_cards = sum(len(s["cards"]) for s in data)
    print(f"Written {out_path.name}: {len(data)} stems, {total_cards} cards")


if __name__ == "__main__":
    build_data()
