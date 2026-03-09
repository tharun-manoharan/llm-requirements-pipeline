# Pipeline Evaluation v3.5 (Cerebras / gpt-oss-120b — refined implicit NF extraction) — IFA

## Dataset

- **Source**: IFA stakeholder elicitation session
- **File**: `datasets/ifa/conversation.txt`
- **Ground truth**: `datasets/ifa/expected.json` — 41 requirements
- **Output**: `results/ifa/output_v3.5_llm.json`
- **Model**: gpt-oss-120b via Cerebras inference API

## What changed from v3.4

Prompt refinements targeting three persistent failure modes identified in v3.4:

1. **Strengthened implicit NF constraint extraction**: The compliance/regulatory pattern examples were made more explicit and the hosting/infrastructure NF category was reinforced with additional triggering language, improving extraction from background statements without modal verbs (Turn 88, 91/92 in IFA).
2. **Improved late-conversation coverage**: Extraction of requirements from late participant turns (Turn 117+) that were consistently missed improved through better prompt context handling.
3. **Real-time event notification signal**: The notification/alert pattern was refined to distinguish subscription setup (GT-020/021) from real-time event triggering (GT-022), enabling both to be extracted from the same turn.

---

## Summary

### Detection accuracy

| Metric | v3.4 (120B + interviewer filter) | **v3.5 (120B + refined NF extraction)** |
|---|---|---|
| Ground-truth requirements | 41 | 41 |
| Pipeline output count | 32 | **35** |
| True positives | 28 | **30** |
| GTs covered | 33 | **39** |
| False positives | 4 | **5** |
| False negatives | 8 | **2** |
| **Precision** | 87.5% | **85.7%** |
| **Recall** | 80.5% | **95.1%** |
| **F1** | 0.839 | **0.901** |

### Priority accuracy

| Metric | v3.4 | **v3.5** |
|---|---|---|
| Priority distribution (output) | 17E / 11P / 1O | **22E / 13P / 0O** |
| GT distribution | 26E / 12P / 3O | 26E / 12P / 3O |
| Priority correct (of TPs) | 57% | **57%** (17/30) |

---

## Classification of each pipeline output

### True Positives (30 outputs → 39 GTs covered)

| REQ | Maps to GT | Type | Priority | Notes |
|---|---|---|---|---|
| REQ-001 | GT-001 | func ✓ | preferred ✗ (GT: essential) | Team budget management — under-prioritised |
| REQ-002 | GT-002 | func ✓ | preferred ✗ (GT: essential) | IFA monitor budget — under-prioritised |
| REQ-003 | GT-003 | func ✓ | preferred ✗ (GT: essential) | Budget policies — under-prioritised |
| REQ-006 | GT-004 | func ✓ | preferred ✓ | IFA admin view all transactions |
| REQ-008 | GT-007 | func ✓ | essential ✓ | Referees insert events via mobile |
| REQ-009 | GT-010 | func ✓ | essential ✓ | All users view game data |
| REQ-010 | GT-011 | func ✓ | essential ✗ (GT: preferred) | Export game data — over-prioritised |
| REQ-011 | GT-012 | func ✓ | preferred ✓ | Team managers view/export data |
| REQ-012 | GT-005 | func ✓ | essential ✓ | Only teams insert budget transactions |
| REQ-014 | GT-006 | func ✓ | essential ✓ | IFA view monetary info, no modification |
| REQ-015 | GT-014 | func ✓ | essential ✓ | Scheduling policies definition |
| REQ-016 | GT-015 + GT-016 | func ✓ | preferred ✗ (GT-015: essential) | Referee allocation + enforcement — GT-015 under-prioritised |
| REQ-017 | GT-017 | func ✓ | essential ✗ (GT: preferred) | Referee availability/preferences — over-prioritised |
| REQ-018 | GT-018 | func ✓ | essential ✓ | Manual rescheduling |
| REQ-019 | GT-019 | func ✓ | essential ✓ | Override rationale + second IFA approval |
| REQ-021 | GT-020 + GT-021 + GT-022 | func ✓ | preferred ✗ (GT-020/021: essential) | Fan subscriptions + push notifications + real-time events — under-prioritised |
| REQ-022 | GT-028 | func ✗ (GT: NF) | essential ✗ (GT: preferred) | Web/mobile apps — type and priority mismatch |
| REQ-023 | GT-029 | func ✗ (GT: NF) | preferred ✗ (GT: essential) | Different interfaces/RBAC — type and priority mismatch |
| REQ-024 | GT-008 + GT-034 | func ✓ | essential ✓ | Referees only update game data; GT-034 type mismatch (NF) |
| REQ-025 | GT-023 + GT-041 | func ✓ | preferred ✗ (GT: optional) | Automatic + fan reminders — over-prioritised |
| REQ-026 | GT-025 | NF ✓ | essential ✓ | 50,000 concurrent users |
| REQ-027 | GT-026 + GT-027 | NF ✓ | essential ✓ (GT-027) / ✗ (GT-026: preferred) | Response times — GT-026 over-prioritised |
| REQ-028 | GT-033 | NF ✓ | essential ✗ (GT: preferred) | Cloud hosting — over-prioritised |
| REQ-029 | GT-030 + GT-031 | NF ✓ | essential ✓ (GT-031) / ✗ (GT-030: preferred) | Localisation + data residency — GT-030 over-prioritised |
| REQ-030 | GT-032 | NF ✓ | preferred ✓ | Encrypt budget data |
| REQ-031 | GT-024 | func ✓ | preferred ✓ | Players manage social network page |
| REQ-032 | GT-036 | func ✓ | essential ✓ | User registration and authentication |
| REQ-033 | GT-037 + GT-039 | func ✓ | essential ✓ | Team registration workflow + manage players/coaches |
| REQ-034 | GT-035 | NF ✗ (GT: func) | essential ✓ | Retain historical archives — type mismatch |
| REQ-035 | GT-040 + GT-038 | func ✓ | essential ✓ | IFA define leagues/seasons + register referees |

### False Positives (5)

| REQ | Reason |
|---|---|
| REQ-004 | "provide alerts for specified violations" (Turn 5) — semantic duplicate of REQ-003; GT-003 (budget policies + alerts) already covered |
| REQ-005 | "allow the financial team to access financial data across teams" (Turn 6) — semantic duplicate of REQ-006; GT-004 already covered |
| REQ-007 | "allow only IFA administrative personnel and teams to access the budgeting system" (Turn 13) — general access control statement; GT-005/GT-006 already covered by REQ-012/REQ-014 |
| REQ-013 | "restrict data access so that each team can only access its own data" (Turn 29) — semantic duplicate of REQ-012; GT-005 already covered |
| REQ-020 | "enforce minimum gap days between matches as defined in the policy" (Turn 53) — semantic duplicate of REQ-015; GT-014 already covered |

### False Negatives (2) — GTs missed

| GT | Missed requirement | Why missed |
|---|---|---|
| GT-009 | Record game events with timestamps and event-specific details (goals, offsides, red cards) | Referee insertion extracted (GT-007 via REQ-008) but the specific event-type detail and timestamping aspect of Turn 17 not extracted separately |
| GT-013 | Automatic scheduling of games per league per season | Scheduling policies extracted (GT-014 via REQ-015) and manual schedule adjustment (GT-018 via REQ-018) but automatic scheduling itself not extracted; Turn 31 content interpreted as policy definition |

---

## What v3.5 improved over v3.4

**F1: 0.839 → 0.901.** Recall increased from 80.5% to 95.1%. Six additional GTs now covered.

**Previously-missed NF constraints now captured:**
- GT-030 (localisation) + GT-031 (data residency) via REQ-029 from Turn 92 — the strengthened compliance/regulatory pattern triggered correctly for the "German data" and localisation statements.
- GT-033 (cloud hosting) via REQ-028 from Turn 88 — the hosting/infrastructure NF category now extracted from the background statement about outsourcing.

**Previously-missed late-conversation requirements now captured:**
- GT-036 (user registration/authentication) via REQ-032 from Turn 117 — now reliably extracted.
- GT-041 (automatic reminder notifications) via REQ-025 from Turn 78 — sourced from a participant turn (spk_1), not the interviewer turn (Turn 77 was spk_0).

**Real-time event notifications now captured:**
- GT-022 (real-time fan notifications when events occur) via REQ-021 — the same requirement that covers GT-020/021 (fan subscriptions and push notifications) now also captures the real-time event triggering aspect.

## Where v3.5 is worse than v3.4

**New FP introduced**: REQ-007 (general budget access control, Turn 13) — a new FP not present in v3.4. The extraction split the access restriction concept across REQ-012 (team-only transactions), REQ-014 (IFA view-only), and REQ-007 (combined access), resulting in a redundant extraction.

**FP count increased**: 4 FPs in v3.4 → 5 FPs in v3.5. The split-extraction pattern for budget access (REQ-004, REQ-005, REQ-007, REQ-013) produced more duplicates.

**Priority accuracy unchanged at 57%**: More TPs but the same proportion have wrong priorities. The model continues to default to essential for functional requirements that GT marks as preferred, and occasionally over-prioritises optional GTs (GT-023, GT-041) as preferred.

---

## Comparison: v3.2 vs v3.3 vs v3.4 vs v3.5 (IFA)

| Metric | v3.2 | v3.3 | v3.4 | **v3.5** |
|---|---|---|---|---|
| Output count | 29 | 30 | 32 | **35** |
| **Precision** | 89.7% | 86.7% | 87.5% | **85.7%** |
| **Recall** | 82.9% | 78.0% | 80.5% | **95.1%** |
| **F1** | 0.861 | 0.821 | 0.839 | **0.901** |
| Priority accuracy | 65% | 65% | 57% | **57%** |
| False positives | 3 | 4 | 4 | **5** |
| False negatives | 7 | 9 | 8 | **2** |

**v3.5 is the best IFA result** (F1=0.901). It recovers 6 GTs that were missed across all prior versions and achieves the highest recall of any version.

---

## Conclusion

v3.5 achieves **F1 = 0.901** on IFA — the best result across all pipeline versions. Recall reaches **95.1%** (39/41 GTs covered), a major improvement from v3.4's 80.5%.

The key breakthrough is reliable extraction of previously-intractable implicit NF constraints: localisation (GT-030), data residency (GT-031), cloud hosting (GT-033), and user authentication (GT-036) are all now captured. The only remaining FNs are GT-009 (event-type detail) and GT-013 (automatic scheduling), both cases where the LLM extracted the surrounding concept but not the specific sub-feature.

Persistent failure modes:
- Priority calibration: 43% of TPs still have wrong priority — the model biases toward essential for functional requirements
- Split-extraction duplicates: 4 of 5 FPs are semantic duplicates; deduplication at Stage 4b is not catching all of them
- Type misclassification: GT-028 and GT-029 (NF in GT) extracted as functional; GT-035 (functional in GT) extracted as NF
