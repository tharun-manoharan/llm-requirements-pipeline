"""Automated evaluation: compute precision, recall, F1, and priority accuracy.

Uses fuzzy string matching (difflib.SequenceMatcher) to match pipeline output
requirements against ground truth. This enables consistent, reproducible
comparisons across pipeline variants without hand-scoring.

Normalisation before matching:
  - lowercase
  - strip leading "the system shall"
  - strip trailing period and whitespace

Match threshold: 0.5 similarity ratio (configurable via MATCH_THRESHOLD).
"""

import difflib

MATCH_THRESHOLD = 0.5


def _normalise(statement: str) -> str:
    s = statement.lower().strip()
    for prefix in ("the system shall ", "the system shall"):
        if s.startswith(prefix):
            s = s[len(prefix):]
            break
    return s.rstrip(". ")


def evaluate(output_reqs: list[dict], ground_truth: list[dict]) -> dict:
    """Compute precision/recall/F1 using fuzzy statement matching.

    Args:
        output_reqs: pipeline output — list of dicts with 'statement' and 'priority'.
        ground_truth: expected requirements — list of dicts with 'statement' and 'priority'.

    Returns:
        dict with keys: precision, recall, f1, priority_accuracy, tp, fp, fn.
    """
    if not output_reqs and not ground_truth:
        return {"precision": 1.0, "recall": 1.0, "f1": 1.0,
                "priority_accuracy": 1.0, "tp": 0, "fp": 0, "fn": 0}

    gt_normalised = [_normalise(r["statement"]) for r in ground_truth]
    out_normalised = [_normalise(r["statement"]) for r in output_reqs]

    gt_matched = [False] * len(ground_truth)
    tp = 0
    fp = 0
    priority_correct = 0
    priority_total = 0

    for i, out_stmt in enumerate(out_normalised):
        best_ratio = 0.0
        best_gt_idx = -1
        for j, gt_stmt in enumerate(gt_normalised):
            if gt_matched[j]:
                continue
            ratio = difflib.SequenceMatcher(None, out_stmt, gt_stmt).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_gt_idx = j

        if best_ratio >= MATCH_THRESHOLD and best_gt_idx != -1:
            tp += 1
            gt_matched[best_gt_idx] = True
            out_priority = output_reqs[i].get("priority", "").lower()
            gt_priority = ground_truth[best_gt_idx].get("priority", "").lower()
            if out_priority and gt_priority:
                priority_total += 1
                if out_priority == gt_priority:
                    priority_correct += 1
        else:
            fp += 1

    fn = sum(1 for m in gt_matched if not m)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    priority_accuracy = priority_correct / priority_total if priority_total > 0 else 0.0

    return {
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
        "priority_accuracy": round(priority_accuracy, 3),
        "tp": tp,
        "fp": fp,
        "fn": fn,
    }
