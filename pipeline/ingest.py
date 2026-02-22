"""Stage 1: Input Ingestion - parse raw conversation text into structured turns."""

import re

# Format A: "Stakeholder: ...", "Developer: ...", "Interviewer: ...", etc.
# Accepts any single word (or hyphenated word) as a role label.
SIMPLE_PATTERN = re.compile(r"^([A-Za-z][\w-]{0,30})\s*:\s*(.+)$", re.IGNORECASE)

# Format B: "[0:01:17] spk_1: ..." (timestamped transcript)
TIMESTAMPED_PATTERN = re.compile(
    r"^\[[\d:]+\]\s*(spk_\d+|[\w\s]+?)\s*:\s*(.+)$", re.IGNORECASE
)


def _detect_format(raw_text: str) -> str:
    """Detect transcript format by checking the first non-empty line."""
    for line in raw_text.splitlines():
        line = line.strip()
        if not line:
            continue
        if SIMPLE_PATTERN.match(line):
            return "simple"
        if TIMESTAMPED_PATTERN.match(line):
            return "timestamped"
    return "simple"


def parse_conversation(raw_text: str) -> list[dict]:
    """Parse raw conversation text into a list of turn dicts.

    Each turn dict has keys: turn_index (int), role (str), text (str).
    Supports two formats:
      - Simple:      "Stakeholder: some text"
      - Timestamped: "[0:01:17] spk_1: some text"
    Lines that don't match the active pattern are appended to the
    previous turn (handles multi-line utterances).
    """
    fmt = _detect_format(raw_text)
    pattern = TIMESTAMPED_PATTERN if fmt == "timestamped" else SIMPLE_PATTERN

    turns = []
    for line in raw_text.splitlines():
        line = line.strip()
        if not line:
            continue

        match = pattern.match(line)
        if match:
            turns.append({
                "turn_index": len(turns),
                "role": match.group(1).strip().lower(),
                "text": match.group(2).strip(),
            })
        elif turns:
            # Multi-line continuation: append to previous turn
            turns[-1]["text"] += " " + line

    return turns
