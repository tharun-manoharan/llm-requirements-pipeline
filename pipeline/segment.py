"""Stage 2: Conversation Segmentation - tag turns as requirement-bearing or not."""

import re

REQUIREMENT_KEYWORDS = [
    "should", "shall", "must", "need", "require",
    "able to", "allow", "enable", "support",
    "send", "notify", "display", "store", "log",
    "encrypt", "authenticate", "validate",
    "performance", "secure", "available", "reliable",
    "scalable", "maintain", "response time",
]

EXCLUSION_PATTERNS = [
    re.compile(
        r"^\s*(ok|okay|yes|no|got it|sure|thanks|thank you|agreed|right)\s*[.!?]?\s*$",
        re.IGNORECASE,
    ),
]


def segment_turns(turns: list[dict]) -> list[dict]:
    """Augment each turn with an 'is_candidate' boolean.

    A turn is a candidate if it is NOT a bare filler phrase AND contains
    at least one requirement keyword.
    """
    result = []
    for turn in turns:
        text_lower = turn["text"].lower()

        # Check exclusion patterns first
        excluded = any(pat.match(turn["text"]) for pat in EXCLUSION_PATTERNS)

        if excluded:
            is_candidate = False
        else:
            is_candidate = any(kw in text_lower for kw in REQUIREMENT_KEYWORDS)

        result.append({**turn, "is_candidate": is_candidate})

    return result
