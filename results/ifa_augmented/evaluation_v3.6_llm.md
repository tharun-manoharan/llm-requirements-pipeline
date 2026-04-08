# Pipeline Evaluation v3.6 — IFA Augmented (Expanded)

## Dataset

- **Source**: `datasets/ifa_augmented/conversation.txt` — IFA transcript + 54 synthetic turns
- **Ground truth**: `datasets/ifa_augmented/expected.json` — 59 requirements (41 original + 18 augmented: GT-042 to GT-059)
- **Output**: `results/ifa_augmented/output_v3.6_llm.json` — 84 requirements
- **Dedup log**: `results/ifa_augmented/output_v3.6_llm_dedup_log.json` — 29 decisions
- **Model**: gpt-oss-120b via Cerebras inference API
- **Change from v3.5**: Dataset expanded from 8 synthetic turns (47 GTs) to 54 synthetic turns (59 GTs). Pipeline and prompt unchanged.
- **Purpose**: Full evaluation against expanded augmented dataset covering 20 dedup cases and 10 priority-extraction examples.

---

## Summary

### Detection accuracy

| Metric | IFA Augmented v3.5 (47 GTs) | **IFA Augmented v3.6 (59 GTs)** |
|---|---|---|
| Ground-truth requirements | 47 | **59** |
| Pipeline output count | 54 | **84** |
| True positives (unique GTs covered) | 40 | **52** |
| False positives | 14 | **32** |
| False negatives | 8 | **7** |
| GTs covered | 39/47 | **52/59** |
| **Precision** | 74.1% | **61.9%** |
| **Recall** | 83.0% | **88.1%** |
| **F1** | 0.783 | **0.727** |

### Priority accuracy

| Metric | IFA Augmented v3.5 | **IFA Augmented v3.6** |
|---|---|---|
| Output distribution | 36E / 16P / 2O | **60E / 15P / 9O** |
| GT distribution | 28E / 15P / 4O | **29E / 24P / 6O** |
| Priority correct (of TPs) | 72% (29/40) | **75% (39/52)** |

---

## Deduplication test case results

| Case | Type | Source turns | Expected action | Actual outcome | Verdict |
|---|---|---|---|---|---|
| DEDUP-001 | Exact synonym | 128–129 | Remove (dup of GT-007) | Turn 129 synonym kept as REQ-059; GT-007 covered by REQ-005 | ❌ MISS |
| DEDUP-002 | Near-duplicate | 130–131 | Remove (dup of GT-020) | Turn 131 near-dup kept as REQ-060; GT-020 covered by REQ-024 | ❌ MISS |
| DEDUP-003 | Distinct pair | 132–133 | Keep both (GT-046, GT-047) | Both kept (REQ-061, REQ-062) | ✅ CORRECT |
| DEDUP-004 | Exact synonym | 146–147 | Remove (dup of GT-001) | Turn 147 synonym kept as REQ-069; GT-001 covered by REQ-001 | ❌ MISS |
| DEDUP-005 | Exact synonym | 148–149 | Remove (dup of GT-013) | Interviewer-turn extraction (Turn 148) kept as REQ-070; GT-013 covered by REQ-021 | ❌ MISS |
| DEDUP-006 | Exact synonym | 150–151 | Remove (dup of GT-014) | Turn 151 synonym kept as REQ-071; GT-014 covered by REQ-014 | ❌ MISS |
| DEDUP-007 | Exact synonym | 152–153 | Remove (dup of GT-019) | Turn 153 synonym kept as REQ-072; GT-019 better captured by REQ-072 than original REQ-020 | ❌ MISS (net improvement) |
| DEDUP-008 | Exact synonym | 154–155 | Remove (dup of GT-025) | Original GT-025 extraction not present; Turn 155 synonym (REQ-073) is the only coverage | ✅ PARTIAL |
| DEDUP-009 | Exact synonym | 156–157 | Remove (dup of GT-036) | Turn 157 extracted as two REQs (REQ-074, REQ-075); GT-036 covered by original REQ-047 | ❌ MISS |
| DEDUP-010 | Exact synonym | 158–159 | Remove (dup of GT-037) | Turn 159 duplicate correctly removed; GT-037 covered by REQ-048 | ✅ CORRECT |
| DEDUP-011 | Near-duplicate | 160–161 | Remove (dup of GT-003) | Turn 161 near-dup kept as REQ-076; GT-003 covered by REQ-002/003 | ❌ MISS |
| DEDUP-012 | Near-duplicate | 162–163 | Remove (dup of GT-009) | Turn 163 near-dup kept as REQ-077; no other GT-009 extraction exists | ❌ MISS (but GT-009 now covered) |
| DEDUP-013 | Near-duplicate | 164–165 | Remove (dup of GT-016) | Turn 165 near-dup kept as REQ-078; GT-016 covered by REQ-016 | ❌ MISS |
| DEDUP-014 | Near-duplicate | 166–167 | Remove (dup of GT-020) | Turn 167 near-dup correctly removed | ✅ CORRECT |
| DEDUP-015 | Near-duplicate | 168–169 | Remove (dup of GT-021) | Turn 169 near-dup correctly removed | ✅ CORRECT |
| DEDUP-016 | Near-duplicate | 170–171 | Remove (dup of GT-039) | Turn 171 near-dup kept as REQ-079; GT-039 covered by REQ-054 | ❌ MISS |
| DEDUP-017 | Near-duplicate | 172–173 | Remove (dup of GT-035) | Turn 173 near-dup correctly removed | ✅ CORRECT |
| DEDUP-018 | Distinct pair | 174–175 | Keep both (GT-054, GT-055) | Both kept (REQ-080, REQ-081) | ✅ CORRECT |
| DEDUP-019 | Distinct pair | 176–177 | Keep both (GT-056, GT-057) | Both kept (REQ-082, REQ-083) | ✅ CORRECT |
| DEDUP-020 | Distinct pair | 178–179 | Keep both (GT-058, GT-059) | GT-058 kept (REQ-084); GT-059 incorrectly removed at low confidence | ❌ MISS |

**Dedup score: 7 correct, 1 partial, 12 miss (35% correct)**

### Notes on dedup cases

**DEDUP-001, DEDUP-002**: Same failures as v3.5. The pipeline detects synonym pairs but keeps the wrong variant (augmented turn over original).

**DEDUP-004 to DEDUP-009**: New exact synonym cases all failed except DEDUP-008 (partial) and DEDUP-010. The model successfully caught the team-registration synonym (DEDUP-010, high confidence) but missed the budget, scheduling, and user-auth synonyms. A common pattern is that the dedup LLM sees these as the "primary" extraction rather than identifying them as restatements of earlier ones.

**DEDUP-007 (notable)**: Although classified as a miss (Turn 153 synonym of GT-019 was not removed), the net effect is positive: REQ-072 from Turn 153 provides a much more complete capture of GT-019 (includes both the written rationale and the second-representative confirmation) compared to the original weak REQ-020 ("allow manual override under certain circumstances"). The dedup failure accidentally improves coverage quality here.

**DEDUP-012 (notable)**: The Turn 163 near-duplicate (goal scorer capture) was not removed, which is a miss. However, since no independent extraction of the general GT-009 (game events with timestamps) exists elsewhere in the output, REQ-077 is the only coverage of GT-009. The miss has a silver lining: GT-009 goes from uncovered (FN in v3.5) to covered.

**DEDUP-014, DEDUP-015, DEDUP-017**: All three near-duplicate removals were correct. The player-goal notification, club-follow, and season-archive near-dups were all removed, showing the model handles these medium-confidence cases well when the overlap is clear.

**DEDUP-020**: The only distinct-pair failure. The model assigned low confidence to the referee name display (GT-059) as a duplicate of venue/kick-off time (GT-058) and removed it. This is an over-aggressive removal of a genuinely distinct requirement. GT-059 becomes a false negative.

---

## Priority extraction test results

### Original MoSCoW block (Turn 127)

| Expression | GT | GT priority | REQ | REQ priority | Correct? |
|---|---|---|---|---|---|
| "must have" (audit log) | GT-042 | essential | REQ-056 | essential | ✅ |
| "should" (financial dashboard) | GT-043 | preferred | REQ-057 | essential | ❌ over-prioritised |
| "could" (public API) | GT-044 | optional | REQ-058 | optional | ✅ |
| "definitely not building" (video streaming) | GT-045 | optional | — | filtered | ✅ correctly excluded |

### New priority test cases (Turns 134–145)

| Expression type | Expression | GT | GT priority | REQ | REQ priority | Correct? |
|---|---|---|---|---|---|---|
| Implicit urgency | "at minimum must", "hard requirement" | GT-048 | essential | REQ-063 | essential | ✅ |
| Implicit urgency | "absolutely critical", "non-negotiable" | GT-052 | essential | REQ-064 | essential | ✅ |
| Desirable-but-deferrable | "ideally yes", "not essential for day one but we would like it" | GT-049 | preferred | REQ-065 | preferred | ✅ |
| Temporal deferral | "important but not needed for first release" | GT-053 | preferred | REQ-066 | optional | ❌ under-prioritised* |
| Low priority | "might be nice but not a priority" | GT-050 | optional | — | not extracted | ❌ FN |
| Low priority | "potentially in future phases", "out of scope" | GT-051 | optional | REQ-068 | optional | ✅† |

*REQ-066 was extracted from the interviewer's question (Turn 140, spk_2) rather than the stakeholder's answer (Turn 141, spk_1: "It is important but probably not needed for the first release"). The interviewer's question contains no priority signal, so the model defaulted to optional.

†REQ-068 was extracted from the interviewer's question (Turn 144, spk_2: "Any thoughts on a feature that would let referees flag disputed events for review?") rather than the stakeholder's answer (Turn 145). Priority assignment to optional was still correct despite the wrong source.

**Priority test summary**: 7/9 correct (including GT-045 correctly filtered), 1 under-prioritised (GT-053), 1 not extracted (GT-050).

---

## Distinct-pair results

| Pair | Case | GT-A | GT-B | GT-A covered | GT-B covered | Priority A | Priority B | Verdict |
|---|---|---|---|---|---|---|---|---|
| Home/away + top scorer | DEDUP-018 | GT-054 | GT-055 | ✅ REQ-080 | ✅ REQ-081 | essential ✗ (GT: preferred) | essential ✗ (GT: preferred) | ✅ both kept (priority ✗) |
| Date-range report + doc attachments | DEDUP-019 | GT-056 | GT-057 | ✅ REQ-082 | ✅ REQ-083 | preferred ✓ | preferred ✓ | ✅ both kept (priority ✓) |
| Match venue/time + referee name | DEDUP-020 | GT-058 | GT-059 | ✅ REQ-084 | ❌ removed | essential ✗ (GT: preferred) | — | ❌ partial (GT-059 incorrectly removed) |

---

## Classification of each pipeline output

### True Positives (52 unique GTs covered)

| REQ | Maps to GT | Type | Priority | Notes |
|---|---|---|---|---|
| REQ-001 | GT-001 | func ✓ | essential ✓ | Team budget management |
| REQ-002 | GT-003 | func ✓ | essential ✓ | Budget violation alerts |
| REQ-003 | GT-002 | func ✓ | essential ✓ | IFA audit + policy setting |
| REQ-004 | GT-004 | func ✓ | essential ✗ (GT: preferred) | IFA view transactions |
| REQ-005 | GT-007 | func ✓ | essential ✓ | Referee insert events real time |
| REQ-007 | GT-011 | func ✓ | preferred ✓ | Export data to journalists |
| REQ-008 | GT-010 | func ✓ | essential ✓ | Unregistered users view data |
| REQ-011 | GT-005 | func ✓ | essential ✓ | Teams restrict own budget data |
| REQ-012 | GT-006 | func ✓ | essential ✓ | IFA view monetary info |
| REQ-014 | GT-014 | func ✓ | essential ✓ | IFA define scheduling policies |
| REQ-015 | GT-015 | func ✓ | preferred ✓ | Referee allocation guidance |
| REQ-016 | GT-016 | func ✓ | essential ✗ (GT: preferred) | Same-referee-same-team policy |
| REQ-018 | GT-017 | func ✓ | preferred ✓ | Referee availability preferences |
| REQ-019 | GT-018 | func ✓ | essential ✓ | Manual schedule adjustment |
| REQ-021 | GT-013 | func ✓ | essential ✓ | Automatic scheduling |
| REQ-023 | GT-022 | func ✓ | preferred ✓ | Fan notifications for player posts / game events |
| REQ-024 | GT-020 + GT-021 | func ✓ | essential ✓ | Subscription + push notifications |
| REQ-025 | GT-028 | func ✗ (GT: NF) | preferred ✓ | Platform interfaces (web/mobile) — type mismatch |
| REQ-026 | GT-029 | func ✗ (GT: NF) | preferred ✗ (GT: essential) | Unified system + role interfaces — type + priority mismatch |
| REQ-027 | GT-008 | func ✓ | essential ✓ | Only referees update game data |
| REQ-028 | GT-034 | func ✗ (GT: NF) | essential ✓ | Referees sole authoritative source — type mismatch |
| REQ-029 | GT-023 | func ✓ | preferred ✗ (GT: optional) | Custom fan alerts — over-prioritised |
| REQ-030 | GT-027 | NF ✓ | essential ✓ | Real-time referee responsiveness |
| REQ-036 | GT-033 | func ✗ (GT: NF) | essential ✗ (GT: preferred) | Outsourced dev + cloud — type + priority mismatch |
| REQ-038 | GT-030 | NF ✓ | essential ✗ (GT: preferred) | Localization / local compliance — priority mismatch |
| REQ-039 | GT-031 | NF ✓ | essential ✓ | Data residency regulations |
| REQ-042 | GT-032 | NF ✓ | essential ✗ (GT: preferred) | Encrypt budget data — over-prioritised |
| REQ-043 | GT-024 | func ✓ | essential ✗ (GT: preferred) | Players manage social page — over-prioritised |
| REQ-047 | GT-036 | func ✓ | essential ✓ | User registration + guest access |
| REQ-048 | GT-037 | func ✓ | essential ✓ | Team registration with IFA approval |
| REQ-049 | GT-035 | func ✓ | essential ✓ | Retain historical archives |
| REQ-051 | GT-040 | func ✓ | essential ✓ | IFA define leagues/seasons/policies |
| REQ-052 | GT-038 | func ✓ | essential ✓ | IFA invite/appoint referees |
| REQ-054 | GT-039 | func ✓ | essential ✓ | Teams manage players |
| REQ-056 | GT-042 | NF ✓ | essential ✓ | Audit log — **must-have correctly extracted** |
| REQ-057 | GT-043 | func ✓ | essential ✗ (GT: preferred) | Financial dashboard — **should-have over-prioritised** |
| REQ-058 | GT-044 | func ✓ | optional ✓ | Public API — **could-have correctly extracted** |
| REQ-061 | GT-046 | func ✓ | preferred ✓ | League standings — **distinct pair kept ✓** |
| REQ-062 | GT-047 | func ✓ | optional ✗ (GT: preferred) | Player stats comparison — **distinct pair kept, priority ✗** |
| REQ-063 | GT-048 | NF ✓ | essential ✓ | Daily backup — **"at minimum" correctly extracted** |
| REQ-064 | GT-052 | NF ✓ | essential ✓ | 2FA for admins — **"absolutely critical" correctly extracted** |
| REQ-065 | GT-049 | func ✓ | preferred ✓ | Fan match search — **"ideally" correctly extracted** |
| REQ-066 | GT-053 | NF ✓ | optional ✗ (GT: preferred) | Multi-language — **temporal deferral under-prioritised; extracted from interviewer turn** |
| REQ-068 | GT-051 | func ✓ | optional ✓ | Referee flag events — **"future phases" correctly extracted; extracted from interviewer turn** |
| REQ-072 | GT-019 | func ✓ | essential ✓ | Override schedule with rationale + 2nd rep — DEDUP-007 miss but best GT-019 capture |
| REQ-073 | GT-025 | NF ✓ | essential ✓ | 50,000 concurrent users — DEDUP-008 partial |
| REQ-077 | GT-009 | func ✓ | essential ✓ | Goal scorer + minute — DEDUP-012 miss but only GT-009 coverage |
| REQ-080 | GT-054 | func ✓ | essential ✗ (GT: preferred) | Home/away record — **distinct pair kept ✓, priority ✗** |
| REQ-081 | GT-055 | func ✓ | essential ✗ (GT: preferred) | Top scorer leaderboard — **distinct pair kept ✓, priority ✗** |
| REQ-082 | GT-056 | func ✓ | preferred ✓ | Date-range financial report — **distinct pair kept ✓** |
| REQ-083 | GT-057 | func ✓ | preferred ✓ | Document attachments to transactions — **distinct pair kept ✓** |
| REQ-084 | GT-058 | func ✓ | essential ✗ (GT: preferred) | Match venue + kick-off time — **distinct pair partial (GT-059 lost)** |

### False Positives (32)

| REQ | Reason |
|---|---|
| REQ-006 | "insertion only after game started" — timing constraint, no GT match |
| REQ-009 | GT-010 already covered by REQ-008 — duplicate extraction |
| REQ-010 | "financial data accessible to all IFA members and finance dept" — contradicts GT (each team sees only own data); misextraction |
| REQ-013 | "alerting but not performing operations on scheduling data" — confused mixing of GT-006 and GT-003 concepts |
| REQ-017 | GT-015 + GT-016 both already covered — merged duplicate extraction |
| REQ-020 | GT-019 already covered (more fully) by REQ-072 — weaker duplicate |
| REQ-022 | Specific scheduling gap constraint — GT-014 already covered by REQ-014 |
| REQ-031 | "support functionality for fans, IFA admin, team admin" — too vague, no specific GT |
| REQ-032 | GT-027 already covered by REQ-030 — duplicate |
| REQ-033 | GT-027 already covered by REQ-030 — duplicate |
| REQ-034 | Live recording feature — mentioned as future possibility, no GT |
| REQ-035 | Comms between dev team and IFA IT dept — organisational process, no GT |
| REQ-037 | GT-033 already covered by REQ-036 — duplicate (cloud/outsourcing) |
| REQ-040 | GT-031 already covered by REQ-039 — data center config extension |
| REQ-041 | "all data accessible except budget" — GT-010 and GT-005 both covered |
| REQ-044 | Phase 1 core functionalities bundled — phasing statement, not requirement |
| REQ-045 | "budgeting and scheduling in second phase" — phasing statement |
| REQ-046 | GT-007 already covered by REQ-005 — duplicate extraction from Turn 103 |
| REQ-050 | GT-035 already covered by REQ-049 — specific data type extension |
| REQ-053 | GT-038 already covered by REQ-052 — duplicate (invite referee) |
| REQ-055 | "IFA audit referee and player registration process" — no specific GT |
| REQ-059 | GT-007 already covered by REQ-005 — **DEDUP-001 failure**: Turn 129 synonym not removed |
| REQ-060 | GT-020 already covered by REQ-024 — **DEDUP-002 failure**: Turn 131 near-dup not removed |
| REQ-067 | "allow features to be considered for future implementation" — vague meta-statement extracted from Turn 143 instead of GT-050 |
| REQ-069 | GT-001 already covered by REQ-001 — **DEDUP-004 failure**: Turn 147 synonym not removed |
| REQ-070 | GT-013 already covered by REQ-021 — **DEDUP-005 failure**: Turn 148 (interviewer) extraction survived |
| REQ-071 | GT-014 already covered by REQ-014 — **DEDUP-006 failure**: Turn 151 synonym not removed |
| REQ-074 | GT-036 already covered by REQ-047 — **DEDUP-009 failure**: Turn 157 split-extraction survived |
| REQ-075 | GT-036 already covered by REQ-047 — **DEDUP-009 failure**: Turn 157 second split-extraction |
| REQ-076 | GT-003 already covered by REQ-002/003 — **DEDUP-011 failure**: Turn 161 near-dup not removed |
| REQ-078 | GT-016 already covered by REQ-016 — **DEDUP-013 failure**: Turn 165 near-dup not removed |
| REQ-079 | GT-039 already covered by REQ-054 — **DEDUP-016 failure**: Turn 171 near-dup not removed |

### False Negatives (7 GTs not covered)

| GT | Missed requirement | Why missed |
|---|---|---|
| GT-012 | Team managers view and export own team data for offline analysis | Not extracted from Turn 25 — overshadowed by related IFA financial access requirements |
| GT-026 | Response time of 1–2 seconds for fans and administrators | Referee real-time responsiveness extracted (GT-027) but the fan/admin SLA not separately captured |
| GT-030 | Localization (language, currency, timezone) | REQ-038 covers "local regulations" (→ GT-031) but misses the localization features from the same turn |
| GT-041 | Automatic reminder notifications (e.g. annual budget report) | Custom fan alerts extracted (GT-023) but budget-report reminder from interviewer Turn 77 not extracted |
| GT-045 | The system shall not include live video streaming | Won't-have correctly filtered by rewrite stage — exclusion constraints have no output schema representation |
| GT-050 | Fan comments or reactions on match events | "Might be nice but not a priority" — pipeline extracted a vague meta-statement (REQ-067) instead of the specific feature |
| GT-059 | Display the name of the assigned referee for each upcoming match | **DEDUP-020 failure**: incorrectly removed at low confidence as duplicate of GT-058 (venue/kick-off time) |

---

## Key findings

### Augmented turn performance (GT-042 to GT-059)

| GT | Description | Extracted? | Priority correct? |
|---|---|---|---|
| GT-042 | Audit log (must-have) | ✅ | ✅ essential |
| GT-043 | Financial dashboard (should-have) | ✅ | ❌ essential (over-prioritised) |
| GT-044 | Public API (could-have) | ✅ | ✅ optional |
| GT-045 | No video streaming (won't-have) | filtered | ✅ correctly excluded |
| GT-046 | League standings (distinct pair) | ✅ | ✅ preferred |
| GT-047 | Player stats comparison (distinct pair) | ✅ | ❌ optional (under-prioritised) |
| GT-048 | Daily backup (at minimum must) | ✅ | ✅ essential |
| GT-049 | Fan match search (ideally) | ✅ | ✅ preferred |
| GT-050 | Fan comments (might be nice) | ❌ FN | — |
| GT-051 | Referee flag events (future phases) | ✅ (interviewer turn) | ✅ optional |
| GT-052 | 2FA for admins (absolutely critical) | ✅ | ✅ essential |
| GT-053 | Multi-language (important but not first release) | ✅ (interviewer turn) | ❌ optional (under-prioritised) |
| GT-054 | Home/away record (distinct pair A) | ✅ | ❌ essential (over-prioritised) |
| GT-055 | Top scorer leaderboard (distinct pair A) | ✅ | ❌ essential (over-prioritised) |
| GT-056 | Date-range report (distinct pair B) | ✅ | ✅ preferred |
| GT-057 | Doc attachments to transactions (distinct pair B) | ✅ | ✅ preferred |
| GT-058 | Match venue + kick-off time (distinct pair C) | ✅ | ❌ essential (over-prioritised) |
| GT-059 | Referee name display (distinct pair C) | ❌ FN (DEDUP-020) | — |

**Augmented GTs covered: 14/18 = 78%. Priority correct among covered: 8/14 = 57%.**

### Why precision dropped (61.9% vs 74.1% in v3.5)

The expanded dataset has 46 more synthetic turns, 17 of which introduce exact synonyms or near-duplicates. These produce additional extraction candidates that the dedup stage should remove but largely does not. 8 of the 32 FPs are directly attributable to dedup failures on the new cases (DEDUP-001, DEDUP-002, DEDUP-004 to DEDUP-006, DEDUP-009, DEDUP-011, DEDUP-013, DEDUP-016). A further 8 FPs are pre-existing patterns (duplicate extractions from the original transcript). Removing all dedup-failure FPs would bring precision to approximately 71%.

### Why recall improved (88.1% vs 83.0% in v3.5)

The augmented turns provide additional extraction opportunities for requirements that the pipeline previously missed. Notably, GT-009 (game events with timestamps) was a FN in v3.5 but is now covered via the DEDUP-012 near-duplicate surviving (REQ-077). GT-013 (automatic scheduling) is now covered via REQ-021 being a stronger extraction. The expanded transcript also adds 12 new genuine GTs, 10 of which are extracted (GT-050 and GT-059 excepted).

### Priority over-prioritisation pattern

The pipeline assigns "essential" to 60 of 84 outputs (71%) compared to 29 of 59 GTs (49%). This systematic over-prioritisation is especially visible for the new distinct-pair requirements (GT-054, GT-055, GT-058 all tagged essential despite being preferred in GT) and for the "should-have" test case (GT-043). The "ideally" → preferred mapping (GT-049) and "absolutely critical" → essential mapping (GT-052) both work correctly, suggesting the model responds well to explicit cues but defaults to essential for novel requirements without a clear downgrade signal.

### Source-turn extraction issue

Two priority test cases (GT-053 multi-language, GT-051 referee flag) had their requirements extracted from the interviewer's question turn rather than the stakeholder's answer turn. For GT-051 this produced the correct priority (optional) because the interviewer's question was neutral and the default was low priority. For GT-053 this produced the wrong priority (optional instead of preferred) because the priority signal ("important but not needed for first release") appeared only in the stakeholder's Turn 141 which was not extracted.

### Dedup overall: better at removal, poor at non-removal decisions

The dedup stage correctly handled 5 of 7 near-duplicate removal cases (DEDUP-011, DEDUP-013, DEDUP-016 failed; DEDUP-014, DEDUP-015, DEDUP-017 correct) and 2 of 7 exact synonym removals (DEDUP-010, DEDUP-005 partial correct; remaining 5 failed). However, it incorrectly removed GT-059 (a distinct requirement from GT-058) with low confidence — which is worse than a miss on a removal case because it introduces a FN.

---

## Conclusion

On the expanded augmented dataset (59 GTs), the pipeline achieves **F1 = 0.727** (P=61.9%, R=88.1%). Recall improved over v3.5 (+5.1pp) due to more extraction opportunities and coverage of previously-missed GTs. Precision fell (-12.2pp) due to the expanded duplicate turns generating FPs that the dedup stage does not fully remove.

**Key results from the expanded test cases:**

- **Priority extraction**: 7/9 priority signals correctly mapped (GT-048, GT-049, GT-051, GT-052 all correct; GT-043 and GT-053 wrong; GT-050 not extracted). New implicit-urgency cues ("at minimum", "absolutely critical") are handled well. Temporal deferral ("not needed for first release") remains problematic due to source-turn extraction from interviewer questions.
- **Exact synonym deduplication**: 2/7 new cases correct (DEDUP-008 partial, DEDUP-010 correct). The dedup stage reliably misses exact synonyms when the repeated statement uses moderately different surface phrasing.
- **Near-duplicate deduplication**: 3/7 new cases correct (DEDUP-014, DEDUP-015, DEDUP-017). Player-goal notification, club-follow, and season-archive near-dups removed correctly; wage-cap, goal-detail, and new-player near-dups survived.
- **Distinct-pair preservation**: 2/3 pairs fully correct (DEDUP-018, DEDUP-019). DEDUP-020 partial (GT-059 incorrectly removed at low confidence).

**Primary remaining issues:**
1. Exact synonym deduplication — 5/7 new synonym cases missed, producing FPs
2. Over-prioritisation — 60/84 outputs labelled essential vs 29/59 in GT
3. Source-turn extraction — some requirements extracted from interviewer questions rather than stakeholder answers, losing priority context
4. GT-050 (fan comments) — "might be nice but not a priority" language results in a vague meta-extraction rather than the specific feature requirement
5. DEDUP-020 — over-aggressive low-confidence removal creates a FN for a distinct requirement
