"""Stages 2+3 (LLM): Semantic requirement extraction from conversation turns.

Replaces the naive keyword-matching segmenter (stage 2) and sentence-level
detector (stage 3) with a single LLM call that identifies all requirement-
bearing sentences in the full conversation.

Output format matches detect_candidates() so stage 4 works unchanged.
"""

import json
import time

from pipeline.llm_client import get_llm_client, LLM_MODEL

_EXTRACT_SYSTEM_PROMPT = """\
You are a senior requirements engineer analysing a stakeholder interview \
transcript. Your task is to identify EVERY sentence or clause that expresses \
a software requirement - something the system-to-be-built must do, support, \
enforce, or exhibit.

Requirements in stakeholder interviews are often implicit. Look for ALL of \
these patterns:
- Explicit demands: "must", "should", "shall", "need to"
- Business rules stated as facts: "each team manages its own budget"
- Access control / permissions: "only X can do Y", "X cannot do Z"
- Process descriptions that imply system behaviour: "the manager approaches \
IFA to open a new team" implies a registration workflow
- Platform / interface preferences: "web based", "mobile application"
- Notification / alert requests: "remind me", "get notified"
- Data visibility rules: "everyone can see", "only the team can access"
- Architectural constraints: "same system, different interfaces"
- Procedural language: "insertion of X is done by Y" implies role-based permission
- Scalability / capacity expectations: "50,000 users"

Do NOT extract:
- Greetings, introductions, or closing remarks
- Questions from developers or stakeholders (sentences ending with ?)
- Meta-conversation: "let us move on", "did that answer your question"
- Descriptions of the CURRENT process unless they clearly state what the \
NEW system should do differently
- Vague agreement: "ok", "sure", "indeed", "right"
- Project planning / phasing: "this should be first phase"
- Closing remarks or pleasantries

For each requirement found, output a JSON object with these fields:
- "sentence": The exact or minimally cleaned text from the transcript that \
contains the requirement. Preserve the speaker's meaning. Remove only \
filler words (uh, um, okay so, yeah, you know). Do not rewrite into \
formal language - that is a later stage's job.
- "source_turn": The integer turn index (0-based) where this text appears.
- "req_type": Either "functional" or "non-functional".
  - non-functional: performance, security, encryption, availability, \
scalability, reliability, response time, localisation, data residency, \
accessibility, auditability, hosting/infrastructure
  - functional: everything else (features, workflows, permissions, data \
access, notifications, UI)

Respond with a JSON object: {"requirements": [...]}

Important:
- Be thorough. It is better to include a borderline requirement than to \
miss a real one. A later stage will filter false positives.
- A single turn may contain multiple requirements. Extract each separately.
- Use the turn index numbers exactly as provided in the input.
- Output ONLY valid JSON. No markdown, no explanation, no preamble.\
"""


def _format_turns_for_llm(turns: list[dict], max_chars_per_turn: int = 500) -> str:
    """Format all conversation turns for the extraction LLM call.

    Truncates very long turns to stay within token budgets.
    """
    lines = []
    for t in turns:
        text = t["text"]
        if len(text) > max_chars_per_turn:
            text = text[:max_chars_per_turn] + "..."
        lines.append(f"[Turn {t['turn_index']}] {t['role']}: {text}")
    return "\n".join(lines)


def _parse_extraction_response(response_text: str, max_turn_index: int) -> list[dict]:
    """Parse and validate the LLM extraction response.

    Returns list of dicts with keys: sentence, source_turn, req_type.
    Silently drops malformed entries rather than crashing.
    """
    data = json.loads(response_text)

    # Handle both {"requirements": [...]} and bare [...]
    if isinstance(data, dict):
        items = data.get("requirements", [])
    elif isinstance(data, list):
        items = data
    else:
        return []

    candidates = []
    for item in items:
        sentence = item.get("sentence", "").strip()
        source_turn = item.get("source_turn")
        req_type = item.get("req_type", "functional").lower()

        if not sentence:
            continue
        if not isinstance(source_turn, int) or source_turn < 0 or source_turn > max_turn_index:
            continue
        if req_type not in ("functional", "non-functional"):
            req_type = "functional"

        candidates.append({
            "sentence": sentence,
            "source_turn": source_turn,
            "req_type": req_type,
        })

    return candidates


def extract_candidates_llm(turns: list[dict]) -> list[dict]:
    """Extract requirement candidates using the LLM (replaces stages 2+3).

    Sends all conversation turns to the LLM in a single call and returns
    candidates in the same format as detect_candidates().
    """
    if not turns:
        return []

    client = get_llm_client()
    user_msg = _format_turns_for_llm(turns)
    max_turn_index = max(t["turn_index"] for t in turns)

    print("  Sending conversation to LLM for requirement extraction...", flush=True)

    _call_kwargs = dict(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": _EXTRACT_SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        response_format={"type": "json_object"},
        max_tokens=8192,
        temperature=0.1,
    )

    resp = None
    for attempt in range(3):
        try:
            resp = client.chat.completions.create(**_call_kwargs)
            break
        except Exception as e:
            err_msg = str(e)
            if "tokens per day" in err_msg.lower() or "tpd" in err_msg.lower():
                print(f"  [daily token limit exhausted - falling back to naive stages 2-3]", flush=True)
                from pipeline.segment import segment_turns
                from pipeline.detect import detect_candidates
                segmented = segment_turns(turns)
                return detect_candidates(segmented)
            wait = 60 * (attempt + 1)  # 60s, 120s, 180s
            if attempt < 2:
                print(f"  [rate limited, waiting {wait}s - attempt {attempt + 1}/3...]", flush=True)
                time.sleep(wait)
            else:
                print("  [still failing after 3 attempts, falling back to naive stages 2-3]", flush=True)
                from pipeline.segment import segment_turns
                from pipeline.detect import detect_candidates
                segmented = segment_turns(turns)
                return detect_candidates(segmented)

    response_text = resp.choices[0].message.content.strip()
    candidates = _parse_extraction_response(response_text, max_turn_index)

    if not candidates:
        print("  [LLM returned 0 candidates, falling back to naive]", flush=True)
        from pipeline.segment import segment_turns
        from pipeline.detect import detect_candidates
        segmented = segment_turns(turns)
        return detect_candidates(segmented)

    print(f"  {len(candidates)} candidate sentences extracted.", flush=True)
    return candidates
