"""Merged pipeline variants for ablation study: modular vs merged stage comparison.

Three variants collapse the LLM stages (extract / rewrite / dedup) in different ways:
  - run_merged_full()           : extract + rewrite + dedup in one LLM call
  - run_merged_extract_rewrite(): extract + rewrite in one call, separate dedup
  - run_merged_rewrite_dedup()  : separate extract, rewrite + dedup in one call

All return (rewritten, dedup_log) compatible with structure_requirements() in run.py.
"""

import json
import time

from pipeline.llm_client import call_llm
from pipeline.extract import extract_candidates_llm, _format_turns_for_llm
from pipeline.deduplicate import deduplicate_requirements

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_VALID_PRIORITIES = {"essential", "preferred", "optional"}
_VALID_TYPES = {"functional", "non-functional"}


def _ensure_shall(statement: str) -> str:
    if not statement.lower().startswith("the system shall"):
        statement = "The system shall " + statement[0].lower() + statement[1:]
    return statement.rstrip() + "." if not statement.endswith(".") else statement


def _parse_req_list(raw: str, max_turn_index: int) -> list[dict]:
    """Parse a JSON requirements array from merged-full or merged-er responses.

    Expected item shape: {statement, type, priority, source_turn}
    Returns dicts compatible with the rewrite stage output format.
    """
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []

    items = data.get("requirements", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])

    result = []
    for item in items:
        statement = item.get("statement", "").strip()
        source_turn = item.get("source_turn")
        req_type = str(item.get("type", "functional")).lower()
        priority = str(item.get("priority", "preferred")).lower()

        if not statement:
            continue
        if not isinstance(source_turn, int) or not (0 <= source_turn <= max_turn_index):
            source_turn = 0
        if req_type not in _VALID_TYPES:
            req_type = "functional"
        if priority not in _VALID_PRIORITIES:
            priority = "preferred"

        statement = _ensure_shall(statement)
        result.append({
            "sentence": statement,
            "normalised": statement,
            "source_turn": source_turn,
            "req_type": req_type,
            "priority": priority,
        })
    return result


def _call_with_retry(call_kwargs: dict, label: str) -> object | None:
    """Retry wrapper around call_llm (up to 3 attempts with backoff).

    Returns the response object or None if all attempts fail.
    """
    for attempt in range(3):
        try:
            return call_llm(**call_kwargs)
        except Exception as e:
            err_msg = str(e)
            if "tokens per day" in err_msg.lower() or "tpd" in err_msg.lower():
                print(f"  [{label}] daily token limit exhausted", flush=True)
                return None
            wait = 60 * (attempt + 1)
            if attempt < 2:
                print(f"  [{label}] rate limited, waiting {wait}s - attempt {attempt + 1}/3...", flush=True)
                time.sleep(wait)
            else:
                print(f"  [{label}] still failing after 3 attempts", flush=True)
                return None
    return None


# ---------------------------------------------------------------------------
# Variant 1: Full merge — extract + rewrite + dedup in one LLM call
# ---------------------------------------------------------------------------

_FULL_SYSTEM_PROMPT = """\
You are a senior requirements engineer. You will be given a stakeholder \
interview transcript. Your task is to:

1. EXTRACT every requirement-bearing sentence or clause.
2. REWRITE each as a clean "The system shall ..." statement.
3. DEDUPLICATE: if two requirements describe the same system behaviour, \
include only the more specific one.

Requirements are often implicit. Look for: explicit demands ("must", "should", \
"shall", "need to"), business rules, access control, process implications, \
platform preferences, notification requests, data visibility rules, \
architectural constraints, scalability expectations, compliance constraints, \
endorsed features from prior systems, and aspirational statements.

Do NOT extract: greetings, questions, meta-conversation, pure operational \
context, vague agreement, or project planning remarks.

PRIORITY: essential (explicitly demanded, strong language), preferred (clearly \
desired), optional (briefly mentioned, uncertain, aspirational).

REQ_TYPE: non-functional (performance, security, availability, scalability, \
reliability, response time, data residency, accessibility, auditability, \
hosting) or functional (everything else).

Output JSON: {"requirements": [{"statement": "The system shall ...", \
"type": "functional|non-functional", "priority": "essential|preferred|optional", \
"source_turn": <0-based int>}]}

Rules: start with "The system shall", end with period, remove filler words, \
do not invent features, output ONLY valid JSON.\
"""


def run_merged_full(turns: list[dict]) -> tuple[list[dict], list[dict]]:
    """Extract, rewrite, and deduplicate in a single LLM call."""
    if not turns:
        return [], []

    max_turn_index = max(t["turn_index"] for t in turns)
    print("  [merged-full] Sending conversation to LLM (extract+rewrite+dedup)...", flush=True)

    resp = _call_with_retry(dict(
        messages=[
            {"role": "system", "content": _FULL_SYSTEM_PROMPT},
            {"role": "user", "content": _format_turns_for_llm(turns)},
        ],
        response_format={"type": "json_object"},
        max_tokens=8192,
        temperature=0.0,
    ), "merged-full")

    if resp is None:
        return [], []

    rewritten = _parse_req_list(resp.choices[0].message.content.strip(), max_turn_index)
    print(f"  {len(rewritten)} requirements extracted, rewritten, and deduped.", flush=True)
    return rewritten, []


# ---------------------------------------------------------------------------
# Variant 2: Extract + rewrite merged, separate dedup
# ---------------------------------------------------------------------------

_ER_SYSTEM_PROMPT = """\
You are a senior requirements engineer. You will be given a stakeholder \
interview transcript. Your task is to:

1. EXTRACT every requirement-bearing sentence or clause.
2. REWRITE each as a clean "The system shall ..." statement with a priority.

Requirements are often implicit. Look for: explicit demands ("must", "should", \
"shall", "need to"), business rules, access control, process implications, \
platform preferences, notification requests, data visibility rules, \
architectural constraints, scalability expectations, compliance constraints, \
endorsed features from prior systems, and aspirational statements.

Do NOT extract: greetings, questions, meta-conversation, pure operational \
context, vague agreement, or project planning remarks.

PRIORITY: essential (explicitly demanded, strong language), preferred (clearly \
desired), optional (briefly mentioned, uncertain, aspirational).

REQ_TYPE: non-functional (performance, security, availability, scalability, \
reliability, response time, data residency, accessibility, auditability, \
hosting) or functional (everything else).

Output JSON: {"requirements": [{"statement": "The system shall ...", \
"type": "functional|non-functional", "priority": "essential|preferred|optional", \
"source_turn": <0-based int>}]}

Rules: start with "The system shall", end with period, remove filler words, \
do not invent features, output ONLY valid JSON.\
"""


def run_merged_extract_rewrite(turns: list[dict]) -> tuple[list[dict], list[dict]]:
    """Extract and rewrite in one LLM call, then run separate deduplication."""
    if not turns:
        return [], []

    max_turn_index = max(t["turn_index"] for t in turns)
    print("  [merged-er] Sending conversation to LLM (extract+rewrite)...", flush=True)

    resp = _call_with_retry(dict(
        messages=[
            {"role": "system", "content": _ER_SYSTEM_PROMPT},
            {"role": "user", "content": _format_turns_for_llm(turns)},
        ],
        response_format={"type": "json_object"},
        max_tokens=8192,
        temperature=0.0,
    ), "merged-er")

    if resp is None:
        return [], []

    rewritten = _parse_req_list(resp.choices[0].message.content.strip(), max_turn_index)
    print(f"  {len(rewritten)} requirements extracted+rewritten.", flush=True)
    return deduplicate_requirements(rewritten, mode="llm")


# ---------------------------------------------------------------------------
# Variant 3: Separate extract, rewrite + dedup merged
# ---------------------------------------------------------------------------

_RD_SYSTEM_PROMPT = """\
You are a requirements engineer. You will be given a numbered list of \
requirement candidate sentences extracted from a stakeholder interview. \
Your task is to:

1. REWRITE each candidate as a clean "The system shall ..." statement.
2. ASSIGN a priority level.
3. DEDUPLICATE: if two candidates describe the same system behaviour, \
include only the more specific one (silently omit the other).

PRIORITY: essential (explicitly demanded, strong language), preferred (clearly \
desired), optional (briefly mentioned, uncertain, aspirational).

Rules: start with "The system shall", end with period, remove filler words, \
omit non-requirements, output ONLY valid JSON.

Output JSON: {"requirements": [{"index": <0-based source index>, \
"statement": "The system shall ...", "priority": "essential|preferred|optional"}]}\
"""


def run_merged_rewrite_dedup(turns: list[dict]) -> tuple[list[dict], list[dict]]:
    """Use the existing modular extract, then rewrite + deduplicate in one LLM call."""
    if not turns:
        return [], []

    candidates = extract_candidates_llm(turns)
    if not candidates:
        return [], []

    user_msg = "\n".join(f"[{i}] Turn {c['source_turn']}: {c['sentence']}" for i, c in enumerate(candidates))
    print(f"  [merged-rd] Sending {len(candidates)} candidates to LLM (rewrite+dedup)...", flush=True)

    resp = _call_with_retry(dict(
        messages=[
            {"role": "system", "content": _RD_SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        response_format={"type": "json_object"},
        max_tokens=4096,
        temperature=0.0,
    ), "merged-rd")

    if resp is None:
        return [], []

    rewritten = _parse_rd_response(resp.choices[0].message.content.strip(), candidates)
    print(f"  {len(rewritten)} requirements rewritten+deduped.", flush=True)
    return rewritten, []


def _parse_rd_response(raw: str, candidates: list[dict]) -> list[dict]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []

    items = data.get("requirements", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])

    result = []
    seen = set()
    for item in items:
        statement = item.get("statement", "").strip()
        index = item.get("index")
        priority = str(item.get("priority", "preferred")).lower()

        if not statement or not isinstance(index, int) or not (0 <= index < len(candidates)) or index in seen:
            continue
        seen.add(index)
        if priority not in _VALID_PRIORITIES:
            priority = "preferred"

        original = candidates[index]
        result.append({
            "sentence": original["sentence"],
            "normalised": _ensure_shall(statement),
            "source_turn": original["source_turn"],
            "req_type": original["req_type"],
            "priority": priority,
        })
    return result
