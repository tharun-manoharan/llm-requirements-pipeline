# Pipeline Evaluation v3.7 — IFA Augmented (Contradiction Cases Added)

## Dataset

- **Source**: `datasets/ifa_augmented/conversation.txt` — IFA transcript + 58 synthetic turns
- **Ground truth**: `datasets/ifa_augmented/expected.json` — 61 requirements (41 original + 20 augmented: GT-042 to GT-061)
- **Output**: `results/ifa_augmented/output_v3.7_llm.json` — 115 requirements
- **Dedup log**: `results/ifa_augmented/output_v3.7_llm_dedup_log.json` — 15 decisions
- **FRET output**: `results/ifa_augmented/output_v3.7_llm_fret.json` — 115 FRET requirements
- **Model**: Qwen-3-235B-A22B-Instruct (Cerebras inference API)
- **Change from v3.6**: Dataset expanded from 54 synthetic turns (59 GTs) to 58 synthetic turns (61 GTs), adding 2 contradiction pairs (GT-060, GT-061). Pipeline and prompt unchanged.
- **Note**: Rate limiting during this run caused 14 rewrite fallbacks to naive mode, producing garbled REQs (see FP analysis). This inflates the FP count and is an artefact of the Cerebras free-tier rate limit, not a fundamental pipeline regression.

---

## Dataset size comparison

| Dataset | Turns | GTs | Turn increase vs original | GT increase vs original |
|---|---|---|---|---|
| IFA (original) | 127 | 41 | — | — |
| IFA Augmented v3.5 | ~135 | 47 | +6% | +15% |
| IFA Augmented v3.6 | ~179 | 59 | +41% | +44% |
| **IFA Augmented v3.7** | **~185** | **61** | **+46%** | **+49%** |

---

## Summary

### Detection accuracy

| Metric | IFA original (v3.5 best) | IFA Aug v3.5 (47 GTs) | IFA Aug v3.6 (59 GTs) | **IFA Aug v3.7 (61 GTs)** |
|---|---|---|---|---|
| Ground-truth requirements | 41 | 47 | 59 | **61** |
| Pipeline output count | 35 | 54 | 84 | **115** |
| True positives (unique GTs covered) | 39 | 39 | 52 | **56** |
| False positives | 3 | 14 | 32 | **59** |
| False negatives | 2 | 8 | 7 | **5** |
| **Precision** | **85.7%** | **74.1%** | **61.9%** | **48.7%** |
| **Recall** | **95.1%** | **83.0%** | **88.1%** | **91.8%** |
| **F1** | **0.901** | **0.783** | **0.727** | **0.636** |

### Priority accuracy

| Metric | IFA Aug v3.6 | **IFA Aug v3.7** |
|---|---|---|
| Output distribution | 60E / 15P / 9O | **73E / 33P / 9O** |
| GT distribution | 29E / 24P / 6O | **32E / 23P / 6O** |
| Priority correct (of TPs) | 75% (39/52) | **79% (44/56)** |

---

## False negatives (5 GTs not covered)

| GT | Missed requirement | Why missed |
|---|---|---|
| GT-026 | Response time of 1–2 seconds for fans and administrators | Referee real-time responsiveness extracted (GT-027) but fan/admin SLA not separately captured |
| GT-030 | Localization (language, currency, timezone) | REQ-055 covers local regulations (→ GT-031) but misses the localization feature from the same turn |
| GT-041 | Automatic reminder notifications (e.g. annual budget report) | Custom fan alerts extracted (GT-023) but budget-report reminder not extracted |
| GT-045 | The system shall not include live video streaming | Won't-have correctly filtered — exclusion constraints have no output schema representation |
| GT-053 | Multi-language user interface | REQ-087 is a garbled rewrite fallback from Turn 141; the multi-language requirement was not cleanly extracted |

GT-050 (fan comments, optional) — a FN in v3.6 — is now covered by REQ-089 ✅

---

## Why precision dropped (48.7% vs 61.9% in v3.6)

Two causes:

**1. Rate-limit rewrite fallbacks (14 garbled REQs):** The Cerebras API rate-limited heavily during this run. When retry also failed, the pipeline fell back to naive regex rewriting, producing statements like "The system shall the teams, for example, and uh on the IFA administrative would work with computers..." (REQ-033). These 14 garbled requirements are all FPs. Without them, precision would be approximately 56/101 = 55.4%.

Garbled REQs: REQ-033, REQ-034, REQ-038, REQ-039, REQ-042, REQ-047, REQ-050, REQ-054, REQ-060, REQ-068, REQ-086, REQ-087, REQ-098, REQ-101.

**2. Expanded duplicate turns:** The additional synonym and near-duplicate turns (DEDUP-004 to DEDUP-017) that were not caught by dedup produce further FPs. This is the same pattern as v3.6, but with more cases.

---

## Deduplication test case results

| Case | Type | Expected action | Actual outcome | Verdict |
|---|---|---|---|---|
| DEDUP-001 | Exact synonym | Remove (dup of GT-007) | REQ-079 (Turn 129) kept; GT-007 covered by REQ-006 | ❌ MISS |
| DEDUP-002 | Near-duplicate | Remove (dup of GT-020) | REQ-080 (Turn 131) kept; GT-020 covered by REQ-030 | ❌ MISS |
| DEDUP-003 | Distinct pair | Keep both (GT-046, GT-047) | REQ-081 + REQ-082 both kept | ✅ CORRECT |
| DEDUP-004 | Exact synonym | Remove (dup of GT-001) | Removed by dedup | ✅ CORRECT |
| DEDUP-005 | Exact synonym | Remove (dup of GT-013) | REQ-093 (Turn 148, interviewer) kept; provides best GT-013 coverage | ❌ MISS (beneficial) |
| DEDUP-006 | Exact synonym | Remove (dup of GT-014) | REQ-094 (Turn 151) kept; provides strong GT-014 coverage | ❌ MISS (beneficial) |
| DEDUP-007 | Exact synonym | Remove (dup of GT-019) | REQ-095 (Turn 152 interviewer) extracted; Turn 153 not clearly in output | ✅ PARTIAL |
| DEDUP-008 | Exact synonym | Remove (dup of GT-025) | REQ-096 (Turn 155) kept; only GT-025 coverage | ✅ PARTIAL |
| DEDUP-009 | Exact synonym | Remove (dup of GT-036) | REQ-097 (Turn 156 interviewer) in output; Turn 157 content not present | ✅ PARTIAL |
| DEDUP-010 | Exact synonym | Remove (dup of GT-037) | REQ-098 (Turn 159) survived as garbled rewrite FP; GT-037 covered by REQ-069 | ❌ MISS |
| DEDUP-011 | Near-duplicate | Remove (dup of GT-003) | Removed by dedup | ✅ CORRECT |
| DEDUP-012 | Near-duplicate | Remove (dup of GT-009) | REQ-100 (Turn 163) kept; only GT-009 coverage | ❌ MISS (beneficial) |
| DEDUP-013 | Near-duplicate | Remove (dup of GT-016) | REQ-102 (Turn 165) kept; only strong GT-016 coverage | ❌ MISS (beneficial) |
| DEDUP-014 | Near-duplicate | Remove (dup of GT-020) | REQ-103 (Turn 167) kept; GT-020 covered by REQ-030 — FP | ❌ MISS |
| DEDUP-015 | Near-duplicate | Remove (dup of GT-021) | Stakeholder answer (Turn 169) removed; REQ-104 (Turn 168 interviewer) kept — GT-021 covered | ✅ CORRECT |
| DEDUP-016 | Near-duplicate | Remove (dup of GT-039) | REQ-105 (Turn 171) kept; GT-039 covered by REQ-074 — FP | ❌ MISS |
| DEDUP-017 | Near-duplicate | Remove (dup of GT-035) | Removed by dedup | ✅ CORRECT |
| DEDUP-018 | Distinct pair | Keep both (GT-054, GT-055) | REQ-107 + REQ-108 both kept | ✅ CORRECT |
| DEDUP-019 | Distinct pair | Keep both (GT-056, GT-057) | REQ-109 + REQ-110 both kept | ✅ CORRECT |
| DEDUP-020 | Distinct pair | Keep both (GT-058, GT-059) | REQ-111 + REQ-112 both kept | ✅ CORRECT |

**Dedup score: 8 correct, 3 partial, 9 miss (40% correct, up from 35% in v3.6)**

Notable improvement: DEDUP-020 (GT-058/GT-059 distinct pair) was incorrectly removed in v3.6 but correctly kept in v3.7. GT-050 (fan comments) moves from FN to TP.

---

## Contradiction test case results

Both contradiction pairs survived dedup and appear in the pipeline output — the correct behaviour for end-to-end FRET testing.

| Case | Requirement A | Requirement B | Both in output? | FRET-detectable? |
|---|---|---|---|---|
| CONTRA-001 | REQ-011 (GT-010) | REQ-114 (GT-060) | ✅ Yes | ⚠️ PARTIAL |
| CONTRA-002 | REQ-093 (GT-013) | REQ-115 (GT-061) | ✅ Yes | ❌ NO |

### CONTRA-001 detail

| | REQ-011 | REQ-114 |
|---|---|---|
| Statement | "The system shall allow unregistered users to access game-related data such as results, goals, and red cards." | "The system shall not allow unregistered users to access game data or results." |
| FRETish | `the system shall always satisfy unregistered_user_game_data_access` | `the system shall never satisfy unregistered_user_access` |
| Timing | `always` | `never` |
| Response var | `unregistered_user_game_data_access` | `unregistered_user_access` |

**Result**: Timing keywords are correct (always vs never) but response variables differ (`unregistered_user_game_data_access` vs `unregistered_user_access`). FRET's realizability checker requires `G(X) ∧ G(!X)` — i.e., the same variable X under both polarities. Because the variable names differ, FRET would NOT automatically flag this as a contradiction. The conflict would require a human to notice the semantic overlap, or a post-processing step to normalise variable names.

### CONTRA-002 detail

| | REQ-093 | REQ-115 |
|---|---|---|
| Statement | "The system shall automatically generate the season schedule for each league at the start of the season." | "The system shall not generate schedules automatically; schedules shall be created manually by administrators." |
| FRETish | `at the start of the season the system shall immediately satisfy season_schedule_generated` | `the system shall never satisfy automatic_schedule_generation` |
| Timing | `immediately` | `never` |
| Response var | `season_schedule_generated` | `automatic_schedule_generation` |

**Result**: Both timing keywords and response variables differ. The LLM assigned `season_schedule_generated` to the affirmative requirement (framing it as a triggered event) and `automatic_schedule_generation` to the negation. FRET would NOT detect this contradiction.

### Contradiction detection conclusion

Neither contradiction pair is directly detectable by FRET's realizability checker in the current pipeline output. The root cause is **response variable inconsistency**: the LLM assigns independently-named variables to semantically related concepts depending on phrasing context. For FRET contradiction detection to work, a response variable normalisation pass would be needed — ensuring that requirements about the same system behaviour use the same `response_var` regardless of surface phrasing. This confirms the finding in `results/fret_investigation.md`.

---

## Priority extraction test results

| Expression type | GT | GT priority | REQ | REQ priority | Correct? |
|---|---|---|---|---|---|
| "must have" (audit log) | GT-042 | essential | REQ-075 | essential | ✅ |
| "should" (financial dashboard) | GT-043 | preferred | REQ-077 | essential | ❌ over-prioritised |
| "could" (public API) | GT-044 | optional | REQ-078 | optional | ✅ |
| "definitely not building" (video streaming) | GT-045 | optional | — | filtered | ✅ correctly excluded |
| "at minimum must", "hard requirement" | GT-048 | essential | REQ-083 | essential | ✅ |
| "absolutely critical", "non-negotiable" | GT-052 | essential | REQ-084 | essential | ✅ |
| "ideally yes", "not essential for day one" | GT-049 | preferred | REQ-085 | preferred | ✅ |
| "might be nice but not a priority" | GT-050 | optional | REQ-089 | optional | ✅ |
| "potentially in future phases", "out of scope" | GT-051 | optional | REQ-091 | optional | ✅ |
| "important but not needed for first release" | GT-053 | preferred | — | not extracted (garbled) | ❌ FN |

**Priority test summary: 8/9 correct** (GT-043 over-prioritised; GT-053 not extracted; GT-045 correctly filtered). Improvement over v3.6 (7/9) — GT-050 is now correctly extracted and prioritised as optional.

---

## Key findings

### What improved from v3.6

- **Recall**: 91.8% vs 88.1% — 2 fewer FNs. GT-050 (fan comments) moved from FN to TP.
- **Dedup**: 8/20 correct vs 7/20 in v3.6. DEDUP-004 and DEDUP-011 correctly removed in v3.7. DEDUP-020 (distinct pair GT-058/GT-059) no longer incorrectly removed.
- **Priority extraction**: 8/9 correct vs 7/9 in v3.6.
- **Contradiction pairs**: Both GT-060 and GT-061 extracted and survive to FRET output (correct behaviour).

### What worsened

- **Precision**: 48.7% vs 61.9% — primarily due to 14 garbled rewrite fallbacks from rate limiting, and more dedup failures from the expanded synonym/near-dup turns.
- **Output count**: 115 vs 84 — the larger transcript generates more extraction candidates.

### Contradiction detection: why it failed

The pipeline correctly extracts both sides of each contradiction, but the FRET translation assigns different `response_var` names to semantically equivalent concepts. This is a systematic issue: the LLM names variables based on local phrasing context without awareness of previously assigned variable names. Two solutions:
1. **Post-processing normalisation**: after FRET translation, run a second LLM pass that consolidates semantically equivalent `response_var` names across requirements.
2. **Prompted variable reuse**: include already-assigned `response_var` names in the FRET prompt context so the LLM can reuse them when appropriate.

### Precision note on rate-limit fallbacks

The 14 garbled REQs (REQ-033, REQ-034, REQ-038, REQ-039, REQ-042, REQ-047, REQ-050, REQ-054, REQ-060, REQ-068, REQ-086, REQ-087, REQ-098, REQ-101) are all artefacts of the Cerebras rate limit exhausting the retry budget. These would be filtered as NOT_A_REQUIREMENT if the LLM had processed them. Excluding them gives adjusted precision = 56/101 = 55.4%, F1 = 0.699 — a more representative measure of pipeline quality.

---

## Conclusion

On the expanded augmented dataset (61 GTs, including 2 contradiction pairs), the pipeline achieves **F1 = 0.636** (P=48.7%, R=91.8%). The precision figure is substantially depressed by 14 garbled rewrite fallbacks caused by rate limiting during this run; adjusted F1 excluding these artefacts is approximately **0.699**.

**Key results from the new test cases:**

- **Contradiction extraction**: Both GT-060 and GT-061 are correctly extracted and survive dedup into the FRET output — the pipeline successfully captures requirements that contradict earlier ones.
- **Contradiction FRET detection**: Neither CONTRA-001 nor CONTRA-002 is detectable by FRET's realizability checker in the current output, because the LLM assigns different `response_var` names to the two sides of each contradiction. Response variable normalisation is required.
- **Priority extraction**: 8/9 priority signals correctly mapped — best result across all augmented evaluations.
- **Distinct-pair deduplication**: 3/3 correct (improvement from 2/3 in v3.6).

**Primary remaining issues:**
1. Exact synonym deduplication — 6+ synonym cases missed, producing FPs
2. Response variable inconsistency in FRET output — prevents automatic contradiction detection
3. Rate-limit rewrite fallbacks — produce garbled FPs; fixable by batching the rewrite stage
4. Over-prioritisation — 73/115 outputs labelled essential vs 32/61 in GT (63% vs 52%)
