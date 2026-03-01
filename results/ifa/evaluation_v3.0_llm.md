# Pipeline Evaluation v3.0 (Cerebras / gpt-oss-120b) — IFA conversation_02

## Dataset

- **Source**: IFA stakeholder requirements elicitation session
- **File**: `datasets/ifa/conversation_02.txt`
- **Ground truth**: `datasets/ifa/expected.json` — 41 requirements
- **Output**: `results/ifa/output_v3.0_llm.json`
- **Model**: gpt-oss-120b via Cerebras inference API

## What changed from v2.0

- Stages 2+3 replaced by a single LLM call (gpt-oss-120b via Cerebras) that reads
  the full conversation and identifies requirements semantically.
- Stage 4 LLM rewriter also uses gpt-oss-120b (previously Llama 3.3 70B via Groq).
- gpt-oss-120b is a 120B-parameter reasoning model — larger than the previous 70B.
- Cerebras inference: 1M tokens/day, 60K tokens/min (eliminates the rate-limit
  failures that blocked this evaluation in previous runs).

---

## Summary

### Detection accuracy

| Metric | v1.0 (Naive) | v2.0 (LLM 70B) | **v3.0 (LLM 120B)** |
|---|---|---|---|
| Ground-truth requirements | 41 | 41 | 41 |
| Pipeline output count | 67 | 23 | **37** |
| True positives (GTs covered) | 27 | 22 | **36** |
| False positives | 40 | 2 | **6** |
| False negatives | 14 | 19 | **5** |
| **Precision** | 40.3% | 91.3% | **83.8%** |
| **Recall** | 65.9% | 53.7% | **87.8%** |
| **F1** | 0.500 | 0.676 | **0.858** |

### End-to-end accuracy

| Metric | v1.0 | v2.0 | **v3.0** |
|---|---|---|---|
| Usable requirement statements | 0 / 67 (0%) | 21 / 23 (91%) | **37 / 37 (100%)** |
| Priority: all essential | — | 23/23 (100%) | **37/37 (100%)** |
| Type classification correct (of TPs) | — | ~95% | **~97%** |

*Note: priority accuracy is 0% — the model assigns "essential" to every output.
This is a known regression introduced in this version (see Analysis section).*

---

## GT coverage

### True Positives — GTs covered (36 of 41)

| REQ | Maps to GT | Notes |
|---|---|---|
| REQ-002 | GT-001 + GT-002 | Merged: team budget management AND IFA monitoring into one statement |
| REQ-003 | GT-003 | Budget policies and alert on violations |
| REQ-004 | GT-004 | "Financial team" = IFA administrators viewing all financial transactions |
| REQ-006 | GT-007 | Referees insert game events via mobile |
| REQ-007 | GT-010 | All users including guests can view game data |
| REQ-008 | GT-011 | Export data for journalists/press |
| REQ-009 | GT-012 | Team managers view and export team data |
| REQ-010 | GT-005 | Budget transaction restriction to teams only |
| REQ-011 | GT-006 | IFA view-only monetary access |
| REQ-012 | GT-013 | Automatic game scheduling |
| REQ-013 | GT-015 | Referee allocation guidance |
| REQ-014 | GT-017 | Referee availability preferences |
| REQ-015 | GT-018 | Manual schedule adjustment |
| REQ-016 | GT-019 | Schedule override with rationale + second IFA approval |
| REQ-018 | GT-014 | Scheduling policies and constraints (minimum gap days) |
| REQ-021 | GT-020 | Push notifications to fans for subscribed games |
| REQ-022 | GT-021 | Fan subscription to games, teams, players |
| REQ-023 | GT-024 | Team and player pages fans can follow |
| REQ-024 | GT-022 | Real-time notifications when game events occur |
| REQ-025 | GT-028 | Web app for admin, mobile for referees and fans |
| REQ-026 | GT-029 | Unified platform with role-based interfaces |
| REQ-027 | GT-008 + GT-034 | Only official referees update game data (sole authoritative source) |
| REQ-028 | GT-023 + GT-041 | Automated reminder notifications |
| REQ-029 | GT-025 | 50,000 concurrent user support |
| REQ-030 | GT-026 + GT-027 | Response time 1–2s general, real-time for referees (merged) |
| REQ-031 | GT-032 | Encrypt budget data |
| REQ-032 | GT-036 | User registration and authentication |
| REQ-034 | GT-037 + GT-039 | Team registration workflow + team resource management (merged) |
| REQ-035 | GT-035 | Historical data and archive retention |
| REQ-036 | GT-040 | IFA defines leagues, seasons, scheduling policies |
| REQ-037 | GT-038 | IFA registers and invites referees |

*REQ-016 also partially covers GT-016 (referee scheduling policies) through the
"no referee assigned to same team twice" constraint, but GT-016's equal distribution
criterion is not explicitly stated.*

### False Positives (6)

| REQ | Reason |
|---|---|
| REQ-001 | "provide proper budgeting functionality" — extracted from Turn 0 (developer opening remark), too generic to map to any specific GT |
| REQ-005 | Duplicate of GT-004 — "administrative users to view diverse transactions" is the same requirement as REQ-004, which already maps to GT-004 |
| REQ-017 | Duplicate of GT-019 — "schedule change approved by two IFA representatives" is extracted twice (also captured by REQ-016) from adjacent turns 43 and 47 |
| REQ-019 | Duplicate of GT-014 — "definition of parameters such as minimum gap days" is a specific instance of scheduling constraints already captured in REQ-018 |
| REQ-020 | Duplicate of GT-014 — "allow users to define scheduling parameters" is the same constraint extracted from Turn 54, already covered by REQ-018 |
| REQ-033 | "provide user profiles with usernames" — not an independent GT; user registration is covered by REQ-032 (GT-036); GT-036 does not separately specify profile/username management |

### False Negatives (5) — GTs missed

| GT | Missed requirement | Why missed |
|---|---|---|
| GT-009 | Record game events (goals, offsides, cards, replacements) with timestamp and event details | The LLM extracted the high-level requirement to record events (GT-007) but missed the detailed event-type specification at Turn 17 |
| GT-016 | Referee scheduling policies: same referee not assigned to same team too often, equal distribution | REQ-013 captures the "no duplicate same-team assignment" rule but not the equal distribution policy. Only partially covered. |
| GT-030 | Localisation: language, currency, timezone | Not extracted — discussed briefly at Turn 91 with no explicit demand phrasing |
| GT-031 | Data residency regulations (e.g. German data stays in Germany) | Not extracted — adjacent to GT-030 at Turn 91, likely lost as a non-functional implicit constraint |
| GT-033 | Cloud hosting with outsourced development | Not extracted — expressed as an assumption rather than a requirement at Turns 87–88 |

---

## Analysis

### What v3.0 improved

**Recall: 53.7% → 87.8%.** This is the primary win. LLM-based extraction in stages
2+3 identified 37 candidates semantically vs 67 by keyword matching, but the quality
is dramatically higher. The 36 GTs covered is the best recall across all versions.

**F1: 0.676 → 0.858.** A 27% relative improvement. The combined effect of better
extraction (more real requirements found) and strong rewriting quality (all 37 outputs
are usable) produces the best overall result.

**False negatives reduced from 19 to 5.** The biggest category of v2.0 FNs was
requirements hidden in noisy conversational filler — these are now found via semantic
extraction. Key examples recovered:
- GT-014 (scheduling constraints): keyword matching never saw "two days between matches"
- GT-020/021/022 (fan notifications): extracted from multi-turn discussion about subscriptions
- GT-039 (team resource management): implicit in the registration workflow description

**Merged requirements are a feature.** Several outputs (REQ-002, REQ-027, REQ-030,
REQ-034) merge two related GTs into a single coherent statement. This is arguably
better for practical use than two near-identical requirements.

**Rewrite quality: 100% usable.** All 37 outputs are clean, professional requirement
statements. Zero poor rewrites. Type classification is correct in ~97% of TPs.

### Where v3.0 still fails

**Priority is broken — all "essential".** The gpt-oss-120b model assigns "essential"
to every single output, making priority classification 0% accurate. The ground truth
has 7 preferred and 2 optional requirements among the TPs. In v2.0 with Llama 70B,
priority was 57% accurate on the IFA dataset. This is a regression introduced by
switching models. The model appears to default to "essential" despite the prompt's
explicit instruction to judge by strength of language.

**Duplicate extraction (6 FPs).** The extraction LLM correctly identifies requirement
regions, but passes multiple overlapping candidates for the same underlying requirement
(e.g. REQ-018/019/020 all capture GT-014's scheduling constraints from adjacent turns
53, 54, 55). The rewrite stage does not deduplicate. A post-processing deduplication
step would reduce FPs significantly.

**Non-functional implicit constraints still missed.** GT-030 (localisation), GT-031
(data residency), and GT-033 (cloud hosting) are all non-functional requirements
expressed as background assumptions. The extraction prompt is tuned to explicit
demands and may need a specific pattern for compliance/regulatory constraints.

---

## Comparison: all IFA versions

| Metric | v1.0 Naive | v1.1 LLM 7B | v1.2 LLM 7B+Ctx | v2.0 LLM 70B | **v3.0 LLM 120B** |
|---|---|---|---|---|---|
| Model | — | Qwen 7B | Qwen 7B | Llama 3.3 70B | **gpt-oss-120b** |
| LLM stages | — | Stage 4 | Stage 4 | Stage 4 | **Stages 2+3+4** |
| Output count | 67 | 41 | 31 | 23 | **37** |
| **Precision** | 40.3% | 75.6% | 80.6% | 91.3% | **83.8%** |
| **Recall** | 65.9% | 70.7% | 61.0% | 53.7% | **87.8%** |
| **F1** | 0.500 | 0.731 | 0.694 | 0.676 | **0.858** |
| Usable outputs | 0% | 61% | 81% | 91% | **100%** |
| Priority accuracy | — | — | 34% | 57% | **0%** |
| False positives | 40 | 10 | 6 | 2 | **6** |
| False negatives | 14 | 12 | 16 | 19 | **5** |

---

## Conclusion

v3.0 achieves **F1 = 0.858** on the IFA dataset — the highest across all versions
and a 27% improvement over v2.0's F1 of 0.676. The primary gain is recall (54% → 88%),
driven by replacing keyword matching with semantic LLM extraction. All 37 outputs are
usable requirement statements, and 36 of 41 ground-truth requirements are recovered.

The remaining bottlenecks are:

| Problem | Impact | Root cause |
|---|---|---|
| Priority always "essential" | 0% priority accuracy | gpt-oss-120b reasoning model overrides format despite prompt |
| Duplicate extraction | 5 FPs | Adjacent turns discussing same requirement extracted multiple times |
| Implicit NF constraints missed | GT-030, GT-031, GT-033 (3 FNs) | Stated as background assumptions, not explicit demands |
| Detailed event specs missed | GT-009 (1 FN) | High-level requirement extracted but detailed attributes omitted |
