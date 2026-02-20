# Pipeline Evaluation v1.1 (LLM Rewrite) — conversation_02.txt

## What changed from v1.0

Only **Stage 4 (Rewrite)** was upgraded. Stages 1–3 and 5 remain identical to v1.0.
The LLM (Qwen/Qwen2.5-7B-Instruct via Hugging Face Inference API) now serves a
dual purpose:

1. **Rewriting** — converts raw conversational sentences into clean "The system
   shall …" statements.
2. **Filtering** — rejects non-requirements (responds `NOT_A_REQUIREMENT`),
   acting as a second-pass detector that reduces false positives.

The naive pipeline produced **67 outputs**. The LLM filtered 26 of those,
leaving **41 outputs**.

---

## Scoring approach

We use the same two dimensions as v1.0 for direct comparison.

**Detection accuracy** measures whether the pipeline found sentences that
*contain* a real requirement, regardless of rewrite quality. Under the LLM
rewrite, precision jumps significantly because the LLM filters out many
non-requirements that the naive pipeline let through.

**End-to-end accuracy** asks: is the final output actually usable as a
requirement statement? In v1.0 this was 0% because every naive rewrite was
garbled. With LLM rewriting, the majority of outputs are now well-formed.

---

## Summary

### Detection accuracy (lenient — did it find the right sentences?)

| Metric | v1.0 (Naive) | v1.1 (LLM Rewrite) | Change |
|---|---|---|---|
| Ground-truth requirements | 41 | 41 | — |
| Pipeline output count | 67 | 41 | −26 |
| True positives (outputs mapping to a GT) | 27 | 31 | +4 |
| False positives (not a real req) | 40 | 10 | −30 |
| False negatives (missed GT reqs) | 14 | 12 | −2 |
| **Precision** | **40.3%** | **75.6%** | **+35.3 pp** |
| **Recall** | **65.9%** | **70.7%** | **+4.8 pp** |
| **F1 Score** | **0.500** | **0.731** | **+0.231** |

### End-to-end accuracy (strict — is the output a usable requirement?)

| Metric | v1.0 (Naive) | v1.1 (LLM Rewrite) | Change |
|---|---|---|---|
| Usable requirement statements | 0 / 67 (0%) | 25 / 41 (61%) | +61 pp |
| Good quality rewrites (of TPs) | 0 / 27 | 17 / 31 (55%) | — |
| Acceptable quality (of TPs) | 0 / 27 | 8 / 31 (26%) | — |
| Poor quality (of TPs) | 27 / 27 | 6 / 31 (19%) | — |
| Type classification correct (of TPs) | 19 / 27 | 24 / 31 (77%) | — |
| Duplicates in output | ~5 | ~5 | — |
| **End-to-end precision** | **0%** | **61%** | **+61 pp** |

---

## Classification of each pipeline output

### True Positives (31) — valid requirements detected

| LLM ID | Maps to GT | Type match? | Rewrite quality | Notes |
|---|---|---|---|---|
| REQ-001 | GT-003 | ✓ func | Acceptable | Captures budget policies but loses "IFA" specificity and "alert on violations" |
| REQ-002 | GT-034 | ✓ NF | Acceptable | Correct intent (reliability) but too vague — misses "referees as sole source" |
| REQ-003 | GT-009 | ✓ func | Good | Clean rewrite of event data storage with timestamps |
| REQ-004 | GT-010 | ✓ func | Acceptable | "Complete dataset" is too broad; GT specifies game data only |
| REQ-005 | GT-010 | ✓ func | Poor | "Final grain data" — garbled transcription artifact preserved |
| REQ-006 | GT-010 | ✓ func | Good | Clean; adds useful nuance about budget data restriction |
| REQ-007 | GT-011 | ✓ func | Good | Clean export requirement, nearly verbatim match |
| REQ-009 | GT-012 | ✓ func | Good | Captures team data review and offline analysis well |
| REQ-010 | GT-004 | ✗ NF→func | Good | Clean statement but typed non-functional instead of functional |
| REQ-012 | GT-013/014 | ✓ func | Acceptable | Captures constraint-based scheduling but vague on specifics |
| REQ-013 | GT-015 | ✓ func | Excellent | Near-verbatim match to ground truth |
| REQ-014 | GT-016/017 | ✓ func | Good | Covers both referee policies and preferences in one statement |
| REQ-015 | GT-018 | ✓ func | Good | Clean; misses "cancellations" context from GT |
| REQ-016 | GT-019 | ✓ func | Good | Captures IFA confirmation; misses "written rationale" detail |
| REQ-017 | GT-019 | ✓ func | Poor | Duplicate; "IFA Scheduler levels" is garbled transcription |
| REQ-018 | GT-014 | ✓ func | Good | Clean; captures specific scheduling constraint |
| REQ-021 | GT-024 | ✓ func | Poor | Mischaracterises intent — says "retrieve and process" when GT is about players posting to fans |
| REQ-023 | GT-034 | ✓ NF | Poor | Too vague — "ensure coherence and reliability" with no context |
| REQ-024 | GT-008/034 | ✓ func | Good | Clean; referees as sole authoritative game data source |
| REQ-025 | GT-020/021 | ✓ func | Good | Excellent; covers fan registration + push notifications |
| REQ-026 | GT-041 | ✓ func | Good | Clean; captures annual report submission |
| REQ-027 | GT-025 | ✗ func→NF | Good | Clean rewrite but typed functional instead of non-functional |
| REQ-028 | GT-026 | ✓ NF | Acceptable | Correct direction but lost specific "1–2 seconds" from GT |
| REQ-029 | GT-027 | ✗ func→NF | Acceptable | "Other stadium activities" is garbled; correct intent |
| REQ-031 | GT-027 | ✗ func→NF | Acceptable | Duplicate of REQ-029; same wrong type |
| REQ-034 | GT-033 | ✗ func→NF | Good | Clean cloud hosting statement; wrong type |
| REQ-035 | GT-030 | ✗ func→NF | Acceptable | Captures localization intent but vague on specifics |
| REQ-036 | GT-031 | ✗ func→NF | Good | Captures data residency; slightly awkward phrasing |
| REQ-037 | GT-036 | ✓ func | Poor | "Internet access" is garbled — should be "system access" |
| REQ-038 | GT-035 | ✓ func | Good | Clean archival requirement |
| REQ-041 | GT-040/038 | ✓ func | Good | Comprehensive compound covering leagues, seasons, referees |

### False Positives (10) — NOT real requirements

| LLM ID | Reason for rejection |
|---|---|
| REQ-008 | Transcription error — "the city" is garbled; "shall not support queries from the city" is not a real requirement |
| REQ-011 | Too vague — "determine the appropriate policy" doesn't specify what kind of policy or any behaviour |
| REQ-019 | Too vague — "allow users to define parameters" with no context |
| REQ-020 | Developer/facilitator prompt — "provide experience improvements for the fans" is not a stakeholder requirement |
| REQ-022 | Hallucinated — Turn 70 was a developer question about unauthorized data; LLM invented a logging/notification requirement |
| REQ-030 | Implementation detail — "notify the user upon connection of the referee to the system" is not a standalone requirement |
| REQ-032 | Developer question rejected by stakeholder — spk_2 asked "do you need two-way communication?" and stakeholder said No |
| REQ-033 | Developer question + garbled transcription — "FAA-related" should be "IFA-related"; not confirmed by stakeholder |
| REQ-039 | Hallucinated from rationale — stakeholder explained *why* data should be kept (gambling analytics); LLM turned it into a "recommendation engine" requirement |
| REQ-040 | Too vague — "store the data" is trivially obvious and duplicates REQ-038 |

### False Negatives (12) — real requirements the pipeline MISSED

| GT ID | Missed requirement | Also missed in v1.0? |
|---|---|---|
| GT-001 | Each team manages its own budget (income and expenses) | Yes |
| GT-002 | IFA monitors and audits team budgets | Yes |
| GT-005 | Budget transactions restricted to teams; teams access only own data | Yes |
| GT-006 | IFA can view all monetary data but not modify it | Yes |
| GT-007 | Referees insert game events in real time using a mobile phone | No — LLM filtered it |
| GT-022 | Notify subscribed fans in real time when game events occur | No — LLM filtered it |
| GT-023 | Fans set custom alerts (e.g. 5 min before game reminder) | Yes |
| GT-028 | Web interface for admin, mobile app for referees/fans | Yes |
| GT-029 | Unified system with different presentation layers + RBAC | Yes |
| GT-032 | Encrypt budget data to prevent leakage | No — LLM filtered it |
| GT-037 | Team registration process (owner submits docs, IFA approves) | Yes |
| GT-039 | Teams manage their own players, coaches, stadium, resources | No — LLM filtered it |

---

## Analysis

### What the LLM rewrite improved

**1. Massive reduction in false positives (40 → 10).** The LLM correctly
filtered out 30 non-requirements: developer questions, meta-conversation,
current state descriptions, greeting/closing fragments, and vague
restatements. This is the biggest win — precision nearly doubled.

**2. Clean, professional rewrites.** 25 of 41 outputs (61%) are now usable
requirement statements, up from 0% in v1.0. All filler words ("uh", "so",
"okay") are removed. Sentences are grammatically correct and follow the "The
system shall …" pattern.

**3. Two additional GTs recovered.** The LLM's cleaner interpretation of
borderline candidates allowed some requirements to surface that were
misclassified in v1.0 (e.g. GT-004, GT-013, GT-020, GT-024, GT-036, GT-038
— 6 previously missed GTs now detected).

### What the LLM rewrite did NOT fix

**1. Same upstream detection gaps.** 8 of the 12 FNs were also missed in v1.0.
These are requirements that stages 1–3 never detected in the first place
(e.g. budget management requirements from Turn 3, RBAC from Turn 68, team
registration from Turn 119). The LLM rewrite stage cannot recover what
stages 1–3 never passed forward.

**2. Type classification unchanged.** 7 of 31 TPs have the wrong
functional/non-functional label (77% correct). This classification happens
in stages 3/5, which were not modified. Performance, infrastructure, and
localization requirements are still incorrectly typed as "functional."

**3. Four new false negatives from over-filtering.** The LLM incorrectly
rejected 4 candidates that were actually valid requirements in the v1.0
evaluation:
- GT-007 (referee mobile event insertion)
- GT-022 (real-time fan notifications)
- GT-032 (budget data encryption)
- GT-039 (team resource management)

These were likely rejected because the raw sentences were heavily embedded
in conversational noise, and the LLM couldn't extract the requirement from
the surrounding context.

**4. Transcription artifacts persist.** The LLM faithfully rewrites garbled
transcriptions: "grain data" (should be "game data"), "FAA" (should be
"IFA"), "internet access" (should be "system access"), "Scheduler levels"
(garbled phrase). It has no way to correct speech-to-text errors.

**5. Hallucination risk.** Two outputs (REQ-022, REQ-039) contain
requirements the stakeholder never actually stated. The LLM inferred
plausible-sounding features from developer questions and rationale
statements. This is a new failure mode not present in the naive pipeline.

### Remaining FP categories

| Category | Count | Examples |
|---|---|---|
| Transcription errors | 1 | REQ-008 ("the city") |
| Too vague to be actionable | 3 | REQ-011, REQ-019, REQ-040 |
| Developer question/prompt | 3 | REQ-020, REQ-032, REQ-033 |
| Hallucinated from context | 2 | REQ-022, REQ-039 |
| Implementation detail | 1 | REQ-030 |

---

## Recommendations for next stages

1. **Upgrade Stage 2/3 (Segment + Detect)** — The 8 persistent FNs from v1.0
   are all upstream detection failures. An LLM-based segmenter/detector could
   identify requirements expressed without keyword triggers (e.g. "each team
   manage its own budget").

2. **Add context window to rewrite** — Currently each sentence is rewritten in
   isolation. Providing the surrounding conversation context (2–3 turns) would
   help the LLM distinguish stakeholder requirements from developer questions
   and rationale statements.

3. **Fix type classification** — Either add an LLM-based classifier in stage 5,
   or extend the non-functional keyword list to catch performance, scalability,
   infrastructure, and localization terms.

4. **Transcription correction pass** — A preprocessing step could fix common
   speech-to-text errors ("grain"→"game", "FAA"→"IFA") before they reach the
   pipeline.

---

## Conclusion

The LLM rewrite stage is a significant upgrade. Adding a single 7B LLM to one
stage improved:

| Metric | v1.0 → v1.1 |
|---|---|
| Precision | 40.3% → 75.6% (+35 pp) |
| Recall | 65.9% → 70.7% (+5 pp) |
| F1 | 0.500 → 0.731 (+0.231) |
| End-to-end usable | 0% → 61% (+61 pp) |

The LLM's dual role as rewriter *and* filter was the biggest contributor — it
eliminated 30 false positives while producing clean, professional requirement
statements. However, the pipeline still misses 12 of 41 ground-truth
requirements (mostly upstream detection failures) and introduces a small
hallucination risk. The next improvement should target stages 2–3 to close the
remaining detection gaps.
