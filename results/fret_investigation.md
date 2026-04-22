# FRET Investigation — Capabilities and Contradiction Detection

## Overview

This document investigates what NASA's FRET (Formal Requirements Elicitation Tool) can do beyond requirement import, with a particular focus on whether it can identify contradicting requirements. It is intended to inform the dissertation discussion of formal verification in the pipeline context.

---

## What the pipeline currently does with FRET

The pipeline's Stage 6 (`pipeline/fret.py`) uses an LLM to decompose each pipeline output into FRETish — FRET's controlled natural language — then writes a FRET-importable JSON file. The decomposition extracts:

| Field | Description | Example |
|---|---|---|
| `component` | System element | `system` |
| `scope` | Mode constraint (optional) | `null` |
| `condition_var` | Boolean trigger (optional) | `movement_command_exceeds_capabilities_or_speed` |
| `timing` | Temporal keyword | `always`, `immediately`, `never` |
| `response_var` | Snake_case behaviour name | `safe_mode` |
| `fulltext` | Complete FRETish sentence | `when movement_command_exceeds_capabilities_or_speed the system shall immediately enter safe_mode` |

The resulting JSON can be imported into FRET via **File → Import Requirements**. We have confirmed this import works correctly for all three datasets (IFA, IFA Augmented, Bristol N1/N2).

**Critical observation**: After import, the `semantics` field in all outputs remains `{}` (empty). FRET populates the `semantics` field only after it internally parses the FRETish `fulltext` of each requirement. This parsing happens inside FRET's UI. The populated semantics contain the formal LTL (Linear Temporal Logic) and CoCoSpec formulas that underlie FRET's analysis capabilities.

---

## What FRET actually does: the full capability map

### 1. FRETish parsing → LTL semantics

When a requirement is created or imported in FRET, FRET's grammar engine parses the FRETish sentence and populates the `semantics` block with:

- **pt** (past-time LTL formula): expresses what must have been true up to this point
- **ft** (future-time LTL formula): expresses what must be true going forward  
- **CoCoSpec**: the Lustre/Kind2-compatible property formula
- **diagram**: a timing diagram of the requirement's behaviour

Example — for `when movement_command_exceeds_capabilities_or_speed the system shall immediately enter safe_mode`, FRET generates approximately:

```
ft: G(movement_command_exceeds_capabilities_or_speed → X safe_mode)
```

This formalises "globally, whenever the trigger holds, at the very next step the response must hold."

For `the system shall never satisfy unauthorised_financial_access`:

```
ft: G(!unauthorised_financial_access)
```

### 2. Consistency and realizability checking (Kind2 integration)

FRET integrates with **Kind2**, a model checker for synchronous systems. Once requirements are formalised, FRET can check whether a set of requirements is **realizable** — i.e., whether there exists any possible implementation that satisfies all requirements simultaneously.

If two requirements are **contradictory**, no implementation can satisfy both, and FRET + Kind2 will report the requirement set as **unrealizable**.

**This is the mechanism for contradiction detection.** It is not a dedicated "find contradictions" feature — it is the realizability checker reporting failure.

#### Worked example relevant to IFA

Suppose the pipeline extracted two requirements:

- `R-A`: `the system shall always satisfy referee_can_update_events`  
  → LTL: `G(referee_can_update_events)`

- `R-B`: `the system shall never satisfy referee_can_update_events`  
  → LTL: `G(!referee_can_update_events)`

`G(referee_can_update_events) ∧ G(!referee_can_update_events)` is unsatisfiable. FRET + Kind2 would report this requirement set as unrealizable, flagging R-A and R-B as the conflicting pair.

This is exactly the scenario the supervisor described: "X should never do Y" vs "X should always do Y."

#### How FRET surfaces this

In FRET's UI, after running realizability analysis:
- Requirements that participate in the contradiction are highlighted
- FRET generates a **counter-example** — a trace showing a scenario in which the requirements cannot simultaneously hold
- The trace can be examined to understand why they conflict

### 3. Completeness checking (variable coverage)

FRET can also check whether the requirements collectively cover all possible system states — specifically, whether for every possible combination of input variables, at least one requirement specifies the system's behaviour. Gaps are reported as **vacuous** or **under-specified** conditions.

### 4. Test case generation

From formalised requirements, FRET can generate test cases that exercise each requirement's condition and timing. For triggered requirements (those with a `condition_var`), FRET generates test inputs that make the condition true and verifies the response follows.

### 5. Natural language ↔ formal alignment checking

FRET's grammar provides structured feedback when a FRETish sentence is ambiguous or does not parse cleanly. The `parse_confidence` field in our pipeline's output (`high` / `medium` / `low`) is a proxy for this: requirements with `low` confidence are those where the LLM struggled to find a clean FRETish mapping, which typically means the natural language requirement is vague or compound.

---

## Limitation: abstract response variables

The most significant limitation for our pipeline is that all `response_var` values are **abstract snake_case identifiers** — e.g., `team_budget_management`, `safe_mode`, `referee_can_update_events`. They are not connected to any formal system model with defined state variables.

This has two consequences:

1. **FRET can parse and formalise the requirements**, but the resulting LTL formulas are expressed over abstract Boolean variables. This is sufficient for **syntactic contradiction detection** (e.g., `G(X) ∧ G(!X)`).

2. **FRET cannot detect semantic contradictions** without a system model. For example, if the pipeline produces:
   - `the system shall always satisfy team_data_access_restricted`
   - `the system shall always satisfy ifa_full_data_access`
   
   These may be semantically contradictory (teams cannot access others' data, but IFA can see everything — which could conflict if "full access" means "including other teams' private data") but FRET sees them as two distinct Boolean variables and has no way to know they conflict.

   To detect semantic contradictions, a system engineer would need to write a **contract** (component model in Lustre/CoCoSpec) that relates these abstract variables to concrete system state.

---

## Contradiction detection: practical assessment

| Scenario | Detectable by FRET? | Notes |
|---|---|---|
| Exact logical contradiction (`shall always X` + `shall never X`) | **Yes** — syntactically | Requires same `response_var` in both requirements |
| Near-logical contradiction (same concept, different variable names) | **No** without model | `team_budget_management` and `budget_management_disabled` look unrelated to FRET |
| Semantic contradiction (requirements imply conflicting system state) | **No** without model | Requires a formal system model (Lustre/AGREE) to express relationships |
| Missing case (no requirement covers a certain input state) | **Partially** — via completeness checking | FRET can flag uncovered input combinations, but only for variables mentioned in requirements |

In practice, for our pipeline's output, FRET would only reliably detect **exact logical contradictions** — where the same `response_var` appears in one requirement under `always` and another under `never`. These are also the easiest contradictions for a human reviewer to spot directly.

---

## What would be needed to go further

To make FRET's contradiction detection genuinely useful for elicitation-derived requirements, the following steps would be needed:

1. **Response variable normalisation**: requirements that describe the same system behaviour should use the same `response_var`. Currently each requirement gets an independently-named variable, so even semantically equivalent requirements look unrelated to FRET. This could be addressed by running the deduplication pass on `response_var` names before FRET export.

2. **Component modelling**: writing a Lustre/CoCoSpec component that defines how `response_var` values relate to each other. For example, defining that `ifa_full_data_access` implies `all_team_budget_data_visible`, which then conflicts with `team_budget_data_restricted_to_team`. This is manual engineering work beyond the scope of automated elicitation.

3. **Scope and condition alignment**: many of our requirements are unconditional (`timing: always`) because the natural language lacks explicit mode or trigger information. Adding scope constraints would allow FRET to check whether two requirements that conflict globally can be reconciled by placing them in different modes.

---

## Summary for dissertation

| FRET capability | Pipeline uses it? | Feasible without model? | Notes |
|---|---|---|---|
| FRETish parsing → LTL | Partially (LLM pre-generates FRETish; FRET not run) | Yes | `semantics` field is empty — FRET not yet run on the imported requirements |
| Exact contradiction detection | No | Yes (for same response_var) | Would require normalised variable names |
| Semantic contradiction detection | No | No | Requires formal system model |
| Realizability checking | No | Partially | Possible for simple requirement sets |
| Completeness checking | No | Partially | Limited by abstract variables |
| Test case generation | No | Partially | Useful for triggered requirements |

**Bottom line**: FRET is a promising formal verification layer for a requirements pipeline, but the gap between natural-language-derived requirements and formally checkable properties is significant. The pipeline currently bridges part of this gap by translating to FRETish, but the `semantics` field — where FRET's actual formal analysis lives — is never populated in our workflow. The pipeline stops at import; the formal analysis requires running FRET's internal tools.

For contradiction detection specifically: FRET can detect exact logical contradictions over shared response variables, but this requires response variable normalisation that the current pipeline does not perform. Semantic contradictions (the more practically interesting case) require a system model that is infeasible to generate automatically from elicitation transcripts.

---

## Recommended next steps (if pursuing FRET further)

1. **Run FRET on the IFA requirements** — import `output_v3.5_llm_fret.json`, let FRET parse the FRETish sentences, and export the populated JSON to see what the `semantics` block looks like in practice.

2. **Introduce a synthetic contradiction** — manually add two IFA requirements with the same `response_var` under `always` and `never`, import into FRET, and run Kind2 realizability checking to verify that FRET flags the conflict. This gives a concrete dissertation result.

3. **Evaluate parse confidence distribution** — examine how many of the pipeline's FRETish sentences parse cleanly (high confidence) vs. poorly (low), and characterise which requirement types consistently fail. This is a meaningful evaluation of the FRETish conversion stage independent of model checking.
