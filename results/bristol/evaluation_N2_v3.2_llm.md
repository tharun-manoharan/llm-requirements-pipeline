# Pipeline Evaluation v3.2 (Cerebras / gpt-oss-120b + deduplication) — N2.txt

## Dataset

- **Source**: Bristol PhD thesis — *The Importance of Trust in Space Teleoperation*
- **Interview**: N2 — industrial robot-arm operator (nuclear reactor maintenance)
- **File**: `datasets/bristol/N2.txt` — 80 turns (Interviewer / Participant)
- **Ground truth**: `datasets/bristol/N2_expected.json` — 13 requirements
- **Output**: `results/bristol/output_N2_v3.2_llm.json`
- **Model**: gpt-oss-120b via Cerebras inference API

## Notes on transcript conversion

N2 was converted from the `Anonymised Transcripts.xlsx` workbook (N2 sheet) using the same
Speaker/Transcript column structure as N1. The N2 sheet stores each speaker turn as individual
rows (rather than continuation rows), so consecutive same-speaker rows were merged. This
produced 80 turns from 306 raw rows.

---

## Summary

### Detection accuracy

| Metric | **v3.2 (120B + dedup)** |
|---|---|
| Ground-truth requirements | 13 |
| Pipeline output count | **14** |
| True positives (distinct outputs → GTs) | **8** |
| GTs covered | **8** |
| False positives | **6** |
| False negatives | **5** |
| **Precision** | **57.1%** |
| **Recall** | **61.5%** |
| **F1** | **0.592** |

### Priority accuracy

| Metric | **v3.2** |
|---|---|
| Priority distribution (output) | 2E / 12P / 0O |
| GT distribution | 4E / 7P / 2O |
| Priority correct (of TPs) | **75%** |

---

## What deduplication removed

The dedup LLM call identified 1 semantic duplicate and removed it:

| Removed statement | Duplicate of | Notes |
|---|---|---|
| "The system shall provide real-time visual feedback of the arm's current position relative to defined boundaries..." (Turn ~) | REQ-012 (no-go zones) | Overlap with the no-go zone visual warning; correctly removed |

---

## Classification of each pipeline output

### True Positives (8 outputs → 8 GTs covered)

| REQ | Maps to GT | Type | Priority | Notes |
|---|---|---|---|---|
| REQ-001 | GT-001 | NF ✗ (GT: func) | essential ✓ | E-stops — type mismatch (pipeline tagged as non-functional); content correct |
| REQ-002 | GT-003 | func ✓ | preferred ✓ | Teach file / predefined arm moves |
| REQ-005 | GT-006 | func ✓ | preferred ✓ | Incremental stages / routing path for large moves |
| REQ-008 | GT-007 | func ✓ | preferred ✗ (GT: essential) | Multiple camera streams — priority under-estimated |
| REQ-009 | GT-009 | NF ✓ | preferred ✓ | Frame rate over resolution |
| REQ-011 | GT-005 | func ✓ | preferred ✓ | Ghost overlay / planned path preview |
| REQ-012 | GT-010 | func ✓ | preferred ✗ (GT: essential) | No-go zones — priority under-estimated |
| REQ-014 | GT-012 | func ✓ | preferred ✓ | Force ratio / load compensation |

### False Positives (6)

| REQ | Reason |
|---|---|
| REQ-003 | Bolt runner cross-threading constraints — extracted from Turn 35 (interviewer question), reflects a general tooling concern rather than a stated system requirement; no GT match |
| REQ-004 | Zero-perceptible latency — describes the existing system's design intent ("it's all designed out"), not a new system requirement; no GT match |
| REQ-006 | Simulation and testing for design change validation — describes the engineering process at Turn 53, not a live teleoperation feature; no GT match |
| REQ-007 | High-definition camera feeds / resolution — not captured in GT (GT-007 is about number/type of views, not resolution quality) |
| REQ-010 | Simultaneous viewing by up to five operators — describes existing shift setup at Turn 64, not a stated requirement; no GT match |
| REQ-013 | LED end-effector illumination for shadow-based depth perception — describes an existing feature used for depth cues (Turn 75); no GT match |

### False Negatives (5) — GTs missed

| GT | Missed requirement | Why missed |
|---|---|---|
| GT-002 | Auto trip to safe state on excessive force | Turn 30 describes the trip feature but REQ-001 focused on the e-stop response time rather than the overforce trip; distinct safety behaviour not extracted separately |
| GT-004 | Pause or stop a pre-programmed arm move mid-execution | Turn 32 mentions emergency stop and pause capability; the extractor merged this with the teach file move feature (REQ-002) and did not extract it as a separate requirement |
| GT-008 | Camera auto-follow mode tracking arm position | Mentioned at Turn 58; extractor captured the bank of cameras (REQ-008) but not the auto-pan/follow behaviour |
| GT-011 | Audible alarm on gripper over-force | Turn 70 explicitly describes the buzzer; the extractor merged this into the no-go zone requirement (REQ-012) rather than extracting a separate gripper monitoring requirement |
| GT-013 | Force feedback sensitivity independent of force ratio | Expressed as an aspiration ("Holy Grail") at Turn 80; extractor captured force ratio (REQ-014) but not the sensitivity-preservation goal |

---

## Analysis

### What went well

**Precision 57.1%** is below N1 v3.2 (61.1%) but reasonable for a first run on a new transcript.
The 8 TPs cover the core safety and operation requirements: e-stops, teach file moves, ghost
preview, frame rate preference, no-go zones, force ratio compensation.

**Priority accuracy 75%** (6/8 correct) is relatively high. The two misses are GT-007 (multiple
cameras, essential) and GT-010 (no-go zones, essential) — both tagged as preferred by the pipeline.

**Ghost mode** (GT-005) and **frame rate priority** (GT-009) are correctly extracted and labelled,
consistent with N1 performance on the same requirement types.

### Root causes of false positives

All 6 FPs fall into the same structural categories seen in N1:
- **Process/maintenance content**: REQ-003 (bolt constraints from Turn 35 question), REQ-006 (design validation process)
- **Existing-state descriptions treated as requirements**: REQ-004 (latency already designed out), REQ-010 (5-person shift setup)
- **Hardware features outside GT scope**: REQ-007 (HD resolution), REQ-013 (LED illumination)

The extraction prompt is not distinguishing between "we already have this" (existing state) and
"the system shall" (stated requirement). This is a consistent failure mode across N1 and N2.

### Root causes of false negatives

- **Merged extraction**: GT-004 (pause/abort mid-move) and GT-011 (gripper alarm) were subsumed
  into REQ-002 and REQ-012 respectively. The extractor found the related concept but did not
  separate the distinct sub-requirements.
- **Aspirational language**: GT-013 (force sensitivity at high force ratio) is framed as
  "that's the Holy Grail" — the same pattern as GT-005 in N1 where design principles stated
  as personal preferences are missed.
- **Behaviour embedded in longer turn**: GT-002 (overforce trip) and GT-008 (camera auto-follow)
  were present in the transcript but buried within turns that yielded only one extracted
  requirement each.

---

## Comparison: N1 vs N2 (v3.2)

| Metric | N1 v3.2 | **N2 v3.2** |
|---|---|---|
| Model | gpt-oss-120b | **gpt-oss-120b** |
| GT count | 16 | **13** |
| Output count | 18 | **14** |
| **Precision** | 61.1% | **57.1%** |
| **Recall** | 87.5% | **61.5%** |
| **F1** | 0.719 | **0.592** |
| Priority accuracy | 55% | **75%** |
| False positives | 7 | **6** |
| False negatives | 2 | **5** |
| GTs covered | 14 | **8** |

---

## Conclusion

v3.2 achieves **F1 = 0.592** on N2 — lower than N1's 0.719. The gap is driven mainly by recall
(61.5% vs 87.5%): the extraction stage missed requirements that were:
1. Merged into a single extracted sentence with a related (but distinct) requirement
2. Expressed as aspirational or embedded in operator commentary rather than stated demands

Precision (57.1% vs 61.1%) is broadly comparable. The same FP categories appear: existing-state
descriptions, process content, and hardware features outside GT scope.

| Problem | Impact | Root cause |
|---|---|---|
| Merged requirements (GT-004, GT-011) | 2 FNs | Extractor collapses adjacent sub-requirements into one candidate |
| Aspirational language (GT-013) | 1 FN | "Holy Grail" framing → not identified as a requirement |
| Embedded in long turn (GT-002, GT-008) | 2 FNs | Single extraction per turn misses secondary behaviours |
| Existing-state FPs (REQ-004, REQ-010) | 2 FPs | Extractor does not distinguish current state from future requirement |
| Process/maintenance FPs (REQ-003, REQ-006) | 2 FPs | Extraction includes engineering process content |
| Hardware-feature FPs (REQ-007, REQ-013) | 2 FPs | Resolution and LED illumination outside software GT scope |
| Essential priority missed (GT-007, GT-010) | 2 TPs wrong priority | Safety-critical features tagged as preferred |
