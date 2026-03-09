# Pipeline Evaluation v3.4 (Cerebras / gpt-oss-120b — interviewer filter + aspirational) — N2.txt

## Dataset

- **Source**: Bristol PhD thesis — *The Importance of Trust in Space Teleoperation*
- **Interview**: N2 — industrial robot-arm operator (nuclear reactor maintenance)
- **File**: `datasets/bristol/N2.txt` — 80 turns (Interviewer / Participant)
- **Ground truth**: `datasets/bristol/N2_expected.json` — 13 requirements
- **Output**: `results/bristol/output_N2_v3.4_llm.json`
- **Model**: gpt-oss-120b via Cerebras inference API

## What changed from v3.3

Same three changes as described in `results/ifa/evaluation_v3.4_llm.md`: interviewer-turn filter, narrowed endorsed-feature rule, aspirational-language pattern.

---

## Summary

### Detection accuracy

| Metric | v3.3 (120B + prompt) | **v3.4 (120B + interviewer filter)** |
|---|---|---|
| Ground-truth requirements | 13 | 13 |
| Pipeline output count | 17 | **15** |
| True positives | 9 | **8** |
| GTs covered | 9 | **8** |
| False positives | 8 | **7** |
| False negatives | 4 | **5** |
| **Precision** | 52.9% | **53.3%** |
| **Recall** | 69.2% | **61.5%** |
| **F1** | 0.599 | **0.571** |

### Priority accuracy

| Metric | v3.3 | **v3.4** |
|---|---|---|
| Priority distribution (output) | 5E / 12P / 0O | **2E / 13P / 0O** |
| GT distribution | 4E / 7P / 2O | 4E / 7P / 2O |
| Priority correct (of TPs) | 67% | **75%** (6/8) |

---

## Classification of each pipeline output

### True Positives (8 outputs → 8 GTs covered)

| REQ | Maps to GT | Type | Priority | Notes |
|---|---|---|---|---|
| REQ-003 | GT-001 | func ✓ | essential ✓ | Emergency stop controls at multiple positions |
| REQ-005 | GT-003 | func ✓ | preferred ✓ | Predefined arm moves from teach files |
| REQ-009 | GT-006 | func ✓ | preferred ✓ | Pre-programmed moves broken into stages with waypoints |
| REQ-010 | GT-009 | NF ✓ | preferred ✓ | Frame rate over resolution |
| REQ-011 | GT-005 | func ✓ | preferred ✓ | Ghost mode displaying planned path preview |
| REQ-012 | GT-010 | func ✓ | preferred ✗ (GT: essential) | No-go zones with warnings — under-prioritised |
| REQ-013 | GT-011 | func ✓ | preferred ✓ | Buzzer alert when gripper over-gripping |
| REQ-015 | GT-012 | func ✓ | essential ✗ (GT: preferred) | Force limits based on weight — over-prioritised |

### False Positives (7)

| REQ | Reason |
|---|---|
| REQ-001 | "allow integration of new diagnostic capabilities into existing technology" (Turn 1) — new FP; generic statement about technology upgrade, no GT match |
| REQ-002 | "use a VR robot simulator with pre-planned movement files to run simulations" (Turn 11) — VR training context persists despite the narrowed endorsed-feature rule; VR simulator is used for operator training, not a live system feature |
| REQ-004 | "stop the system within a tenth of a second when emergency stop is activated" (Turn 29) — response time spec for the e-stop; no GT covers this timing detail |
| REQ-006 | "detect out-of-sequence commands and reject or auto-execute next move" (Turn 33) — extracted from a participant turn describing a system behaviour, but no GT match; same FP category as v3.3 REQ-004 (interviewer-origin) but now sourced from a participant confirmation turn |
| REQ-007 | "include Bolt Runner constraints to prevent cross-threading" (Turn 35) — tool-specific constraint; same FP as v3.3 |
| REQ-008 | "flag and avoid any perceptible delay, even as short as one millisecond" (Turn 41) — describes existing system latency design, not a new requirement; same FP as v3.2/v3.3 |
| REQ-014 | "provide a 3-D spatial image using a camera with integrated light to aid depth perception" (Turn 75) — existing hardware feature description; same FP as v3.3 |

### False Negatives (5) — GTs missed

| GT | Missed requirement | Why missed |
|---|---|---|
| GT-002 | Auto trip to safe state on excessive force | Turn 30 covers this but extraction focused on e-stop (REQ-003) and e-stop timing (REQ-004); the overforce trip not separately extracted |
| GT-004 | Pause or stop a pre-programmed arm move mid-execution | Turn 32 discusses pause capability; extraction produced REQ-006 (out-of-sequence detection from participant Turn 33) rather than the participant's pause capability from Turn 31/32 |
| GT-007 | At least two camera views simultaneously — fixed overhead + adjustable close-up | Turn 6/56/58 discuss cameras; no extraction from these turns in this run |
| GT-008 | Camera auto-follow mode tracking arm position | Turn 58 content not extracted; same miss as v3.2/v3.3 |
| GT-013 | Force feedback sensitivity independent of force-ratio setting | Turn 80 (aspirational "Holy Grail" language); the aspirational-language rule was intended to capture this but did not — REQ-015 extracted force limits (GT-012) instead |

---

## What v3.4 changed vs v3.3

**Removed interviewer-turn FPs**: v3.3 REQ-004 ("detect out-of-order commands", Turn 32 interviewer) and REQ-005 ("perform standard tasks", Turn 34 interviewer) are gone — the interviewer-turn filter worked for these two. Net: 2 FPs removed.

**New/persisting FPs**: REQ-001 (diagnostic integration, Turn 1 — new FP), REQ-004 (e-stop timing, Turn 29 participant — new FP) added. Net: 2 new FPs.

**Lost GT-007 coverage**: v3.3 covered GT-007 (multiple cameras) via REQ-010. v3.4 does not extract this — the camera discussion (Turns 6/56/58) may now lack extraction signal since some of those turns are interviewer-led.

**GT-013 (aspirational) still missed**: The new aspirational-language rule did not extract GT-013 ("Holy Grail" haptic sensitivity from Turn 80). REQ-015 captures the force-ratio feature from the same turn but not the independent sensitivity goal.

Net change: 2 FPs removed, 2 added, 1 GT lost (GT-007). F1: 0.599 → 0.571.

---

## Comparison: v3.2 vs v3.3 vs v3.4 (N2)

| Metric | v3.2 | v3.3 | **v3.4** |
|---|---|---|---|
| Output count | 14 | 17 | **15** |
| **Precision** | 57.1% | 52.9% | **53.3%** |
| **Recall** | 61.5% | 69.2% | **61.5%** |
| **F1** | 0.592 | 0.599 | **0.571** |
| Priority accuracy | 75% | 67% | **75%** |
| False positives | 6 | 8 | **7** |
| False negatives | 5 | 4 | **5** |

**v3.3 remains best for N2 (F1=0.599).** v3.4 is a slight regression.

---

## Conclusion

v3.4 achieves **F1 = 0.571** on N2 — a slight regression from v3.3 (0.599). The interviewer-turn filter removed 2 confirmed interviewer-turn FPs but added new FPs and lost GT-007 coverage. The net effect is negative for N2.

The aspirational-language rule failed to capture GT-013 ("Holy Grail" haptic sensitivity) — the same turn (Turn 80) produced REQ-015 (force limits) instead, suggesting the model prioritises the concrete requirement over the aspirational ideal when both are present in the same turn.

| Problem | Impact | Status in v3.4 |
|---|---|---|
| VR simulator FP (REQ-002) | 1 FP | Persists — endorsed-feature narrowing insufficient |
| Diagnostic integration FP (REQ-001) | 1 FP | New in v3.4 — generic Turn 1 statement now extracted |
| E-stop timing FP (REQ-004) | 1 FP | New in v3.4 — sub-requirement extracted from Turn 29 |
| Interviewer-turn FPs (v3.3 REQ-004, REQ-005) | 2 FPs | Fixed ✓ |
| Bolt runner FP (REQ-007) | 1 FP | Persists |
| Perceptible delay FP (REQ-008) | 1 FP | Persists |
| LED/3D camera FP (REQ-014) | 1 FP | Persists |
| Camera auto-follow FN (GT-008) | 1 FN | Persists |
| Multiple cameras FN (GT-007) | 1 FN | Newly missed (was covered in v3.3) |
| Aspirational sensitivity FN (GT-013) | 1 FN | Persists — new rule did not help |
