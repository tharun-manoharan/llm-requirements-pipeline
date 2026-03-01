# Pipeline Evaluation v3.0 (Cerebras / gpt-oss-120b) — N1.txt

## Dataset

- **Source**: Bristol PhD thesis — *The Importance of Trust in Space Teleoperation*
- **Interview**: N1 — industrial robot-arm operator (nuclear/hazardous environments)
- **File**: `datasets/bristol/N1.txt` — 101 turns (Interviewer / Participant)
- **Ground truth**: `datasets/bristol/N1_expected.json` — 16 requirements
- **Output**: `results/bristol/output_N1_v3.0_llm.json`
- **Model**: gpt-oss-120b via Cerebras inference API

## What changed from v2.0

- Stages 2+3 replaced by a single LLM call that reads the full interview semantically.
- Stage 4 LLM rewriter also uses gpt-oss-120b (previously Llama 3.3 70B via Groq).
- gpt-oss-120b is a 120B-parameter reasoning model — larger than the previous 70B.

---

## Summary

### Detection accuracy

| Metric | v1.0 (Naive) | v2.0 (LLM 70B) | **v3.0 (LLM 120B)** |
|---|---|---|---|
| Ground-truth requirements | 16 | 16 | 16 |
| Pipeline output count | 31 | 16 | **21** |
| True positives (GTs covered) | 5 | 9 | **13** |
| False positives | 26 | 7 | **8** |
| False negatives | 11 | 7 | **3** |
| **Precision** | 16.1% | 56.3% | **61.9%** |
| **Recall** | 31.3% | 56.3% | **81.3%** |
| **F1** | 0.213 | 0.563 | **0.703** |

### End-to-end accuracy

| Metric | v1.0 | v2.0 | **v3.0** |
|---|---|---|---|
| Usable requirement statements | 0 / 31 (0%) | 9 / 16 (56%) | **18 / 21 (86%)** |
| Priority distribution | all preferred | 13 essential, 2 preferred | **5 essential, 15 preferred** |
| Priority correct (of TPs) | — | 5 / 9 (56%) | **7 / 13 (54%)** |
| Type classification correct (of TPs) | — | 9 / 9 (100%) | **12 / 13 (92%)** |

*Priority accuracy is roughly maintained at ~54% — the 120B model uses "preferred"
much more than the 70B model did, which better matches the GT distribution (4E/7P/1O),
but over-corrects slightly in the opposite direction (5E/15P vs 4E/7P/1O in GT).*

---

## Classification of each pipeline output

### True Positives (13 GTs covered)

| REQ | Maps to GT | Type | Priority | Rewrite quality | Notes |
|---|---|---|---|---|---|
| REQ-002 | GT-001 | func ✓ | essential ✓ | Excellent | Safe mode on over-speed — key miss in v2.0, now caught |
| REQ-003 | GT-003 + GT-004 | func ✓ | essential ✓ / ✗(GT-004: preferred) | Excellent | Merged joint display + colour feedback — both GTs captured in one statement |
| REQ-007 | GT-006 | func ✓ | preferred ✓ | Good | Teach files / waypoint navigation |
| REQ-008 | GT-007 | func ✓ | preferred ✓ | Good | Home button to known state |
| REQ-011 | GT-009 | func ✓ | preferred ✓ | Good | Variable viewpoint camera |
| REQ-012 | GT-008 | func ✓ | essential ✓ | Good | Fixed camera views |
| REQ-013 | GT-010 | func ✓ | preferred ✗ (GT: optional) | Acceptable | Adaptive camera zoom — partial match; GT specifies "narrows as end-effector approaches target", REQ says "camera follows view while zooming out" |
| REQ-015 | GT-016 | NF ✓ | preferred ✓ | Excellent | Prioritise resolution over frame rate |
| REQ-016 | GT-015 | func ✓ | preferred ✗ (GT: essential) | Good | Force feedback — GT-015 also requires adjustable sensitivity, which REQ-016 omits |
| REQ-017 | GT-012 | func ✓ | preferred ✓ | Excellent | Ghost mode — key miss in v2.0, now caught via "gives confidence" evaluative language |
| REQ-018 | GT-013 | func ✓ | preferred ✗ (GT: essential) | Good | No-go zones |
| REQ-019 | GT-014 | func ✓ | preferred ✓ | Good | Audible alarm approaching no-go zone |
| REQ-010 | GT-015 | func ✓ | preferred ✗ (GT: essential) | Good | Subtle tactile feedback (duplicate pathway to GT-015 alongside REQ-016) |

### False Positives (8)

| REQ | Reason |
|---|---|
| REQ-001 | "baseline and variant configurations (extended arms, lift capacity, waterproofing)" — extracted from a discussion about different project versions (Turn 13); describes hardware variants, not a software requirement. No GT match. |
| REQ-004 | "50% extension beyond original timeframe" — Turn 35; participant describes an existing scheduling rule, not a system requirement. No GT match. |
| REQ-005 | "stops or guides to ensure cable remains within defined area" — Turn 37; hardware safety constraint, not in GT scope. Speculative or out of scope. |
| REQ-006 | "model the whole scene exactly in simulation" — Turn 41; participant endorses their current simulation fidelity positively. No GT match — described as existing behaviour. |
| REQ-009 | "move robot close to target autonomously then hand over control" — Turn 46; related to GT-006 (waypoint navigation) but emphasises the handover concept not captured in GT. Borderline FP. |
| REQ-014 | "support optional 3D cameras" — Turn 69; participant mentions 3D cameras speculatively ("could potentially"). Not in GT. |
| REQ-020 | "computer vision to recognise materials, enforce no-go zones, provide visual cues" — Turn 89; same speculative material-recognition discussion that produced FPs in v2.0. Still extracted despite uncertainty language. |
| REQ-021 | "detect overload causing gripper fingers to open and provide feedback" — Turn 95; describes a current hardware behaviour as an observed fact, not a stated requirement. No GT match. |

### False Negatives (3) — GTs the pipeline missed

| GT | Missed requirement | Why missed |
|---|---|---|
| GT-002 | Software soft stops and hardware hard stops (joint range limits) | Discussed at Turn 17 immediately after the safe mode exchange. The LLM may have treated this as implementation detail of GT-001 and not extracted a separate requirement. |
| GT-005 | Minimal, non-intrusive feedback design | Expressed as a personal preference at Turn 23 ("I'd want information but not overload") without modal verbs. The LLM correctly ignored this as too implicit. Prompt pattern for "design philosophy as requirement" would help. |
| GT-011 | AR alignment overlay on camera view | Discussed at Turn 66. The participant describes the concept positively but without endorsing it as a requirement. Not extracted — the evaluative language pattern did not fire here. |

---

## Analysis

### Where v3.0 improved over v2.0

**Recall: 56.3% → 81.3%.** The four additional GTs recovered are the key wins:

- **GT-001 (safe mode)**: v2.0 filtered this as a current-state description; the larger
  120B model correctly reads "when a movement exceeds the system's capability" as a
  safety requirement, not just a description of existing behaviour.
- **GT-012 (ghost mode)**: v2.0 missed this entirely. The participant says "ghost mode
  is useful… gives super confidence". The 120B model recognises "X is useful / gives
  confidence" as requirement endorsement — a pattern v2.0 consistently missed.
- **GT-003 and GT-004** are merged into a single precise requirement (REQ-003) that
  captures both joint display and colour-coded feedback in one statement — arguably
  better than two separate requirements.
- **GT-007 (home button)**: v2.0 caught this; v3.0 continues to catch it and also
  adds the context of repeatable tasks.

**Priority discrimination is restored.** Unlike v2.0 (which labelled 13/16 as
"essential"), v3.0 labels only 5 as essential and 15 as preferred, much closer to the
GT distribution of 4 essential / 7 preferred / 1 optional. Priority accuracy is 54%
(7/13 correct among TPs) — roughly matching v2.0's 56%.

**Rewrite quality: 86% usable.** 18 of 21 outputs are clean usable statements.
REQ-001, REQ-004, REQ-006 are technically well-written but describe the wrong thing
(hardware details, scheduling rules, simulation).

### Where v3.0 still fails

**False positives from speculative/hardware content (+1 vs v2.0).** The extraction
LLM casts a wider net, recovering more requirements but also pulling in more edge-case
content: hardware variant discussion (REQ-001), cable routing (REQ-005), simulation
fidelity (REQ-006), and the same material-recognition speculation as v2.0 (REQ-020).

**GT-002 (soft/hard stops) still missed.** Described at Turn 17 immediately after the
safe-mode discussion, this is a close second to GT-001 and the LLM appears to have
treated it as implementation context rather than a separate requirement.

**GT-005 (minimal feedback design) still missed.** This non-functional design principle
remains consistently difficult — expressed only as a personal preference without any
modal verb or explicit demand phrasing.

**GT-011 (AR overlay) now missed.** v2.0 did not catch this either. The participant
endorses AR at Turn 66 without a strong recommendation, and neither version extracts it.

---

## Comparison: IFA vs Bristol N1 — v3.0

| Metric | IFA (conv_02) v3.0 | Bristol N1 v3.0 |
|---|---|---|
| Ground truth requirements | 41 | 16 |
| Pipeline outputs | 37 | 21 |
| True positives (GTs covered) | 36 | 13 |
| False positives | 6 | 8 |
| False negatives | 5 | 3 |
| **Precision** | **83.8%** | **61.9%** |
| **Recall** | **87.8%** | **81.3%** |
| **F1** | **0.858** | **0.703** |

The IFA dataset continues to produce higher precision because it is a structured
elicitation session — participants articulate requirements explicitly. Bristol N1 is
an interview mixing requirements with hardware descriptions, speculative ideas, and
observed system behaviours. This drives precision down even as recall improves.

---

## Comparison: all Bristol N1 versions

| Metric | v1.0 Naive | v2.0 LLM 70B | **v3.0 LLM 120B** |
|---|---|---|---|
| Model | — | Llama 3.3 70B | **gpt-oss-120b** |
| LLM stages | — | Stage 4 | **Stages 2+3+4** |
| Output count | 31 | 16 | **21** |
| **Precision** | 16.1% | 56.3% | **61.9%** |
| **Recall** | 31.3% | 56.3% | **81.3%** |
| **F1** | 0.213 | 0.563 | **0.703** |
| Usable outputs | 0% | 56% | **86%** |
| Priority accuracy | — | 56% | **54%** |
| False positives | 26 | 7 | **8** |
| False negatives | 11 | 7 | **3** |

---

## Conclusion

On Bristol N1, v3.0 achieves **F1 = 0.703** — a 25% relative improvement over v2.0's
0.563. Recall rises from 56.3% to 81.3%, recovering 4 additional ground-truth
requirements that v2.0 missed. The most notable recoveries are GT-001 (safe mode)
and GT-012 (ghost mode), both of which required understanding endorsement language
that keyword-matching and the smaller 70B model consistently failed to extract.

| Problem | Impact | Root cause |
|---|---|---|
| Hardware/speculative content extracted | 5/8 FPs | Wider semantic extraction net captures discussion about hardware variants, cable routing, simulation — no GT for these |
| GT-002 (soft/hard stops) missed | 1 FN | Adjacent to GT-001 at Turn 17; treated as implementation context |
| GT-005 (minimal feedback design) missed | 1 FN | Design principle stated as personal preference, no modal verbs |
| GT-011 (AR overlay) missed | 1 FN | Endorsement without explicit recommendation — evaluative language pattern not triggered |
| Priority over-correction | 54% accuracy | 120B model over-labels as "preferred" (15/21) vs GT distribution (7 preferred of 12 non-essential) |
