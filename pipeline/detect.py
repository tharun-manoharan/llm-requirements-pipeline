"""Stage 3: Candidate Requirement Detection — extract and classify requirement sentences."""

import re

from pipeline.segment import REQUIREMENT_KEYWORDS

NON_FUNCTIONAL_KEYWORDS = [
    "performance", "secure", "security", "available", "availability",
    "reliable", "reliability", "scalable", "scalability",
    "maintain", "maintainability", "response time", "latency",
    "uptime", "throughput", "encrypt", "backup", "audit",
    "comply", "compliance", "accessible", "accessibility",
]

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def _classify(sentence: str) -> str:
    """Return 'non-functional' if sentence contains an NF keyword, else 'functional'."""
    lower = sentence.lower()
    for kw in NON_FUNCTIONAL_KEYWORDS:
        if kw in lower:
            return "non-functional"
    return "functional"


def detect_candidates(segmented_turns: list[dict]) -> list[dict]:
    """Extract individual candidate requirement sentences from tagged turns.

    Filters to is_candidate==True turns, splits into sentences, discards
    questions, keeps sentences with requirement keywords, and classifies type.
    """
    candidates = []
    for turn in segmented_turns:
        if not turn.get("is_candidate"):
            continue

        sentences = SENTENCE_SPLIT.split(turn["text"])

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            # Discard questions
            if sentence.endswith("?"):
                continue
            # Keep only sentences with a requirement keyword
            lower = sentence.lower()
            if not any(kw in lower for kw in REQUIREMENT_KEYWORDS):
                continue

            candidates.append({
                "sentence": sentence,
                "source_turn": turn["turn_index"],
                "req_type": _classify(sentence),
            })

    return candidates
