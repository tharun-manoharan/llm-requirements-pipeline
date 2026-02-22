# Pipeline Evaluation v1.0 (Naive) - conversation_02.txt

## Scoring approach

We evaluate the pipeline on two separate dimensions:

**Detection accuracy** measures whether the pipeline found sentences that
*contain* a real requirement, regardless of how badly the output is written.
This is a lenient measure - if the source sentence has a genuine requirement
buried in it, we count it as detected. Under this lens the pipeline scores an
F1 of 0.50, but this overstates its usefulness because many "detected" items
are still garbled beyond recognition.

**End-to-end accuracy** asks: is the final output actually usable as a
requirement statement? This means the rewrite must be well-formed, free of
conversational filler, and express a clear "shall" statement. Under this
stricter lens, **0 out of 67** outputs are acceptable. Every single rewrite
either blindly prepends "The system shall" to raw conversational text
(preserving "uh", "so", "okay", incomplete sentences) or captures something
that is not a requirement at all. The end-to-end precision is effectively **0%**.

Both dimensions matter for comparison with later LLM-enhanced versions: we want
to improve detection (fewer false positives/negatives) *and* produce clean,
usable requirement statements.

## Summary

### Detection accuracy (lenient - did it find the right sentences?)

| Metric | Value |
|---|---|
| Ground-truth requirements | 41 |
| Pipeline output count | 67 |
| True positives (valid req detected) | 27 |
| False positives (not a real req) | 40 |
| False negatives (missed real req) | 14 |
| **Precision** | **27 / 67 = 40.3%** |
| **Recall** | **27 / 41 = 65.9%** |
| **F1 Score** | **0.500** |

### End-to-end accuracy (strict - is the output a usable requirement?)

| Metric | Value |
|---|---|
| Usable requirement statements | 0 / 67 |
| Type classification correct (of TPs) | 19 / 27 |
| Duplicates in output | ~5 |
| **End-to-end precision** | **0%** |

---

## Classification of each pipeline output

### True Positives (27) - valid requirements, even if poorly rewritten

| Pipeline ID | Maps to GT | Notes |
|---|---|---|
| REQ-003 | GT-multiple | High-level mention of budget/reporting/scheduling/fan portals - very loose |
| REQ-004 | GT-003 | Budget policy + alerts - good detection |
| REQ-005 | GT-034 | Information should be reliable - correct NF |
| REQ-006 | GT-009 | Events have timestamp + details - good |
| REQ-007 | GT-010 | Everyone can see data - good |
| REQ-008 | GT-010 | Guests can see game data - good (partial dup of REQ-007) |
| REQ-009 | GT-010 | Unregistered users see game data, not budget - good |
| REQ-010 | GT-011 | Export data for journalists - good |
| REQ-014 | GT-012 | Team admin can view data - good |
| REQ-018 | GT-014 | Scheduling constraints - good |
| REQ-019 | GT-015 | Referee allocation guidance - good |
| REQ-020 | GT-016,017 | Referee policy + preferences - good, rich |
| REQ-021 | GT-018 | Reschedule games - good |
| REQ-022 | GT-018 | Manual schedule adjustment - duplicate of REQ-021 |
| REQ-025 | GT-019 | Second IFA rep must confirm changes - good |
| REQ-028 | GT-014 | Minimum gap between games - good |
| REQ-030 | GT-014 | Define scheduling parameters - good |
| REQ-038 | GT-008,034 | Referees as sole official data source - good |
| REQ-041 | GT-020,021 | Fans register + push notifications - good |
| REQ-043 | GT-025 | 50k simultaneous users - good, but WRONG type (classified functional, should be NF) |
| REQ-044 | GT-026 | Reasonable response time - correct NF type |
| REQ-045 | GT-027 | Referee app real-time priority - good, but WRONG type (classified functional, should be NF) |
| REQ-047 | GT-027 | Referee high priority during game - duplicate of REQ-045 |
| REQ-051 | GT-033 | Cloud hosting - good, but WRONG type (classified functional, should be NF) |
| REQ-052 | GT-030 | Localization - good |
| REQ-057 | GT-032 | Budget data encryption - correct NF type |
| REQ-061 | GT-035 | Keep all past archives - good |

### False Positives (40) - NOT real requirements

| Pipeline ID | Reason for rejection |
|---|---|
| REQ-001 | Introduction/greeting - "we're doing I'm ***..." |
| REQ-002 | Meta-conversation - "we just need to start recording" |
| REQ-011 | Current state observation - "this is not available now" |
| REQ-012 | Observation - "referee data is not confidential" |
| REQ-013 | Negation/clarification - "I'm not expecting the city will support queries" |
| REQ-015 | Developer question - "our financial data is available to everybody?" |
| REQ-016 | Meta-conversation - "we understand the requirements" |
| REQ-017 | Vague restatement - "need to determine policy" (no specific requirement) |
| REQ-023 | Conversational fragment - "we might override... you need to explicate" |
| REQ-024 | Conversational fragment - "you need to explain the rationale" (duplicate context of REQ-025) |
| REQ-026 | Developer paraphrase/question - "you need approval from two?" |
| REQ-027 | Conversation navigation - "I think we need to move to the fans" |
| REQ-029 | Developer paraphrase - "you mentioned this in your software" |
| REQ-031 | Developer prompt - "you need experience improvements for the fans" |
| REQ-032 | Current state description - "fans need to pull information" |
| REQ-033 | Current state problem - "you need to look for it" |
| REQ-034 | Current state problem - "they need to look for it" |
| REQ-035 | Current state problem - "if a player posts a message, you should look for it" |
| REQ-036 | Developer question - "we were looking for clarification about unauthorized data" |
| REQ-037 | Vague - "it's coherent and reliable" (fragment, no clear requirement) |
| REQ-039 | Context/negative - "they don't need to look forward news portal" |
| REQ-040 | Developer question/prompt - "enhance stakeholder communication" |
| REQ-042 | Developer statement, not a system req - "team manager has to submit a report" |
| REQ-046 | Incomplete sentence - "when referee is connected, you should get" |
| REQ-048 | Developer question - "do you need two way communication?" |
| REQ-049 | Developer question - "is there any scenario where..." |
| REQ-050 | Developer question - "do we need a live recording feature?" |
| REQ-053 | Conversational - "I'm not sure if it's right for every country..." |
| REQ-054 | Vague/meta - "we should take this into consideration" |
| REQ-055 | Developer question - "should your IT team decide?" |
| REQ-056 | Vague/meta - "we should define it as an initiative to discuss" |
| REQ-058 | Project phasing, not a system requirement - "this should be at the first phase" |
| REQ-059 | Incomplete/meaningless - "the officials should be" |
| REQ-060 | Captured but barely recognisable - very garbled |
| REQ-062 | Rationale fragment - "the reason that it should be kept" |
| REQ-063 | Rationale fragment - "allow recommendation reasoning for gambling" |
| REQ-064 | Duplicate of REQ-061 - "we need to keep the data" |
| REQ-065 | Somewhat valid but it's a compound list that should be split |
| REQ-066 | Closing meta - "no more requirements on your side" |
| REQ-067 | Closing meta - "send me an email if you have problems" |

### False Negatives (14) - real requirements the pipeline MISSED

| GT ID | Missed requirement |
|---|---|
| GT-001 | Each team manages its own budget |
| GT-002 | IFA monitors/audits team budgets |
| GT-004 | IFA admin can view all team transactions |
| GT-005 | Budget transactions restricted to teams; teams access only own data |
| GT-006 | IFA can view but not modify monetary data |
| GT-013 | Automatic game scheduling per league per season |
| GT-020 | Push notifications to fans (partially captured in REQ-041 but core push mechanism missed) |
| GT-023 | Fan custom alerts (e.g. remind 5 min before game) |
| GT-024 | Players manage social network pages / post messages |
| GT-028 | Web interface for admin, mobile app for referees/fans |
| GT-029 | Unified system with different presentation layers + RBAC |
| GT-036 | User registration required; guests get limited access |
| GT-037 | Team registration process (owner submits docs, IFA approves) |
| GT-038 | IFA registers/invites referees |

---

## Root cause analysis - why does the naive pipeline struggle?

### Stage 2 (Segment) problems
- **Over-triggering**: Keywords like "need", "should", "able to" appear constantly in casual speech ("we need to move to the fans", "you need to look for it"). The keyword list has no concept of context.
- **Missing context**: Turns that describe real requirements but use different language (e.g. "each team manage its own budget") get skipped because they lack the exact keywords.

### Stage 3 (Detect) problems
- **Question filtering too weak**: Questions like "Do you expect or need a two way communication?" aren't filtered because they don't end with "?" (period-terminated due to transcription quirks), or they appear mid-sentence.
- **Sentence splitting inadequate**: The transcript uses very little punctuation, so the sentence splitter (split on `.!?`) produces huge multi-sentence chunks or misses boundaries entirely.
- **No conversational-vs-requirement discrimination**: Current state descriptions ("fans need to pull information"), meta-conversation ("we understand the requirements"), and developer prompts all pass through.

### Stage 4 (Rewrite) problems
- **Fallback dominates**: Almost every sentence falls through to the fallback rule (prepend "The system shall" + lowercase first char), producing unreadable output like "The system shall so it it should have the ability to..."
- **No cleanup of filler words**: "uh", "so", "you know", "okay" are all preserved verbatim.
- **No semantic understanding**: The rewriter cannot distinguish a requirement from a rationale, question, or observation.

### Stage 3+5 (Type classification) problems
- Requirements about **performance** (50k users, response time) and **infrastructure** (cloud hosting) are classified as "functional" because the keyword list for non-functional is too narrow and doesn't match all the ways people express NFRs in speech.

---

## Conclusion

The naive keyword-based pipeline achieves a **detection F1 of 0.50** (40% precision, 66% recall) but an **end-to-end usable output rate of 0%** on this real-world IFA stakeholder conversation. The main bottlenecks are:

1. **Detection**: Too many false positives from conversational noise (questions, meta-talk, current-state descriptions)
2. **Rewriting**: The rule-based rewriter cannot handle unstructured speech - 0% of rewrites are acceptable
3. **Missed requirements**: Important requirements stated without trigger keywords are lost entirely
4. **Type classification**: 8 of 27 true positives have the wrong functional/non-functional label

An LLM-based approach should significantly improve all four areas by understanding context and intent rather than relying on keyword matching.
