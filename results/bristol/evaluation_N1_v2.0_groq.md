# Pipeline Evaluation v2.0 (Groq / Llama 3.3 70B) — N1.txt

## Dataset

- **Source**: Bristol PhD thesis — *The Importance of Trust in Space Teleoperation*
- **Interview**: N1 — industrial robot-arm operator (nuclear/hazardous environments)
- **File**: `datasets/bristol/N1.txt` — 101 turns (Interviewer / Participant)
- **Ground truth**: `datasets/bristol/N1_expected.json` — 16 requirements
- **Output**: `results/bristol/output_N1_v2.0_groq.json`

## What changed from v1.0 (naive)

- Stages 2+3 replaced by a single LLM call (Llama 3.3 70B via Groq) that reads
  the full conversation and extracts requirement-bearing sentences semantically.
- Stage 4 LLM rewriter with 2-turn context window (same as IFA v2.0).
- Same model and prompts as the IFA v2.0 evaluation.

---

## Summary

### Detection accuracy

| Metric | v1.0 (Naive) | **v2.0 (LLM 70B)** |
|---|---|---|
| Ground-truth requirements | 16 | 16 |
| Pipeline output count | 31 | **16** |
| True positives | 9 outputs → 5 GTs | **9 outputs → 9 GTs** |
| False positives | 22 | **7** |
| False negatives | 11 | **7** |
| **Precision** | 29.0% | **56.3%** |
| **Recall** | 31.3% | **56.3%** |
| **F1** | 0.301 | **0.563** |

### End-to-end accuracy

| Metric | v1.0 | **v2.0** |
|---|---|---|
| Usable requirement statements | 0 / 31 (0%) | **9 / 16 (56%)** |
| Rewrite quality: Excellent | 0 | **3** |
| Rewrite quality: Good | 0 | **4** |
| Rewrite quality: Acceptable | 0 | **2** |
| Rewrite quality: Poor | 31 | **0** |
| Type classification correct (of TPs) | 9/9 (100%*) | **9/9 (100%*)** |

*Both versions score 100% on type for their TPs, but this is partly because the
two NF requirements (GT-005, GT-016) are mostly missed or correctly classified
only when detected — not a meaningful signal.

### Priority accuracy

| Metric | Value |
|---|---|
| Ground truth distribution | 4 essential, 7 preferred, 1 optional |
| Pipeline output distribution | 13 essential, 2 preferred, 1 optional |
| Priority correct (of TPs) | 5 / 9 (56%) |

Same over-indexing on "essential" seen in the IFA v2.0 evaluation — the model
rarely uses "preferred" and never uses "optional" for confirmed requirements.

---

## Classification of each pipeline output

### True Positives (9)

| LLM ID | Maps to GT | Type | Priority | Rewrite quality | Notes |
|---|---|---|---|---|---|
| REQ-005 | GT-003 | func ✓ | essential ✓ | Excellent | "display current position of each joint within its range on the MMI screens" — verbatim |
| REQ-006 | GT-004 | func ✓ | essential ✗ (GT: preferred) | Good | "change colours when approaching limits" — slightly vague, should say "colour-coded feedback" |
| REQ-010 | GT-009 | func ✓ | essential ✗ (GT: preferred) | Good | "variable viewpoint to allow the user to look around" — good |
| REQ-011 | GT-008 | func ✓ | essential ✓ | Good | "fixed camera views in addition to variable viewpoints" — captures the fixed+variable combo |
| REQ-012 | GT-011 | func ✓ | essential ✗ (GT: preferred) | Acceptable | "overlay on the screen as a guide" — loses "alignment" and "new task" context |
| REQ-013 | GT-013 | func ✓ | essential ✓ | Good | "no-go zone to prevent damage to surrounding objects" — good; loses "configurable" |
| REQ-014 | GT-014 | func ✓ | essential ✗ (GT: preferred) | Excellent | "produce an alarm or noise to alert the user when approaching a no-go zone" — near-verbatim |
| REQ-015 | GT-016 | NF ✓ | preferred ✓ | Acceptable | "high image resolution" — correct but loses "prioritised over frame rate" rationale |
| REQ-016 | GT-015 | func ✓ | essential ✓ | Excellent | "force feedback to indicate when moving forward and when to stop" — excellent |

### False Positives (7)

| LLM ID | Reason |
|---|---|
| REQ-001 | Rehabilitation arm context — participant discussing a *different* system and expressing uncertainty ("I'm not sure how that works") |
| REQ-002 | Material recognition speculation — investigation started "two weeks ago", participant unsure "how it transfers over"; not a stated requirement |
| REQ-003 | Derived from REQ-002 — hallucinated extension of the speculative material recognition discussion |
| REQ-004 | Interviewer suggestion ("you could send the robot in, it maps out…") — participant gave a tentative "yeah potentially" |
| REQ-007 | Duplicate of REQ-002 — second extraction of the same material recognition speculation |
| REQ-008 | "more durable" — description of the current system's improvement over the previous one, not a stated requirement |
| REQ-009 | "minimal latency" — participant describing the current system positively ("super minimal, hardly noticeable"), not stating a requirement |

### False Negatives (7) — real requirements the pipeline MISSED

| GT ID | Missed requirement | Notes |
|---|---|---|
| GT-001 | Safe mode on over-speed command | Participant describes existing behaviour as fact — LLM may have treated it as a current-state description |
| GT-002 | Software soft stops and hardware hard stops | Same — described factually without modal verbs |
| GT-005 | Minimal non-intrusive feedback design | Expressed as personal preference ("I'd want information but not overload") — LLM may not have extracted the design principle |
| GT-006 | Pre-programmed waypoint navigation | Participant describes an existing feature positively ("the operator was there in case") — LLM extracted the broader material recognition speculation instead |
| GT-007 | One-button home position recall | Embedded in a longer discussion about autonomous control — likely filtered as a description rather than requirement |
| GT-010 | Adaptive camera zoom near target | Personal preference ("cameras zoomed in with me") — too implicit for extraction |
| GT-012 | Ghost mode / predicted end-position preview | Participant endorses an existing feature ("ghost mode is useful… gives super confidence") — evaluative phrasing not extracted |

---

## Analysis

### Where the LLM improved over naive

**Detection recall doubled** (31.3% → 56.3%). The LLM correctly identified 9 of
16 requirements including GT-004, GT-008, GT-009, GT-011, GT-013, GT-014, GT-016
which keyword matching missed entirely. The key wins are the features the
participant endorsed explicitly: no-go zones, camera views, AR overlay, force
feedback, and image resolution.

**Rewrite quality: 0% → 56% usable.** Every true positive is a clean, usable
requirement statement. Three are near-verbatim ("MMI joint position display",
"approaching a no-go zone alarm", "force feedback to indicate movement direction").
Zero poor rewrites.

**Type classification** is correct for all 9 TPs (8 functional, 1 NF). The NF
requirement GT-016 (resolution priority) is correctly identified.

### Where the LLM still fails

**False positives from speculative content.** 4 of 7 FPs come from the
material-recognition discussion (Turns 89-94) where the participant described an
investigation that had just started. The LLM extracted these as requirements even
though they were prefaced with uncertainty ("I'm not quite sure how that transfers
over"). The IFA v2.0 had only 2 FPs — the interview format makes it harder to
distinguish between confirmed requirements and aspirational/speculative ideas.

**Endorsed existing features missed.** GT-001, GT-002, GT-006, GT-007, GT-012
are all cases where the participant described an existing system feature positively
(implying "we need this in the new system too"). The LLM correctly filtered many
current-state descriptions as NOT_A_REQUIREMENT but also over-filtered some that
expressed genuine requirements. This is a known challenge for interview data
vs structured elicitation sessions.

**Priority: over-labelled as essential.** 13 of 16 outputs are "essential". Only
2 preferred, 0 optional in the TP set. GT-004, GT-009, GT-011, GT-014 should be
"preferred" — the participant expressed clear desire but not urgency.

---

## Comparison: IFA vs Bristol N1

| Metric | IFA (conv_02) v2.0 | Bristol N1 v2.0 |
|---|---|---|
| Ground truth requirements | 41 | 16 |
| Pipeline outputs | 23 | 16 |
| True positives | 21 | 9 |
| False positives | 2 | 7 |
| False negatives | 19 | 7 |
| **Precision** | **91.3%** | **56.3%** |
| **Recall** | **53.7%** | **56.3%** |
| **F1** | **0.676** | **0.563** |
| Usable outputs | 21/23 (91%) | 9/16 (56%) |

The IFA conversation produces far better precision (91% vs 56%) because it is
a structured requirements elicitation session — both roles are aligned on the
goal of specifying requirements. Interview data mixes requirements with:
- Descriptions of current systems (filtered as NOT_A_REQUIREMENT)
- Speculative / aspirational ideas (incorrectly extracted as requirements)
- Endorsed existing features (missed as NOT_A_REQUIREMENT)

Bristol N1 recall (56%) is slightly higher than IFA recall (54%), suggesting the
LLM handles the interview's evaluative language ("is useful", "is a great idea")
better than it handles the IFA's noisy conversational filler.

---

## Conclusion

On the Bristol N1 interview the LLM pipeline achieves **F1 = 0.563** vs 0.301
for the naive baseline — an 87% improvement. All 9 true positives produce
usable requirement statements. The remaining bottlenecks are:

| Problem | Impact | Root cause |
|---|---|---|
| Speculative content extracted | 4/7 FPs | Interview discusses aspirational ideas without clear modal verbs |
| Endorsed existing features missed | 5/7 FNs | Positive factual descriptions filtered as current-state |
| Priority over-labelled | 4/9 TPs wrong priority | Same 70B model bias seen in IFA v2.0 |
| Ghost mode / evaluative language missed | GT-012 | "X is useful" not reliably extracted |

The extract.py prompt was tuned for elicitation sessions. A targeted prompt
addition for interview data — specifically recognising "X is/was useful / a great
idea / gives confidence" as a requirement endorsement — should recover GT-012 and
similar evaluative-language requirements.
