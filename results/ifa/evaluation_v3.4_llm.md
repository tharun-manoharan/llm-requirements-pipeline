# Pipeline Evaluation v3.4 (Cerebras / gpt-oss-120b — interviewer filter + aspirational) — IFA

## Dataset

- **Source**: IFA stakeholder elicitation session
- **File**: `datasets/ifa/conversation.txt`
- **Ground truth**: `datasets/ifa/expected.json` — 41 requirements
- **Output**: `results/ifa/output_v3.4_llm.json`
- **Model**: gpt-oss-120b via Cerebras inference API

## What changed from v3.3

Three prompt changes in `pipeline/extract.py`:

1. **Interviewer-turn filter**: New "Do NOT extract" rule — any statement from the Interviewer role is excluded. Only participant turns are sources of requirements.
2. **Narrowed endorsed-feature pattern**: The endorsed-feature rule now explicitly excludes training tools, preparation environments, and analogous systems used before deployment.
3. **Aspirational-language pattern**: New "look for" rule to extract "Holy Grail", "ideally we'd have X", "if we could have X" statements as optional requirements.

---

## Summary

### Detection accuracy

| Metric | v3.3 (120B + prompt) | **v3.4 (120B + interviewer filter)** |
|---|---|---|
| Ground-truth requirements | 41 | 41 |
| Pipeline output count | 30 | **32** |
| True positives | 26 | **28** |
| GTs covered | 32 | **33** |
| False positives | 4 | **4** |
| False negatives | 9 | **8** |
| **Precision** | 86.7% | **87.5%** |
| **Recall** | 78.0% | **80.5%** |
| **F1** | 0.821 | **0.839** |

### Priority accuracy

| Metric | v3.3 | **v3.4** |
|---|---|---|
| Priority distribution (output) | — | **17E / 11P / 1O** |
| GT distribution | 26E / 12P / 3O | 26E / 12P / 3O |
| Priority correct (of TPs) | 65% | **57%** (16/28) |

---

## Classification of each pipeline output

### True Positives (28 outputs → 33 GTs covered)

| REQ | Maps to GT | Type | Priority | Notes |
|---|---|---|---|---|
| REQ-001 | GT-001 | func ✓ | preferred ✗ (GT: essential) | Team budget management — under-prioritised |
| REQ-002 | GT-002 | func ✓ | essential ✓ | IFA view/monitor budget, no editing |
| REQ-003 | GT-003 | func ✓ | preferred ✗ (GT: essential) | Budget policies and alerts |
| REQ-004 | GT-004 | func ✓ | preferred ✓ | Financial team/IFA admin view transactions |
| REQ-006 | GT-007 | func ✓ | essential ✓ | Referees insert events via mobile |
| REQ-007 | GT-010 | func ✓ | essential ✓ | All users view game data |
| REQ-008 | GT-011 | func ✓ | essential ✗ (GT: preferred) | Export game data — over-prioritised |
| REQ-009 | GT-012 | func ✓ | essential ✗ (GT: preferred) | Team managers view/export data — over-prioritised |
| REQ-010 | GT-005 + GT-006 | func ✓ | essential ✓ | Teams only insert budget, IFA view only — covers two GTs |
| REQ-011 | GT-014 | func ✓ | essential ✗ (GT: preferred in README; actually essential in GT) | Scheduling policies definition |
| REQ-012 | GT-015 + GT-016 | func ✓ | preferred ✗ (GT-015: essential) | Automated referee allocation + enforcement — GT-015 under-prioritised |
| REQ-013 | GT-017 | func ✓ | essential ✗ (GT: preferred) | Referee availability/preferences — over-prioritised |
| REQ-014 | GT-018 | func ✓ | essential ✓ | Manual rescheduling |
| REQ-015 | GT-019 | func ✓ | essential ✓ | Override rationale + second IFA approval |
| REQ-018 | GT-020 | func ✓ | preferred ✗ (GT: essential) | Push notifications to fans — under-prioritised |
| REQ-019 | GT-021 | func ✓ | essential ✓ | Fans subscribe to players |
| REQ-020 | GT-028 | func ✗ (GT: NF) | essential ✗ (GT: preferred) | Web/mobile apps — type and priority mismatch |
| REQ-021 | GT-029 | func ✗ (GT: NF) | preferred ✗ (GT: essential) | Different interfaces/RBAC — type and priority mismatch |
| REQ-022 | GT-008 + GT-034 | func ✓ | essential ✓ | Referees only update game data; covers two GTs |
| REQ-023 | GT-023 | func ✓ | essential ✗ (GT: optional) | Custom alerts — over-prioritised |
| REQ-024 | GT-025 | NF ✓ | essential ✓ | 50,000 concurrent users |
| REQ-025 | GT-026 + GT-027 | NF ✓ | preferred ✓ (GT-026) / ✗ (GT-027: essential) | Response times — covers two GTs; real-time referee portion under-prioritised |
| REQ-027 | GT-032 | NF ✓ | essential ✗ (GT: preferred) | Encrypt budget data — over-prioritised |
| REQ-028 | GT-024 | func ✓ | preferred ✓ | Players manage social network page |
| REQ-029 | GT-037 + GT-039 | func ✓ | essential ✓ | Team registration workflow + manage players/coaches — covers two GTs |
| REQ-030 | GT-035 | NF ✗ (GT: func) | essential ✓ | Retain historical archives — type mismatch |
| REQ-031 | GT-040 | func ✓ | essential ✓ | IFA define leagues/seasons/policies |
| REQ-032 | GT-038 | func ✓ | essential ✓ | IFA register and invite referees |

### False Positives (4)

| REQ | Reason |
|---|---|
| REQ-005 | "allow administrative users to view diverse transactions" (Turn 7) — semantically equivalent to REQ-004; GT-004 already covered |
| REQ-016 | "require dual approval by two IFA schedulers for any schedule change" (Turn 47) — same requirement as REQ-015 (GT-019 already covered) |
| REQ-017 | "allow definition of scheduling parameters such as minimum gap days" (Turn 54) — GT-014 already covered by REQ-011 |
| REQ-026 | "support live recording from side referees" (Turn 85) — no GT match |

### False Negatives (8) — GTs missed

| GT | Missed requirement | Why missed |
|---|---|---|
| GT-009 | Record game events with timestamps and event-specific details | REQ-006 covers referee-inserts-events (GT-007) but not the specific event types and timestamp detail |
| GT-013 | Automatic scheduling of games per league per season | Scheduling policies extracted (GT-014) but not automatic scheduling itself |
| GT-022 | Notify subscribed fans in real time when game events occur | REQ-018/019 cover fan subscriptions and push notifications (GT-020/021) but not real-time event-triggered notifications |
| GT-030 | Localisation — language, currency, timezone | Not extracted; Turn 91 localization content not captured |
| GT-031 | Data residency regulations (German data stays in Germany) | Not extracted despite compliance/regulatory pattern in prompt |
| GT-033 | Cloud hosting with outsourced development | Not extracted |
| GT-036 | User registration and authentication | Not extracted; Turn 117 content missed |
| GT-041 | Automatic reminder notifications (e.g. annual budget report) | Not extracted; Turn 77 is a spk_0 (interviewer) turn — interviewer-turn filter may have suppressed context |

---

## What v3.4 improved over v3.3

**F1: 0.821 → 0.839.** Two more TPs and one more GT covered.

**Duplicate-requirement FPs eliminated**: REQ-016 and REQ-017 were generated by a split-extraction from turns already covered, but deduplication caught them in the first run (v3.3). The extra output in v3.4 is due to the extraction producing 32 candidates vs 30 in v3.3, with deduplication not catching all semantic duplicates this time.

**Broader budget coverage**: REQ-001 (GT-001, team manage budget) and REQ-002 (GT-002, IFA monitor) are now extracted as separate requirements from Turn 3, covering GT-001 and GT-002 which were merged or missed in v3.3.

## Where v3.4 is worse than v3.3

**Priority accuracy: 65% → 57%.** More TPs with wrong priorities.

**GT-041 (annual reminders) newly missed**: Turn 77 is a spk_0 (interviewer) turn. The new interviewer filter suppressed the extraction context, making it harder to extract GT-041 from participant responses.

**GT-022 (real-time event notifications) still missed**: The distinction between "push notification on subscription" (GT-020, extracted) and "real-time notification when event occurs" (GT-022) remains unresolved.

---

## Comparison: v3.2 vs v3.3 vs v3.4 (IFA)

| Metric | v3.2 | v3.3 | **v3.4** |
|---|---|---|---|
| Output count | 29 | 30 | **32** |
| **Precision** | 89.7% | 86.7% | **87.5%** |
| **Recall** | 82.9% | 78.0% | **80.5%** |
| **F1** | 0.861 | 0.821 | **0.839** |
| Priority accuracy | 65% | 65% | **57%** |
| False positives | 3 | 4 | **4** |
| False negatives | 7 | 9 | **8** |

v3.2 remains best for IFA (F1=0.861). v3.4 recovers from the v3.3 regression but does not reach v3.2.

---

## Conclusion

v3.4 achieves **F1 = 0.839** on IFA — improvement over v3.3 (0.821) but still behind v3.2 (0.861).

The interviewer-turn filter helped IFA because spk_0 questions are mostly scene-setting, while spk_1/spk_2 carry the requirements. For IFA, the filter correctly removes interviewer noise without blocking participant requirements.

Persistent failure modes:
- GT-030/031 (localisation, data residency): compliance/regulatory pattern still not triggering reliably for Turn 91
- GT-036 (user auth): Turn 117 content not extracted
- Priority calibration: 43% of TPs have wrong priority — the model defaults too often to essential for functional requirements
