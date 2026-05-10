"""Experiment runner: compare modular vs merged pipeline variants.

Runs all 4 pipeline modes against IFA, Bristol N1, and Bristol N2 datasets,
then computes precision/recall/F1 and saves a comparison table to
results/modular_vs_merged.md.

Usage:
    python -m eval.run_experiment                 # run all modes on all datasets
    python -m eval.run_experiment --dry-run       # load existing outputs, skip LLM calls
    python -m eval.run_experiment --dataset IFA   # run one dataset only
    python -m eval.run_experiment --mode modular  # run one mode only

Note: automated F1 scores use fuzzy matching (threshold 0.5) and will differ
from the hand-scored values in results/*/evaluation_*.md. All modes are
evaluated identically, so relative differences are meaningful.
"""

import json
import os
import sys
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from eval.evaluate import evaluate

DATASETS = {
    "IFA": {
        "conversation": os.path.join(BASE_DIR, "datasets", "ifa", "conversation.txt"),
        "ground_truth": os.path.join(BASE_DIR, "datasets", "ifa", "expected.json"),
        "results_dir": os.path.join(BASE_DIR, "results", "ifa"),
        "prefix": "",
    },
    "Bristol N1": {
        "conversation": os.path.join(BASE_DIR, "datasets", "bristol", "N1.txt"),
        "ground_truth": os.path.join(BASE_DIR, "datasets", "bristol", "N1_expected.json"),
        "results_dir": os.path.join(BASE_DIR, "results", "bristol"),
        "prefix": "N1_",
    },
    "Bristol N2": {
        "conversation": os.path.join(BASE_DIR, "datasets", "bristol", "N2.txt"),
        "ground_truth": os.path.join(BASE_DIR, "datasets", "bristol", "N2_expected.json"),
        "results_dir": os.path.join(BASE_DIR, "results", "bristol"),
        "prefix": "N2_",
    },
}

MODES = ["modular", "merged-full", "merged-er", "merged-rd"]

MODE_LABELS = {
    "modular":     "Modular (current)",
    "merged-full": "Merged full (E+R+D)",
    "merged-er":   "Merged E+R, sep. D",
    "merged-rd":   "Sep. E, Merged R+D",
}

MODE_DESCRIPTION = {
    "modular":     "3 separate LLM stages: extract -> rewrite (N calls) -> dedup",
    "merged-full": "1 LLM call: extract + rewrite + dedup together",
    "merged-er":   "1 LLM call: extract + rewrite; then separate dedup call",
    "merged-rd":   "Separate extract call; then 1 LLM call: rewrite + dedup",
}


def output_filename(dataset_name: str, mode: str, paths: dict) -> str:
    prefix = paths["prefix"]
    slug = mode.replace("-", "_")
    return os.path.join(paths["results_dir"], f"output_{prefix}{slug}.json")


def run_mode(mode: str, raw_text: str, turns=None) -> list[dict]:
    """Run a specific pipeline mode and return structured requirements."""
    from pipeline.ingest import parse_conversation
    from pipeline.run import structure_requirements

    if mode == "modular":
        from pipeline.run import run_pipeline
        requirements, _ = run_pipeline(raw_text, rewrite_mode="llm")
        return requirements

    if turns is None:
        turns = parse_conversation(raw_text)

    if mode == "merged-full":
        from pipeline.merged import run_merged_full
        rewritten, _ = run_merged_full(turns)
        return structure_requirements(rewritten, turns)

    if mode == "merged-er":
        from pipeline.merged import run_merged_extract_rewrite
        rewritten, _ = run_merged_extract_rewrite(turns)
        return structure_requirements(rewritten, turns)

    if mode == "merged-rd":
        from pipeline.merged import run_merged_rewrite_dedup
        rewritten, _ = run_merged_rewrite_dedup(turns)
        return structure_requirements(rewritten, turns)

    raise ValueError(f"Unknown mode: {mode}")


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args

    filter_dataset = None
    if "--dataset" in args:
        idx = args.index("--dataset")
        filter_dataset = args[idx + 1] if idx + 1 < len(args) else None

    filter_mode = None
    if "--mode" in args:
        idx = args.index("--mode")
        filter_mode = args[idx + 1] if idx + 1 < len(args) else None

    datasets_to_run = {k: v for k, v in DATASETS.items()
                       if filter_dataset is None or k == filter_dataset}
    modes_to_run = [m for m in MODES if filter_mode is None or m == filter_mode]

    all_results = {}

    for dataset_name, paths in datasets_to_run.items():
        all_results[dataset_name] = {}
        print(f"\n{'='*64}")
        print(f"  Dataset: {dataset_name}")
        print(f"{'='*64}")

        with open(paths["ground_truth"]) as f:
            ground_truth = json.load(f)
        with open(paths["conversation"]) as f:
            raw_text = f.read()

        from pipeline.ingest import parse_conversation
        turns = parse_conversation(raw_text)

        for mode in modes_to_run:
            out_file = output_filename(dataset_name, mode, paths)

            if dry_run and os.path.exists(out_file):
                print(f"\n  [{mode}] Loading {out_file}")
                with open(out_file) as f:
                    requirements = json.load(f)
            else:
                print(f"\n  [{mode}] Running... ({MODE_DESCRIPTION[mode]})")
                start = time.time()
                requirements = run_mode(mode, raw_text, turns if mode != "modular" else None)
                elapsed = time.time() - start
                print(f"  [{mode}] Done in {elapsed:.1f}s -> {len(requirements)} requirements")

                os.makedirs(paths["results_dir"], exist_ok=True)
                with open(out_file, "w") as f:
                    json.dump(requirements, f, indent=2)
                print(f"  [{mode}] Saved -> {out_file}")

            metrics = evaluate(requirements, ground_truth)
            all_results[dataset_name][mode] = {**metrics, "n_output": len(requirements)}

            print(
                f"  [{mode}] P={metrics['precision']:.3f}  "
                f"R={metrics['recall']:.3f}  "
                f"F1={metrics['f1']:.3f}  "
                f"PriAcc={metrics['priority_accuracy']:.3f}  "
                f"(TP={metrics['tp']}, FP={metrics['fp']}, FN={metrics['fn']})"
            )

    if len(modes_to_run) > 1 and len(datasets_to_run) > 0:
        _save_comparison_table(all_results, modes_to_run)


def _save_comparison_table(all_results: dict, modes: list[str]):
    datasets = list(all_results.keys())

    lines = [
        "# Modular vs Merged Pipeline — Empirical Comparison",
        "",
        "Automated evaluation using fuzzy statement matching (threshold=0.5).",
        "All modes evaluated identically; relative differences are meaningful.",
        "",
        "**Note on model:** The modular baseline uses pre-computed v3.5 results (Qwen3-235B via Cerebras).",
        "Merged modes used Llama-3.3-70B via Together AI (Cerebras was unavailable during this run).",
        "Score differences may reflect model capability as well as architecture — treat merged-vs-modular",
        "comparisons as indicative only. Comparisons *between* merged modes are apples-to-apples.",
        "",
        "Note: absolute scores also differ from hand-scored results in `results/*/evaluation_*.md`.",
        "",
    ]

    for dataset in datasets:
        ds_results = all_results[dataset]
        if not ds_results:
            continue
        # use any available mode to get fn count for GT total
        sample = next(iter(ds_results.values()))
        n_gt = sample["tp"] + sample["fn"]
        lines.append(f"## {dataset}  (ground truth: {n_gt} requirements)")
        lines.append("")
        lines.append("| Mode                 | Output | P     | R     | F1    | Pri.Acc | TP | FP | FN |")
        lines.append("|----------------------|--------|-------|-------|-------|---------|----|----|-----|")
        for mode in modes:
            if mode not in ds_results:
                continue
            m = ds_results[mode]
            label = MODE_LABELS.get(mode, mode)
            lines.append(
                f"| {label:<20} | {m['n_output']:6d} "
                f"| {m['precision']:.3f} | {m['recall']:.3f} "
                f"| {m['f1']:.3f} | {m['priority_accuracy']:.3f}   "
                f"| {m['tp']:2d} | {m['fp']:2d} | {m['fn']:2d} |"
            )
        lines.append("")

    lines += [
        "## Mode descriptions",
        "",
    ]
    for mode in modes:
        lines.append(f"- **{MODE_LABELS[mode]}**: {MODE_DESCRIPTION[mode]}")
    lines.append("")

    table_text = "\n".join(lines)
    output_path = os.path.join(BASE_DIR, "results", "modular_vs_merged.md")
    with open(output_path, "w") as f:
        f.write(table_text)

    print(f"\n{'='*64}")
    print(table_text)
    print(f"Comparison table saved -> {output_path}")


if __name__ == "__main__":
    main()
