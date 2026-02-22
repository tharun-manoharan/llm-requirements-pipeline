# Pipeline Evaluation v1.0 (Naive) — N1.txt

## Dataset

- **Source**: Bristol PhD thesis — *The Importance of Trust in Space Teleoperation*
- **Interview**: N1 — industrial robot-arm operator (nuclear/hazardous environments)
- **File**: `datasets/bristol/N1.txt` — 101 turns (Interviewer / Participant)
- **Ground truth**: `datasets/bristol/N1_expected.json` — 16 requirements

---

## Scoring approach

Same two-dimension scoring used for `conversation_02.txt` evaluations:

**Detection accuracy** — did the pipeline surface a sentence that *contains* the
real requirement? Lenient: we count it even if the extracted text is garbled.

**End-to-end accuracy** — is the final rewritten statement actually usable as a
"The system shall …" requirement? All rewrites must be well-formed, artefact-free,
and semantically correct.

---

## Summary

### Detection accuracy

| Metric | Value |
|---|---|
| Ground-truth requirements | 16 |
| Pipeline output count | 31 |
| True positives (valid req detected) | 9 outputs → 5 unique GTs |
| False positives (not a real req) | 22 |
| False negatives (missed real req) | 11 |
| **Precision** | **9 / 31 = 29.0%** |
| **Recall** | **5 / 16 = 31.3%** |
| **F1** | **0.301** |

### End-to-end accuracy

| Metric | Value |
|---|---|
| Usable requirement statements | 0 / 31 (0%) |
| Type classification correct (of TPs) | 9 / 9 (100% — but all classified functional; NF reqs entirely missed) |
| Priority correct (of TPs) | 5 / 9 (55%) |
| Duplicates in output | ~5 (GT-006 ×2, GT-008 ×2, GT-011 ×2, GT-015 ×2) |
| **End-to-end precision** | **0%** |

---

## Classification of each pipeline output

### True Positives (9 outputs → 5 unique GTs)

| Pipeline ID | Maps to GT | Notes |
|---|---|---|
| REQ-018 | GT-006 | Waypoint navigation — "operator was there in case…arm went up to that position" |
| REQ-019 | GT-007 | Home position — "hit the home button…goes to a state where that tool is" — best capture |
| REQ-020 | GT-006 | Duplicate of REQ-018 — "programming it to get you to the point where you need to take control" |
| REQ-022 | GT-015 | Force feedback — "need to be able to feel that it's going incorrectly" |
| REQ-023 | GT-008 | Fixed camera — "and that's where it should always be" — extremely vague, barely identifiable |
| REQ-024 | GT-008 | Fixed camera — "a camera view…you've always got that view" — clearer duplicate |
| REQ-026 | GT-011 | AR overlay — "did give you a good idea of where you needed to be especially on a new task" |
| REQ-028 | GT-011 | AR overlay — "this is the angle, you need to be at so you did actually use that" — duplicate |
| REQ-029 | GT-015 | Force feedback — "can tell when you're supposed to be moving forward and if you're not…stop" — duplicate |

### False Positives (22)

| Pipeline ID | Reason for rejection |
|---|---|
| REQ-001 | Intro / meta — participant clarifying context with the interviewer |
| REQ-002 | Project update — team site visit, not a system requirement |
| REQ-003 | Technology comparison — describes current system, not a need |
| REQ-004 | Company background — "technology has bridged two companies" |
| REQ-005 | Future plan description — "upgrading again" / baseline system aspiration |
| REQ-006 | Product-line comment — "need to start looking to variants", not a req |
| REQ-007 | Analogy — colleague/robot capability analogy, not a req statement |
| REQ-008 | Hazard description — what happens if someone over-strains tendons |
| REQ-009 | Current state description — "the kit itself is very, very reliable" |
| REQ-010 | Speculation — participant unsure if temperature changes display colour |
| REQ-011 | Current state description — "latency is hardly noticeable" |
| REQ-012 | Operational principle — don't pressure operators; not a system feature |
| REQ-013 | Operational guideline — task timing buffer (+50%); not a system feature |
| REQ-014 | Operational constraint — "couldn't say…done in one minute"; process not system |
| REQ-015 | Operational constraint — time frame covering all abilities; process not system |
| REQ-016 | Physical cable management — environment guides, not software no-go zones |
| REQ-017 | Operational procedure — "model the whole scene in simulation" before the task |
| REQ-021 | Rationale — why human control is needed for screw-starting; not a req |
| REQ-025 | Negative statement — "VR won't work for precision tasks" |
| REQ-027 | Diminishing need — "once done several times, you get the idea"; not a req |
| REQ-030 | Application speculation — material sorting scenario; not a stated req |
| REQ-031 | Interviewer suggestion — participant gave a tentative "yeah potentially"; not confirmed |

### False Negatives (11) — real requirements the pipeline MISSED

| GT ID | Missed requirement | Why missed |
|---|---|---|
| GT-001 | Safe mode on over-speed command | Expressed as description ("it will just go into a safe mode"), not a keyword-bearing sentence |
| GT-002 | Software soft stops and hardware hard stops | "There are hard, there are soft stops" — no trigger keywords ("need", "should", "shall") |
| GT-003 | Joint range display on operator interface | Described as existing fact, no requirement keywords |
| GT-004 | Colour-coded visual warning at joint limits | "changes colours" — no trigger keyword in that sentence |
| GT-005 | Minimal non-intrusive feedback design | "I'd want information but not overload information" — keyword "want" absent from REQUIREMENT_KEYWORDS |
| GT-009 | Variable / repositionable camera viewpoint | "that would be very good to have" — "want" not in keyword list |
| GT-010 | Adaptive camera zoom near target | Personal preference description — no trigger keywords |
| GT-012 | Ghost mode / predicted end-position preview | "it is useful…gives super confidence" — "useful" not a trigger keyword |
| GT-013 | Configurable no-go zones | "no go zone is a great idea" — "idea" not a trigger keyword |
| GT-014 | Audible alarm on no-go zone approach | "an alarm would be good" — "would be good" not in keyword list |
| GT-016 | Resolution prioritised over frame rate | Expressed as preference ("I would take resolution over frame rate") — "take" not a keyword |

---

## Root cause analysis

### Stage 2 (Segment) — keyword mismatch with interview language

The REQUIREMENT_KEYWORDS list was tuned for software requirements-elicitation
dialogues ("need", "should", "must", "shall"). Interview participants describing
their teleoperation systems use different vocabulary:

- **"want"** — "that would be very good to have", "I'd want" (GT-005, GT-009, GT-010)
- **"idea"** — "no go zone is a great idea" (GT-013)
- **"would be good"** — "an alarm would be good" (GT-014)
- **"useful" / "helpful"** — "ghost mode is useful" (GT-012)
- **Factual statements without modal verbs** — "changes colours", "it will just go into a safe mode", "there are soft stops" (GT-001–GT-004)

Interview speech expresses requirements implicitly: by describing existing
system features positively (signalling "keep this"), describing gaps negatively,
or by agreeing with the interviewer's suggestion. The keyword filter misses all
of these patterns.

### Stage 3 (Detect) — no conversational context

Requirements in interviews are often ratified rather than stated. GT-012 and
GT-013 come from evaluative statements ("ghost mode is useful", "no go zone is
a great idea") that follow the interviewer's suggestion. Without context, these
look like filler statements and are not captured.

### Stage 4 (Rewrite) — same pathology as conversation_02

Every rewrite prepends "The system shall" directly to raw speech, preserving
transcription artefacts, false starts, and off-topic fragments. 0% of the 31
outputs are usable.

### Type and priority classification

All 31 outputs are labelled **functional / preferred**. Since the 2 NF
requirements (GT-005, GT-016) were not detected at all, the apparent 100% type
accuracy for TPs is an artefact — the classifier never had to distinguish.
Priority is uniformly "preferred", so it is correct for 3 of the 5 matched GTs
by coincidence (GT-006, GT-007, GT-011 are preferred) but wrong for GT-008
(essential) and GT-015 (essential).

---

## Comparison with conversation_02 (naive baseline)

| Metric | conversation_02 | N1 (Bristol) |
|---|---|---|
| Ground-truth requirements | 41 | 16 |
| Pipeline output count | 67 | 31 |
| True positives | 27 | 9 |
| False positives | 40 | 22 |
| False negatives | 14 | 11 |
| Precision | 40.3% | 29.0% |
| Recall | 65.9% | 31.3% |
| **F1** | **0.500** | **0.301** |
| Usable outputs | 0% | 0% |

The naive pipeline performs substantially worse on the interview data.
The gap is driven by:
1. Interview language uses evaluative / preference vocabulary rather than
   modal verbs — the keyword filter misses ~70% of requirements.
2. Interview transcripts are longer relative to their requirements density —
   101 turns, only 16 requirements — so more conversational noise passes through.

---

## Conclusion

The naive pipeline achieves a **detection F1 of 0.301** on the Bristol N1
interview (vs 0.500 on the IFA conversation). Key bottlenecks:

1. **Keyword mismatch**: Interview language omits "shall/must/need" — keywords
   must be extended or replaced with semantic detection.
2. **Evaluative phrasing missed**: "X is a great idea", "X would be good", "X
   gives confidence" are all common interview requirement signals not captured
   by keyword matching.
3. **Rewriting**: Identical 0% usable failure as conversation_02 — no
   improvement expected without an LLM rewrite stage.
4. **Type/priority**: Not meaningful to assess — both NF requirements missed
   upstream; priority defaults to "preferred" throughout.

An LLM-based approach (v1.1+) should perform relatively better here than on
conversation_02, because the main bottleneck is semantic understanding of
evaluative language rather than conversational noise filtering.
