# Pipeline Evaluation v3.3 (Cerebras / gpt-oss-120b — prompt improvements) — N1.txt

## Dataset

- **Source**: Bristol PhD thesis — *The Importance of Trust in Space Teleoperation*
- **Interview**: N1 — industrial robot-arm operator (nuclear/hazardous environments)
- **File**: `datasets/bristol/N1.txt` — 101 turns (Interviewer / Participant)
- **Ground truth**: `datasets/bristol/N1_expected.json` — 16 requirements
- **Output**: `results/bristol/output_N1_v3.3_llm.json`
- **Model**: gpt-oss-120b via Cerebras inference API

## What changed from v3.2

Same prompt and temperature changes as described in `evaluation_v3.3_llm.md` (IFA).

---

## Summary

### Detection accuracy

| Metric | v3.2 (120B + dedup) | **v3.3 (120B + prompt)** |
|---|---|---|
| Ground-truth requirements | 16 | 16 |
| Pipeline output count | 18 | **18** |
| True positives | 11 | **12** |
| GTs covered (incl. merged) | 14 | **14** |
| False positives | 7 | **6** |
| False negatives | 2 | **2** |
| **Precision** | 61.1% | **66.7%** |
| **Recall** | 87.5% | **87.5%** |
| **F1** | 0.719 | **0.757** |

### Priority accuracy

| Metric | v3.2 | **v3.3** |
|---|---|---|
| Priority distribution (output) | 3E / 15P / 0O | **4E / 14P / 0O** |
| GT distribution | 4E / 7P / 1O | 4E / 7P / 1O |
| Priority correct (of TPs) | 55% | **58%** |

---

## Classification of each pipeline output

### True Positives (12 outputs → 14 GTs covered)

| REQ | Maps to GT | Type | Priority | Notes |
|---|---|---|---|---|
| REQ-002 | GT-001 | func ✓ | essential ✓ | Safe mode on over-capacity movement |
| REQ-003 | GT-002 | func ✓ | essential ✓ | Hard and soft stops in software + hardware — **NEW in v3.3** |
| REQ-004 | GT-003 + GT-004 | func ✓ | essential ✓ / ✗(GT-004: preferred) | Joint range display + colour feedback merged |
| REQ-007 | GT-006 | func ✓ | essential ✗ (GT: preferred) | Teach file / waypoint navigation — over-prioritised |
| REQ-008 | GT-007 | func ✓ | preferred ✓ | One-button home / tool-storage recall |
| REQ-010 | GT-008 | func ✓ | preferred ✗ (GT: essential) | Fixed camera views — under-prioritised |
| REQ-011 | GT-009 | func ✓ | preferred ✓ | Variable / adjustable camera viewpoint |
| REQ-012 | GT-011 | func ✓ | preferred ✓ | AR alignment overlay — **NEW in v3.3** |
| REQ-013 | GT-016 | NF ✓ | preferred ✓ | Prioritise resolution over frame rate — **NEW in v3.3** |
| REQ-014 | GT-015 | func ✓ | preferred ✗ (GT: essential) | Force / haptic feedback — under-prioritised; **NEW in v3.3** |
| REQ-015 | GT-012 | func ✓ | preferred ✓ | Ghost mode / predicted end position |
| REQ-016 | GT-013 + GT-014 | func ✓ | essential ✓ / ✗(GT-014: preferred) | No-go zones + audible alarm merged |

### False Positives (6)

| REQ | Reason |
|---|---|
| REQ-001 | "provide a baseline configuration and allow creation of variant configurations for extended arm, waterproofing" (Turn 13) — hardware variants; no GT match; same FP category as v3.2 |
| REQ-005 | "allow tasks to have a configurable time limit with an additional 50% time buffer" (Turn 35, interviewer) — scheduling rule mentioned by interviewer; no GT match; same FP as v3.2 |
| REQ-006 | "provide a complete simulation that models the entire scene exactly" (Turn 41) — the participant endorses scene simulation for task planning, but no GT match; extracted due to new "endorsed feature" pattern |
| REQ-009 | "enable handover of control to the operator after autonomous movement completes" (Turn 46) — GT-006 already covered by REQ-007; adds handover concept not in GT |
| REQ-017 | "use computer vision to recognise material types" (Turn 89) — speculative discussion; same FP as v3.2 |
| REQ-018 | "detect overload on the gripper, indicate when fingers are opening or closing" (Turn 95) — describes observed hardware behaviour; no GT match; same FP as v3.2 |

### False Negatives (2) — GTs missed

| GT | Missed requirement | Why missed |
|---|---|---|
| GT-005 | Minimal, non-intrusive feedback design | Expressed as personal preference at Turn 23 with no modal verb; consistently missed across all versions |
| GT-010 | Adaptive camera zoom narrowing as end-effector approaches target | REQ-011 covers manual zoom (GT-009); the auto-adaptive aspect is not separately extracted |

---

## What v3.3 improved over v3.2

**Four new GTs covered (GT-002, GT-011, GT-015, GT-016):**

- **GT-002 (hard and soft stops)**: Turn 17 participant says "there are soft stops in the software and there's hard stops within the kit itself." v3.2 missed this because the extractor did not surface Turn 17. In v3.3, the extraction picks up Turn 17 directly as REQ-003.

- **GT-011 (AR overlay)**: Turn 66 participant describes the AR alignment overlay. Previously missed in v3.2; REQ-012 now correctly extracts this.

- **GT-015 (force/haptic feedback)**: Turn 76 participant describes force feedback. Previously missed in v3.2; REQ-014 now extracts it (though priority under-estimated: preferred vs essential GT).

- **GT-016 (resolution over frame rate)**: Turn 74 participant states the resolution preference. Previously missed in v3.2; REQ-013 now extracts it correctly.

**One fewer FP** (7 → 6): The cable guide FP (Turn 37) from v3.2 is still present as REQ-004 removed, but instead REQ-001 and REQ-006 are the new FPs. Net FP count is 6 vs 7 in v3.2.

Actually: v3.2 had FPs: REQ-001 (hardware variants), REQ-005 (50% time), REQ-006 (cable guides), REQ-007 (simulate scene), REQ-009 (autonomous handover), REQ-017 (material recognition), REQ-018 (gripper overload) = 7 FPs. v3.3 drops cable guide FP but adds scene simulation FP = 6 FPs.

**F1: 0.719 → 0.757.** Precision improves (61.1% → 66.7%) while recall holds (87.5%). The four new GTs covered are offset by one GT that dropped coverage (GT-010 adaptive zoom, which was a TP in v3.2's REQ-011 at preferred priority).

---

## Conclusion

v3.3 achieves **F1 = 0.757** and **precision 66.7%** — both improvements over v3.2 (F1 0.719,
precision 61.1%). Recall holds at **87.5%**. This is the best result for the N1 interview
across all versions.

The four new GT coverages (GT-002 hard stops, GT-011 AR overlay, GT-015 force feedback,
GT-016 resolution preference) reflect the prompt changes enabling the extractor to surface
requirements from turns that were previously missed. The remaining FPs are in the same
structural categories as v3.2: hardware descriptions (REQ-001), interviewer-turn extractions
(REQ-005), speculative content (REQ-017), and operational hardware behaviour (REQ-018).

| Problem | Impact | Root cause |
|---|---|---|
| Hardware variant FP (REQ-001) | 1 FP | Physical arm configurations outside software GT scope |
| Interviewer scheduling rule (REQ-005) | 1 FP | 50% time buffer from interviewer, not requirement |
| Scene simulation endorsed FP (REQ-006) | 1 FP | Participant endorses simulation for task planning; no GT |
| Handover-after-autonomous FP (REQ-009) | 1 FP | GT-006 already covered; handover extension not in GT |
| Speculative material recognition (REQ-017) | 1 FP | "Just started investigating" — uncertainty language not filtered |
| Gripper overload detection (REQ-018) | 1 FP | Hardware behaviour observation; no GT match |
| GT-005 missed | 1 FN | Design principle as personal preference; no modal verb |
| GT-010 missed | 1 FN | Auto-adaptive zoom not separately extracted from manual zoom |
