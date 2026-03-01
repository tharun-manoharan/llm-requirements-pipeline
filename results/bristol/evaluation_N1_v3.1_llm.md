# Pipeline Evaluation v3.1 (Cerebras / gpt-oss-120b + priority fix) — N1.txt

## Dataset

- **Source**: Bristol PhD thesis — *The Importance of Trust in Space Teleoperation*
- **Interview**: N1 — industrial robot-arm operator (nuclear/hazardous environments)
- **File**: `datasets/bristol/N1.txt` — 101 turns (Interviewer / Participant)
- **Ground truth**: `datasets/bristol/N1_expected.json` — 16 requirements
- **Output**: `results/bristol/output_N1_v3.1_llm.json`
- **Model**: gpt-oss-120b via Cerebras inference API

## What changed from v3.0

- Rewrite prompt updated with three few-shot examples (one per priority level).
- "Do NOT default to preferred" instruction replaced with a calibrated note that
  most conversational requirements are preferred, reserving essential for strong
  demand language.

---

## Summary

### Detection accuracy

| Metric | v1.0 (Naive) | v2.0 (LLM 70B) | v3.0 (LLM 120B) | **v3.1 (120B + priority fix)** |
|---|---|---|---|---|
| Ground-truth requirements | 16 | 16 | 16 | 16 |
| Pipeline output count | 31 | 16 | 21 | **26** |
| True positives (distinct outputs → GTs) | 5 | 9 | 12 | **14** |
| GTs covered (incl. merged) | 5 | 9 | 13 | **15** |
| False positives | 26 | 7 | 8 | **12** |
| False negatives | 11 | 7 | 3 | **1** |
| **Precision** | 16.1% | 56.3% | 57.1% | **53.8%** |
| **Recall** | 31.3% | 56.3% | 81.3% | **93.8%** |
| **F1** | 0.213 | 0.563 | 0.703 | **0.684** |

### Priority accuracy

| Metric | v2.0 | v3.0 | **v3.1** |
|---|---|---|---|
| Priority distribution (output) | 13E / 2P / 0O | 5E / 15P / 0O | **6E / 19P / 1O** |
| GT distribution | 4E / 7P / 1O | 4E / 7P / 1O | 4E / 7P / 1O |
| Priority correct (of TPs) | 56% | 54% | **71%** |

---

## Classification of each pipeline output

### True Positives (14 outputs → 15 GTs covered)

| REQ | Maps to GT | Type | Priority | Notes |
|---|---|---|---|---|
| REQ-003 | GT-001 | func ✓ | essential ✓ | Safe mode on over-speed |
| REQ-004 | GT-002 | func ✓ | essential ✓ | **New catch** — hard stops in software and hardware; missed in all previous versions |
| REQ-005 | GT-003 + GT-004 | func ✓ | essential ✓ / ✗(GT-004: preferred) | Merged: joint display + colour feedback |
| REQ-009 | GT-006 | func ✓ | preferred ✓ | Teach files / waypoint navigation |
| REQ-010 | GT-007 | func ✓ | preferred ✓ | Home button to known state |
| REQ-013 | GT-009 | func ✓ | optional ✗ (GT: preferred) | Variable camera viewpoint — priority under-estimated |
| REQ-014 | GT-008 | func ✓ | essential ✓ | Fixed camera view |
| REQ-015 | GT-010 | func ✓ | preferred ✗ (GT: optional) | Adaptive camera zoom — priority over-estimated |
| REQ-016 | GT-011 | func ✓ | preferred ✓ | **New catch** — AR overlay; missed in all previous versions |
| REQ-018 | GT-016 | NF ✓ | preferred ✓ | Prioritise resolution over frame rate |
| REQ-019 | GT-015 | func ✓ | preferred ✗ (GT: essential) | Force feedback — essential in GT, model assigns preferred |
| REQ-020 | GT-012 | func ✓ | preferred ✓ | Ghost mode / predicted end position |
| REQ-022 | GT-013 | func ✓ | preferred ✗ (GT: essential) | No-go zones — essential in GT, model assigns preferred |
| REQ-023 | GT-014 | func ✓ | preferred ✓ | Audible alarm near no-go zone |

### False Positives (12)

| REQ | Reason |
|---|---|
| REQ-001 | Predefined movements for muscle memory — rehabilitation arm context (Turn 3); not part of the main system under specification |
| REQ-002 | Variant hardware configurations (extended arm, waterproofing) — describes physical variants, not software requirements |
| REQ-006 | 50% time allowance extension — describes an existing scheduling rule, not a system feature |
| REQ-007 | Cable stops/guides — hardware constraint outside GT scope |
| REQ-008 | Model entire scene in simulation — describes existing simulation capability positively; no GT match |
| REQ-011 | Autonomous approach then hand over control — related to GT-006 (waypoint navigation) but GT-006 already covered by REQ-009; adds handover concept not in GT |
| REQ-012 | Haptic feedback when motion incorrect — GT-015 (force feedback) already covered by REQ-019; duplicate extraction from adjacent turns |
| REQ-017 | "Highest possible resolution at all times" — GT-016 (prioritise resolution over frame rate) already covered by REQ-018; REQ-017 over-states the requirement |
| REQ-021 | Ghost mode trajectory display — GT-012 already covered by REQ-020; REQ-021 adds detail about pre-planned movement path not stated in GT |
| REQ-024 | Computer vision material recognition — speculative discussion ("just started investigating") with no GT; same FP as v3.0 |
| REQ-025 | Material-recognition-based no-go zones — extension of speculative content in REQ-024; no GT |
| REQ-026 | Overload detection and grip release — describes observed hardware behaviour at Turn 95; no GT match |

### False Negatives (1) — GTs missed

| GT | Missed requirement | Why missed |
|---|---|---|
| GT-005 | Minimal, non-intrusive feedback design | Expressed at Turn 23 as a personal preference ("I'd want information but not overload") with no modal verb or explicit demand. Consistently missed across all versions — requires a specific pattern for design principle requirements. |

---

## Analysis

### What v3.1 improved over v3.0

**GT-002 (soft/hard stops) now caught.** REQ-004 captures "enforce hard stops in
software and ensure hardware also enforces hard stops." This was missed across all
previous versions because the participant described it factually at Turn 17 immediately
after the safe-mode discussion. The larger extraction net now surfaces it as a separate
requirement.

**GT-011 (AR overlay) now caught.** REQ-016 captures the AR guidance overlay from
Turn 66. The participant endorses it ("that kind of overlay really helps") and the
120B model correctly reads this as a requirement endorsement.

**Recall: 81.3% → 93.8%.** Only 1 GT is now missed (GT-005). This is the best
recall on the Bristol dataset across all versions by a large margin.

**Priority accuracy: 54% → 71%.** The few-shot prompt fix restores discrimination
across all three priority levels. The model now produces 6E/19P/1O vs the GT
distribution of 4E/7P/1O — a much closer fit than the all-essential output of
earlier versions.

### Where v3.1 still fails

**False positives increased (8 → 12).** The extraction found 26 candidates vs 21
in v3.0. The additional candidates include:
- REQ-001 (rehabilitation arm context) — extracted from a brief early aside
- REQ-008 (scene simulation) — positive description of existing capability
- REQ-017 (max resolution) and REQ-021 (ghost mode trajectory) — duplicate
  extractions of GT-016 and GT-012 already covered

The Bristol interview produces more FPs than the IFA session because the format
mixes requirements with hardware descriptions, operational anecdotes, and speculative
discussions. The precision (53.8%) reflects this structural challenge.

**GT-005 (minimal non-intrusive feedback) still missed.** This design principle
appears only as a first-person preference statement at Turn 23 with no modal verb.
It has been missed in every version. A targeted pattern — "I'd want X but not Y",
"too much X is bad" — would be needed to capture this class of requirement.

**Priority for force feedback and no-go zones is wrong.** GT-015 (force feedback)
and GT-013 (no-go zones) are both essential in the GT but labelled preferred. The
participant discusses these in a matter-of-fact way without repeating or emphasising
them, which the model interprets as lower priority.

---

## Comparison: all Bristol N1 versions

| Metric | v1.0 Naive | v2.0 LLM 70B | v3.0 LLM 120B | **v3.1 LLM 120B** |
|---|---|---|---|---|
| Model | — | Llama 3.3 70B | gpt-oss-120b | **gpt-oss-120b** |
| LLM stages | — | Stage 4 | Stages 2+3+4 | **Stages 2+3+4** |
| Output count | 31 | 16 | 21 | **26** |
| **Precision** | 16.1% | 56.3% | 57.1% | **53.8%** |
| **Recall** | 31.3% | 56.3% | 81.3% | **93.8%** |
| **F1** | 0.213 | 0.563 | 0.703 | **0.684** |
| Usable outputs | 0% | 56% | 86% | **88%** |
| Priority accuracy | — | 56% | 54% | **71%** |
| False positives | 26 | 7 | 8 | **12** |
| False negatives | 11 | 7 | 3 | **1** |
| GTs covered | 5 | 9 | 13 | **15** |

---

## Conclusion

v3.1 achieves **recall of 93.8%** — the best across all Bristol N1 versions — while
catching GT-002 (hard stops) and GT-011 (AR overlay) for the first time. Only GT-005
remains unrecovered across all versions. Priority accuracy improves to 71% (from 54%)
with all three priority levels now in use.

The F1 of **0.684** is marginally below v3.0's 0.703 due to higher false positives
(12 vs 8) — the wider extraction net recovers more real requirements but also pulls
in more hardware descriptions and speculative content. This precision-recall trade-off
is inherent to the interview format.

| Problem | Impact | Root cause |
|---|---|---|
| Hardware / operational FPs | 7/12 FPs | Wider extraction net catches arm variants, cable routing, simulation detail, overload behaviour |
| Speculative content | 2/12 FPs (REQ-024, 025) | Material-recognition investigation extracted despite uncertainty language |
| Duplicate extractions | 3/12 FPs (REQ-012, 017, 021) | Same GT covered by multiple candidates from adjacent turns |
| GT-005 missed | 1 FN | Design principle stated as personal preference with no modal verb; no pattern to extract it |
| Force feedback / no-go zones under-prioritised | 2 TPs wrong priority | Essential requirements stated factually without emphasis |
