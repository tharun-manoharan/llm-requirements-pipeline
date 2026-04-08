"""Stage 4b: Deduplication - collapse semantically equivalent requirements.

Supports two modes:
  - naive: no-op (returns list unchanged)
  - llm:   single LLM batch call that identifies semantic duplicates across
           the full requirements list and returns the subset to keep

Returns a tuple (filtered_list, decisions) where decisions is a list of dicts:
  [{"removed": str, "duplicate_of": str, "confidence": "high"|"medium"|"low",
    "reason": str}, ...]
"""

import json
import time

_DEDUP_SYSTEM_PROMPT = """\
You are a requirements engineer reviewing a list of software requirements \
extracted from a stakeholder interview.

Your task: identify SEMANTIC DUPLICATES — pairs of requirements that describe \
the same underlying system behaviour, even if phrased differently.

Rules:
- A requirement is a duplicate only if another in the list already covers \
the same system behaviour.
- When one of a duplicate pair must be removed, remove the LESS SPECIFIC one. \
If equally specific, remove the one with the higher index (later in the list).
- Do NOT remove requirements that are related but distinct. \
  Examples of DISTINCT (keep both): \
  "prevent movement into no-go zones" and "sound an alarm near no-go zones" — \
  different system actions, both should be kept.
- When in doubt, keep both.

Output: a JSON array of objects, one per requirement to REMOVE. Each object must have:
  "index"        : 0-based index of the requirement to remove
  "duplicate_of" : 0-based index of the requirement it duplicates (the one being kept)
  "confidence"   : "high" | "medium" | "low"
  "reason"       : one short sentence explaining why they are duplicates

If no duplicates exist, output an empty array [].
Output ONLY the JSON array — no explanation, no markdown.\
"""


def deduplicate_requirements(
    rewritten: list[dict],
    mode: str = "naive",
) -> tuple[list[dict], list[dict]]:
    """Remove semantically duplicate requirements.

    Args:
        rewritten: list of requirement dicts (output of rewrite stage).
        mode: "naive" (passthrough) or "llm" (LLM-based dedup).

    Returns:
        (filtered_list, decisions) where decisions records each removal with
        confidence and reason. decisions is empty for naive mode.
    """
    if mode != "llm" or len(rewritten) < 2:
        return rewritten, []

    return _deduplicate_with_llm(rewritten)


def _format_requirements(rewritten: list[dict]) -> str:
    lines = []
    for i, req in enumerate(rewritten):
        lines.append(f"[{i}] Turn {req['source_turn']}: {req['normalised']}")
    return "\n".join(lines)


def _deduplicate_with_llm(rewritten: list[dict]) -> tuple[list[dict], list[dict]]:
    """Call the LLM to identify duplicate indices, then remove them."""
    from pipeline.llm_client import get_llm_client, LLM_MODEL

    client = get_llm_client()
    user_msg = _format_requirements(rewritten)

    print(
        f"  Deduplicating {len(rewritten)} requirements with LLM...",
        end=" ",
        flush=True,
    )

    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": _DEDUP_SYSTEM_PROMPT},
                    {"role": "user", "content": user_msg},
                ],
                max_tokens=2048,
                temperature=0.0,
            )
            break
        except Exception as e:
            err_msg = str(e)
            if "tokens per day" in err_msg.lower() or "tpd" in err_msg.lower():
                print("[daily token limit exhausted, skipping dedup]")
                return rewritten, []
            wait = 60 * (attempt + 1)
            if attempt < 2:
                print(
                    f"[rate limited, waiting {wait}s - attempt {attempt + 1}/3...]",
                    end=" ",
                    flush=True,
                )
                time.sleep(wait)
            else:
                print("[still failing after 3 attempts, skipping dedup]")
                return rewritten, []
    else:
        return rewritten, []

    msg = resp.choices[0].message
    content = msg.content or getattr(msg, "reasoning", None) or ""
    raw = content.strip()
    decisions = _parse_decisions(raw, max_index=len(rewritten) - 1)
    indices_to_remove = {d["index"] for d in decisions}

    if decisions:
        print(f"removing {len(decisions)} duplicate(s)")
        for d in decisions:
            kept = rewritten[d["duplicate_of"]]["normalised"][:50]
            gone = rewritten[d["index"]]["normalised"][:50]
            print(f"    [{d['confidence']}] \"{gone}...\"")
            print(f"          => duplicate of \"{kept}...\"")
            print(f"          reason: {d['reason']}")
    else:
        print("no duplicates found")

    dedup_log = [
        {
            "removed": rewritten[d["index"]]["normalised"],
            "duplicate_of": rewritten[d["duplicate_of"]]["normalised"],
            "confidence": d["confidence"],
            "reason": d["reason"],
        }
        for d in decisions
    ]

    return [req for i, req in enumerate(rewritten) if i not in indices_to_remove], dedup_log


def _parse_decisions(raw: str, max_index: int) -> list[dict]:
    """Parse a JSON array of dedup decision objects from the LLM response.

    Each object must have: index, duplicate_of, confidence, reason.
    Returns an empty list if parsing fails or indices are out of range.
    """
    VALID_CONFIDENCE = {"high", "medium", "low"}

    # Strip any markdown fences the model might add
    cleaned = raw.strip().strip("`").strip()
    if cleaned.startswith("json"):
        cleaned = cleaned[4:].strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("[")
        end = cleaned.rfind("]")
        if start != -1 and end != -1 and end > start:
            try:
                data = json.loads(cleaned[start : end + 1])
            except json.JSONDecodeError:
                return []
        else:
            return []

    if not isinstance(data, list):
        return []

    decisions = []
    for item in data:
        if not isinstance(item, dict):
            continue
        try:
            idx = int(item["index"])
            dup_of = int(item["duplicate_of"])
        except (KeyError, TypeError, ValueError):
            continue
        if not (0 <= idx <= max_index and 0 <= dup_of <= max_index and idx != dup_of):
            continue
        confidence = str(item.get("confidence", "low")).lower()
        if confidence not in VALID_CONFIDENCE:
            confidence = "low"
        reason = str(item.get("reason", "")).strip()
        decisions.append({"index": idx, "duplicate_of": dup_of, "confidence": confidence, "reason": reason})

    return decisions
