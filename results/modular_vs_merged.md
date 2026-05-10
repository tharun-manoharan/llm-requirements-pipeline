# Modular vs Merged Pipeline — Empirical Comparison

Automated evaluation using fuzzy statement matching (threshold=0.5).
All modes evaluated identically; relative differences are meaningful.

**Note on model:** The modular baseline uses pre-computed v3.5 results (Qwen3-235B via Cerebras).
Merged modes used Llama-3.3-70B via Together AI (Cerebras was unavailable during this run).
Score differences may reflect model capability as well as architecture — treat merged-vs-modular
comparisons as indicative only. Comparisons *between* merged modes are apples-to-apples.

Note: absolute scores also differ from hand-scored results in `results/*/evaluation_*.md`.

## IFA  (ground truth: 41 requirements)

| Mode                 | Output | P     | R     | F1    | Pri.Acc | TP | FP | FN |
|----------------------|--------|-------|-------|-------|---------|----|----|-----|
| Modular (current)    |     35 | 0.686 | 0.585 | 0.632 | 0.583   | 24 | 11 | 17 |
| Merged full (E+R+D)  |     43 | 0.581 | 0.610 | 0.595 | 0.720   | 25 | 18 | 16 |
| Merged E+R, sep. D   |     48 | 0.625 | 0.732 | 0.674 | 0.767   | 30 | 18 | 11 |
| Sep. E, Merged R+D   |     34 | 0.588 | 0.488 | 0.533 | 0.700   | 20 | 14 | 21 |

## Bristol N1  (ground truth: 16 requirements)

| Mode                 | Output | P     | R     | F1    | Pri.Acc | TP | FP | FN |
|----------------------|--------|-------|-------|-------|---------|----|----|-----|
| Modular (current)    |     17 | 0.235 | 0.250 | 0.242 | 0.750   |  4 | 13 | 12 |
| Merged full (E+R+D)  |     22 | 0.409 | 0.562 | 0.474 | 0.556   |  9 | 13 |  7 |
| Merged E+R, sep. D   |     21 | 0.286 | 0.375 | 0.324 | 0.500   |  6 | 15 | 10 |
| Sep. E, Merged R+D   |     17 | 0.059 | 0.062 | 0.061 | 1.000   |  1 | 16 | 15 |

## Bristol N2  (ground truth: 13 requirements)

| Mode                 | Output | P     | R     | F1    | Pri.Acc | TP | FP | FN |
|----------------------|--------|-------|-------|-------|---------|----|----|-----|
| Modular (current)    |     12 | 0.083 | 0.077 | 0.080 | 1.000   |  1 | 11 | 12 |
| Merged full (E+R+D)  |     10 | 0.100 | 0.077 | 0.087 | 1.000   |  1 |  9 | 12 |
| Merged E+R, sep. D   |     10 | 0.100 | 0.077 | 0.087 | 0.000   |  1 |  9 | 12 |
| Sep. E, Merged R+D   |     13 | 0.000 | 0.000 | 0.000 | 0.000   |  0 | 13 | 13 |

## Mode descriptions

- **Modular (current)**: 3 separate LLM stages: extract -> rewrite (N calls) -> dedup
- **Merged full (E+R+D)**: 1 LLM call: extract + rewrite + dedup together
- **Merged E+R, sep. D**: 1 LLM call: extract + rewrite; then separate dedup call
- **Sep. E, Merged R+D**: Separate extract call; then 1 LLM call: rewrite + dedup
