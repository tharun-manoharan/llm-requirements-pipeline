"""Pipeline orchestrator - chains all 5 stages and provides a CLI entry point."""

import json
import sys

from pipeline.ingest import parse_conversation
from pipeline.segment import segment_turns
from pipeline.detect import detect_candidates
from pipeline.extract import extract_candidates_llm
from pipeline.rewrite import rewrite_requirements
from pipeline.structure import structure_requirements

DIVIDER = "=" * 72


def run_pipeline(raw_text: str, rewrite_mode: str = "naive") -> list[dict]:
    """Run the full pipeline and return structured requirements."""
    turns = parse_conversation(raw_text)

    if rewrite_mode == "llm":
        candidates = extract_candidates_llm(turns)
    else:
        segmented = segment_turns(turns)
        candidates = detect_candidates(segmented)

    rewritten = rewrite_requirements(candidates, mode=rewrite_mode, turns=turns)
    return structure_requirements(rewritten, turns)


def run_pipeline_trace(raw_text: str, rewrite_mode: str = "naive") -> list[dict]:
    """Run the full pipeline, printing each stage's output along the way."""

    # --- Stage 1 ---
    print(f"\n{DIVIDER}")
    print("  STAGE 1: INGEST  (raw text -> structured turns)")
    print(DIVIDER)
    turns = parse_conversation(raw_text)
    print(f"  Parsed {len(turns)} turns:\n")
    for t in turns:
        text_preview = t["text"][:80] + ("..." if len(t["text"]) > 80 else "")
        print(f'    Turn {t["turn_index"]:3d}  [{t["role"]:12s}]  "{text_preview}"')

    if rewrite_mode == "llm":
        # --- Stages 2+3 (LLM) ---
        print(f"\n{DIVIDER}")
        print("  STAGES 2+3: LLM EXTRACT  (semantic requirement extraction)")
        print(DIVIDER)
        candidates = extract_candidates_llm(turns)
        print(f"\n  {len(candidates)} candidate sentences extracted:\n")
        for c in candidates:
            text_preview = c["sentence"][:70] + ("..." if len(c["sentence"]) > 70 else "")
            print(f'    [{c["req_type"]:15s}]  Turn {c["source_turn"]:3d}  "{text_preview}"')
    else:
        # --- Stage 2 ---
        print(f"\n{DIVIDER}")
        print("  STAGE 2: SEGMENT  (tag requirement-bearing turns)")
        print(DIVIDER)
        segmented = segment_turns(turns)
        yes = sum(1 for t in segmented if t["is_candidate"])
        no = len(segmented) - yes
        print(f"  {yes} candidates, {no} skipped\n")
        for t in segmented:
            marker = ">> CANDIDATE" if t["is_candidate"] else "   skip"
            text_preview = t["text"][:70] + ("..." if len(t["text"]) > 70 else "")
            print(f'    Turn {t["turn_index"]:3d}  {marker:13s}  "{text_preview}"')

        # --- Stage 3 ---
        print(f"\n{DIVIDER}")
        print("  STAGE 3: DETECT  (extract sentences, classify type, filter questions)")
        print(DIVIDER)
        candidates = detect_candidates(segmented)
        print(f"  {len(candidates)} candidate sentences extracted:\n")
        for c in candidates:
            text_preview = c["sentence"][:70] + ("..." if len(c["sentence"]) > 70 else "")
            print(f'    [{c["req_type"]:15s}]  Turn {c["source_turn"]:3d}  "{text_preview}"')

    # --- Stage 4 ---
    print(f"\n{DIVIDER}")
    label = "LLM" if rewrite_mode == "llm" else "NAIVE"
    print(f"  STAGE 4: REWRITE [{label}]  (normalise to 'The system shall ...')")
    print(DIVIDER)
    rewritten = rewrite_requirements(candidates, mode=rewrite_mode, turns=turns)
    kept = len(rewritten)
    filtered = len(candidates) - kept
    print(f"\n  {kept} requirements rewritten, {filtered} filtered out:\n")
    for r in rewritten:
        before = r["sentence"][:60] + ("..." if len(r["sentence"]) > 60 else "")
        after = r["normalised"][:60] + ("..." if len(r["normalised"]) > 60 else "")
        print(f"    BEFORE: \"{before}\"")
        print(f"    AFTER:  \"{after}\"")
        print()

    # --- Stage 5 ---
    print(DIVIDER)
    print("  STAGE 5: STRUCTURE  (assign IDs, final JSON)")
    print(DIVIDER)
    result = structure_requirements(rewritten, turns)
    print(json.dumps(result, indent=2))

    return result


def main():
    """Read from a file argument or stdin, run pipeline, print JSON to stdout.

    Usage:
        python -m pipeline.run <file>                Normal mode (JSON only)
        python -m pipeline.run --trace <file>         Trace mode (every stage)
        python -m pipeline.run --llm <file>           LLM rewrite mode
        python -m pipeline.run --llm --trace <file>   LLM + trace
    """
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    trace = "--trace" in sys.argv
    rewrite_mode = "llm" if "--llm" in sys.argv else "naive"

    if args:
        with open(args[0], "r") as f:
            raw = f.read()
    else:
        raw = sys.stdin.read()

    if trace:
        run_pipeline_trace(raw, rewrite_mode=rewrite_mode)
    else:
        result = run_pipeline(raw, rewrite_mode=rewrite_mode)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
