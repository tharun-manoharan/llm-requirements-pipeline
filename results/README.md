# Results

Pipeline outputs (JSON) and evaluation reports (Markdown) for each dataset
and pipeline version. Inputs live in `datasets/`.

## Structure

```
results/
  ifa/                              # IFA stakeholder conversation (datasets/ifa/)
    output_v1.0_naive.json          # Raw pipeline output — naive mode
    output_v1.1_llm.json            # Raw pipeline output — LLM rewrite (Qwen 7B)
    output_v1.2_llm_context.json    # Raw pipeline output — LLM + context window
    output_v2.0_groq.json           # Raw pipeline output — Groq Llama 70B
    evaluation_v1.0_naive.md
    evaluation_v1.1_llm_rewrite.md
    evaluation_v1.2_llm_context.md
    evaluation_v2.0_groq.md

  bristol/                          # Bristol teleoperation interviews (datasets/bristol/)
    evaluation_N1_v1.0_naive.md
    ...
```

## Naming conventions

| Pattern | Meaning |
|---|---|
| `output_vX.Y_<label>.json` | JSON produced by running the pipeline on the dataset |
| `evaluation_vX.Y_<label>.md` | Hand-scored evaluation of that output against ground truth |

Version numbers align with the pipeline version that produced them (v1.0 naive,
v1.1 LLM, v1.2 LLM+context, v2.0 Groq 70B, …).

For Bristol interviews the dataset ID (N1, N2, …) is included in the filename.
