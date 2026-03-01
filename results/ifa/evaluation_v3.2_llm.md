# Pipeline Evaluation v3.2 (Cerebras / gpt-oss-120b + deduplication) — IFA conversation_02

## Dataset

- **Source**: IFA stakeholder requirements elicitation session
- **File**: `datasets/ifa/conversation.txt`
- **Ground truth**: `datasets/ifa/expected.json` — 41 requirements
- **Output**: `results/ifa/output_v3.2_llm.json`
- **Model**: gpt-oss-120b via Cerebras inference API

## What changed from v3.1

- New Stage 4b: LLM deduplication call added between rewrite and structure.
- After all candidates are rewritten, a single LLM batch call receives every
  normalised statement and returns the indices of semantic duplicates to remove.
- No changes to extraction prompt, rewrite prompt, or model.

---

## Summary

### Detection accuracy

| Metric | v2.0 (LLM 70B) | v3.1 (LLM 120B) | **v3.2 (120B + dedup)** |
|---|---|---|---|
| Ground-truth requirements | 41 | 41 | 41 |
| Pipeline output count | 23 | 32 | **29** |
| True positives (distinct outputs → GTs) | 21 | 28 | **26** |
| GTs covered (incl. merged) | 22 | 35 | **34** |
| False positives | 2 | 4 | **3** |
| False negatives | 19 | 6 | **7** |
| **Precision** | 91.3% | 87.5% | **89.7%** |
| **Recall** | 53.7% | 85.4% | **82.9%** |
| **F1** | 0.676 | 0.864 | **0.861** |

### Priority accuracy

| Metric | v3.1 | **v3.2** |
|---|---|---|
| Priority distribution (output) | 20E / 12P / 0O | **17E / 12P / 0O** |
| GT distribution (relevant TPs) | 28E / 7P / 2O | 28E / 7P / 2O |
| Priority correct (of TPs) | 64% | **65%** |

---

## What deduplication removed

The dedup LLM call identified 2 semantic duplicates and removed them:

| Removed statement | Duplicate of | Notes |
|---|---|---|
| "The system shall require that schedule changes receive approval…" (Turn 48) | REQ-017 (Turn 43, GT-019) | Second extraction of the schedule-override approval requirement from an adjacent discussion turn |
| "The system shall allow the IFA to appoint and register referees." (Turn 123) | REQ-029 (Turn 121, GT-038) | REQ-029 already covers referee registration as part of its merged statement |

Both removals are correct — the dedup kept the more complete/earlier statement in each case.

---

## False Positives (3)

| REQ | Reason |
|---|---|
| REQ-004 | "allow the financial team to access the financial data of the teams" — Turn 6 (spk_2, developer); developer paraphrased the stakeholder's requirement; no independent GT. Dedup did not catch this because REQ-005 (the nearest match) covers GT-004 from a different angle. |
| REQ-011 | "restrict each team to access only its own data" — Turn 29; second half of GT-005 already covered by REQ-010 from the same turn. The dedup did not identify this as a duplicate because the two statements use different phrasing (insert vs access). |
| REQ-018 | "enforce minimum gap days between matches as defined in the policy" — Turn 50 (spk_0, interviewer turn); GT-014 already covered by REQ-013 (Turn 31). Also extracted from an interviewer question rather than stakeholder statement. |

---

## False Negatives (7) — GTs missed

| GT | Missed requirement | Why missed |
|---|---|---|
| GT-009 | Record game events with timestamps | High-level referee mobile access extracted (GT-007) but detailed event schema not surfaced; same miss as v3.1 |
| GT-013 | Automatic game scheduling per league/season | REQ-013 covers "define scheduling policies" (GT-014) but automatic scheduling as a distinct system behaviour was not extracted in this run |
| GT-024 | Players manage own social network page | Not extracted — Turn 96 brief aside, no demand language; same miss as v3.1 |
| GT-030 | Localisation: language, currency, timezone | Not extracted — stated as background assumption; same miss as v3.1 |
| GT-031 | Data residency regulations | Not extracted — same pattern as GT-030; same miss as v3.1 |
| GT-033 | Cloud hosting with outsourced development | Not extracted — framed as assumption; same miss as v3.1 |
| GT-036 | User registration and authentication | Not extracted in this run — Turn 117 was not identified as a requirement-bearing turn by the extractor (extraction variability; covered in v3.1) |

---

## Comparison: all IFA versions

| Metric | v1.0 Naive | v1.1 LLM 7B | v1.2 LLM 7B+Ctx | v2.0 LLM 70B | v3.1 LLM 120B | **v3.2 LLM 120B** |
|---|---|---|---|---|---|---|
| Model | — | Qwen 7B | Qwen 7B | Llama 3.3 70B | gpt-oss-120b | **gpt-oss-120b** |
| LLM stages | — | Stage 4 | Stage 4 | Stage 4 | Stages 2+3+4 | **Stages 2+3+4+4b** |
| Output count | 67 | 41 | 31 | 23 | 32 | **29** |
| **Precision** | 40.3% | 75.6% | 80.6% | 91.3% | 87.5% | **89.7%** |
| **Recall** | 65.9% | 70.7% | 61.0% | 53.7% | 85.4% | **82.9%** |
| **F1** | 0.500 | 0.731 | 0.694 | 0.676 | 0.864 | **0.861** |
| Usable outputs | 0% | 61% | 81% | 91% | 100% | **100%** |
| Priority accuracy | — | — | 34% | 57% | 64% | **65%** |
| False positives | 40 | 10 | 6 | 2 | 4 | **3** |
| False negatives | 14 | 12 | 16 | 19 | 6 | **7** |
| GTs covered | 27 | 29 | 25 | 22 | 35 | **34** |

---

## Conclusion

v3.2 reduces false positives from 4 to **3** and improves precision from 87.5% to
**89.7%** by correctly removing two semantic duplicates: the Turn 48 schedule-
approval restatement and the Turn 123 referee-registration duplicate.

F1 is **0.861** — essentially unchanged from v3.1's 0.864. Recall dropped
marginally (85.4% → 82.9%), accounting for one additional missed GT (GT-013:
automatic scheduling, GT-036: user authentication). Both misses are due to
**extraction variability** in this run, not deduplication — GT-013 and GT-036
were covered in v3.1 by the extractor identifying the relevant turns.

The deduplication stage is conservative by design: it flagged only clear
semantic duplicates and left borderline cases (REQ-004 developer rephrasing,
REQ-011 same-turn split of GT-005) in place. A tighter same-turn filter could
catch REQ-011, but risks incorrectly collapsing genuinely distinct same-turn
requirements.

| Problem | Impact | Root cause |
|---|---|---|
| Developer rephrasing (REQ-004) | 1 FP | spk_2 paraphrase; no GT for developer-initiated statement |
| Same-turn split (REQ-011) | 1 FP | Different phrasing for same GT; dedup missed due to vocabulary gap |
| Interviewer-turn extraction (REQ-018) | 1 FP | Extractor picked up constraint from interviewer summary, not stakeholder |
| Implicit NF constraints (GT-030, 031, 033) | 3 FNs | Background assumptions without modal verbs |
| GT-036 (user auth) missed this run | 1 FN | Extraction variability; covered in v3.1 |
| GT-013 (auto scheduling) missed this run | 1 FN | Extraction variability; covered in v3.1 |
