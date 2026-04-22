# IFA Augmented Dataset

**Status:** Public
**Based on:** `datasets/ifa/` (the original IFA sports system requirements-elicitation session)
**Purpose:** Stress-test the pipeline's deduplication, priority-extraction, and FRET contradiction-detection stages with concrete, annotated examples.

---

## What was changed and why

The original `datasets/ifa/` transcript was **not modified**. This dataset is a copy of that transcript with **58 new dialogue turns appended** before the closing remarks (after the original Turn 125). The original 41 ground-truth requirements are unchanged; 20 new requirements (GT-042 to GT-061) are added, including 2 requirements that intentionally contradict existing ones (GT-060, GT-061).

### Change 1 — MoSCoW priority language (Turns 126–127)

**What:** A new exchange was added where the interviewer explicitly asks the stakeholder to prioritise using must-have / should-have / could-have / won't-have language, and the stakeholder responds accordingly.

**Why:** The original IFA transcript expresses priority implicitly through phrasing ("I would expect", "it might be", "definitely not"). This addition creates explicit MoSCoW-style priority markers so we can evaluate whether the pipeline correctly maps:
- "must have" → `essential`
- "should" → `preferred`
- "could" → `optional`
- "won't" / "definitely not building" → `optional` (exclusion constraint)

**New requirements added:**
| ID | Statement | Priority | Notes |
|----|-----------|----------|-------|
| GT-042 | The system shall maintain a complete audit log of all actions performed by IFA administrators. | essential | must-have |
| GT-043 | The system shall provide a financial summary dashboard showing key budget metrics across all teams for the IFA. | preferred | should-have |
| GT-044 | The system shall provide a public API for journalists to access game data programmatically. | optional | could-have |
| GT-045 | The system shall not include live video streaming from the pitch. | optional | won't-have (exclusion constraint) |

---

### Change 2 — Exact synonym (Turns 128–129)

**What:** The interviewer asks a clarifying question that causes the stakeholder to restate the referee real-time reporting requirement (GT-007) using different words.

**Why:** Creates a ground-truth **high-confidence duplicate** for deduplication evaluation. The restated requirement ("The system shall allow referees to enter match events into the application in real time during a game.") describes the same system behaviour as GT-007, just with different surface phrasing. A correct deduplication should remove it with **high** confidence.

**Documented in:** `dedup_cases.json` as `DEDUP-001`.

---

### Change 3 — Near-duplicate (Turns 130–131)

**What:** The interviewer asks specifically about schedule-change notifications for subscribed fans, and the stakeholder confirms.

**Why:** Creates a ground-truth **medium-confidence near-duplicate**. The extracted requirement ("The system shall automatically notify fans who have registered to a game when the schedule for that game is adjusted.") is a specific case of GT-020 ("The system shall push notifications to fans who subscribe to specific games, players, or events."). GT-020 already covers this scenario; the new requirement adds no genuinely new behaviour. However, because it names a specific scenario (schedule changes) not explicitly listed in GT-020, a model might assign medium rather than high confidence — which is the expected and desirable outcome.

**Documented in:** `dedup_cases.json` as `DEDUP-002`.

---

### Change 4 — Distinct pair (Turns 132–133)

**What:** The interviewer asks two questions: whether the system should show live league standings, and whether fans should be able to compare player statistics. The stakeholder says yes to both.

**Why:** Creates two new requirements that are **related but genuinely distinct** — deduplication should keep both. This tests that the model does not over-aggressively remove requirements simply because they are thematically related (both are about exposing data to fans).

**New requirements added:**
| ID | Statement | Priority |
|----|-----------|----------|
| GT-046 | The system shall display current league standings to all users. | preferred |
| GT-047 | The system shall allow fans to compare player statistics side by side. | preferred |

**Documented in:** `dedup_cases.json` as `DEDUP-003`.

---

### Changes 5–8 — Priority extraction examples (Turns 134–145)

**What:** Six further exchanges elicit new genuine requirements using varied priority language: implicit urgency ("hard requirement", "at minimum must"), explicit criticism ("absolutely critical", "non-negotiable"), desirable-but-deferrable ("ideally", "not essential for day one"), temporal deferral ("not needed for the first release"), and low priority ("might be nice", "not a priority", "future phases").

**Why:** The first priority block (Change 1) tests only explicit MoSCoW vocabulary. These exchanges extend coverage to the hedged and implicit priority signals that appear in real elicitation transcripts, creating a more demanding test of the pipeline's priority-extraction stage.

**New requirements added:**
| ID | Statement | Priority | Language cue |
|----|-----------|----------|--------------|
| GT-048 | The system shall perform daily backups of all system data. | essential | "at minimum must", "hard requirement" |
| GT-052 | The system shall require two-factor authentication for IFA administrator accounts. | essential | "absolutely critical", "non-negotiable" |
| GT-049 | The system shall allow fans to search for upcoming matches by team name or date. | preferred | "ideally yes", "not essential for day one but we would like it" |
| GT-053 | The system shall support a multi-language user interface. | preferred | "important but not needed for first release", temporal deferral |
| GT-050 | The system shall allow fans to post comments or reactions on match events. | optional | "might be nice but not a priority", "if there is time" |
| GT-051 | The system shall allow referees to flag disputed match events for review. | optional | "potentially in future phases", "out of scope for now" |

---

### Changes 9–15 — Further exact synonyms (Turns 146–159)

**What:** Seven exchanges in which the interviewer asks recap confirmation questions. In each case the stakeholder restates an existing requirement verbatim or with surface-level paraphrase, covering: team budget management (GT-001), automatic scheduling (GT-013), scheduling policies (GT-014), two-IFA-representative override (GT-019), 50,000-user capacity (GT-025), registration and guest access (GT-036), and team registration approval (GT-037).

**Why:** Extends the exact-synonym test set from 1 case to 8 (DEDUP-001 + DEDUP-004 to DEDUP-010), covering a wider range of requirement types (functional, non-functional; scheduling, budget, access control).

**Documented in:** `dedup_cases.json` as `DEDUP-004` to `DEDUP-010`.

---

### Changes 16–22 — Further near-duplicates (Turns 160–173)

**What:** Seven exchanges in which the interviewer asks about a specific scenario that is already covered by a general existing requirement. Each stakeholder response introduces a specific-instance requirement that correct deduplication should remove at medium confidence: wage-cap violation alert (GT-003), goal scorer capture (GT-009), no back-to-back same-team referee assignment (GT-016), player-goal subscriber notification (GT-020), club-level fan follow (GT-021), registering a newly signed player (GT-039), and preserving season league tables (GT-035).

**Why:** Extends the near-duplicate test set from 1 case to 8 (DEDUP-002 + DEDUP-011 to DEDUP-017), providing broader coverage of the medium-confidence removal decision across different requirement domains.

**Documented in:** `dedup_cases.json` as `DEDUP-011` to `DEDUP-017`.

---

### Changes 23–25 — Further distinct pairs (Turns 174–179)

**What:** Three exchanges in which the interviewer asks about two related but genuinely distinct features, and the stakeholder confirms both. The pairs are: (a) separate home/away record display (GT-054) and top goal-scorer leaderboard (GT-055); (b) IFA date-range financial report (GT-056) and team transaction document attachments (GT-057); (c) match venue and kick-off time display (GT-058) and assigned referee name display (GT-059).

**Why:** Extends the distinct-keep test set from 1 pair to 4 (DEDUP-003 + DEDUP-018 to DEDUP-020). Each pair is thematically related, testing that the model does not over-aggressively remove requirements that are similar in topic but describe genuinely different system behaviours.

**New requirements added:**
| ID | Statement | Priority |
|----|-----------|----------|
| GT-054 | The system shall display each team's home and away match record separately within the league standings. | preferred |
| GT-055 | The system shall display a top goal-scorer leaderboard for the current season. | preferred |
| GT-056 | The system shall allow IFA administrators to generate a financial summary report for any specified date range. | preferred |
| GT-057 | The system shall allow team administrators to attach supporting documents (such as invoices or contracts) to individual budget transactions. | preferred |
| GT-058 | The system shall display the venue and kick-off time for each scheduled match. | preferred |
| GT-059 | The system shall display the name of the assigned referee for each upcoming match. | preferred |

**Documented in:** `dedup_cases.json` as `DEDUP-018` to `DEDUP-020`.

---

## Files

| File | Description |
|------|-------------|
| `conversation.txt` | Augmented transcript (original IFA + 58 new turns) |
| `expected.json` | Ground-truth requirements (GT-001 to GT-061; deduplication duplicates excluded; contradicting pairs both included) |
| `dedup_cases.json` | Annotated deduplication test cases with expected confidence levels and actions |
| `contradiction_cases.json` | Annotated contradiction test cases with expected FRETish translations and FRET detection mechanism |
| `README.md` | This file |

---

---

### Changes 26–27 — Contradiction pairs (Turns 180–183)

**What:** Two exchanges in which the stakeholder reverses a position taken earlier in the original session, producing requirements that directly contradict pre-existing ground-truth requirements.

**Why:** Tests the pipeline end-to-end for contradiction detection via the FRET stage. For FRET to detect a contradiction it needs two requirements where the same `response_var` appears under `always` and `never` respectively. Both contradiction pairs are designed so the concept is identical and the LLM is highly likely to assign the same `response_var` to both FRETish translations. The expected LTL pattern is `G(X) ∧ G(!X)`, which is unsatisfiable — FRET's Kind2 realizability checker will report the requirement set as unrealizable and highlight the conflicting pair.

**New requirements added:**

| ID | Statement | Contradicts | FRET-detectable? |
|----|-----------|-------------|-----------------|
| GT-060 | The system shall never allow unregistered users to access game data or results. | GT-010 | Yes — same `response_var` under `always`/`never` |
| GT-061 | The system shall never automatically generate match schedules. | GT-013 | Yes — same `response_var` under `always`/`never` |

**Documented in:** `contradiction_cases.json` as `CONTRA-001` and `CONTRA-002`.

---

## Contradiction test summary

| Case | Contradicting GTs | Source turns | Expected FRETish A | Expected FRETish B | FRET-detectable |
|------|-------------------|-------------|-------------------|--------------------|-----------------|
| CONTRA-001 | GT-010 vs GT-060 | 21 vs 180–181 | `always satisfy unregistered_user_game_data_access` | `never satisfy unregistered_user_game_data_access` | Yes |
| CONTRA-002 | GT-013 vs GT-061 | 43 vs 182–183 | `always satisfy automatic_match_schedule_generation` | `never satisfy automatic_match_schedule_generation` | Yes |

---

## Deduplication test summary

| Case | Type | Source turns | Expected action | Expected confidence |
|------|------|-------------|-----------------|-------------------|
| DEDUP-001 | Exact synonym | 128–129 | Remove (dup of GT-007) | high |
| DEDUP-002 | Near-duplicate | 130–131 | Remove (dup of GT-020) | medium |
| DEDUP-003 | Distinct pair | 132–133 | Keep both (GT-046, GT-047) | N/A |
| DEDUP-004 | Exact synonym | 146–147 | Remove (dup of GT-001) | high |
| DEDUP-005 | Exact synonym | 148–149 | Remove (dup of GT-013) | high |
| DEDUP-006 | Exact synonym | 150–151 | Remove (dup of GT-014) | high |
| DEDUP-007 | Exact synonym | 152–153 | Remove (dup of GT-019) | high |
| DEDUP-008 | Exact synonym | 154–155 | Remove (dup of GT-025) | high |
| DEDUP-009 | Exact synonym | 156–157 | Remove (dup of GT-036) | high |
| DEDUP-010 | Exact synonym | 158–159 | Remove (dup of GT-037) | high |
| DEDUP-011 | Near-duplicate | 160–161 | Remove (dup of GT-003) | medium |
| DEDUP-012 | Near-duplicate | 162–163 | Remove (dup of GT-009) | medium |
| DEDUP-013 | Near-duplicate | 164–165 | Remove (dup of GT-016) | medium |
| DEDUP-014 | Near-duplicate | 166–167 | Remove (dup of GT-020) | medium |
| DEDUP-015 | Near-duplicate | 168–169 | Remove (dup of GT-021) | medium |
| DEDUP-016 | Near-duplicate | 170–171 | Remove (dup of GT-039) | medium |
| DEDUP-017 | Near-duplicate | 172–173 | Remove (dup of GT-035) | medium |
| DEDUP-018 | Distinct pair | 174–175 | Keep both (GT-054, GT-055) | N/A |
| DEDUP-019 | Distinct pair | 176–177 | Keep both (GT-056, GT-057) | N/A |
| DEDUP-020 | Distinct pair | 178–179 | Keep both (GT-058, GT-059) | N/A |

---

## Priority extraction test summary

| Turn | Priority cue | Type | Expected priority | Requirement |
|------|-------------|------|-------------------|-------------|
| 127 | "must have" | explicit MoSCoW | essential | GT-042 (audit log) |
| 127 | "should" | explicit MoSCoW | preferred | GT-043 (financial dashboard) |
| 127 | "could" | explicit MoSCoW | optional | GT-044 (public API) |
| 127 | "definitely not building" | explicit MoSCoW | optional | GT-045 (no video streaming) |
| 135 | "at minimum must", "hard requirement" | implicit urgency | essential | GT-048 (daily backup) |
| 137 | "absolutely critical", "non-negotiable" | implicit urgency | essential | GT-052 (2FA for admins) |
| 139 | "ideally yes", "not essential for day one but we would like it" | desirable-but-deferrable | preferred | GT-049 (fan match search) |
| 141 | "important but not needed for first release" | temporal deferral | preferred | GT-053 (multi-language UI) |
| 143 | "might be nice but not a priority", "if there is time" | low priority | optional | GT-050 (fan comments) |
| 145 | "potentially in future phases", "out of scope for now" | low priority | optional | GT-051 (referee flag disputed events) |
