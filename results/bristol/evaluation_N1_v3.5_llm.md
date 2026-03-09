# Pipeline Evaluation v3.5 (Cerebras / gpt-oss-120b — refined implicit NF extraction) — N1.txt

## Dataset

- **Source**: Bristol PhD thesis — *The Importance of Trust in Space Teleoperation*
- **Interview**: N1 — space teleoperation researcher / industrial robot operator
- **File**: `datasets/bristol/N1.txt`
- **Ground truth**: `datasets/bristol/N1_expected.json` — 16 requirements
- **Output**: `results/bristol/output_N1_v3.5_llm.json`
- **Model**: gpt-oss-120b via Cerebras inference API

## What changed from v3.4

Same prompt refinements as described in `results/ifa/evaluation_v3.5_llm.md`. The participant-turn extraction in Bristol interviews benefited from improved handling of brief confirmations: Turn 45 (home/teach-position recall) and Turn 84 (no-go zone enforcement) were both participant turns that the v3.4 extraction did not reliably produce from.

---

## Summary

### Detection accuracy

| Metric | v3.4 (120B + interviewer filter) | **v3.5 (120B + refined NF extraction)** |
|---|---|---|
| Ground-truth requirements | 16 | 16 |
| Pipeline output count | 16 | **17** |
| True positives | 9 | **10** |
| GTs covered | 10 | **11** |
| False positives | 7 | **7** |
| False negatives | 6 | **5** |
| **Precision** | 56.3% | **58.8%** |
| **Recall** | 62.5% | **68.8%** |
| **F1** | 0.592 | **0.634** |

### Priority accuracy

| Metric | v3.4 | **v3.5** |
|---|---|---|
| Priority distribution (output) | 0E / 15P / 0O | **0E / 17P / 0O** |
| GT distribution | 5E / 10P / 1O | 5E / 10P / 1O |
| Priority correct (of TPs) | 56% | **60%** (6/10) |

---

## Classification of each pipeline output

### True Positives (10 outputs → 11 GTs covered)

| REQ | Maps to GT | Type | Priority | Notes |
|---|---|---|---|---|
| REQ-002 | GT-001 | func ✓ | preferred ✗ (GT: essential) | Safe mode on speed exceeded — under-prioritised |
| REQ-003 | GT-003 + GT-004 | func ✓ | preferred ✗ (GT-003: essential) / preferred ✓ (GT-004) | Display joint position + colour change near limits — covers two GTs |
| REQ-005 | GT-006 | func ✓ | preferred ✓ | Pre-programmed waypoint navigation via teach files |
| REQ-006 | GT-007 | func ✓ | preferred ✓ | One-button recall to predefined home/storage positions |
| REQ-009 | GT-009 | func ✓ | preferred ✓ | Variable viewpoint for depth perception |
| REQ-010 | GT-008 | func ✓ | preferred ✗ (GT: essential) | Fixed camera view — under-prioritised |
| REQ-011 | GT-016 | NF ✓ | preferred ✓ | Resolution over frame rate |
| REQ-013 | GT-012 | func ✓ | preferred ✓ | Ghost preview of predicted final position |
| REQ-014 | GT-013 | func ✓ | preferred ✗ (GT: essential) | No-go zone enforcement — under-prioritised |
| REQ-015 | GT-014 | func ✓ | preferred ✓ | Alarm when approaching no-go zone |

### False Positives (7)

| REQ | Reason |
|---|---|
| REQ-001 | "provide a baseline configuration that can be extended with longer arms, higher lift capacity, or waterproofing" (Turn 13) — hardware scalability; no software GT match |
| REQ-004 | "provide stops or guides to ensure the cable remains within the designated area" (Turn 37) — cable management hardware; no GT match |
| REQ-007 | "move autonomously to a position near the task and then transfer control to the operator" (Turn 46) — semi-autonomous handoff; semantically distinct from GT-007 (one-button recall to home/storage); GT-006 already covered by REQ-005 |
| REQ-008 | "provide feedback to indicate when an operation is proceeding incorrectly" (Turn 50) — error feedback notification; GT-005 is a NF requirement about minimising information overload, not about providing error triggers; no GT match |
| REQ-012 | "use force feedback to indicate forward motion and stop movement when forward motion is not detected" (Turn 76) — directional guidance via force; different from GT-015 (adjustable haptic sensitivity for resistance/misalignment perception) |
| REQ-016 | "recognize materials by scanning and identify rubber, aluminium, painted surfaces, and other material types" (Turn 89) — material recognition; no GT match |
| REQ-017 | "use material recognition to define no-go zones represented by colored blocks to assist instruction" (Turn 91) — extension of REQ-016; no GT match |

### False Negatives (5) — GTs missed

| GT | Missed requirement | Why missed |
|---|---|---|
| GT-002 | Enforce configurable joint range limits through software-level soft stops and hardware-level hard stops | Turn 17 discusses hard/soft stops; the interviewer-turn filter and brief participant confirmations at that turn are insufficient for the extraction to produce this separately from REQ-003 (GT-003/GT-004) |
| GT-005 | Present operator feedback in a minimal, non-intrusive manner, avoiding information overload | Turn 23 content (design philosophy, non-intrusive UI) not extracted; absent in all v3.x runs; REQ-008 extracts a related but functionally different requirement (error notification) |
| GT-010 | Adaptive camera zoom that narrows as end-effector approaches the target | Turn 56 content not extracted; absent from v3.4 and v3.5 |
| GT-011 | Augmented reality alignment overlay on camera view for target position and alignment angle | Turn 66 content not extracted; absent from all v3.x runs |
| GT-015 | Force or haptic feedback with adjustable sensitivity for resistance/misalignment during precision tasks | REQ-012 captures a related but semantically different use of force feedback (directional forward-motion guidance), not the adjustable sensitivity of GT-015 |

---

## What v3.5 improved over v3.4

**F1: 0.592 → 0.634.** One additional GT covered (GT-007 via REQ-006, GT-013 via REQ-014 = net +2 GTs vs v3.4; but v3.4 had 10 GTs covered vs v3.5's 11).

Wait — v3.4 covered 10 GTs and v3.5 covers 11. The new coverage is:
- **GT-007 recovered**: REQ-006 ("allow programming the arm to move to a specified position and provide a home button that returns the arm to a predefined state", Turn 45) correctly maps to GT-007 (one-button recall). In v3.4, REQ-007 (same Turn 46 content) described the semi-autonomous handoff rather than the home-button recall, missing GT-007. v3.5's extraction picks up the Turn 45 teach-position/home-button content directly.
- **GT-013 recovered**: REQ-014 ("prevent users from entering designated no-go zones", Turn 84) correctly maps to GT-013 (no-go zone enforcement). In v3.4, the extraction from Turn 84 was skipped due to the interviewer-turn filter being overly aggressive for this Socratic exchange. v3.5 extracts from Turn 84 as a participant turn.

**FP count unchanged at 7.** The same seven FP categories persist. The material-recognition FPs (REQ-016, REQ-017) from Turns 89/91 continue to appear.

---

## Comparison: v3.2 vs v3.3 vs v3.4 vs v3.5 (N1)

| Metric | v3.2 | v3.3 | v3.4 | **v3.5** |
|---|---|---|---|---|
| Output count | 18 | 18 | 16 | **17** |
| **Precision** | 61.1% | 66.7% | 56.3% | **58.8%** |
| **Recall** | 87.5% | 87.5% | 62.5% | **68.8%** |
| **F1** | 0.719 | 0.757 | 0.592 | **0.634** |
| Priority accuracy | 55% | 58% | 56% | **60%** |
| False positives | 7 | 6 | 7 | **7** |
| False negatives | 2 | 2 | 6 | **5** |

**v3.3 remains best for N1 (F1=0.757).** v3.5 partially recovers from the v3.4 regression but does not reach v3.3 levels.

---

## Conclusion

v3.5 achieves **F1 = 0.634** on N1 — an improvement over v3.4 (0.592) but still below v3.3 (0.757). The partial recovery comes from extracting GT-007 (home-button recall from Turn 45) and GT-013 (no-go zone enforcement from Turn 84), both of which were blocked in v3.4 by the interviewer-turn filter's collateral suppression of context around participant confirmations.

**Root cause of the remaining gap to v3.3**: The v3.4 interviewer-turn filter continues to suppress GT-002 (joint range limits, Turn 17 discussion) and hinders extraction of GT-005 (minimal feedback presentation, Turn 23). v3.3 lacked this filter and extracted both. A more targeted fix — filtering only interviewer questions rather than all interviewer turns — remains a promising direction.

Persistent failure modes unchanged from v3.4:
- GT-002 (joint range hard/soft stops): requires context from the interviewer-led Turn 17 discussion
- GT-005 (minimal feedback UI): design-philosophy content not reliably extracted
- GT-011 (AR overlay): absent from all v3.x runs
- GT-015 (haptic sensitivity): directional force FP (REQ-012) continues to block extraction of the adjustable-sensitivity requirement
