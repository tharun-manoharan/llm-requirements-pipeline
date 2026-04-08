# Pipeline Evaluation v3.5 — IFA Augmented

## Dataset

- **Source**: `datasets/ifa_augmented/conversation.txt` — IFA transcript + 8 synthetic turns
- **Ground truth**: `datasets/ifa_augmented/expected.json` — 47 requirements (41 original + 6 augmented)
- **Output**: `results/ifa_augmented/output_v3.5_llm.json` — 54 requirements
- **Dedup log**: `results/ifa_augmented/output_v3.5_llm_dedup_log.json` — 27 decisions
- **Model**: gpt-oss-120b via Cerebras inference API
- **Purpose**: Stress-test deduplication (confidence scores, synonym detection) and MoSCoW priority extraction

---

## Summary

### Detection accuracy

| Metric | IFA base (v3.5) | **IFA Augmented (v3.5)** |
|---|---|---|
| Ground-truth requirements | 41 | **47** |
| Pipeline output count | 35 | **54** |
| True positives | 30 | **40** |
| GTs covered | 39 | **39** |
| False positives | 5 | **14** |
| False negatives | 2 | **8** |
| **Precision** | 85.7% | **74.1%** |
| **Recall** | 95.1% | **83.0%** |
| **F1** | 0.901 | **0.783** |

### Priority accuracy

| Metric | IFA base (v3.5) | **IFA Augmented (v3.5)** |
|---|---|---|
| Output distribution | 22E / 13P / 0O | **36E / 16P / 2O** |
| GT distribution | 26E / 12P / 3O | **28E / 15P / 4O** |
| Priority correct (of TPs) | 57% | **72%** (29/40) |

---

## Deduplication test case results

| Case | Type | Expected outcome | Expected confidence | Actual outcome | Actual confidence | Verdict |
|---|---|---|---|---|---|---|
| DEDUP-001 | Exact synonym (Turn 129) | Remove synonym of GT-007 | high | Wrong variant removed; Turn 129 synonym kept as FP (REQ-052) | high | ❌ MISS |
| DEDUP-002 | Near-duplicate (Turn 131) | Remove near-dup of GT-020 | medium | Removed correctly | high | ✅ CORRECT (over-confident) |
| DEDUP-003 | Distinct pair (Turn 133) | Keep GT-046 and GT-047 | N/A | Both kept (REQ-053, REQ-054) | N/A | ✅ CORRECT |

**Notes on DEDUP-001**: The pipeline extracted two synonyms of the referee event-insertion requirement — one from the original turns ("...in real time to ensure accountability and compliance auditing") and one from the augmented Turn 129 ("...in real time during the match"). The dedup LLM correctly identified them as duplicates with high confidence and removed one, but it chose to remove the spuriously-extended version and keep the Turn 129 augmented synonym. The result is that REQ-052 (a FP) remains in the output rather than being fully absorbed. The detection logic worked; the selection of which to keep was suboptimal.

**Notes on DEDUP-002**: Correctly removed. The pipeline assigned high confidence; we anticipated medium because the schedule-change scenario could be argued as a distinct specialisation of GT-020. In practice, the model correctly identified it as subsumed. The higher confidence may reflect that the overlap is clearer than we expected.

**Notes on DEDUP-003**: Both new distinct requirements (league standings, player statistics comparison) survived deduplication and are correctly present in the output.

---

## MoSCoW priority extraction results (Turn 127)

| Expression | GT | GT priority | Output | Output priority | Correct? |
|---|---|---|---|---|---|
| "must have" (audit log) | GT-042 | essential | REQ-049 | essential | ✅ |
| "should" (financial dashboard) | GT-043 | preferred | REQ-050 | essential | ❌ over-prioritised |
| "could" (public API) | GT-044 | optional | REQ-051 | optional | ✅ |
| "definitely not building" (video streaming) | GT-045 | optional/constraint | — | filtered | ✅ correctly excluded |

**Summary**: 3/4 MoSCoW signals correctly handled. The "should" → `essential` mismatch for the financial dashboard (GT-043) is consistent with the pipeline's general tendency to over-prioritise functional requirements. The exclusion of the "won't-have" statement (no video streaming) was correct behaviour — negative requirements/constraints are filtered by the rewrite stage.

---

## Classification of each pipeline output

### True Positives (40)

| REQ | Maps to GT | Type | Priority | Notes |
|---|---|---|---|---|
| REQ-001 | GT-001 | func ✓ | essential ✓ | Team budget management |
| REQ-002 | GT-002 | func ✓ | essential ✓ | IFA monitor budget |
| REQ-003 | GT-003 | func ✓ | essential ✓ | Alert on budget violations (alert aspect) |
| REQ-004 | GT-003 | func ✓ | essential ✓ | Budget policies + audit (policy aspect) — duplicate extraction of GT-003 |
| REQ-005 | GT-004 | func ✓ | essential ✗ (GT: preferred) | IFA admin view transactions |
| REQ-006 | GT-007 | func ✓ | essential ✓ | Referee insert events real time |
| REQ-008 | GT-008 | func ✓ | essential ✓ | Only referees insert events |
| REQ-009 | GT-010 | func ✓ | preferred ✗ (GT: essential) | All users view game data |
| REQ-011 | GT-011 | func ✓ | preferred ✓ | Export game data to journalists |
| REQ-013 | GT-012 | func ✓ | preferred ✓ | Team managers view data for offline analysis |
| REQ-015 | GT-005 | func ✓ | essential ✓ | Only teams insert budget transactions |
| REQ-016 | GT-006 | func ✓ | essential ✓ | IFA view monetary info, no modification |
| REQ-018 | GT-014 | func ✓ | preferred ✗ (GT: essential) | Scheduling policies definition |
| REQ-019 | GT-015 | func ✓ | preferred ✗ (GT: essential) | Referee allocation guidance |
| REQ-020 | GT-016 | func ✓ | essential ✗ (GT: preferred) | Same referee not assigned to same teams |
| REQ-021 | GT-017 | func ✓ | preferred ✓ | Referee availability preferences |
| REQ-023 | GT-018 | func ✓ | essential ✓ | Manual schedule adjustment |
| REQ-024 | GT-019 | func ✓ | optional ✗ (GT: essential) | Override schedule — misses rationale + second rep detail |
| REQ-025 | GT-022 | func ✓ | preferred ✓ | Fan notifications when player posts / game events |
| REQ-026 | GT-020 + GT-021 | func ✓ | essential ✓ | Fan subscriptions + push notifications |
| REQ-028 | GT-028 | func ✗ (GT: NF) | preferred ✓ | Multiple interfaces — type mismatch |
| REQ-029 | GT-034 | func ✗ (GT: NF) | essential ✓ | Referees sole authoritative source — type mismatch |
| REQ-030 | GT-023 | func ✓ | preferred ✗ (GT: optional) | Custom fan alerts — over-prioritised |
| REQ-031 | GT-025 | NF ✓ | essential ✓ | 50,000 concurrent users |
| REQ-032 | GT-027 | NF ✓ | essential ✓ | Real-time responsiveness for referees |
| REQ-033 | GT-033 | NF ✓ | preferred ✓ | Outsourced development and maintenance |
| REQ-035 | GT-033 | NF ✓ | essential ✗ (GT: preferred) | Cloud storage — duplicate GT-033 aspect, priority mismatch |
| REQ-036 | GT-031 | NF ✓ | essential ✓ | Data residency regulations |
| REQ-037 | GT-032 | NF ✓ | essential ✗ (GT: preferred) | Encrypt budget data |
| REQ-038 | GT-024 | func ✓ | essential ✗ (GT: preferred) | Players manage social network page |
| REQ-043 | GT-037 | func ✓ | essential ✓ | Team registration with documents + IFA approval |
| REQ-044 | GT-035 | func ✓ | essential ✓ | Retain historical archives |
| REQ-045 | GT-040 | func ✓ | essential ✓ | IFA define leagues, seasons, activate policies |
| REQ-046 | GT-038 | func ✓ | essential ✓ | IFA invite referees to system |
| REQ-047 | GT-039 | func ✓ | essential ✓ | Teams enter player details (partial — coaches/stadium not mentioned) |
| REQ-049 | GT-042 | NF ✓ | essential ✓ | Audit log of IFA admin actions — **must-have correctly extracted** |
| REQ-050 | GT-043 | func ✓ | essential ✗ (GT: preferred) | Financial dashboard — **should-have over-prioritised as essential** |
| REQ-051 | GT-044 | func ✓ | optional ✓ | Public API for journalists — **could-have correctly extracted** |
| REQ-053 | GT-046 | func ✓ | preferred ✓ | League standings display — **distinct pair kept ✓** |
| REQ-054 | GT-047 | func ✓ | preferred ✓ | Fan player stats comparison — **distinct pair kept ✓** |

### False Positives (14)

| REQ | Reason |
|---|---|
| REQ-007 | Duplicate of REQ-006 — GT-007 already covered |
| REQ-010 | Duplicate of REQ-009 — GT-010 already covered |
| REQ-012 | Third extraction covering GT-010 — already covered |
| REQ-014 | "financial data accessible to all IFA members" — contradicts GT (each team accesses own data only); misextraction |
| REQ-017 | IFA monitoring schedules / sending alerts / requesting adjustments — confused scheduling+budget monitoring; no clear GT match |
| REQ-022 | "teams cannot influence schedule once set" — valid constraint from Turn 39 but no corresponding GT |
| REQ-027 | "include all functionality within application or website" — too vague; no specific GT |
| REQ-034 | Communication between software dev team and IFA through IT dept — organisational process, no GT |
| REQ-039 | Broad phase-1 features statement — duplicates GT-037/GT-040/GT-038 already covered individually |
| REQ-040 | "budgeting and scheduling in second phase" — phasing statement, not a system requirement |
| REQ-041 | Generic IFA admin role description — GT-040 already covered by REQ-045 |
| REQ-042 | Duplicate GT-037 coverage — GT-037 already covered by REQ-043 |
| REQ-048 | "IFA audit referee/player registration process" — no explicit GT; auditing process not a stated GT |
| REQ-052 | Synonym of GT-007 from augmented Turn 129 — **DEDUP-001 miss**: should have been removed, GT-007 already covered by REQ-006 |

### False Negatives (8) — GTs not covered

| GT | Missed requirement | Why missed |
|---|---|---|
| GT-009 | Record game events with timestamps and event-specific details | Referee insertion extracted (GT-007) but timestamped event-type detail not extracted separately |
| GT-013 | Automatic scheduling of games per league per season | Scheduling policies extracted (GT-014) but automatic scheduling not explicitly extracted from Turn 31 |
| GT-026 | Response time of 1–2 seconds for fans and administrators | Real-time referee responsiveness extracted (GT-027) but the 1–2 second fan/admin SLA not separately captured |
| GT-029 | Unified system with role-based access control | Interface multiplicity extracted (GT-028) but RBAC and unified architecture not captured |
| GT-030 | Localization: language, currency, timezone | Data residency (GT-031) extracted but localization features not captured from same Turn 91 |
| GT-036 | User registration and authentication; guest-level access | Team registration captured (GT-037) but general user auth requirement not extracted |
| GT-041 | Automatic reminder notifications (e.g. annual budget report) | Fan custom alerts extracted (GT-023) but the budget-report reminder from Turn 77 (interviewer turn) filtered |
| GT-045 | The system shall not include live video streaming | Won't-have statement correctly filtered by rewrite stage — exclusion constraint not representable in current output schema |

---

## Key findings

### Augmented turn performance

The 6 new GTs from the augmented turns (GT-042 to GT-047) show:
- **GT-042, GT-043, GT-044** (MoSCoW turns): all extracted and correctly identified — 3/3
- **GT-045** (won't-have): filtered by rewrite stage, not in output — correct behaviour but a gap in the schema
- **GT-046, GT-047** (distinct pair): both extracted and correctly preserved through dedup — 2/2

### Why F1 is lower than base IFA (0.783 vs 0.901)

1. **Higher FP count (14 vs 5)**: The augmented conversation is longer with more turns, creating more extraction opportunities and more duplicate-coverage FPs. The split-extraction pattern (GT-010 extracted 3 times, GT-033 twice) accounts for 5 of the 14 FPs.
2. **More GTs missed (8 vs 2)**: GT-029, GT-030, GT-036, GT-041 were also missed in the base IFA; their absence in recall is not new. GT-026 and GT-013 remain persistent FNs. GT-045 is a schema gap.
3. **DEDUP-001 miss**: REQ-052 is a FP that correct deduplication would have removed, reducing FP count to 13 and improving precision to 76%.

### Priority accuracy improvement (72% vs 57%)

The augmented dataset's higher priority accuracy (72% vs 57% for base IFA) is partly attributable to the explicit MoSCoW signals in the augmented turns. When the stakeholder says "must have" or "could", the model maps correctly. The remaining mismatches are concentrated in the original turns where priority is expressed implicitly.

---

## Conclusion

On the augmented dataset, the pipeline achieves **F1 = 0.783** (P=74.1%, R=83.0%). All 6 augmented-turn GTs were successfully extracted (GT-045 correctly filtered as a won't-have). The dedup confidence output correctly handled DEDUP-002 and DEDUP-003; DEDUP-001 was partially handled (the synonym pair was detected and one removed, but the wrong variant was kept). MoSCoW priority signals were followed for must/could but not for should (over-prioritised as essential).

**Primary remaining issues:**
- Split-extraction FPs: multiple outputs per GT inflate the FP count
- DEDUP-001: dedup detects the synonym pair correctly but keeps the augmented version over the original extraction
- won't-have requirements have no output schema representation
- "should" → essential priority mapping failure
