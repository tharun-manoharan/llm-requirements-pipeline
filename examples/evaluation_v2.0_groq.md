# Pipeline Evaluation v2.0 (Groq / Llama 3.3 70B) — conversation_02.txt

## What changed from v1.2

- **Model upgrade**: Qwen/Qwen2.5-7B-Instruct (HF API) replaced with
  **Llama 3.3 70B** via **Groq API** — a 10x larger model with hardware-
  accelerated inference.
- **Speed**: 67 candidates processed in ~10 seconds (vs 3-5 minutes on HF).
- Context window (2 surrounding turns) and priority classification retained
  from v1.2 — same prompt, same pipeline stages 1-3-5.

---

## Summary

### Detection accuracy

| Metric | v1.0 Naive | v1.1 LLM 7B | v1.2 LLM 7B+Ctx | **v2.0 LLM 70B** |
|---|---|---|---|---|
| Ground-truth requirements | 41 | 41 | 41 | 41 |
| Pipeline output count | 67 | 41 | 31 | **23** |
| True positives | 27 | 31 | 25 | **21** |
| False positives | 40 | 10 | 6 | **2** |
| False negatives | 14 | 12 | 16 | **19** |
| **Precision** | 40.3% | 75.6% | 80.6% | **91.3%** |
| **Recall** | 65.9% | 70.7% | 61.0% | **53.7%** |
| **F1** | 0.500 | 0.731 | 0.694 | **0.676** |

### End-to-end accuracy

| Metric | v1.0 | v1.1 | v1.2 | **v2.0** |
|---|---|---|---|---|
| Usable statements | 0/67 (0%) | 25/41 (61%) | 25/31 (81%) | **21/23 (91%)** |
| Rewrite quality: Excellent | 0 | 0 | 0 | **2** |
| Rewrite quality: Good | 0 | 17 | 15 | **14** |
| Rewrite quality: Acceptable | 0 | 8 | 10 | **5** |
| Rewrite quality: Poor | 27 | 6 | 0 | **0** |
| Type classification correct (of TPs) | 19/27 (70%) | 24/31 (77%) | 20/25 (80%) | **16/21 (76%)** |

### Priority accuracy

| Metric | v1.2 (7B) | **v2.0 (70B)** |
|---|---|---|
| Ground truth distribution | 25 essential, 14 preferred, 2 optional | same |
| Pipeline output distribution | 0 essential, 30 preferred, 1 optional | **20 essential, 0 preferred, 3 optional** |
| Priority correct (of TPs) | ~34% | **57% (12/21)** |

The 70B model now makes meaningful priority distinctions — **57% accuracy**
vs the 7B model's 34%. However, it over-indexes on "essential" (20/23 outputs)
and never uses "preferred". The model treats most confirmed requirements as
essential and only marks vague or uncertain items as optional.

---

## Classification of each pipeline output

### True Positives (21)

| LLM ID | Maps to GT | Type | Priority | Rewrite quality | Notes |
|---|---|---|---|---|---|
| REQ-002 | GT-003 | func ✓ | essential ✓ | Acceptable | Budget policies — loses "alert on violations" |
| REQ-003 | GT-009 | func ✓ | optional ✗ (GT: essential) | Acceptable | Event timestamps — loses specific event types |
| REQ-004 | GT-010 | func ✓ | essential ✓ | Excellent | Near-verbatim match to ground truth |
| REQ-005 | GT-012 | func ✓ | essential ✗ (GT: preferred) | Good | Team offline analysis |
| REQ-006 | GT-015 | func ✓ | essential ✓ | Good | Referee allocation guidance |
| REQ-007 | GT-016/017 | func ✓ | essential ✗ (GT: preferred) | Good | Referee policy + preferences in one statement |
| REQ-008 | GT-018 | func ✓ | essential ✓ | Good | Manual schedule adjustment |
| REQ-009 | GT-019 | func ✓ | essential ✓ | Acceptable | Confirmation requirement — loses "written rationale" |
| REQ-010 | GT-019 | func ✓ | essential ✓ | Good | Duplicate of REQ-009, clearer phrasing |
| REQ-011 | GT-014 | func ✓ | essential ✓ | Good | Specific constraint — minimum gap |
| REQ-013 | GT-008/034 | func ✗ (GT-034: NF) | essential ✓ | Good | Referees as sole data source |
| REQ-014 | GT-041 | func ✓ | essential ✗ (GT: optional) | Acceptable | Annual report — loses "automatic reminder" aspect |
| REQ-015 | GT-026 | NF ✓ | essential ✗ (GT: preferred) | Acceptable | Response time — lost "1-2 seconds" |
| REQ-016 | GT-027 | func ✗ (GT: NF) | essential ✓ | Good | Referee real-time priority |
| REQ-017 | GT-027 | func ✗ (GT: NF) | essential ✓ | Good | Duplicate — event reporting priority |
| REQ-018 | GT-033 | func ✗ (GT: NF) | essential ✗ (GT: preferred) | Good | Cloud hosting |
| REQ-019 | GT-031 | func ✗ (GT: NF) | optional ✗ (GT: essential) | Acceptable | Local regulations — vague |
| REQ-020 | GT-032 | NF ✓ | optional ✗ (GT: preferred) | Excellent | Near-verbatim: budget data encryption |
| REQ-021 | GT-036 | func ✓ | essential ✓ | Good | User registration |
| REQ-022 | GT-035 | func ✓ | essential ✓ | Good | Retain past archives |
| REQ-023 | GT-040/038 | func ✓ | essential ✓ | Good | Leagues, seasons, referees, policies |

### False Positives (2)

| LLM ID | Reason |
|---|---|
| REQ-001 | Developer introduction from Turn 0 — describes project scope, not a stakeholder requirement |
| REQ-012 | Too vague — "allow parameters to be defined within it" with no specifics |

### False Negatives (19)

| GT ID | Missed requirement | Also missed in v1.1? | Also missed in v1.2? |
|---|---|---|---|
| GT-001 | Each team manages its own budget | Yes | Yes |
| GT-002 | IFA monitors and audits team budgets | Yes | Yes |
| GT-004 | IFA administrators view all team financial transactions | No | No |
| GT-005 | Budget transactions restricted to teams | Yes | Yes |
| GT-006 | IFA view but not modify monetary data | Yes | Yes |
| GT-007 | Referees insert events in real time via mobile | No | Yes |
| GT-011 | Export game data for journalists/press | No | No |
| GT-013 | Automatic scheduling of games per league | No | No |
| GT-020 | Push notifications to subscribed fans | No | No |
| GT-021 | Fans register and subscribe for notifications | No | No |
| GT-022 | Real-time fan notifications on game events | No | Yes |
| GT-023 | Fan custom alerts (5 min before game) | Yes | Yes |
| GT-024 | Players manage social network page | No | No |
| GT-025 | Support 50,000 simultaneous users | No | Yes |
| GT-028 | Web for admin, mobile for referees/fans | Yes | Yes |
| GT-029 | Unified system + RBAC | Yes | Yes |
| GT-030 | Localization (language, currency, timezone) | No | No |
| GT-037 | Team registration process | Yes | Yes |
| GT-039 | Teams manage players/coaches/stadium | No | Yes |

**Breakdown of 19 false negatives:**
- **8 upstream gaps** (stages 2-3 never detected them): GT-001, GT-002, GT-005,
  GT-006, GT-023, GT-028, GT-029, GT-037
- **11 over-filtered by LLM** (stages 2-3 found them but the 70B model rejected
  them as NOT_A_REQUIREMENT): GT-004, GT-007, GT-011, GT-013, GT-020, GT-021,
  GT-022, GT-024, GT-025, GT-030, GT-039

---

## Analysis

### What the 70B model improved

**1. Near-zero false positives (2 vs 6/10/40).** Only 2 of 23 outputs are
invalid — a developer introduction and a vague parameter statement. This is
the cleanest output of any version. Precision hit **91.3%**.

**2. Zero poor-quality rewrites.** Every TP is usable as a requirement
statement (21/21). No garbled transcription artifacts, no hallucinated features.
The 70B model produces professional, clean English consistently.

**3. Priority actually works.** 57% priority accuracy vs 34% with the 7B model.
The model correctly identifies most core requirements as "essential" and uses
"optional" for uncertain items. It still over-uses "essential" (never outputs
"preferred"), but the discrimination is meaningful.

**4. Speed.** ~10 seconds for 67 candidates vs 3-5 minutes on HF API.

### What got worse

**1. Recall dropped to 53.7%.** The 70B model filters too aggressively —
it rejected 11 valid requirements that stages 2-3 had correctly identified.
This includes major features like fan notifications (GT-020/021/022), referee
mobile input (GT-007), game scheduling (GT-013), and data export (GT-011).

**2. Over-filtering is the dominant problem.** Of 19 FNs, 11 are LLM
over-filtering (not upstream gaps). The 70B model is better at recognising
well-structured requirements but worse at extracting requirements from noisy
conversational text — it classifies them as "not a requirement" instead.

### Precision vs recall tradeoff across versions

| Version | Precision | Recall | F1 | Character |
|---|---|---|---|---|
| v1.0 Naive | 40.3% | 65.9% | 0.500 | High recall, no filtering |
| v1.1 LLM 7B | 75.6% | 70.7% | **0.731** | Best balance |
| v1.2 LLM 7B+Ctx | 80.6% | 61.0% | 0.694 | Context helps precision, hurts recall |
| v2.0 LLM 70B | **91.3%** | 53.7% | 0.676 | Highest quality, lowest recall |

The clear pattern: **bigger/smarter models are better filters but more
aggressive**. The 70B model produces the highest quality output but catches
the fewest requirements.

### Priority analysis

| Priority | Correct | Incorrect | Notes |
|---|---|---|---|
| essential | 12 ✓ | 5 ✗ (should be preferred/optional) | Model over-labels as essential |
| preferred | 0 | 0 | Model never uses this label |
| optional | 0 ✓ | 3 ✗ (2 should be essential, 1 preferred) | Rare but sometimes misapplied |

The 70B model treats "preferred" as if it doesn't exist — everything is either
"essential" (strong requirement) or "optional" (uncertain). This binary thinking
is better than the 7B model's uniform "preferred" but still misses the middle
tier.

---

## Recommendations

1. **Best current configuration for balanced results: v1.1** (Qwen 7B, no
   context). It has the highest F1 (0.731) and catches the most requirements.

2. **Best for quality: v2.0** (Llama 70B). If the priority is clean, usable
   output over completeness, v2.0 gives 91% precision and zero poor rewrites.

3. **To improve recall**: The bottleneck is now clearly in stages 2-3. Upgrading
   the keyword-based segmenter and detector with an LLM would close the 8
   upstream gaps and potentially reduce over-filtering by passing cleaner
   candidates to the rewrite stage.

4. **To fix priority**: The 70B model needs explicit few-shot examples showing
   "preferred" items — stakeholder desires that are clearly stated but not
   emphasised as critical. The current prompt doesn't give enough signal for
   the middle tier.

---

## Conclusion

v2.0 demonstrates that a 10x larger model dramatically improves output quality:
**91% precision, 91% usable, 57% priority accuracy, zero poor rewrites**.
However, it does not improve recall — the 70B model is an even more aggressive
filter than the 7B model with context.

The pipeline's remaining bottlenecks:

| Problem | Impact | Fix |
|---|---|---|
| Stages 2-3 miss requirements | 8 FNs (upstream) | LLM-based segmenter/detector |
| 70B model over-filters | 11 FNs (Stage 4) | Better prompt / few-shot examples |
| No "preferred" priority | 0/14 preferred items correct | Few-shot examples for middle tier |
| Type classification | 76% correct | LLM-based classifier in Stage 3/5 |
