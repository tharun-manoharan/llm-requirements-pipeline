"""Stage 4b: Deduplication - collapse semantically equivalent requirements.

Supports two modes:
  - naive: no-op (returns list unchanged)
  - llm:   single LLM batch call that identifies semantic duplicates across
           the full requirements list and returns the subset to keep
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

Output: a JSON array of 0-based indices to REMOVE. \
If no duplicates exist, output an empty array.
Output ONLY the JSON array — no explanation, no markdown.\
"""


def deduplicate_requirements(
    rewritten: list[dict],
    mode: str = "naive",
) -> list[dict]:
    """Remove semantically duplicate requirements.

    Args:
        rewritten: list of requirement dicts (output of rewrite stage).
        mode: "naive" (passthrough) or "llm" (LLM-based dedup).

    Returns:
        Filtered list with duplicates removed.
    """
    if mode != "llm" or len(rewritten) < 2:
        return rewritten

    return _deduplicate_with_llm(rewritten)


def _format_requirements(rewritten: list[dict]) -> str:
    lines = []
    for i, req in enumerate(rewritten):
        lines.append(f"[{i}] Turn {req['source_turn']}: {req['normalised']}")
    return "\n".join(lines)


def _deduplicate_with_llm(rewritten: list[dict]) -> list[dict]:
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
                return rewritten
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
                return rewritten
    else:
        return rewritten

    msg = resp.choices[0].message
    content = msg.content or getattr(msg, "reasoning", None) or ""
    raw = content.strip()
    indices_to_remove = _parse_indices(raw, max_index=len(rewritten) - 1)

    if indices_to_remove:
        removed = [rewritten[i]["normalised"][:60] for i in indices_to_remove]
        print(f"removing {len(indices_to_remove)} duplicate(s)")
        for s in removed:
            print(f"    - {s}...")
    else:
        print("no duplicates found")

    return [req for i, req in enumerate(rewritten) if i not in indices_to_remove]


def _parse_indices(raw: str, max_index: int) -> set[int]:
    """Parse a JSON array of indices from the LLM response.

    Returns an empty set if parsing fails or indices are out of range.
    """
    # Strip any markdown fences the model might add
    cleaned = raw.strip().strip("`").strip()
    if cleaned.startswith("json"):
        cleaned = cleaned[4:].strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        # Try to find a JSON array substring
        start = cleaned.find("[")
        end = cleaned.rfind("]")
        if start != -1 and end != -1 and end > start:
            try:
                data = json.loads(cleaned[start : end + 1])
            except json.JSONDecodeError:
                return set()
        else:
            return set()

    if not isinstance(data, list):
        return set()

    return {int(i) for i in data if isinstance(i, int) and 0 <= i <= max_index}
