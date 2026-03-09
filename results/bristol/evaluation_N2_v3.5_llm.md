# Pipeline Evaluation v3.5 (Cerebras / gpt-oss-120b — refined implicit NF extraction) — N2.txt

## Dataset

- **Source**: Bristol PhD thesis — *The Importance of Trust in Space Teleoperation*
- **Interview**: N2 — industrial robot-arm operator (nuclear reactor maintenance)
- **File**: `datasets/bristol/N2.txt` — 80 turns (Interviewer / Participant)
- **Ground truth**: `datasets/bristol/N2_expected.json` — 13 requirements
- **Output**: `results/bristol/output_N2_v3.5_llm.json`
- **Model**: gpt-oss-120b via Cerebras inference API

## What changed from v3.4

Same prompt refinements as described in `results/ifa/evaluation_v3.5_llm.md`. For N2 the refinements had mixed effects: the camera-view extraction improved (GT-007 now covered) but the extraction from Turn 30 (emergency stop positions + force-trip) shifted focus and lost GT-001 and GT-011.

---

## Summary

### Detection accuracy

| Metric | v3.4 (120B + interviewer filter) | **v3.5 (120B + refined NF extraction)** |
|---|---|---|
| Ground-truth requirements | 13 | 13 |
| Pipeline output count | 15 | **12** |
| True positives | 8 | **7** |
| GTs covered | 8 | **7** |
| False positives | 7 | **5** |
| False negatives | 5 | **6** |
| **Precision** | 53.3% | **58.3%** |
| **Recall** | 61.5% | **53.8%** |
| **F1** | 0.571 | **0.560** |

### Priority accuracy

| Metric | v3.4 | **v3.5** |
|---|---|---|
| Priority distribution (output) | 2E / 13P / 0O | **0E / 12P / 0O** |
| GT distribution | 4E / 7P / 2O | 4E / 7P / 2O |
| Priority correct (of TPs) | 75% | **71%** (5/7) |

---

## Classification of each pipeline output

### True Positives (7 outputs → 7 GTs covered)

| REQ | Maps to GT | Type | Priority | Notes |
|---|---|---|---|---|
| REQ-001 | GT-007 | func ✓ | preferred ✗ (GT: essential) | Front-facing overhead camera + foldable close-up camera — two simultaneous views — under-prioritised |
| REQ-003 | GT-003 | func ✓ | preferred ✓ | Predefined arm movements stored in files, button-triggered |
| REQ-007 | GT-006 | func ✓ | preferred ✓ | Pre-programmed moves broken into stages/waypoints for operator monitoring |
| REQ-008 | GT-009 | NF ✓ | preferred ✓ | High refresh rates — frame rate priority over resolution |
| REQ-009 | GT-005 | func ✓ | preferred ✓ | Ghost mode indicating predicted final position |
| REQ-010 | GT-010 | func ✓ | preferred ✗ (GT: essential) | Virtual walls blocking movement into restricted areas — under-prioritised |
| REQ-012 | GT-012 | func ✓ | preferred ✓ | Force-ratio settings to control apparent weight of heavy loads |

### False Positives (5)

| REQ | Reason |
|---|---|
| REQ-002 | "respond to emergency stop button press within one tenth of a second" (Turn 29) — timing specification for emergency stop; no GT covers the response-time detail (GT-001 is about multiple hardware e-stop positions, not timing); same FP category as v3.4 |
| REQ-004 | "provide assistance during a tricky manoeuvre, such as placing an object between a series of tiles" (Turn 33) — vague capability request; no GT match |
| REQ-005 | "provide a Bolt Runner constraint feature that allows tightening a bolt regardless of orientation" (Turn 35) — tool-specific constraint; same FP as v3.4 |
| REQ-006 | "detect a delay of at least one millisecond and generate a notification indicating that operation should be paused for one minute" (Turn 41) — describes existing system latency design, not a new requirement; same FP as v3.3/v3.4 |
| REQ-011 | "include a camera with an integrated light to create shadows for 3D spatial perception" (Turn 75) — existing hardware feature description; same FP as v3.4 |

### False Negatives (6) — GTs missed

| GT | Missed requirement | Why missed |
|---|---|---|
| GT-001 | Multiple hardware emergency stops accessible at several positions around the workstation | Turn 30 was previously extracted as a TP (v3.4 REQ-003). In v3.5, the extraction from Turn 29/30 shifted focus to the timing detail (REQ-002, FP) and the multiple-positions aspect of GT-001 was not separately extracted |
| GT-002 | Automatically trip to a safe state when the arm exerts excessive force against an obstacle | Turn 30 covers this; in v3.5 neither this nor GT-001 were extracted as TPs from Turn 30 |
| GT-004 | Allow the operator to pause or immediately stop a pre-programmed arm move while executing | Turn 32 discusses pause capability; REQ-004 (Turn 33) is extracted instead as vague "assistance" — the specific pause/stop capability is missed |
| GT-008 | Camera auto-follow mode that pans and tracks the arm's position | Turn 58 content not extracted; same miss as all prior versions |
| GT-011 | Audible alarm when gripper force exceeds a configured threshold | Turn 70 content not extracted in v3.5; was covered in v3.4 (REQ-013) |
| GT-013 | Maintain haptic force feedback sensitivity independent of the force-ratio setting | Turn 80 (aspirational "Holy Grail" language); aspirational-language rule did not help; REQ-012 captures force limits (GT-012) instead — same miss as v3.3/v3.4 |

---

## What v3.5 changed vs v3.4

**GT-007 newly covered**: REQ-001 ("front-facing camera that looks straight down...and a foldable camera arm...that supplies a 3D view", Turn 5) correctly maps to GT-007 (at least two simultaneous camera views). This was missed in all prior versions due to the camera discussion spanning multiple turns (6, 56, 58); the Turn 5 participant statement was the clearest extraction signal and v3.5 captures it.

**GT-001 and GT-011 lost**: v3.4 covered GT-001 (emergency stop positions via REQ-003) and GT-011 (gripper alarm via REQ-013). In v3.5, the Turn 29/30 extraction produced REQ-002 (e-stop timing, FP) rather than the multiple-positions content of GT-001. Turn 70 (gripper alarm) was not extracted at all.

**FP count reduced**: 7 FPs in v3.4 → 5 FPs in v3.5. The two diagnostic-integration FP (v3.4 REQ-001, Turn 1) and one additional FP were removed. Three FPs from v3.4 (Bolt Runner, perceptible delay, LED camera) persist.

**Net change**: +1 GT gained (GT-007), −2 GTs lost (GT-001, GT-011). F1: 0.571 → 0.560.

---

## Comparison: v3.2 vs v3.3 vs v3.4 vs v3.5 (N2)

| Metric | v3.2 | v3.3 | v3.4 | **v3.5** |
|---|---|---|---|---|
| Output count | 14 | 17 | 15 | **12** |
| **Precision** | 57.1% | 52.9% | 53.3% | **58.3%** |
| **Recall** | 61.5% | 69.2% | 61.5% | **53.8%** |
| **F1** | 0.592 | 0.599 | 0.571 | **0.560** |
| Priority accuracy | 75% | 67% | 75% | **71%** |
| False positives | 6 | 8 | 7 | **5** |
| False negatives | 5 | 4 | 5 | **6** |

**v3.3 remains best for N2 (F1=0.599).** v3.5 continues the N2 regression trend.

---

## Conclusion

v3.5 achieves **F1 = 0.560** on N2 — a slight regression from v3.4 (0.571). Precision improves (fewer FPs) but recall drops as two v3.4 TPs are lost.

The N2 regression across v3.3→v3.5 reflects a consistent pattern: prompt changes that help other datasets (by reducing over-extraction or improving NF constraint identification) shift the extraction focus in N2 turns that were previously yielding correct TPs. The Turn 29/30 content (emergency stops) is the most fragile: it contains multiple distinct requirements (GT-001 multiple positions, GT-002 force-trip, timing) and the model's attention moves between them across versions.

| Problem | Impact | Status in v3.5 |
|---|---|---|
| Emergency stop multiple-positions FN (GT-001) | 1 FN | Newly missed (was covered in v3.4) |
| Force-trip FN (GT-002) | 1 FN | Persists |
| VR simulator FP (v3.3) | 1 FP | Fixed ✓ (removed in v3.4, absent in v3.5) |
| Diagnostic integration FP (v3.4 REQ-001) | 1 FP | Fixed ✓ |
| E-stop timing FP (REQ-002) | 1 FP | Persists |
| Gripper alarm FN (GT-011) | 1 FN | Newly missed (was covered in v3.4) |
| Bolt runner FP (REQ-005) | 1 FP | Persists |
| Perceptible delay FP (REQ-006) | 1 FP | Persists |
| LED/3D camera FP (REQ-011) | 1 FP | Persists |
| Camera auto-follow FN (GT-008) | 1 FN | Persists |
| Aspirational sensitivity FN (GT-013) | 1 FN | Persists |
