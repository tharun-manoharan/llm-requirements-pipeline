"""Stage 6: FRET Export - convert structured requirements to FRETish format.

Generates a JSON file importable into NASA's FRET (Formal Requirements
Elicitation Tool).  Each requirement is decomposed by an LLM into the
FRETish grammar:

    [SCOPE] [CONDITION] COMPONENT shall [TIMING] RESPONSE

The exported JSON includes pre-computed LTL semantics and variable
declarations so no manual steps are required after import into FRET.
"""

import json
import re
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
# Core LLM conversion
# ---------------------------------------------------------------------------

def _call_llm(statement: str, retries: int = 3,
              known_vars: list[dict] | None = None) -> dict | None:
    """Ask the LLM to fretify one requirement.  Returns parsed JSON or None."""
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
            break
        except Exception as e:
            if "429" in str(e) and attempt < retries:
                wait = 10 * (attempt + 1)
                print(f"[429 rate-limit, waiting {wait}s...]", end=" ", flush=True)
                time.sleep(wait)
            else:
                raise

    raw = resp.choices[0].message.content.strip()
    if raw.startswith("```"):
        lines = raw.splitlines()
        raw = "\n".join(line for line in lines if not line.startswith("```")).strip()
    return json.loads(raw)


# ---------------------------------------------------------------------------
# Semantics pre-computation
# ---------------------------------------------------------------------------

def _parse_fretish_fallback(fulltext: str) -> dict | None:
    """Extract fretish fields from fulltext when the LLM decomposition failed.

    Handles the error-fallback fulltexts like
    'the system shall always satisfy req_005'.
    """
    m = re.match(
        r'^(?:when\s+(\S+)\s+)?the\s+(\S+)\s+shall\s+(\S+)\s+satisfy\s+(\S+)$',
        fulltext.strip(),
    )
    if not m:
        return None
    condition_var, component, timing, response_var = m.groups()
    return {
        "component": component,
        "scope": None,
        "condition_var": condition_var,
        "timing": timing,
        "response_var": response_var,
        "response_description": "",
        "parse_confidence": "low",
    }


def _compute_fretish_text_ranges(
    fulltext: str, component: str, timing: str, condition_var: str | None,
    scope_text: str | None = None,
) -> dict | None:
    """Return character-position ranges for each FRETish token in fulltext.

    Returns None if the fulltext doesn't match the expected structure.
    """
    ranges: dict = {}

    if scope_text:
        if not fulltext.startswith(scope_text):
            return None
        ranges["scopeTextRange"] = [0, len(scope_text) - 1]

    if condition_var:
        cond_phrase = f"when {condition_var}"
        cond_pos = fulltext.find(cond_phrase)
        if cond_pos == -1:
            return None
        ranges["conditionTextRange"] = [cond_pos, cond_pos + len(cond_phrase) - 1]

    comp_phrase = f"the {component}"
    comp_start = fulltext.find(comp_phrase)
    if comp_start == -1:
        return None
    comp_end = comp_start + len(comp_phrase) - 1
    ranges["componentTextRange"] = [comp_start, comp_end]

    shall_pos = fulltext.find(" shall ", comp_end)
    if shall_pos == -1:
        return None
    timing_start = shall_pos + 7  # len(" shall ") == 7

    # Implicit timing: "shall satisfy X" without a timing keyword
    if fulltext[timing_start:timing_start + 8] == "satisfy ":
        ranges["responseTextRange"] = [timing_start, len(fulltext) - 1]
        return ranges

    timing_end = timing_start + len(timing) - 1
    ranges["timingTextRange"] = [timing_start, timing_end]

    satisfy_pos = fulltext.find(" satisfy ", timing_end)
    if satisfy_pos == -1:
        return None
    ranges["responseTextRange"] = [satisfy_pos + 1, len(fulltext) - 1]

    return ranges


def _build_fret_formulas(timing: str, R: str, C: str | None) -> dict | None:
    """Compute LTL formula fields for the six standard no-scope patterns.

    Returns None for unsupported combinations (e.g. scoped, eventually).
    Formulas verified against exported FRET semantics for always/never/immediately
    with and without a regular condition.  The null_regular_always case is
    derived by analogy with null_regular_never (replacing !R with R).
    """
    post = {
        "post_condition":          f"({R})",
        "post_condition_unexp_pt":  R,
        "post_condition_unexp_ft":  R,
        "post_condition_unexp_pctl":R,
        "post_condition_SMV_pt":    R,
        "post_condition_SMV_ft":    R,
        "post_condition_MLTL_ft":   R,
        "post_condition_PRISM_pctl":R,
    }

    if C is None:
        if timing == "always":
            ft = f"(LAST V {R})"
            pt = f"(H {R})"
            return {
                **post,
                "ft": ft, "pt": pt,
                "pctl":         f"(P>=1[(G {R})])",
                "ptExpanded":   pt,
                "ftExpanded":   ft,
                "pctlExpanded": f"(P>=1[(G {R})])",
                "CoCoSpecCode": f"H({R})",
                "ftInfAUExpanded": f"(G {R})",
                "mltlExpanded": "(G[0,M] p0)",
                "WESTMapping":  f"p0: {R}",
                "R2U2Code":     R,
            }
        if timing == "eventually":
            ft = f"((! LAST) U {R})"
            pt = f"(O {R})"
            return {
                **post,
                "ft": ft, "pt": pt,
                "pctl":         f"(P>=1[(F {R})])",
                "ptExpanded":   pt,
                "ftExpanded":   ft,
                "pctlExpanded": f"(P>=1[(F {R})])",
                "CoCoSpecCode": f"O({R})",
                "ftInfAUExpanded": f"(F {R})",
                "mltlExpanded": "(F[0,M] p0)",
                "WESTMapping":  f"p0: {R}",
                "R2U2Code":     f"(F {R})",
            }
        if timing == "never":
            ft = f"(LAST V (! {R}))"
            pt = f"(H (! {R}))"
            return {
                **post,
                "ft": ft, "pt": pt,
                "pctl":         f"(P>=1[(G (! {R}))])",
                "ptExpanded":   pt,
                "ftExpanded":   ft,
                "pctlExpanded": f"(P>=1[(G (! {R}))])",
                "CoCoSpecCode": f"H(not ({R}))",
                "ftInfAUExpanded": f"(G (! {R}))",
                "mltlExpanded": "(G[0,M] (! p0))",
                "WESTMapping":  f"p0: {R}",
                "R2U2Code":     f"(! {R})",
            }
        if timing == "immediately":
            pt = f"(H ((Z FALSE) -> {R}))"
            return {
                **post,
                "ft": R, "pt": pt,
                "pctl":         f"(P>=1[{R}])",
                "ptExpanded":   pt,
                "ftExpanded":   R,
                "pctlExpanded": f"(P>=1[{R}])",
                "CoCoSpecCode": f"H((ZtoPre(false) => {R}))",
                "ftInfAUExpanded": R,
                "mltlExpanded": "p0",
                "WESTMapping":  f"p0: {R}",
                "R2U2Code":     f"((TAU == 0) -> {R})",
            }

    else:  # has condition C
        cond = {
            "regular_condition_unexp_pt":   C,
            "regular_condition_unexp_ft":   C,
            "regular_condition_unexp_pctl": C,
            "regular_condition_SMV_pt":     C,
            "regular_condition_SMV_ft":     C,
            "regular_condition_MLTL_ft":    C,
            "regular_condition_PRISM_pctl": C,
        }
        if timing == "immediately":
            ft = (f"((LAST V (((! {C}) & ((! LAST) & (X {C})))"
                  f" -> (X {R}))) & ({C} -> {R}))")
            pt   = f"(H (({C} & (Z (! {C}))) -> {R}))"
            pctl = (f"P>=1[((G (((! {C}) & (X {C})) =>"
                    f" (X (P>=1[{R}])))) & ({C} => (P>=1[{R}])))]")
            return {
                **post, **cond,
                "ft": ft, "pt": pt, "pctl": pctl,
                "ptExpanded":   pt,
                "ftExpanded":   ft,
                "pctlExpanded": pctl,
                "CoCoSpecCode": f"H((({C} and ZtoPre(not ({C}))) => {R}))",
                "ftInfAUExpanded": (f"((G (((! {C}) & (X {C}))"
                                    f" -> (X {R}))) & ({C} -> {R}))"),
                "mltlExpanded": (f"((G[0,M] (((! p0) & (F[1,1] p0))"
                                 f" -> (F[1,1] p1))) & (p0 -> p1))"),
                "WESTMapping":  f"p0: {C}<br/>p1: {R}",
                "R2U2Code":     (f"((((! {C}) && (F[1,1] {C}))"
                                 f" -> (F[1,1] {R})) && (((TAU == 0) && {C}) -> {R}))"),
            }
        if timing == "never":
            ft = (f"((LAST V (((! {C}) & ((! LAST) & (X {C})))"
                  f" -> (X (LAST V (! {R}))))) & ({C} -> (LAST V (! {R}))))")
            pt   = f"(H ((H (! {C})) | (! {R})))"
            pctl = (f"P>=1[((G (((! {C}) & (X {C})) =>"
                    f" (X (P>=1[(G (! {R}))])))) & ({C} => (P>=1[(G (! {R}))])))]")
            return {
                **post, **cond,
                "ft": ft, "pt": pt, "pctl": pctl,
                "ptExpanded":   pt,
                "ftExpanded":   ft,
                "pctlExpanded": pctl,
                "CoCoSpecCode": f"H((H(not ({C})) or not ({R})))",
                "ftInfAUExpanded": (f"((G (((! {C}) & (X {C}))"
                                    f" -> (X (G (! {R}))))) & ({C} -> (G (! {R}))))"),
                "mltlExpanded": (f"((G[0,M] (((! p0) & (F[1,1] p0))"
                                 f" -> (G[1,M] (! p1)))) & (p0 -> (G[0,M] (! p1))))"),
                "WESTMapping":  f"p0: {C}<br/>p1: {R}",
                "R2U2Code":     (f"((((! {C}) && (F[1,1] {C}))"
                                 f" -> (G[1,M] (! {R}))) && (((TAU == 0) && {C})"
                                 f" -> (G[0,M] (! {R}))))"),
            }
        if timing == "always":
            ft = (f"((LAST V (((! {C}) & ((! LAST) & (X {C})))"
                  f" -> (X (LAST V {R})))) & ({C} -> (LAST V {R})))")
            pt   = f"(H ((H (! {C})) | {R}))"
            pctl = (f"P>=1[((G (((! {C}) & (X {C})) =>"
                    f" (X (P>=1[(G {R})])))) & ({C} => (P>=1[(G {R})])))]")
            return {
                **post, **cond,
                "ft": ft, "pt": pt, "pctl": pctl,
                "ptExpanded":   pt,
                "ftExpanded":   ft,
                "pctlExpanded": pctl,
                "CoCoSpecCode": f"H((H(not ({C})) or {R}))",
                "ftInfAUExpanded": (f"((G (((! {C}) & (X {C}))"
                                    f" -> (X (G {R})))) & ({C} -> (G {R})))"),
                "mltlExpanded": (f"((G[0,M] (((! p0) & (F[1,1] p0))"
                                 f" -> (G[1,M] p1))) & (p0 -> (G[0,M] p1)))"),
                "WESTMapping":  f"p0: {C}<br/>p1: {R}",
                "R2U2Code":     (f"((((! {C}) && (F[1,1] {C}))"
                                 f" -> (G[1,M] {R})) && (((TAU == 0) && {C})"
                                 f" -> (G[0,M] {R})))"),
            }

    return None


def _build_fret_formulas_in_scope(S: str, timing: str, R: str, C: str | None) -> dict | None:
    """LTL formulas for 'in S' scope — verified against FRET export (REQ-079, REQ-081)."""
    post = {
        "post_condition":            f"({R})",
        "post_condition_unexp_pt":   R,
        "post_condition_unexp_ft":   R,
        "post_condition_unexp_pctl": R,
        "post_condition_SMV_pt":     R,
        "post_condition_SMV_ft":     R,
        "post_condition_MLTL_ft":    R,
        "post_condition_PRISM_pctl": R,
    }
    if C is None:
        if timing == "always":
            ft = f"(LAST V ({S} -> {R}))"
            pt = f"(H ({S} -> {R}))"
            pctl = f"(P>=1[(G ({S} -> {R}))])"
            return {
                **post,
                "ft": ft, "pt": pt, "pctl": pctl,
                "ptExpanded":      pt,
                "ftExpanded":      ft,
                "pctlExpanded":    pctl,
                "CoCoSpecCode":    f"H(({S} => {R}))",
                "ftInfAUExpanded": f"(G ({S} -> {R}))",
                "mltlExpanded":    "(G[0,M] (p0 -> p1))",
                "WESTMapping":     f"p0: {S}<br/>p1: {R}",
                "R2U2Code":        f"({S} -> {R})",
            }
        if timing == "never":
            ft = f"(LAST V ({S} -> (! {R})))"
            pt = f"(H ({S} -> (! {R})))"
            pctl = f"(P>=1[(G ({S} -> (! {R})))])"
            return {
                **post,
                "ft": ft, "pt": pt, "pctl": pctl,
                "ptExpanded":      pt,
                "ftExpanded":      ft,
                "pctlExpanded":    pctl,
                "CoCoSpecCode":    f"H(({S} => not ({R})))",
                "ftInfAUExpanded": f"(G ({S} -> (! {R})))",
                "mltlExpanded":    "(G[0,M] (p0 -> (! p1)))",
                "WESTMapping":     f"p0: {S}<br/>p1: {R}",
                "R2U2Code":        f"({S} -> (! {R}))",
            }
    return None


def _build_fret_formulas_after_scope(S: str, timing: str, R: str, C: str | None) -> dict | None:
    """LTL formulas for 'after S' scope — verified against FRET export (REQ-031, REQ-090).

    FLin_S (unexpanded) is the falling-edge trigger of S.
    Expanded future-time:  (S & !LAST & X(!S))
    Expanded past-time:    (!S & Y(S)) & Y(H(!(!S & Y(S))))
    """
    FLin = f"FLin_{S}"
    FLin_ft_exp = f"(({S} & (! LAST)) & (X (! {S})))"
    FLin_pt_exp = f"(((! {S}) & (Y {S})) & (Y (H (! ((! {S}) & (Y {S}))))))"

    post = {
        "post_condition":            f"({R})",
        "post_condition_unexp_pt":   R,
        "post_condition_unexp_ft":   R,
        "post_condition_unexp_pctl": R,
        "post_condition_SMV_pt":     R,
        "post_condition_SMV_ft":     R,
        "post_condition_MLTL_ft":    R,
        "post_condition_PRISM_pctl": R,
    }

    # Special case: eventually (verified for no-condition only)
    if timing == "eventually" and C is None:
        inner_ft = f"((! LAST) U {R})"
        ft = f"(((! {FLin}) U ({FLin} & (X {inner_ft}))) | (LAST V (! {FLin})))"
        pt = f"((O {FLin}) -> (! ((! {R}) S ((! {R}) & {FLin}))))"
        return {
            **post,
            "ft": ft, "pt": pt,
            "ftExpanded":   ft.replace(FLin, FLin_ft_exp),
            "ptExpanded":   pt.replace(FLin, FLin_pt_exp),
            "CoCoSpecCode": "", "pctl": "", "pctlExpanded": "",
        }

    # All other timings: get inner formula from null-scope builder then wrap
    inner = _build_fret_formulas(timing, R, C)
    if inner is None:
        return None

    inner_ft = inner["ft"]
    ft = f"(((! {FLin}) U ({FLin} & (X {inner_ft}))) | (LAST V (! {FLin})))"

    if C is None:
        if timing == "always":
            pt = f"((O {FLin}) -> ({R} S ({R} & {FLin})))"
        elif timing == "never":
            pt = f"((O {FLin}) -> ((! {R}) S ((! {R}) & {FLin})))"
        elif timing == "immediately":
            pt = f"((O {FLin}) -> ({R} S ({R} & {FLin})))"
        else:
            return None
    else:  # has condition C — verified for immediately (REQ-031)
        trigger = f"({C} & ((Y (! {C})) | {FLin}))"
        inner_mod = f"({trigger} -> (! {R}))" if timing == "never" else f"({trigger} -> {R})"
        pt = f"((O {FLin}) -> ({inner_mod} S ({inner_mod} & {FLin})))"

    return {
        **inner,
        "ft": ft, "pt": pt,
        "ftExpanded":   ft.replace(FLin, FLin_ft_exp),
        "ptExpanded":   pt.replace(FLin, FLin_pt_exp),
        "CoCoSpecCode": "", "pctl": "", "pctlExpanded": "",
    }


def _build_fret_semantics_scoped(
    scope_type: str, S: str, scope_text: str,
    component: str, timing: str, R: str, C: str | None, fulltext: str,
) -> dict:
    """Assemble the FRET semantics object for 'in S' or 'after S' scoped requirements."""
    text_ranges = _compute_fretish_text_ranges(
        fulltext, component, timing, C, scope_text=scope_text,
    )
    if text_ranges is None:
        return {}

    if scope_type == "in":
        formulas = _build_fret_formulas_in_scope(S, timing, R, C)
    else:
        formulas = _build_fret_formulas_after_scope(S, timing, R, C)

    if formulas is None:
        return {}

    scope_dict: dict = {"type": scope_type}
    if scope_type == "after":
        scope_dict.update({"exclusive": False, "required": False})

    condition_type = "regular" if C else "null"
    # S must be first — FRET uses this list to resolve formula variables
    variables = [S] + ([C] if C else []) + [R]

    if C:
        trigger_part = (
            f"TRIGGER: first point in the interval if <b><i>({C})</i></b> is true "
            f"and any point where <b><i>({C})</i></b> becomes true."
        )
        diagram_vars = f"TC = <b><i>({C})</i></b>, Response = <b><i>({R})</i></b>."
    else:
        trigger_part = "TRIGGER: first point in the scope interval."
        diagram_vars = f"Response = <b><i>({R})</i></b>."

    behavior = {
        "never":       f"<b><i>({R})</i></b> must be false within the scope.",
        "immediately": f"<b><i>({R})</i></b> must hold at the trigger point.",
    }.get(timing, f"<b><i>({R})</i></b> must hold throughout the scope.")

    description = (
        f"SCOPE: in the interval defined by <b><i>({S})</i></b>.<br>"
        f"{trigger_part}<br>"
        f"REQUIRED BEHAVIOR: for every trigger, {behavior}"
    )
    prob_description = description.replace(
        "REQUIRED BEHAVIOR: for every trigger,",
        "REQUIRED BEHAVIOR: for every trigger, with probability >=1,",
    )

    semantics: dict = {
        "type":        "nasa",
        "scope":       scope_dict,
        "condition":   condition_type,
        "probability": "null",
        "timing":      timing,
        "response":    "satisfaction",
        "variables":   variables,
        "component_name": component,
        **text_ranges,
        "diagramVariables":          diagram_vars,
        "description":               description,
        "probabilistic_description": prob_description,
        "diagram": (
            f"_media/user-interface/examples/svgDiagrams/"
            f"{scope_type}_{condition_type}_{timing}_satisfaction.svg"
        ),
        "scope_mode_pt": "BAD_PT",
        "scope_mode_ft": "BAD_FT",
        **formulas,
        "component": component,
    }

    if C:
        semantics["qualifier_word"]    = "when"
        semantics["pre_condition"]     = f"({C})"
        semantics["regular_condition"] = f"({C})"

    return semantics


def _build_fret_semantics(fret_data: dict, fulltext: str) -> dict:
    """Assemble the full FRET semantics object from LLM fretification output.

    Covers null-scope and 'in S' / 'after S' scoped requirements with
    timing always/never/immediately (plus eventually for after-scope).
    Returns {} for unsupported patterns so FRET still accepts the import.
    """
    component = fret_data.get("component") or "system"
    timing    = (fret_data.get("timing") or "always").lower()
    R         = fret_data.get("response_var")
    C         = fret_data.get("condition_var") or None
    scope     = fret_data.get("scope") or None

    # Fix 1: error fallbacks — LLM failed, parse response_var from the fulltext
    if not R:
        parsed = _parse_fretish_fallback(fulltext)
        if parsed is None:
            return {}
        component = parsed["component"] or "system"
        timing    = (parsed["timing"] or "always").lower()
        R         = parsed["response_var"]
        C         = parsed.get("condition_var") or None
        scope     = None
        if not R:
            return {}

    # Fix 2: scope / condition present in decomp but absent from fulltext — ignore them
    if scope and scope not in fulltext:
        scope = None
    if C and f"when {C}" not in fulltext:
        C = None

    # Scoped requirements — dispatch before timing check (after S supports eventually)
    if scope:
        scope_lower = scope.lower()
        if scope_lower.startswith("in "):
            S = scope[3:].strip().replace(" ", "_")
            if timing not in ("always", "never"):
                return {}
            return _build_fret_semantics_scoped("in", S, scope, component, timing, R, C, fulltext)
        if scope_lower.startswith("after "):
            S = scope[6:].strip().replace(" ", "_")
            if timing not in ("always", "never", "immediately", "eventually"):
                return {}
            return _build_fret_semantics_scoped("after", S, scope, component, timing, R, C, fulltext)
        return {}

    # Null scope
    if timing not in ("always", "never", "immediately", "eventually"):
        return {}

    text_ranges = _compute_fretish_text_ranges(fulltext, component, timing, C)
    if text_ranges is None:
        return {}

    formulas = _build_fret_formulas(timing, R, C)
    if formulas is None:
        return {}

    condition_type = "regular" if C else "null"
    variables = ([C] if C else []) + [R]

    # Natural-language description fields
    scope_part   = "SCOPE: in the interval defined by the entire execution."
    if C:
        trigger_part = (
            f"TRIGGER: first point in the interval if <b><i>({C})</i></b> is true "
            f"and any point in the interval where <b><i>({C})</i></b> becomes true (from false)."
        )
        diagram_vars = f"TC = <b><i>({C})</i></b>, Response = <b><i>({R})</i></b>."
    else:
        trigger_part = "TRIGGER: first point in the interval."
        diagram_vars = f"Response = <b><i>({R})</i></b>."

    if timing == "never":
        behavior = (f"<b><i>({R})</i></b> must be false at all time points "
                    f"between (and including) the trigger and the end of the interval.")
    elif timing == "immediately":
        behavior = (f"if trigger holds then <b><i>({R})</i></b> also holds "
                    f"at the same time point.")
    else:
        behavior = (f"<b><i>({R})</i></b> must hold at all time points "
                    f"between (and including) the trigger and the end of the interval.")

    description = (f"{scope_part}<br>{trigger_part}<br>"
                   f"REQUIRED BEHAVIOR: for every trigger, {behavior}")
    prob_description = description.replace(
        "REQUIRED BEHAVIOR: for every trigger,",
        "REQUIRED BEHAVIOR: for every trigger, with probability >=1,",
    )

    semantics: dict = {
        "type":        "nasa",
        "scope":       {"type": "null"},
        "condition":   condition_type,
        "probability": "null",
        "timing":      timing,
        "response":    "satisfaction",
        "variables":   variables,
        "component_name": component,
        **text_ranges,
        "diagramVariables":       diagram_vars,
        "description":            description,
        "probabilistic_description": prob_description,
        "diagram": (f"_media/user-interface/examples/svgDiagrams/"
                    f"null_{condition_type}_{timing}_satisfaction.svg"),
        "scope_mode_pt": "BAD_PT",
        "scope_mode_ft": "BAD_FT",
        **formulas,
        "component": component,
    }

    if C:
        semantics["qualifier_word"]     = "when"
        semantics["pre_condition"]      = f"({C})"
        semantics["regular_condition"]  = f"({C})"

    return semantics


# ---------------------------------------------------------------------------
# Variable declarations
# ---------------------------------------------------------------------------

def _build_variables_list(fret_reqs: list[dict], project_name: str) -> list[dict]:
    """Collect every unique FRETish variable and return FRET variable records."""
    seen: dict[str, dict] = {}

    for req in fret_reqs:
        decomp    = req.get("_fret_decomposition", {})
        req_uuid  = req.get("_id", "")
        component = decomp.get("component") or "system"

        # For error fallbacks, derive variables from the fulltext
        if decomp.get("parse_confidence") == "error":
            parsed = _parse_fretish_fallback(req.get("fulltext", ""))
            if parsed:
                decomp = {**decomp, **parsed}
                component = parsed.get("component") or "system"

        # (var_name, description, idType)
        candidates = [
            (decomp.get("response_var"),  decomp.get("response_description", ""), "Output"),
            (decomp.get("condition_var"), "", "Input"),
        ]

        # Extract scope variable(s) — Input because the environment defines the mode
        scope_str = decomp.get("scope") or ""
        fulltext  = req.get("fulltext", "")
        if scope_str:
            scope_lower = scope_str.lower()
            rest = scope_str
            for prefix in ("only after ", "after ", "only in ", "in ",
                           "only before ", "before ", "not in "):
                if scope_lower.startswith(prefix):
                    rest = scope_str[len(prefix):]
                    break
            # Handle "X and Y" compound scopes (e.g. "only after A and B")
            for part in re.split(r'\s+and\s+', rest, flags=re.IGNORECASE):
                s_var = part.strip().replace(" ", "_")
                if s_var:
                    candidates.append((s_var, "", "Input"))

        for var_name, description, id_type in candidates:
            if not var_name:
                continue
            if var_name not in seen:
                seen[var_name] = {
                    "reqs":        [],
                    "description": description or "",
                    "component":   component,
                    "idType":      id_type,
                }
            elif seen[var_name]["idType"] == "Input" and id_type == "Output":
                # A variable used as both condition and response — treat as Output
                seen[var_name]["idType"] = "Output"
            if req_uuid:
                seen[var_name]["reqs"].append(req_uuid)

    return [
        {
            "project":            project_name,
            "component_name":     info["component"],
            "variable_name":      var_name,
            "reqs":               info["reqs"],
            "dataType":           "boolean",
            "idType":             info["idType"],
            "moduleName":         "",
            "description":        info["description"],
            "assignment":         "",
            "assignmentVariables":  [],
            "copilotAssignment":  "",
            "r2u2Assignment":     "",
            "smvAssignment":      "",
            "smvAssignmentVariables": [],
            "modeRequirement":    "",
            "modeldoc":           False,
            "modeldoc_id":        "",
            "modeldoc_vectorIndex": None,
            "modelComponent":     "",
            "completed":          True,
            "r2u2Completed":      True,
            "smvCompleted":       True,
            "_id": f"{project_name}{info['component']}{var_name}",
        }
        for var_name, info in seen.items()
    ]


# ---------------------------------------------------------------------------
# Per-requirement conversion
# ---------------------------------------------------------------------------

def _fretify_one(req: dict, known_vars: list[dict] | None = None) -> dict:
    """Convert a single pipeline requirement dict into a FRET requirement dict."""
    statement = req["statement"]
    fret_data = _call_llm(statement, known_vars=known_vars)

    fulltext = fret_data.get("fretish", "")

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
        "fulltext": fulltext,
        "status": req["priority"],
        "_fret_decomposition": {
            "component":            fret_data.get("component"),
            "scope":                fret_data.get("scope"),
            "condition_var":        fret_data.get("condition_var"),
            "timing":               fret_data.get("timing"),
            "response_var":         fret_data.get("response_var"),
            "response_description": fret_data.get("response_description"),
            "parse_confidence":     fret_data.get("parse_confidence"),
        },
        "semantics": _build_fret_semantics(fret_data, fulltext),
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def fretify_requirements(
    requirements: list[dict],
    project_name: str = "LLM-Pipeline",
) -> list[dict]:
    """Convert a list of structured pipeline requirements to FRET format."""
    total = len(requirements)
    fret_reqs = []
    known_vars: list[dict] = []

    for i, req in enumerate(requirements):
        req_with_project = {**req, "_project": project_name}

        print(f"  [FRET] {i + 1}/{total}  {req['id']} ...", end=" ", flush=True)
        try:
            fret_req = _fretify_one(req_with_project, known_vars=known_vars)
            confidence = fret_req["_fret_decomposition"]["parse_confidence"]
            sem_ok = bool(fret_req["semantics"])
            print(f"OK [{confidence}]{'  semantics:auto' if sem_ok else '  semantics:manual'}")
            fret_reqs.append(fret_req)

            decomp = fret_req["_fret_decomposition"]
            if decomp.get("response_var") and decomp.get("response_description"):
                known_vars.append({
                    "response_var":         decomp["response_var"],
                    "response_description": decomp["response_description"],
                })
        except Exception as e:
            err = str(e)
            if "tokens per day" in err.lower() or "tpd" in err.lower():
                print("[daily token limit — stopping FRET export early]")
                break
            print(f"[ERROR: {err[:60]}]")
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

        time.sleep(4)

    return fret_reqs


def export_fret_json(
    requirements: list[dict],
    output_path: str,
    project_name: str = "LLM-Pipeline",
) -> list[dict]:
    """Fretify requirements and write a FRET-importable JSON file.

    Exports {"requirements": [...], "variables": [...]} — the full FRET
    project format — with pre-computed LTL semantics and boolean variable
    declarations so no manual steps are needed after import.
    """
    fret_reqs = fretify_requirements(requirements, project_name)
    variables = _build_variables_list(fret_reqs, project_name)

    # Clean export: keep _id (FRET uses it) but strip internal pipeline fields
    _STRIP = {"_fret_decomposition", "_project"}
    export_reqs = [
        {k: v for k, v in r.items() if k not in _STRIP}
        for r in fret_reqs
    ]

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"requirements": export_reqs, "variables": variables}, f, indent=2)

    # Analysis file keeps the full decomposition for internal review
    analysis_path = output_path.replace(".json", "_analysis.json")
    with open(analysis_path, "w", encoding="utf-8") as f:
        json.dump({"requirements": fret_reqs, "variables": variables}, f, indent=2)

    # Summary
    confidences = [
        r["_fret_decomposition"].get("parse_confidence", "?") for r in fret_reqs
    ]
    for level in ("high", "medium", "low", "error"):
        count = confidences.count(level)
        if count:
            print(f"  FRET confidence  — {level}: {count}/{len(fret_reqs)}")

    auto_sem = sum(1 for r in fret_reqs if r.get("semantics"))
    print(f"  Semantics pre-computed : {auto_sem}/{len(fret_reqs)}")
    print(f"  Variables declared     : {len(variables)}")

    return fret_reqs
