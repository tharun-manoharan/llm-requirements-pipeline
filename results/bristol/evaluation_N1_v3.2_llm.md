# Pipeline Evaluation v3.2 (Cerebras / gpt-oss-120b + deduplication) — N1.txt

## Dataset

- **Source**: Bristol PhD thesis — *The Importance of Trust in Space Teleoperation*
- **Interview**: N1 — industrial robot-arm operator (nuclear/hazardous environments)
- **File**: `datasets/bristol/N1.txt` — 101 turns (Interviewer / Participant)
- **Ground truth**: `datasets/bristol/N1_expected.json` — 16 requirements
- **Output**: `results/bristol/output_N1_v3.2_llm.json`
- **Model**: gpt-oss-120b via Cerebras inference API

## What changed from v3.1

- New Stage 4b: LLM deduplication call added between rewrite and structure.
- All other pipeline components (extraction prompt, rewrite prompt, model) unchanged.

---

## Summary

### Detection accuracy

| Metric | v1.0 (Naive) | v2.0 (LLM 70B) | v3.1 (LLM 120B) | **v3.2 (120B + dedup)** |
|---|---|---|---|---|
| Ground-truth requirements | 16 | 16 | 16 | 16 |
| Pipeline output count | 31 | 16 | 26 | **18** |
| True positives (distinct outputs → GTs) | 5 | 9 | 14 | **11** |
| GTs covered (incl. merged) | 5 | 9 | 15 | **14** |
| False positives | 26 | 7 | 12 | **7** |
| False negatives | 11 | 7 | 1 | **2** |
| **Precision** | 16.1% | 56.3% | 53.8% | **61.1%** |
| **Recall** | 31.3% | 56.3% | 93.8% | **87.5%** |
| **F1** | 0.213 | 0.563 | 0.684 | **0.719** |

### Priority accuracy

| Metric | v3.1 | **v3.2** |
|---|---|---|
| Priority distribution (output) | 6E / 19P / 1O | **3E / 15P / 0O** |
| GT distribution | 4E / 7P / 1O | 4E / 7P / 1O |
| Priority correct (of TPs) | 71% | **55%** |

---

## What deduplication removed

The dedup LLM call identified 1 semantic duplicate and removed it:

| Removed statement | Duplicate of | Notes |
|---|---|---|
| "The system shall support predefined movements." (Turn 3) | REQ-008 (Turn 43) teach files / pre-programmed paths | Movement presets / teach files are the same concept; dedup correctly removed the less specific Turn 3 reference |

---

## Classification of each pipeline output

### True Positives (11 outputs → 14 GTs covered)

| REQ | Maps to GT | Type | Priority | Notes |
|---|---|---|---|---|
| REQ-002 | GT-001 | func ✓ | essential ✓ | Safe mode on over-speed |
| REQ-003 | GT-002 | func ✓ | essential ✓ | Hard stops in software |
| REQ-004 | GT-003 + GT-004 | func ✓ | essential ✓ / ✗(GT-004: preferred) | Merged: joint display + colour feedback |
| REQ-008 | GT-006 | func ✓ | preferred ✓ | Teach files / waypoint navigation |
| REQ-010 | GT-008 + GT-009 | func ✓ | preferred ✗(GT-008: essential) / ✓(GT-009) | Fixed + variable camera views merged |
| REQ-011 | GT-010 | func ✓ | preferred ✗ (GT: optional) | Adaptive camera zoom — priority over-estimated |
| REQ-012 | GT-011 | func ✓ | preferred ✓ | AR overlay |
| REQ-013 | GT-016 | NF ✓ | preferred ✓ | Prioritise resolution over frame rate |
| REQ-014 | GT-015 | func ✓ | preferred ✗ (GT: essential) | Force feedback — under-prioritised |
| REQ-015 | GT-012 | func ✓ | preferred ✓ | Ghost mode / predicted end position |
| REQ-016 | GT-013 + GT-014 | func ✓ | preferred ✗(GT-013: essential) / ✓(GT-014) | No-go zones + audible alarm merged |

### False Positives (7)

| REQ | Reason |
|---|---|
| REQ-001 | Variant hardware configurations (extended arm, waterproofing) — describes physical hardware variants, not software requirements; same FP as v3.1 REQ-002 |
| REQ-005 | 50% time allowance extension — extracted from an interviewer turn (Turn 34); describes an existing scheduling rule, not a system feature |
| REQ-006 | Cable stops/guides — hardware constraint outside GT scope; same FP category as v3.1 REQ-007 |
| REQ-007 | Model entire scene in simulation — describes existing simulation capability positively; no GT match; same FP as v3.1 REQ-008 |
| REQ-009 | Autonomous approach then hand over control — GT-006 already covered by REQ-008; adds handover concept not in GT; same FP as v3.1 REQ-011 |
| REQ-017 | Computer vision material recognition — speculative discussion ("just started investigating") with no GT; same FP as v3.1 REQ-024 |
| REQ-018 | Gripper overload detection and drop feedback — describes observed hardware behaviour at Turn 95; no GT match; same FP as v3.1 REQ-026 |

### False Negatives (2) — GTs missed

| GT | Missed requirement | Why missed |
|---|---|---|
| GT-005 | Minimal, non-intrusive feedback design | Expressed as personal preference at Turn 23 with no modal verb; consistently missed across all versions |
| GT-007 | One-button recall to home / tool-storage positions | Turn 45 not extracted in this run — extraction variability; was covered in v3.1 (REQ-010) |

---

## Analysis

### What v3.2 improved over v3.1

**Precision: 53.8% → 61.1%.** The dedup removed 1 genuine FP ("predefined movements"
duplicate of teach files). The extraction stage also produced fewer candidates
overall (20 extracted vs ~40 in v3.1), which further reduced noise from
hardware/operational FPs. The 7 remaining FPs are the same structural categories
as v3.1: hardware descriptions, interviewer-turn extractions, and speculative content.

**F1: 0.684 → 0.719.** The lower output count yields a better precision-recall
balance for this run, even though recall dropped.

### Where v3.2 is worse than v3.1

**Recall: 93.8% → 87.5%.** Only 14 GTs covered vs 15 in v3.1. GT-007
(one-button home recall, Turn 45) was not extracted in this run — extraction
variability, not a dedup issue. The dedup kept all unique GT-matching outputs.

**Priority accuracy: 71% → 55%.** The smaller extraction set surfaces different
turns — REQ-010 merges fixed and variable camera (GT-008 essential + GT-009
preferred) and inherits the preferred label for the merged pair, which under-
prioritises GT-008. REQ-016 merges no-go zones (GT-013 essential) with audible
alarm (GT-014 preferred) and also uses preferred. These merged requirements
inherit the lower priority when they span an essential and a preferred GT.

### Extraction variability note

v3.1 extracted ~40 raw candidates and had 26 outputs. v3.2 extracted 20 raw
candidates and produced 18 outputs. The LLM extraction (Stage 2+3) uses
temperature=0.1 and is not fully deterministic across API calls. The reduction
in candidates accounts for both the recall drop and most of the false-positive
reduction — fewer candidates means less speculative content but also fewer
genuine requirements extracted.

---

## Comparison: all Bristol N1 versions

| Metric | v1.0 Naive | v2.0 LLM 70B | v3.1 LLM 120B | **v3.2 LLM 120B** |
|---|---|---|---|---|
| Model | — | Llama 3.3 70B | gpt-oss-120b | **gpt-oss-120b** |
| LLM stages | — | Stage 4 | Stages 2+3+4 | **Stages 2+3+4+4b** |
| Output count | 31 | 16 | 26 | **18** |
| **Precision** | 16.1% | 56.3% | 53.8% | **61.1%** |
| **Recall** | 31.3% | 56.3% | 93.8% | **87.5%** |
| **F1** | 0.213 | 0.563 | 0.684 | **0.719** |
| Usable outputs | 0% | 56% | 88% | **100%** |
| Priority accuracy | — | 54% | 71% | **55%** |
| False positives | 26 | 7 | 12 | **7** |
| False negatives | 11 | 7 | 1 | **2** |
| GTs covered | 5 | 9 | 15 | **14** |

---

## Conclusion

v3.2 achieves **F1 = 0.719** and **precision 61.1%** — both the best across all
Bristol N1 versions. Recall is 87.5%, which is lower than v3.1's 93.8% peak due
to extraction variability (GT-007 missed this run). GT-005 (non-intrusive
feedback design) remains the only GT consistently missed across all versions.

The deduplication stage correctly identified and removed 1 FP duplicate in this
run. The larger precision improvement (53.8% → 61.1%) is primarily a result of
the extraction producing a tighter, less noisy candidate set in this run.

| Problem | Impact | Root cause |
|---|---|---|
| Hardware / operational FPs | 4/7 FPs (REQ-001, 006, 007, 018) | Extraction captures arm variants, cable routing, simulation, overload behaviour |
| Speculative content | 1/7 FP (REQ-017) | Material-recognition investigation despite uncertainty language |
| Adjacent-turn handover FP | 1/7 FP (REQ-009) | GT-006 already covered; handover extension not in GT |
| Interviewer-turn extraction | 1/7 FP (REQ-005) | 50% time buffer stated by interviewer, not participant |
| GT-005 missed | 1 FN | Design principle stated as personal preference with no modal verb |
| GT-007 missed this run | 1 FN | Extraction variability; covered in v3.1 |
| Force feedback under-prioritised | 1 TP wrong priority | Essential requirement stated factually; model assigns preferred |
| No-go zones under-prioritised | 1 TP wrong priority (merged) | Merged with preferred GT-014; essential GT-013 gets preferred label |
