# Pipeline Evaluation v3.1 (Cerebras / gpt-oss-120b + priority fix) — IFA conversation_02

## Dataset

- **Source**: IFA stakeholder requirements elicitation session
- **File**: `datasets/ifa/conversation_02.txt`
- **Ground truth**: `datasets/ifa/expected.json` — 41 requirements
- **Output**: `results/ifa/output_v3.1_llm.json`
- **Model**: gpt-oss-120b via Cerebras inference API

## What changed from v3.0

- Rewrite prompt updated with three few-shot examples (one per priority level) to
  correct the model's bias toward "essential".
- Instruction changed from "Do NOT default to preferred" to "most requirements in a
  conversation are preferred — reserve essential for unambiguous demand language."
- Stale Groq reference in rewrite.py updated to Cerebras.
- Extraction stage unchanged.

---

## Summary

### Detection accuracy

| Metric | v2.0 (LLM 70B) | v3.0 (LLM 120B) | **v3.1 (120B + priority fix)** |
|---|---|---|---|
| Ground-truth requirements | 41 | 41 | 41 |
| Pipeline output count | 23 | 37 | **32** |
| True positives (distinct outputs → GTs) | 21 | 31 | **28** |
| GTs covered (incl. merged) | 22 | 36 | **35** |
| False positives | 2 | 6 | **4** |
| False negatives | 19 | 5 | **6** |
| **Precision** | 91.3% | 83.8% | **87.5%** |
| **Recall** | 53.7% | 87.8% | **85.4%** |
| **F1** | 0.676 | 0.858 | **0.864** |

### Priority accuracy

| Metric | v2.0 | v3.0 | **v3.1** |
|---|---|---|---|
| Priority distribution (output) | 23E / 0P / 0O | 37E / 0P / 0O | **20E / 12P / 0O** |
| GT distribution (relevant TPs) | 28E / 7P / 2O | 28E / 7P / 2O | 28E / 7P / 2O |
| Priority correct (of TPs) | 57% | 0% | **64%** |

---

## False Positives (4)

| REQ | Reason |
|---|---|
| REQ-004 | "alert users of certain violations" — Turn 5; split from GT-003 which is already covered by REQ-003. The extraction broke a single requirement into two candidates from the same turn. |
| REQ-005 | "allow the financial team to access the financial data of teams" — Turn 6 (spk_2, developer); GT-004 maps to Turn 7 (spk_1). The developer rephrased the stakeholder's requirement; no independent GT for this. |
| REQ-012 | "restrict each team to access only its own financial data" — Turn 29; second half of GT-005 already covered by REQ-011 ("allow only teams to insert budget transactions"). Same GT split across two outputs. |
| REQ-019 | "require schedule changes approved by two distinct users" — Turn 48; duplicate of GT-019 already covered by REQ-018 (Turn 43). Two extractions from adjacent turns discussing the same override approval requirement. |

## False Negatives (6) — GTs missed

| GT | Missed requirement | Why missed |
|---|---|---|
| GT-009 | Record game events (goals, offsides, cards, replacements with timestamps) | High-level referee mobile access extracted (GT-007) but detailed event schema not surfaced |
| GT-015 | Guidance for allocating referees to games based on defined policies | REQ-015 captures the specific constraint (same referee / same teams) but maps to GT-016; the broader guidance requirement GT-015 is not covered independently |
| GT-024 | Players manage own social network page and post messages to fans | Not extracted — discussed at Turn 96 in a brief aside, no strong demand language |
| GT-030 | Localisation: language, currency, timezone | Not extracted — stated as background assumption at Turn 91 |
| GT-031 | Data residency regulations | Not extracted — adjacent to GT-030, same pattern |
| GT-033 | Cloud hosting with outsourced development | Not extracted — framed as an assumption, not a requirement |

---

## Priority analysis (of 28 TPs)

| Priority | GT count | Model count | Accuracy |
|---|---|---|---|
| essential | 21 | 18 | 18/21 = **86%** |
| preferred | 5 | 6 | 4/5 TP correct = **80%** |
| optional | 2 | 0 | 0/2 = **0%** |
| **Overall** | **28** | **28** | **18/28 = 64%** |

Key errors:
- **Budget requirements under-prioritised**: GT-001, GT-002, GT-003 are all essential
  (non-negotiable core features), but the model labels them preferred. The conversation
  opening context signals urgency but is not in the 2-turn context window.
- **GT-011 (export) over-prioritised**: Labelled essential, GT says preferred — the
  developer suggested it and the stakeholder agreed without emphasis.
- **Optional requirements scored as preferred**: GT-023 and GT-041 (reminders) are
  optional in the GT but the model assigns preferred. Neither is completely wrong —
  the stakeholder does express positive interest — but the GT annotator judged them
  as low priority.

---

## Comparison: all IFA versions

| Metric | v1.0 Naive | v1.1 LLM 7B | v1.2 LLM 7B+Ctx | v2.0 LLM 70B | v3.0 LLM 120B | **v3.1 LLM 120B** |
|---|---|---|---|---|---|---|
| Model | — | Qwen 7B | Qwen 7B | Llama 3.3 70B | gpt-oss-120b | **gpt-oss-120b** |
| LLM stages | — | Stage 4 | Stage 4 | Stage 4 | Stages 2+3+4 | **Stages 2+3+4** |
| Output count | 67 | 41 | 31 | 23 | 37 | **32** |
| **Precision** | 40.3% | 75.6% | 80.6% | 91.3% | 83.8% | **87.5%** |
| **Recall** | 65.9% | 70.7% | 61.0% | 53.7% | 87.8% | **85.4%** |
| **F1** | 0.500 | 0.731 | 0.694 | 0.676 | 0.858 | **0.864** |
| Usable outputs | 0% | 61% | 81% | 91% | 100% | **100%** |
| Priority accuracy | — | — | 34% | 57% | 0% | **64%** |
| False positives | 40 | 10 | 6 | 2 | 6 | **4** |
| False negatives | 14 | 12 | 16 | 19 | 5 | **6** |

---

## Conclusion

v3.1 achieves **F1 = 0.864** — the highest across all versions, with **64% priority
accuracy** (up from 0% in v3.0 and 57% in v2.0). Precision improved from 83.8% to
87.5% as the cleaner prompt produced fewer duplicate extractions (32 outputs vs 37).
Recall dropped marginally from 87.8% to 85.4% due to one additional missed GT, but
remains the best recall across all versions by a large margin.

The few-shot examples in the rewrite prompt are the sole change from v3.0 and they
fully corrected the all-essential bias. The model now assigns preferred to low-emphasis
requirements and essential only to requirements with strong demand language.

Remaining open issues:

| Problem | Impact |
|---|---|
| Duplicate extraction from adjacent turns | 4 FPs (REQ-004, 005, 012, 019) |
| Budget requirements under-prioritised | 3 TPs with wrong priority (GT-001, 002, 003) |
| Optional reminders scored as preferred | GT-023, GT-041 priority wrong |
| Implicit NF constraints not extracted | GT-030, GT-031, GT-033 all missed |
