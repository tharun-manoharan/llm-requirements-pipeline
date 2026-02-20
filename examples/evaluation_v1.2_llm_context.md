# Pipeline Evaluation v1.2 (LLM Rewrite + Context Window) — conversation_02.txt

## What changed from v1.1

- Stage 4 LLM now receives **surrounding conversation context** (2 turns
  either side of the target sentence) to improve priority classification
  and filtering decisions.
- Output schema now includes a **priority** field (`essential`/`preferred`/`optional`).
- Same Qwen/Qwen2.5-7B-Instruct model via Hugging Face Inference API.

The context window made the LLM filter **more aggressively** — output dropped
from 41 items (v1.1) to 31 items. This improved precision but reduced recall.

---

## Summary

### Detection accuracy

| Metric | v1.0 (Naive) | v1.1 (LLM) | v1.2 (LLM+Context) |
|---|---|---|---|
| Ground-truth requirements | 41 | 41 | 41 |
| Pipeline output count | 67 | 41 | 31 |
| True positives | 27 | 31 | 25 |
| False positives | 40 | 10 | 6 |
| False negatives | 14 | 12 | 16 |
| **Precision** | **40.3%** | **75.6%** | **80.6%** |
| **Recall** | **65.9%** | **70.7%** | **61.0%** |
| **F1** | **0.500** | **0.731** | **0.694** |

### End-to-end accuracy

| Metric | v1.0 | v1.1 | v1.2 |
|---|---|---|---|
| Usable statements | 0/67 (0%) | 25/41 (61%) | 25/31 (81%) |
| Type classification correct (of TPs) | 19/27 | 24/31 | 20/25 |

### Priority accuracy

| Metric | Value |
|---|---|
| Ground truth distribution | 25 essential, 14 preferred, 2 optional |
| Pipeline output distribution | 0 essential, 30 preferred, 1 optional |
| Priority accuracy | ~34% (model defaults to "preferred") |

Priority classification is a known limitation of the 7B model — it lacks the
nuance to differentiate stakeholder emphasis. Marked for future improvement
with a larger model or dedicated classification pass.

---

## Classification of each pipeline output

### True Positives (25)

| LLM ID | Maps to GT | Rewrite quality | Notes |
|---|---|---|---|
| REQ-002 | GT-003 | Good | Budget policies |
| REQ-003 | GT-034 | Acceptable | Reliability — vague but valid |
| REQ-004 | GT-009 | Good | Event timestamps and details |
| REQ-005 | GT-010 | Good | Guest data access |
| REQ-006 | GT-010 | Good | Unregistered users see game data, not budget — specific |
| REQ-007 | GT-011 | Good | Data export for press |
| REQ-008 | GT-012 | Good | Team offline analysis |
| REQ-009 | GT-004 | Acceptable | Financial data access for IFA |
| REQ-010 | GT-013/014 | Acceptable | Constraint-based scheduling — vague |
| REQ-011 | GT-015 | Excellent | Referee allocation guidance — near-verbatim |
| REQ-012 | GT-016/017 | Good | Referee policies + preferences |
| REQ-013 | GT-018 | Good | Manual schedule adjustment |
| REQ-014 | GT-019 | Acceptable | Approval for override — partial |
| REQ-015 | GT-014 | Good | Minimum gap constraint — specific |
| REQ-016 | GT-014 | Good | Scheduling parameters |
| REQ-019 | GT-020/024 | Good | Player message notifications |
| REQ-021 | GT-008/034 | Good | Referees as sole data source |
| REQ-022 | GT-041 | Acceptable | Auto reminders |
| REQ-023 | GT-020/021 | Good | Fan subscription notifications |
| REQ-024 | GT-026 | Acceptable | Response time — lost specific "1-2 seconds" |
| REQ-026 | GT-027 | Good | Referee real-time priority |
| REQ-027 | GT-033 | Good | Cloud hosting |
| REQ-028 | GT-030 | Acceptable | Localization — vague |
| REQ-029 | GT-031 | Good | German data residency |
| REQ-031 | GT-032 | Good | Budget data encryption |

### False Positives (6)

| LLM ID | Reason |
|---|---|
| REQ-001 | Developer introduction from Turn 0 — not a stakeholder requirement |
| REQ-017 | Too vague — "allow users to define parameters" with no specifics |
| REQ-018 | Developer prompt — "provide improved fan experience" is not a requirement |
| REQ-020 | Hallucinated — developer question about unauthorized data turned into a feature |
| REQ-025 | Implementation detail — referee connection notification |
| REQ-030 | Developer question — not confirmed by stakeholder |

### False Negatives (16)

| GT ID | Missed requirement | Also missed in v1.1? |
|---|---|---|
| GT-001 | Each team manages its own budget | Yes |
| GT-002 | IFA monitors and audits team budgets | Yes |
| GT-005 | Budget transactions restricted to teams | Yes |
| GT-006 | IFA view but not modify monetary data | Yes |
| GT-007 | Referees insert events via mobile in real time | v1.1 caught this |
| GT-022 | Real-time fan notifications on game events | v1.1 caught this |
| GT-023 | Fan custom alerts (5 min before game) | Yes |
| GT-025 | Support 50,000 simultaneous users | v1.1 caught this |
| GT-028 | Web for admin, mobile for referees/fans | Yes |
| GT-029 | Unified system + RBAC | Yes |
| GT-035 | Retain all historical data | v1.1 caught this |
| GT-036 | User registration and authentication | v1.1 caught this |
| GT-037 | Team registration process | Yes |
| GT-038 | IFA register/invite referees | v1.1 caught this |
| GT-039 | Teams manage players/coaches/stadium | v1.1 caught this |
| GT-040 | IFA define leagues/seasons | v1.1 caught this |

The context window caused the LLM to filter out 8 requirements that v1.1
had captured (GT-007, GT-022, GT-025, GT-035, GT-036, GT-038, GT-039, GT-040).
This is over-filtering — the additional context made the LLM more conservative.

---

## Tradeoff analysis: v1.1 vs v1.2

Adding context improved **precision** (75.6% → 80.6%) and **rewrite quality**
(61% → 81% usable) but hurt **recall** (70.7% → 61.0%).

The context window helps the LLM:
- Write better rewrites (more specific, e.g. "red cards and goals")
- Filter out more developer questions and meta-conversation

But it also causes over-filtering of valid requirements that appear in noisy
conversational context. The net effect on F1 is slightly negative (0.731 → 0.694).

**Recommendation**: The v1.1 configuration (no context) gives better overall
F1. Context should be revisited with a larger model that can distinguish
requirement-bearing sentences from surrounding noise more reliably.

---

## Conclusion

v1.2 demonstrates the precision/recall tradeoff of adding context. While output
quality is the highest yet (81% usable, only 6 false positives), the recall
drop means more real requirements are missed. The remaining bottlenecks are
unchanged:

1. **Stages 2-3** miss requirements entirely (8 of 16 FNs are upstream gaps)
2. **Over-filtering** by the context-aware LLM (8 new FNs vs v1.1)
3. **Priority classification** is non-functional at 7B model size
4. **Type classification** still has errors in stages 3/5
