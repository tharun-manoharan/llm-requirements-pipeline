"""Naive pipeline: keyword-based segmentation (stage 2) and detection (stage 3).

Used as the no-LLM baseline and as a fallback when the LLM is unavailable.
"""

import re

REQUIREMENT_KEYWORDS = [
    "should", "shall", "must", "need", "require",
    "able to", "allow", "enable", "support",
    "send", "notify", "display", "store", "log",
    "encrypt", "authenticate", "validate",
    "performance", "secure", "available", "reliable",
    "scalable", "maintain", "response time",
]

NON_FUNCTIONAL_KEYWORDS = [
    "performance", "secure", "security", "available", "availability",
    "reliable", "reliability", "scalable", "scalability",
    "maintain", "maintainability", "response time", "latency",
    "uptime", "throughput", "encrypt", "backup", "audit",
    "comply", "compliance", "accessible", "accessibility",
]

_EXCLUSION_PATTERNS = [
    re.compile(
        r"^\s*(ok|okay|yes|no|got it|sure|thanks|thank you|agreed|right)\s*[.!?]?\s*$",
        re.IGNORECASE,
    ),
]

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def segment_turns(turns: list[dict]) -> list[dict]:
    """Augment each turn with an 'is_candidate' boolean.

    A turn is a candidate if it is NOT a bare filler phrase AND contains
    at least one requirement keyword.
    """
    result = []
    for turn in turns:
        text_lower = turn["text"].lower()
        excluded = any(pat.match(turn["text"]) for pat in _EXCLUSION_PATTERNS)
        if excluded:
            is_candidate = False
        else:
            is_candidate = any(kw in text_lower for kw in REQUIREMENT_KEYWORDS)
        result.append({**turn, "is_candidate": is_candidate})
    return result


def detect_candidates(segmented_turns: list[dict]) -> list[dict]:
    """Extract individual candidate requirement sentences from tagged turns.

    Filters to is_candidate==True turns, splits into sentences, discards
    questions, keeps sentences with requirement keywords, and classifies type.
    """
    candidates = []
    for turn in segmented_turns:
        if not turn.get("is_candidate"):
            continue
        for sentence in _SENTENCE_SPLIT.split(turn["text"]):
            sentence = sentence.strip()
            if not sentence or sentence.endswith("?"):
                continue
            lower = sentence.lower()
            if not any(kw in lower for kw in REQUIREMENT_KEYWORDS):
                continue
            req_type = "non-functional" if any(kw in lower for kw in NON_FUNCTIONAL_KEYWORDS) else "functional"
            candidates.append({
                "sentence": sentence,
                "source_turn": turn["turn_index"],
                "req_type": req_type,
            })
    return candidates
