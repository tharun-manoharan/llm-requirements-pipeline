# Pipeline Evaluation v3.3 (Cerebras / gpt-oss-120b — prompt improvements) — IFA conversation_02

## Dataset

- **Source**: IFA stakeholder requirements elicitation session
- **File**: `datasets/ifa/conversation.txt`
- **Ground truth**: `datasets/ifa/expected.json` — 41 requirements
- **Output**: `results/ifa/output_v3.3_llm.json`
- **Model**: gpt-oss-120b via Cerebras inference API

## What changed from v3.2

- `pipeline/extract.py` temperature changed from 0.1 → 0.0 (reproducible extraction).
- Extraction prompt updated with:
  1. Two new "look for" patterns: (a) compliance/regulatory constraints stated as background
     facts, (b) features of an existing system the participant endorses as desirable.
  2. Two new "do not extract" patterns: (a) operational context that is not a system feature
     (team sizes, shift patterns, physical environment), (b) engineering/maintenance processes.
  3. Simplified "single vs multiple requirements" guidance replacing the previous v3.1 single
     instruction — emphasises splitting only genuinely different capabilities, not two attributes
     of the same feature in the same sentence.
- No changes to rewrite prompt, dedup prompt, or model.

---

## Summary

### Detection accuracy

| Metric | v3.1 (LLM 120B) | v3.2 (120B + dedup) | **v3.3 (120B + prompt)** |
|---|---|---|---|
| Ground-truth requirements | 41 | 41 | 41 |
| Pipeline output count | 32 | 29 | **30** |
| True positives | 28 | 26 | **26** |
| GTs covered (incl. merged) | 35 | 34 | **32** |
| False positives | 4 | 3 | **4** |
| False negatives | 6 | 7 | **9** |
| **Precision** | 87.5% | 89.7% | **86.7%** |
| **Recall** | 85.4% | 82.9% | **78.0%** |
| **F1** | 0.864 | 0.861 | **0.821** |

### Priority accuracy

| Metric | v3.2 | **v3.3** |
|---|---|---|
| Priority distribution (output) | 17E / 12P / 0O | **19E / 11P / 0O** |
| GT distribution | 28E / 7P / 2O | 28E / 7P / 2O |
| Priority correct (of TPs) | 65% | **65%** |

---

## False Positives (4)

| REQ | Reason |
|---|---|
| REQ-004 | "allow administrative users to view diverse transactions" (Turn 7, spk_2 developer) — GT-004 already covered by REQ-003 from Turn 6; developer paraphrasing creates near-duplicate |
| REQ-015 | "require approval from two IFA reviewers for any schedule change" (Turn 48) — GT-019 already covered by REQ-014 (Turn 43); second extraction from a different turn discussing the same constraint |
| REQ-016 | "enforce a minimum gap of two days between matches" (Turn 53, spk_0 interviewer) — GT-014 already covered by REQ-010 (Turn 31); extracted from an interviewer question rather than stakeholder statement |
| REQ-030 | "deliver all notifications within the application and not via email" (Turn 66) — no GT match; describes notification channel preference not captured in ground truth |

## False Negatives (9) — GTs missed

| GT | Missed requirement | Why missed |
|---|---|---|
| GT-006 | IFA can view all monetary information but not perform operations | REQ-009 covers the team-side restriction; the IFA view-only constraint was not extracted separately from Turn 29 in this run |
| GT-009 | Record game events with timestamps and event-specific details | Turn 17 extracted as REQ-005 (referee real-time insertion); the detailed event schema not separately surfaced; same miss as v3.2 |
| GT-013 | Automatic scheduling of games per league per season | Turn 31 extracted as REQ-010 (scheduling policies); automatic scheduling as a distinct behaviour not extracted; same miss as v3.2 |
| GT-027 | Real-time, high-priority responsiveness for referee interface | Turn 80 extracted as REQ-024 (1–2 second response time); referee real-time priority not separately extracted |
| GT-030 | Localisation: language, currency, timezone | Turn 91 not extracted in this run; same pattern as v3.1/v3.2; implicit compliance constraint |
| GT-031 | Data residency regulations | Same pattern as GT-030 |
| GT-033 | Cloud hosting with outsourced development | Framed as assumption; same miss across all versions |
| GT-036 | User registration and authentication | Turn 117 not extracted in this run; extraction variability |
| GT-039 | Teams manage their own players, coaches, stadium | Turn 121 extracted as REQ-029 covering IFA powers (leagues, seasons, referees); team resource management not included |

---

## What v3.3 improved over v3.2

**Requirement consolidation**: Several compound GTs that were split across two outputs in v3.2
are now correctly captured in a single statement:
- REQ-001 unifies GT-001 (team budget management) + GT-002 (IFA monitoring) from Turn 3
- REQ-009 unifies both halves of GT-005 (team-only insertion + own-data access) from Turn 29
- REQ-014 unifies both parts of GT-019 (rationale + second-representative confirmation) from Turn 43
- REQ-021 unifies GT-008 + GT-034 (referee-only updates + data coherence) from Turn 73
- REQ-022 unifies GT-023 + GT-041 (fan custom alerts + automatic reminders) from Turn 78

**Reproducibility**: temperature=0.0 makes extraction deterministic and eliminates run-to-run
variability in candidate sets.

## Where v3.3 is worse than v3.2

**Recall: 82.9% → 78.0%.** Two additional GTs missed compared to v3.2:
- **GT-027** (referee real-time responsiveness) merged into the single REQ-024 response-time
  statement rather than extracted separately.
- **GT-039** (team resource management) not extracted from Turn 121, which focused on IFA powers.

**F1: 0.861 → 0.821.** The recall drop is not compensated by precision improvement. The
extraction produced one additional FP (REQ-015, a Turn 48 near-duplicate of GT-019) compared
to v3.2.

**GT-030/031 (localisation/data residency) still missed.** These were covered in early
v3.3 iterations but not in this final run. The implicit NF constraint pattern in the prompt
should catch these but the extraction did not surface Turn 91 in this run.

---

## Conclusion

v3.3 achieves **F1 = 0.821** — lower than v3.2's 0.861. The temperature=0.0 stabilisation
is a net gain. The prompt improvements that consolidate compound requirements are clearly
beneficial (fewer near-duplicate outputs for GT-001/002, GT-005, GT-019). However, this
consolidation also causes recall regressions: requirements that were separately extracted in
v3.2 (GT-027, GT-039) are now subsumed into a merged statement that covers the more prominent
GT and misses the secondary one.

v3.3 is the recommended version for Bristol-style unstructured interviews (see N1 evaluation:
F1 improved from 0.719 → 0.757). For the IFA structured elicitation dataset, v3.2 remains
the best result.

| Problem | Impact | Root cause |
|---|---|---|
| Developer paraphrase (REQ-004) | 1 FP | Turn 6 developer rephrasing; no independent GT |
| Adjacent-turn near-duplicate (REQ-015) | 1 FP | Turn 48 re-states Turn 43 override requirement |
| Interviewer-turn extraction (REQ-016) | 1 FP | Turn 53 minimum-gap question by interviewer |
| In-app notification channel (REQ-030) | 1 FP | No GT for delivery channel preference |
| IFA view-only (GT-006) missed | 1 FN | Merged into REQ-009 which focuses on team restrictions |
| Referee real-time priority (GT-027) | 1 FN | Subsumed into general response-time REQ-024 |
| Localisation / data residency (GT-030/031) | 2 FNs | Turn 91 not extracted in this run |
| User auth (GT-036) | 1 FN | Extraction variability on Turn 117 |
| Team resource management (GT-039) | 1 FN | Turn 121 focused on IFA powers, team management not extracted |
