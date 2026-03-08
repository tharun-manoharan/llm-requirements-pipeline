# Pipeline Evaluation v3.3 (Cerebras / gpt-oss-120b — prompt improvements) — N2.txt

## Dataset

- **Source**: Bristol PhD thesis — *The Importance of Trust in Space Teleoperation*
- **Interview**: N2 — industrial robot-arm operator (nuclear reactor maintenance)
- **File**: `datasets/bristol/N2.txt` — 80 turns (Interviewer / Participant)
- **Ground truth**: `datasets/bristol/N2_expected.json` — 13 requirements
- **Output**: `results/bristol/output_N2_v3.3_llm.json`
- **Model**: gpt-oss-120b via Cerebras inference API

## What changed from v3.2

Same prompt and temperature changes as described in `evaluation_v3.3_llm.md` (IFA).

---

## Summary

### Detection accuracy

| Metric | v3.2 (120B + dedup) | **v3.3 (120B + prompt)** |
|---|---|---|
| Ground-truth requirements | 13 | 13 |
| Pipeline output count | 14 | **17** |
| True positives | 8 | **9** |
| GTs covered | 8 | **9** |
| False positives | 6 | **8** |
| False negatives | 5 | **4** |
| **Precision** | 57.1% | **52.9%** |
| **Recall** | 61.5% | **69.2%** |
| **F1** | 0.592 | **0.599** |

### Priority accuracy

| Metric | v3.2 | **v3.3** |
|---|---|---|
| Priority distribution (output) | 2E / 12P / 0O | **5E / 12P / 0O** |
| GT distribution | 4E / 7P / 2O | 4E / 7P / 2O |
| Priority correct (of TPs) | 75% | **67%** |

---

## Classification of each pipeline output

### True Positives (9 outputs → 9 GTs covered)

| REQ | Maps to GT | Type | Priority | Notes |
|---|---|---|---|---|
| REQ-002 | GT-001 | func ✓ | essential ✓ | Emergency stops — response time included |
| REQ-003 | GT-003 | func ✓ | preferred ✓ | Predefined arm moves / teach files |
| REQ-008 | GT-006 | func ✓ | preferred ✓ | Pre-programmed moves broken into stages |
| REQ-010 | GT-007 | func ✓ | preferred ✗ (GT: essential) | Multiple camera feeds — under-prioritised |
| REQ-011 | GT-009 | NF ✗ (GT: NF ✓, but func ✗) | preferred ✓ | Frame rate over resolution — extracted from interviewer turn (Turn 60) |
| REQ-013 | GT-005 | func ✓ | preferred ✓ | Ghost overlay of planned path |
| REQ-014 | GT-010 | func ✓ | preferred ✗ (GT: essential) | No-go zones — under-prioritised |
| REQ-015 | GT-011 | func ✓ | preferred ✓ | Gripper over-force audible alarm — correctly separated from no-go zones |
| REQ-017 | GT-012 | func ✓ | essential ✗ (GT: preferred) | Force-ratio / load compensation — over-prioritised |

### False Positives (8)

| REQ | Reason |
|---|---|
| REQ-001 | "allow users to run pre-planned movement files in a VR robot simulator" (Turn 11) — VR training environment; no GT match; new FP from "endorsed features" pattern extracting training context |
| REQ-004 | "detect out-of-order commands and either reject or auto-correct" (Turn 32, interviewer) — extracted from an interviewer question; no GT match |
| REQ-005 | "be able to perform standard tasks such as aligning and screwing a nut with feedback" (Turn 34, interviewer) — interviewer question paraphrasing a scenario; no GT match |
| REQ-006 | "allow arm to insert bolt regardless of orientation using bolt runner constraints" (Turn 37) — same FP category as v3.2; bolt runner constraint not in GT |
| REQ-007 | "have essentially zero perceptible delay" (Turn 41) — describes existing system's designed-out latency; same FP as v3.2 |
| REQ-009 | "provide high-definition cameras for the operator view" (Turn 55) — HD resolution not in GT; same FP category as v3.2 |
| REQ-012 | "support a large shared display, such as a 75-inch TV, enabling multiple operators to view simultaneously" (Turn 61) — operational setup description; no GT match; same FP as v3.2 REQ-010 |
| REQ-016 | "include built-in illumination LEDs in cameras to improve depth perception via shadows" (Turn 75) — hardware feature; no GT match; same FP as v3.2 |

### False Negatives (4) — GTs missed

| GT | Missed requirement | Why missed |
|---|---|---|
| GT-002 | Auto trip to safe state on excessive force | Turn 30 describes the trip/overforce feature but extraction focused on the e-stop (REQ-002); the force-trip behaviour not separately extracted |
| GT-004 | Pause or stop a pre-programmed move mid-execution | Turn 32 discusses pause/emergency stop during a move; the extraction from Turn 32 produced the interviewer-turn FP (REQ-004) rather than the participant's pause capability |
| GT-008 | Camera auto-follow mode tracking arm position | Turn 58 mentions camera auto-follow; not extracted in this run |
| GT-013 | Force feedback sensitivity independent of force ratio | Expressed as aspiration ("Holy Grail") at Turn 80; extractor captured force ratio (REQ-017) but not the sensitivity-preservation goal |

---

## What v3.3 improved over v3.2

**One new GT covered (GT-011)**: The gripper over-force audible alarm (GT-011, Turn 69)
is now extracted as a separate requirement (REQ-015). In v3.2, it was merged into the
no-go zone requirement (REQ-012). The simplified extraction rule correctly keeps these
as separate outputs since they appear in different turns (Turn 67 for no-go zones,
Turn 69 for gripper alarm).

**F1: 0.592 → 0.599.** Recall improves (61.5% → 69.2%) at a small precision cost.

## Where v3.3 is worse than v3.2

**Precision: 57.1% → 52.9%.** Two additional FPs: REQ-001 (VR simulation training,
extracted due to the "endorsed features" pattern treating training context as a requirement)
and REQ-005 (interviewer question paraphrase). These are new FP categories introduced by
the prompt changes.

**Priority accuracy: 75% → 67%.** REQ-017 (force ratio) is over-prioritised (essential
vs preferred GT). The smaller set of correctly-prioritised TPs accounts for the drop.

---

## Comparison: N1 vs N2 (v3.3)

| Metric | N1 v3.3 | **N2 v3.3** |
|---|---|---|
| GT count | 16 | **13** |
| Output count | 18 | **17** |
| **Precision** | 66.7% | **52.9%** |
| **Recall** | 87.5% | **69.2%** |
| **F1** | 0.757 | **0.599** |
| Priority accuracy | 58% | **67%** |
| False positives | 6 | **8** |
| False negatives | 2 | **4** |

---

## Conclusion

v3.3 achieves **F1 = 0.599** on N2 — a slight improvement over v3.2 (0.592). The key
gain is GT-011 (gripper alarm) now correctly separated from the no-go zone requirement.

The persistent failure modes across both N1 and N2 in v3.3:
- **Interviewer-turn extraction**: REQ-004, REQ-005, REQ-011 all originate from
  interviewer questions, not participant statements. The "questions ending with ?"
  filter is insufficient for declarative interviewer utterances.
- **Operational setup FPs**: REQ-007 (zero latency), REQ-012 (shared display),
  REQ-009 (HD cameras) — descriptions of existing system context treated as
  requirements despite the updated "do not extract" guidance.
- **Endorsed-feature over-extraction**: REQ-001 (VR simulation) extracted because
  the participant says "we had VR simulation and it was useful" — the new "endorsed
  features" pattern introduces this FP category.

| Problem | Impact | Root cause |
|---|---|---|
| VR simulation endorsed FP (REQ-001) | 1 FP | Training context extracted by "endorsed feature" pattern |
| Interviewer-turn extractions (REQ-004, REQ-005) | 2 FPs | Declarative interviewer statements not filtered by "?" rule |
| Bolt runner constraint (REQ-006) | 1 FP | Same as v3.2 |
| Existing-state FPs (REQ-007, REQ-009, REQ-012) | 3 FPs | Operational context not fully filtered despite prompt update |
| LED illumination FP (REQ-016) | 1 FP | Hardware depth-perception feature; no GT match |
| Auto trip on overforce (GT-002) | 1 FN | Turn 30 extraction focused on e-stop, not overforce trip |
| Pause mid-move (GT-004) | 1 FN | Turn 32 produced an interviewer-turn FP instead of participant's pause capability |
| Camera auto-follow (GT-008) | 1 FN | Not extracted in this run |
| Force sensitivity independent of ratio (GT-013) | 1 FN | Aspirational language; only force ratio extracted |
