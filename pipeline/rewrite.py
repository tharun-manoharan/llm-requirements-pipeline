"""Stage 4: Requirement Rewriting / Normalisation - convert to 'The system shall …' form.

Supports two modes:
  - naive:  regex-based rewrite rules (no external dependencies)
  - llm:    uses Groq API with Llama 3.3 70B to rewrite via an LLM
"""

import re
import time

from pipeline.llm_client import get_llm_client, LLM_MODEL

# ---------------------------------------------------------------------------
# Naive (regex) rewriter - kept as fallback
# ---------------------------------------------------------------------------

REWRITE_RULES = [
    # Rule 1: "users should/shall/must be able to X"
    (
        re.compile(
            r"(?:users?|the user|they|stakeholders?)\s+(?:should|shall|must)\s+be\s+able\s+to\s+(.+)",
            re.IGNORECASE,
        ),
        "The system shall allow users to {0}",
    ),
    # Rule 2: "users/system/it should/shall/must X"
    (
        re.compile(
            r"(?:users?|the user|the system|it|they|we)\s+(?:should|shall|must)\s+(.+)",
            re.IGNORECASE,
        ),
        "The system shall {0}",
    ),
    # Rule 3: imperative verb with optional leading filler ("Yes, send them…")
    (
        re.compile(
            r"^(?:yes,?\s*|no,?\s*|ok,?\s*|sure,?\s*)?"
            r"(send|display|store|log|notify|validate|encrypt|authenticate|"
            r"generate|create|delete|update|allow|enable|support|provide)\s+(.+)",
            re.IGNORECASE,
        ),
        "The system shall {0} {1}",
    ),
]


def _ensure_period(s: str) -> str:
    """Ensure the string ends with exactly one period."""
    s = s.rstrip()
    s = s.rstrip(".")
    return s + "."


def _apply_rules(sentence: str) -> str:
    """Apply rewrite rules in order; first match wins."""
    for pattern, template in REWRITE_RULES:
        match = pattern.match(sentence)
        if match:
            groups = match.groups()
            result = template.format(*groups)
            return _ensure_period(result)

    # Fallback: prepend "The system shall" + lowered first char
    body = sentence[0].lower() + sentence[1:] if sentence else sentence
    return _ensure_period(f"The system shall {body}")


# ---------------------------------------------------------------------------
# LLM rewriter - Groq API (Llama 3.3 70B)
# ---------------------------------------------------------------------------

_LLM_MODEL = LLM_MODEL

_SYSTEM_PROMPT = """\
You are a requirements engineer. You will be given a sentence from a \
stakeholder conversation transcript, along with surrounding context. \
Your job is to rewrite the TARGET sentence as a single, clean software \
requirement in the form "The system shall ..." and assign a priority level.

Output format (exactly one line):
  PRIORITY | The system shall ...

Where PRIORITY is one of:
- essential - core functionality the stakeholder explicitly demands, repeats, \
or emphasises (strong language like "must", "need", "only X can", "critical")
- preferred - clearly desired but the system could work without it
- optional - briefly mentioned, uncertain ("maybe", "might", "could"), or \
agreed to without strong conviction

Use the surrounding context to judge priority - look for emphasis, repetition, \
and strength of language. Do NOT default to preferred; make a real judgement.

Rules:
- Output ONLY the priority and rewritten requirement in the format above.
- Remove all filler words (uh, um, okay, so, yeah, you know, like, etc.).
- Remove conversational artefacts and false starts.
- Keep the technical meaning intact - do not invent features not mentioned.
- Use clear, professional English.
- The requirement must start with "The system shall" and end with a period.
- If the sentence is NOT actually a system requirement, respond with exactly: NOT_A_REQUIREMENT

The following are NOT system requirements - respond NOT_A_REQUIREMENT for these:
- Greetings or introductions
- Questions from developers or stakeholders
- Conversational navigation ("let us move on to...", "we covered this...")
- Descriptions of current problems ("currently they need to...", "you need to look for it")
- Meta-conversation ("we understand the requirements", "let me find the exact wording")
- Vague statements with no specific system behaviour
- Project planning ("this should be first phase")
- Closing remarks or pleasantries\
"""

_VALID_PRIORITIES = {"essential", "preferred", "optional"}


def _rewrite_with_llm(sentence: str, context: str = "") -> tuple[str, str] | None:
    """Call the LLM to rewrite a sentence.

    Returns (priority, normalised_statement) or None if not a requirement.
    """
    client = get_llm_client()

    if context:
        user_msg = f"Context:\n{context}\n\nTARGET sentence:\n{sentence}"
    else:
        user_msg = sentence

    resp = client.chat.completions.create(
        model=_LLM_MODEL,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        max_tokens=200,
        temperature=0.1,
    )

    result = resp.choices[0].message.content.strip()

    if "NOT_A_REQUIREMENT" in result:
        return None

    # Parse "priority | The system shall ..." format
    if "|" in result:
        priority_str, statement = result.split("|", 1)
        priority = priority_str.strip().lower()
        statement = _ensure_period(statement.strip())
        if priority not in _VALID_PRIORITIES:
            priority = "preferred"  # safe default
    else:
        # LLM didn't follow format - treat whole response as statement
        statement = _ensure_period(result)
        priority = "preferred"

    return priority, statement


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def rewrite_requirements(candidates: list[dict], mode: str = "naive",
                         turns: list[dict] | None = None) -> list[dict]:
    """Augment each candidate with a 'normalised' statement and priority.

    Args:
        candidates: list of candidate dicts from the detect stage.
        mode: "naive" for regex rules, "llm" for HF LLM.
        turns: parsed conversation turns (used by LLM mode for context).
    """
    if mode == "llm":
        return _rewrite_llm_batch(candidates, turns or [])

    # Default: naive regex rewriter (always assigns "preferred" - no signal)
    result = []
    for candidate in candidates:
        normalised = _apply_rules(candidate["sentence"])
        result.append({**candidate, "normalised": normalised, "priority": "preferred"})
    return result


def _build_context(source_turn: int, turns: list[dict], window: int = 2) -> str:
    """Build a context snippet from surrounding turns."""
    if not turns:
        return ""
    turn_map = {t["turn_index"]: t for t in turns}
    indices = sorted(turn_map.keys())
    lines = []
    for idx in indices:
        if abs(idx - source_turn) <= window and idx != source_turn:
            t = turn_map[idx]
            snippet = t["text"][:150]
            lines.append(f"[{t['role']}]: {snippet}")
    return "\n".join(lines)


def _rewrite_llm_batch(candidates: list[dict], turns: list[dict]) -> list[dict]:
    """Rewrite all candidates using the LLM, filtering out non-requirements."""
    result = []
    total = len(candidates)

    for i, candidate in enumerate(candidates):
        print(f"    LLM rewriting {i + 1}/{total}...", end=" ", flush=True)

        context = _build_context(candidate["source_turn"], turns)

        try:
            llm_result = _rewrite_with_llm(candidate["sentence"], context)
        except Exception as e:
            err_msg = str(e)
            if "tokens per day" in err_msg.lower() or "tpd" in err_msg.lower():
                print(f"[daily token limit exhausted, falling back to naive for remaining]")
                # Naive-rewrite all remaining candidates
                for remaining in candidates[i:]:
                    normalised = _apply_rules(remaining["sentence"])
                    result.append({**remaining, "normalised": normalised, "priority": "preferred"})
                return result
            # Per-minute rate limit - wait and retry
            print(f"[rate limited, waiting 60s...]", end=" ", flush=True)
            time.sleep(60)
            try:
                llm_result = _rewrite_with_llm(candidate["sentence"], context)
            except Exception:
                print(f"[still failing, falling back to naive]")
                normalised = _apply_rules(candidate["sentence"])
                result.append({**candidate, "normalised": normalised, "priority": "preferred"})
                continue

        if llm_result is None:
            print("[filtered - not a requirement]")
            continue

        priority, normalised = llm_result
        print(f"OK [{priority}]")
        result.append({**candidate, "normalised": normalised, "priority": priority})

        # Throttle to stay within Groq free-tier rate limits (~30 req/min)
        time.sleep(2)

    return result
