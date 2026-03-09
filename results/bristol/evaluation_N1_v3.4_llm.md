# Pipeline Evaluation v3.4 (Cerebras / gpt-oss-120b — interviewer filter + aspirational) — N1.txt

## Dataset

- **Source**: Bristol PhD thesis — *The Importance of Trust in Space Teleoperation*
- **Interview**: N1 — space teleoperation researcher / industrial robot operator
- **File**: `datasets/bristol/N1.txt`
- **Ground truth**: `datasets/bristol/N1_expected.json` — 16 requirements
- **Output**: `results/bristol/output_N1_v3.4_llm.json`
- **Model**: gpt-oss-120b via Cerebras inference API

## What changed from v3.3

Same three changes as IFA v3.4: interviewer-turn filter, narrowed endorsed-feature rule, aspirational-language pattern. See `results/ifa/evaluation_v3.4_llm.md` for details.

---

## Summary

### Detection accuracy

| Metric | v3.3 (120B + prompt) | **v3.4 (120B + interviewer filter)** |
|---|---|---|
| Ground-truth requirements | 16 | 16 |
| Pipeline output count | 18 | **16** |
| True positives | 12 | **9** |
| GTs covered | 14 | **10** |
| False positives | 6 | **7** |
| False negatives | 2 | **6** |
| **Precision** | 66.7% | **56.3%** |
| **Recall** | 87.5% | **62.5%** |
| **F1** | 0.757 | **0.592** |

### Priority accuracy

| Metric | v3.3 | **v3.4** |
|---|---|---|
| Priority distribution (output) | — | **0E / 15P / 0O** |
| GT distribution | 5E / 10P / 1O | 5E / 10P / 1O |
| Priority correct (of TPs) | 58% | **56%** (5/9) |

---

## Classification of each pipeline output

### True Positives (9 outputs → 10 GTs covered)

| REQ | Maps to GT | Type | Priority | Notes |
|---|---|---|---|---|
| REQ-002 | GT-001 | func ✓ | preferred ✗ (GT: essential) | Safe mode on speed exceeded — under-prioritised |
| REQ-003 | GT-003 + GT-004 | func ✓ | preferred ✗ (GT-003: essential) / preferred ✓ (GT-004) | Display joint position + colour change near limits — covers two GTs |
| REQ-006 | GT-006 | func ✓ | preferred ✓ | Pre-programmed waypoint navigation via teach files |
| REQ-008 | GT-009 | func ✓ | preferred ✓ | Variable viewpoint for depth perception |
| REQ-009 | GT-008 | func ✓ | preferred ✗ (GT: essential) | Fixed camera view — under-prioritised |
| REQ-010 | GT-010 | func ✓ | preferred ✗ (GT: optional) | Adaptive camera zoom — over-prioritised |
| REQ-011 | GT-016 | NF ✓ | preferred ✓ | Resolution over frame rate |
| REQ-013 | GT-012 | func ✓ | preferred ✓ | Ghost preview of predicted final position |
| REQ-014 | GT-014 | func ✓ | preferred ✓ | Alarm when approaching no-go zone |

### False Positives (7)

| REQ | Reason |
|---|---|
| REQ-001 | "provide baseline configuration adaptable for project-specific requirements (longer arms, waterproofing)" (Turn 13) — hardware scalability; not a software GT |
| REQ-004 | "allow a timeframe to be extended by 50% as a buffer" (Turn 35) — operational scheduling detail; no GT match |
| REQ-005 | "provide stops or guides to keep the cable within designated boundaries" (Turn 37) — cable management hardware; no GT match |
| REQ-007 | "move the robot close to the target and transfer control to the operator for final positioning" (Turn 46) — semi-autonomous handoff; semantically distinct from GT-007 (one-button recall to home/storage) |
| REQ-012 | "use force feedback to indicate when forward motion is required and stop movement if not moving forward" (Turn 76) — directional guidance via force, different from GT-015 (haptic resistance perception for misalignment) |
| REQ-015 | "recognize materials such as rubber, aluminium, painted surfaces through visual scanning" (Turn 89) — material recognition; no GT match |
| REQ-016 | "feed material recognition into no-go zone and use coloured blocks as visual cues" (Turn 91) — extension of REQ-015; no GT match |

### False Negatives (6) — GTs missed

| GT | Missed requirement | Why missed |
|---|---|---|
| GT-002 | Enforce configurable joint range limits via soft and hard stops | Turn 17 discusses hard/soft stops; likely an interviewer-led discussion. With the interviewer-turn filter, the extraction context is reduced to the participant's brief confirmation, which was insufficient to extract GT-002 separately from GT-003/GT-004 |
| GT-005 | Present operator feedback in a minimal, non-intrusive manner | Turn 23 content (design philosophy, non-intrusive UI) not extracted; absent in all v3.x runs |
| GT-007 | One-button recall to predefined home or tool-storage positions | Turn 45 content missed; REQ-007 captures related semi-autonomous positioning but differs semantically |
| GT-011 | Augmented reality alignment overlay on camera view | Turn 66 content not extracted; absent from all v3.x runs — may be primarily in an interviewer-framed question with participant confirmation only |
| GT-013 | Configurable no-go zones that physically prevent robot from entering | REQ-014 captures the alarm (GT-014) but the physical enforcement / configurable exclusion zones aspect is missed; Turn 84 likely interviewer-led |
| GT-015 | Force or haptic feedback with adjustable sensitivity for resistance/misalignment perception | REQ-012 captures a related but semantically different use of force feedback (directional guidance), not the adjustable haptic perception of GT-015 |

---

## What caused the N1 regression

**Recall: 87.5% → 62.5%.** Four more GTs missed compared to v3.3.

The Bristol N1 interview follows a Socratic pattern: the Interviewer proposes or describes features ("Could you have hard stops on joint limits?") and the Participant confirms or elaborates. In v3.3, the LLM was extracting requirements informed by both sides of the dialogue. The new interviewer-turn filter blocks the interviewer's side — but the Participant's confirmations are often brief ("Yes, exactly" or "We do have those") without independently describing the feature. This means the feature described by the Interviewer no longer makes it into the extraction.

**GTs lost due to interviewer-filter collateral damage:**
- GT-002 (joint range hard/soft stops, Turn 17 — likely interviewer-led)
- GT-013 (no-go zone enforcement, Turn 84 — likely interviewer-led)
- Possibly GT-007 and GT-015 (brief participant confirmations of interviewer-described features)

**New FPs not in v3.3:**
- REQ-001 (hardware baseline config from Turn 13) — new extraction
- REQ-004 (50% timeframe buffer from Turn 35) — new extraction
- REQ-005 (cable guides from Turn 37) — new extraction; possible participant turn not previously extracted due to deduplication

---

## Comparison: v3.2 vs v3.3 vs v3.4 (N1)

| Metric | v3.2 | v3.3 | **v3.4** |
|---|---|---|---|
| Output count | 18 | 18 | **16** |
| **Precision** | 61.1% | 66.7% | **56.3%** |
| **Recall** | 87.5% | 87.5% | **62.5%** |
| **F1** | 0.719 | 0.757 | **0.592** |
| Priority accuracy | 55% | 58% | **56%** |
| False positives | 7 | 6 | **7** |
| False negatives | 2 | 2 | **6** |

**v3.3 remains best for N1 (F1=0.757).** v3.4 represents a significant regression driven entirely by the recall drop.

---

## Conclusion

v3.4 achieves **F1 = 0.592** on N1 — a significant regression from v3.3 (0.757). The interviewer-turn filter, which helped IFA, is damaging for the Bristol interview format where requirements are often elicited via interviewer questions and brief participant confirmations.

The v3.4 changes are net negative for N1:
- The aspirational-language rule added no new TPs (N1 has no "Holy Grail" style statements)
- The narrowed endorsed-feature rule added no benefit (N1 has no VR simulator or training context)
- The interviewer-turn filter removed 4 GTs from coverage and added 3 new FPs

**Root cause**: The interviewer-turn filter is too aggressive for interview-style data. A more targeted fix would filter only interviewer *questions* (sentences ending with ?) while allowing extraction from participant turns that respond to interviewer prompts — which is what v3.3 already attempted via the "?" filter.
