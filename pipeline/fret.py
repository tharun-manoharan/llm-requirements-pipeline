"""Stage 6: FRET Export - convert structured requirements to FRETish format.

Generates a JSON file importable into NASA's FRET (Formal Requirements
Elicitation Tool).  Each requirement is decomposed by an LLM into the
FRETish grammar:

    [SCOPE] [CONDITION] COMPONENT shall [TIMING] RESPONSE

The exported JSON can be imported directly into FRET via
File > Import Requirements.
"""

import json
import time
import uuid

from pipeline.llm_client import get_llm_client, LLM_MODEL

# ---------------------------------------------------------------------------
# LLM prompt
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """\
You are a formal requirements engineer using NASA's FRET tool.
Your job is to convert a natural-language software requirement into
FRETish — the structured controlled language used by FRET.

FRETish grammar (all fields except COMPONENT and SHALL are optional):
  [SCOPE] [CONDITION] COMPONENT shall [TIMING] RESPONSE

Field rules
-----------
COMPONENT  : The system element. Use "system" unless the requirement
             clearly targets a named subsystem (e.g. "budget_module").
             Must be a single snake_case token.

SCOPE      : A mode constraint introduced by "in", "only in", "after",
             "only after", "before", "only before", or "not in".
             Omit unless the requirement is explicitly mode-specific.

CONDITION  : A boolean trigger introduced by "when", "if", "whenever",
             "upon", or "unless".  Omit for unconditional requirements.
             Use a short snake_case variable name for the trigger.

TIMING     : One of: always | eventually | immediately | never | next |
             finally | within N units | for N units | after N units |
             until COND | before COND
             - "always"      → ongoing state / invariant
             - "immediately" → triggered response (needs CONDITION)
             - "eventually"  → eventual delivery / liveness
             - "never"       → prohibition
             Omit timing for simple "shall satisfy" statements.

RESPONSE   : A short snake_case boolean variable name that captures the
             core behaviour.  Keep it under 6 words joined by underscores.
             Also provide a one-sentence English gloss.

Output format — respond with ONLY valid JSON, no markdown:
{
  "fretish": "<the complete FRETish sentence>",
  "component": "<component token>",
  "scope": null or "<scope text>",
  "condition_var": null or "<trigger variable name>",
  "timing": "<timing keyword or null>",
  "response_var": "<snake_case response variable>",
  "response_description": "<one-sentence English gloss of response_var>",
  "parse_confidence": "high" | "medium" | "low"
}

Use parse_confidence to signal how well the requirement maps to FRETish:
  high   → clean mapping, unambiguous timing and response
  medium → timing or condition required inference; meaning preserved
  low    → vague, compound, or too domain-specific to formalise cleanly

Examples
--------
Input: "The system shall allow each team to manage its own budget independently."
Output:
{
  "fretish": "the system shall always satisfy team_budget_management",
  "component": "system",
  "scope": null,
  "condition_var": null,
  "timing": "always",
  "response_var": "team_budget_management",
  "response_description": "Each team can independently manage its own budget.",
  "parse_confidence": "high"
}

Input: "The system shall notify users when a transaction exceeds the budget limit."
Output:
{
  "fretish": "when transaction_exceeds_budget the system shall immediately satisfy user_budget_notification_sent",
  "component": "system",
  "scope": null,
  "condition_var": "transaction_exceeds_budget",
  "timing": "immediately",
  "response_var": "user_budget_notification_sent",
  "response_description": "A notification has been sent to the user that the budget limit was exceeded.",
  "parse_confidence": "high"
}

Input: "The system shall never allow unauthorised users to access financial records."
Output:
{
  "fretish": "the system shall never satisfy unauthorised_financial_access",
  "component": "system",
  "scope": null,
  "condition_var": null,
  "timing": "never",
  "response_var": "unauthorised_financial_access",
  "response_description": "An unauthorised user has accessed financial records.",
  "parse_confidence": "high"
}
"""


# ---------------------------------------------------------------------------
# Core conversion
# ---------------------------------------------------------------------------

def _call_llm(statement: str, retries: int = 3,
              known_vars: list[dict] | None = None) -> dict | None:
    """Ask the LLM to fretify one requirement.  Returns parsed JSON or None.

    Retries up to `retries` times on 429 rate-limit responses.

    known_vars: list of {"response_var": ..., "response_description": ...} dicts
    accumulated from previously processed requirements in this run.  Passed to
    the LLM so it can reuse the same variable name when the behaviour matches.
    """
    client = get_llm_client()

    user_msg = statement
    if known_vars:
        var_lines = "\n".join(
            f"  - {v['response_var']}: {v['response_description']}"
            for v in known_vars
        )
        user_msg = (
            f"{statement}\n\n"
            f"Already-assigned response variables in this requirement set "
            f"(reuse the exact name if the behaviour matches):\n{var_lines}"
        )

    for attempt in range(retries + 1):
        try:
            resp = client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": user_msg},
                ],
                max_tokens=400,
                temperature=0.1,
            )
            break  # success
        except Exception as e:
            if "429" in str(e) and attempt < retries:
                wait = 10 * (attempt + 1)
                print(f"[429 rate-limit, waiting {wait}s...]", end=" ", flush=True)
                time.sleep(wait)
            else:
                raise

    raw = resp.choices[0].message.content.strip()

    # Strip markdown code fences if present
    if raw.startswith("```"):
        lines = raw.splitlines()
        raw = "\n".join(
            line for line in lines if not line.startswith("```")
        ).strip()

    return json.loads(raw)


def _fretify_one(req: dict, known_vars: list[dict] | None = None) -> dict:
    """Convert a single pipeline requirement dict into a FRET requirement dict."""
    statement = req["statement"]
    fret_data = _call_llm(statement, known_vars=known_vars)

    return {
        "_id": str(uuid.uuid4()),
        "reqid": req["id"],
        "parent_reqid": "",
        "project": req.get("_project", "LLM-Pipeline"),
        "rationale": statement,
        "comments": (
            f"Type: {req['type']} | "
            f"Priority: {req['priority']} | "
            f"Source: {req['source']} | "
            f"FRET confidence: {fret_data.get('parse_confidence', '?')}"
        ),
        "fulltext": fret_data["fretish"],
        "status": req["priority"],
        # Store decomposition for evaluation / reporting
        "_fret_decomposition": {
            "component":            fret_data.get("component"),
            "scope":                fret_data.get("scope"),
            "condition_var":        fret_data.get("condition_var"),
            "timing":               fret_data.get("timing"),
            "response_var":         fret_data.get("response_var"),
            "response_description": fret_data.get("response_description"),
            "parse_confidence":     fret_data.get("parse_confidence"),
        },
        # FRET fills this in after parsing fulltext — we leave it empty
        "semantics": {},
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def fretify_requirements(
    requirements: list[dict],
    project_name: str = "LLM-Pipeline",
) -> list[dict]:
    """Convert a list of structured pipeline requirements to FRET format.

    Args:
        requirements: output of structure_requirements() — list of dicts
                      with id, type, priority, statement, source.
        project_name: name of the FRET project to stamp on each requirement.

    Returns:
        List of FRET requirement dicts ready for JSON export.
    """
    total = len(requirements)
    fret_reqs = []
    known_vars: list[dict] = []

    for i, req in enumerate(requirements):
        # Inject project name so _fretify_one can read it
        req_with_project = {**req, "_project": project_name}

        print(
            f"  [FRET] {i + 1}/{total}  {req['id']} ...",
            end=" ",
            flush=True,
        )
        try:
            fret_req = _fretify_one(req_with_project, known_vars=known_vars)
            confidence = fret_req["_fret_decomposition"]["parse_confidence"]
            print(f"OK [{confidence}]")
            fret_reqs.append(fret_req)
            # Accumulate assigned vars so subsequent requirements can reuse them
            decomp = fret_req["_fret_decomposition"]
            if decomp.get("response_var") and decomp.get("response_description"):
                known_vars.append({
                    "response_var": decomp["response_var"],
                    "response_description": decomp["response_description"],
                })
        except Exception as e:
            err = str(e)
            if "tokens per day" in err.lower() or "tpd" in err.lower():
                print("[daily token limit — stopping FRET export early]")
                break
            print(f"[ERROR: {err[:60]}]")
            # Keep the requirement with a fallback FRETish statement
            fret_reqs.append({
                "_id": str(uuid.uuid4()),
                "reqid": req["id"],
                "parent_reqid": "",
                "project": project_name,
                "rationale": req["statement"],
                "comments": (
                    f"Type: {req['type']} | Priority: {req['priority']} | "
                    f"Source: {req['source']} | FRET confidence: error"
                ),
                "fulltext": f"the system shall always satisfy {req['id'].lower().replace('-', '_')}",
                "status": req["priority"],
                "_fret_decomposition": {"parse_confidence": "error"},
                "semantics": {},
            })

        # Throttle to stay within Cerebras rate limits
        time.sleep(4)

    return fret_reqs


def export_fret_json(
    requirements: list[dict],
    output_path: str,
    project_name: str = "LLM-Pipeline",
) -> list[dict]:
    """Fretify requirements and write them to a FRET-importable JSON file.

    Args:
        requirements: output of structure_requirements().
        output_path:  path to write the JSON file.
        project_name: FRET project name.

    Returns:
        The list of FRET requirement dicts that were written.
    """
    fret_reqs = fretify_requirements(requirements, project_name)

    # FRET imports a plain JSON array of requirement objects.
    # Strip internal fields (prefixed with _) before export so FRET
    # does not choke on unexpected keys.
    export_list = [
        {k: v for k, v in r.items() if not k.startswith("_")}
        for r in fret_reqs
    ]

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(export_list, f, indent=2)

    # Also write a fuller version with decomposition for our own analysis
    analysis_path = output_path.replace(".json", "_analysis.json")
    with open(analysis_path, "w", encoding="utf-8") as f:
        json.dump(fret_reqs, f, indent=2)

    # Print confidence summary
    confidences = [
        r["_fret_decomposition"].get("parse_confidence", "?")
        for r in fret_reqs
    ]
    for level in ("high", "medium", "low", "error"):
        count = confidences.count(level)
        if count:
            print(f"  FRET confidence — {level}: {count}/{len(fret_reqs)}")

    return fret_reqs
