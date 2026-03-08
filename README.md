# LLM Requirements Pipeline

A pipeline that extracts structured software requirements from raw
stakeholder conversation transcripts. The project incrementally adds LLM
capabilities to each stage and measures improvement against a manually curated
ground truth.

## Pipeline Architecture

```
conversation.txt
       |
       v
 [1. INGEST]       Parse raw text into structured turns
       |
       v
 [2. SEGMENT]      Tag requirement-bearing turns
 [3. DETECT]       Extract sentences, classify type
       |            naive: keyword matching + sentence split
       |            llm:   single semantic extraction call (stages 2+3 merged)
       v
 [4. REWRITE]      Normalise to "The system shall ..." + assign priority
       |            naive: regex rules  |  llm: gpt-oss-120b via Cerebras
       v
 [4b. DEDUP]       Remove semantically equivalent requirements (LLM mode only)
       |
       v
 [5. STRUCTURE]    Assign IDs, emit final JSON
       |
       v
  requirements.json
```

In `--llm` mode, stages 2+3 are replaced by a single semantic extraction call
(`pipeline/extract.py`) that sends the full conversation to the LLM - bypassing
keyword matching entirely. This catches requirements that keyword matching misses
(business rules stated as facts, implicit permissions, procedural language, etc.).

Stage 4b (`pipeline/deduplicate.py`) is a single batch LLM call that receives
all rewritten requirements and removes semantic duplicates - candidates from
adjacent turns that describe the same underlying system behaviour.

| Stage | Module | Naive | LLM |
|-------|--------|-------|-----|
| 1. Ingest | `pipeline/ingest.py` | Regex parser | - |
| 2+3. Extract | `pipeline/extract.py` | - | gpt-oss-120b (Cerebras) |
| 2. Segment | `pipeline/segment.py` | Keyword matching | (replaced by extract) |
| 3. Detect | `pipeline/detect.py` | Sentence split + classify | (replaced by extract) |
| 4. Rewrite | `pipeline/rewrite.py` | Regex rules | gpt-oss-120b (Cerebras) |
| 4b. Dedup | `pipeline/deduplicate.py` | - (passthrough) | gpt-oss-120b (Cerebras) |
| 5. Structure | `pipeline/structure.py` | ID assignment | - |
| Shared | `pipeline/llm_client.py` | - | Cerebras client |

## Progress and Results

Evaluated against three datasets:
- **IFA** - `datasets/ifa/conversation.txt`: structured requirements elicitation session, **41 ground-truth requirements**
- **Bristol N1** - `datasets/bristol/N1.txt`: unstructured research interview, **16 ground-truth requirements**
- **Bristol N2** - `datasets/bristol/N2.txt`: unstructured research interview (different participant), **13 ground-truth requirements**

### IFA dataset - comparison across versions

| Metric | v1.0 Naive | v1.1 LLM 7B | v1.2 LLM 7B+Ctx | v2.0 LLM 70B | v3.1 LLM 120B | v3.2 LLM 120B | **v3.3 LLM 120B** |
|---|---|---|---|---|---|---|---|
| Model | - | Qwen 7B (HF) | Qwen 7B (HF) | Llama 3.3 70B (Groq) | gpt-oss-120b (Cerebras) | gpt-oss-120b (Cerebras) | **gpt-oss-120b (Cerebras)** |
| LLM stages | - | Stage 4 only | Stage 4 only | Stage 4 only | Stages 2+3+4 | Stages 2+3+4+4b | **Stages 2+3+4+4b** |
| Output count | 67 | 41 | 31 | 23 | 32 | 29 | **30** |
| **Precision** | 40.3% | 75.6% | 80.6% | 91.3% | 87.5% | 89.7% | **86.7%** |
| **Recall** | 65.9% | 70.7% | 61.0% | 53.7% | 85.4% | 82.9% | **78.0%** |
| **F1 Score** | 0.500 | 0.731 | 0.694 | 0.676 | 0.864 | 0.861 | **0.821** |
| Usable outputs | 0% | 61% | 81% | 91% | 100% | 100% | **100%** |
| Priority accuracy | - | - | 34% | 57% | 64% | 65% | **65%** |
| False positives | 40 | 10 | 6 | 2 | 4 | 3 | **4** |
| False negatives | 14 | 12 | 16 | 19 | 6 | 7 | **9** |
| Speed | instant | ~3-5 min | ~3-5 min | ~10 sec | ~3 min | ~4 min | **~4 min** |

### Bristol N1 dataset - comparison across versions

| Metric | v1.0 Naive | v2.0 LLM 70B | v3.1 LLM 120B | v3.2 LLM 120B | **v3.3 LLM 120B** |
|---|---|---|---|---|---|
| Model | - | Llama 3.3 70B (Groq) | gpt-oss-120b (Cerebras) | gpt-oss-120b (Cerebras) | **gpt-oss-120b (Cerebras)** |
| LLM stages | - | Stage 4 only | Stages 2+3+4 | Stages 2+3+4+4b | **Stages 2+3+4+4b** |
| Output count | 31 | 16 | 26 | 18 | **18** |
| **Precision** | 16.1% | 56.3% | 53.8% | 61.1% | **66.7%** |
| **Recall** | 31.3% | 56.3% | 93.8% | 87.5% | **87.5%** |
| **F1 Score** | 0.213 | 0.563 | 0.684 | 0.719 | **0.757** |
| Usable outputs | 0% | 56% | 88% | 100% | **100%** |
| Priority accuracy | - | 54% | 71% | 55% | **58%** |
| False positives | 26 | 7 | 12 | 7 | **6** |
| False negatives | 11 | 7 | 1 | 2 | **2** |

### Bristol N2 dataset - comparison across versions

| Metric | v3.2 LLM 120B | **v3.3 LLM 120B** |
|---|---|---|
| Model | gpt-oss-120b (Cerebras) | **gpt-oss-120b (Cerebras)** |
| LLM stages | Stages 2+3+4+4b | **Stages 2+3+4+4b** |
| Output count | 14 | **17** |
| **Precision** | 57.1% | **52.9%** |
| **Recall** | 61.5% | **69.2%** |
| **F1 Score** | 0.592 | **0.599** |
| Usable outputs | 100% | **100%** |
| Priority accuracy | 75% | **67%** |
| False positives | 6 | **8** |
| False negatives | 5 | **4** |

### Key findings

- **v1.0 (Naive baseline)**: Keyword matching finds many candidates but has
  extremely high noise (40 false positives) and 0% of outputs are usable
  requirements - the regex rewriter just prepends "The system shall" to raw
  conversational text.

- **v1.1 (LLM rewrite - Qwen 7B)**: Adding a 7B LLM to Stage 4 nearly doubled
  precision (40% → 76%) and took usable output from 0% to 61%. The LLM serves
  dual purpose: rewriting and filtering non-requirements.

- **v1.2 (LLM + context window - Qwen 7B)**: Passing 2 surrounding turns as
  context improved precision further (81%) and output quality (81% usable), but
  the 7B model became too aggressive at filtering, dropping recall to 61%.
  Priority classification non-functional (34% accuracy, model defaults to "preferred").

- **v2.0 (Groq / Llama 3.3 70B)**: Upgrading to a 10x larger model dramatically
  improved output quality - **91% precision, 91% usable, zero poor rewrites, and
  57% priority accuracy**. The 70B model is a much better rewriter and filter,
  but it is also more aggressive, dropping recall to 54%.

- **v3.1 (Cerebras / gpt-oss-120b - Stages 2+3+4)**: Replacing keyword matching
  with semantic LLM extraction in stages 2+3 addresses the recall bottleneck.
  Recall rises from 54% to **85%** while precision holds at **87.5%**, giving the
  best F1 across all versions (**0.864**). A few-shot prompt fix brings priority
  accuracy to **64%**. Model and provider switched from Groq to Cerebras
  (gpt-oss-120b, 120B parameters) to eliminate daily token limit failures.

- **v3.2 (Cerebras / gpt-oss-120b - Stages 2+3+4+4b)**: A new Stage 4b
  deduplication call receives all rewritten requirements in a single LLM batch
  and removes semantic duplicates. IFA precision improves from 87.5% to **89.7%**
  (3 FPs vs 4) while F1 holds at **0.861**. Bristol N1 precision improves from
  53.8% to **61.1%** and F1 from 0.684 to **0.719**. N2 baseline run achieves
  F1 = 0.592.

- **v3.3 (Cerebras / gpt-oss-120b - prompt improvements)**: Extraction
  temperature lowered from 0.1 to **0.0** for reproducibility. Prompt additions:
  compliance/regulatory NF constraint patterns, existing-state disambiguation,
  and a refined multi-requirement splitting rule (split only for genuinely
  different capabilities, not two aspects of the same feature). Bristol N1
  improves to **F1 = 0.757** (best N1 result). N2 improves slightly to **F1 =
  0.599**. IFA regresses to F1 = 0.821 (v3.2 = 0.861) due to new FPs from the
  endorsed-feature pattern. Persistent failure modes: interviewer-turn extraction,
  operational-setup FPs, and aspirational-language FNs.

### What's next

1. **Interviewer-turn filtering** - REQ-004/005 in N2 v3.3 originate from
   declarative interviewer statements, not participant requirements. The current
   "sentences ending with ?" filter is insufficient. A speaker-role check
   (reject all extractions sourced solely from Interviewer turns) would eliminate
   this category of FP.
2. **Endorsed-feature over-extraction** - the v3.3 "endorsed features" pattern
   extracts training-context descriptions (e.g. VR simulation) as requirements.
   The pattern needs a narrower scope: only endorse features directly applicable
   to the target system, not analogous tools used in preparation.
3. **Implicit NF constraint extraction** - GT-030 (localisation), GT-031 (data
   residency), GT-033 (cloud hosting) are consistently missed in IFA. These are
   stated as background assumptions without modal verbs; the compliance/regulatory
   pattern added in v3.3 partially addresses this but has not yet reliably
   triggered for these turns.
4. **Aspirational-language FNs** - GT-013 (N2) and similar "Holy Grail" /
   wish-list statements are missed because they don't use requirement language.
   An explicit extraction rule for aspirational or future-ideal statements
   (e.g. "that would be ideal", "if we could have X") would improve recall on
   optional requirements.
5. **Additional Bristol transcripts** - N3, N4, S1–S3, U1–U3, O1–O3 remain
   unconverted. Adding them would provide a more robust generalisation test
   across different operator roles and interview styles.

## Output Format

```json
[
  {
    "id": "REQ-001",
    "type": "functional",
    "priority": "essential",
    "statement": "The system shall allow users to specify budget policies within the system.",
    "source": "Turn 5 (spk_1)"
  }
]
```

Fields:
- **id**: Sequential identifier (REQ-001, REQ-002, ...)
- **type**: `functional` or `non-functional`
- **priority**: `essential`, `preferred`, or `optional`
- **statement**: Normalised requirement in "The system shall ..." form
- **source**: Turn number and speaker from the original transcript

## Demo Guide

### Prerequisites

```bash
pip install openai python-dotenv
```

Create a `.env` file in the project root:
```
CEREBRAS_API_KEY=your_cerebras_api_key_here
```

Get a free API key (no credit card required) at [cloud.cerebras.ai](https://cloud.cerebras.ai).

### Running the pipeline

**1. Naive mode (no API needed, instant):**
```bash
python -m pipeline.run datasets/ifa/conversation.txt
```

**2. Naive mode with trace (shows all 5 stages):**
```bash
python -m pipeline.run --trace datasets/ifa/conversation.txt
```

**3. LLM mode (requires Cerebras API key):**
```bash
python -m pipeline.run --llm datasets/ifa/conversation.txt
```

**4. LLM mode with trace:**
```bash
python -m pipeline.run --llm --trace datasets/ifa/conversation.txt
```

### Running tests

```bash
python -m pytest tests/ -v
```

### Pre-generated outputs

All outputs are saved in `results/` - no API key needed to review them:

| File | Description |
|---|---|
| `datasets/ifa/conversation.txt` | IFA stakeholder elicitation session |
| `datasets/ifa/expected.json` | Ground truth - 41 requirements |
| `datasets/bristol/N1.txt` | Bristol N1 research interview |
| `datasets/bristol/N1_expected.json` | Ground truth - 16 requirements |
| `results/ifa/output_v1.0_naive.json` | Naive pipeline output (67 items) |
| `results/ifa/output_v2.0_groq.json` | LLM v2.0 output (23 items, Llama 70B) |
| `results/ifa/output_v3.1_llm.json` | LLM v3.1 output (32 items, gpt-oss-120b) |
| `results/ifa/output_v3.2_llm.json` | LLM v3.2 output (29 items, gpt-oss-120b + dedup) |
| `results/ifa/evaluation_v1.0_naive.md` | Evaluation of naive baseline |
| `results/ifa/evaluation_v2.0_groq.md` | Evaluation of Llama 70B via Groq |
| `results/ifa/evaluation_v3.1_llm.md` | Evaluation of v3.1 |
| `results/ifa/evaluation_v3.2_llm.md` | Evaluation of v3.2 |
| `results/ifa/output_v3.3_llm.json` | LLM v3.3 output (30 items, gpt-oss-120b + prompt improvements) |
| `results/ifa/evaluation_v3.3_llm.md` | Evaluation of v3.3 |
| `results/bristol/output_N1_v1.0_naive.json` | Bristol naive output (31 items) |
| `results/bristol/output_N1_v2.0_groq.json` | Bristol LLM v2.0 output (16 items) |
| `results/bristol/output_N1_v3.1_llm.json` | Bristol LLM v3.1 output (26 items, gpt-oss-120b) |
| `results/bristol/output_N1_v3.2_llm.json` | Bristol LLM v3.2 output (18 items, gpt-oss-120b + dedup) |
| `results/bristol/evaluation_N1_v2.0_groq.md` | Bristol evaluation of v2.0 |
| `results/bristol/evaluation_N1_v3.1_llm.md` | Bristol evaluation of v3.1 |
| `results/bristol/evaluation_N1_v3.2_llm.md` | Bristol N1 evaluation of v3.2 |
| `results/bristol/output_N1_v3.3_llm.json` | Bristol N1 LLM v3.3 output (18 items, gpt-oss-120b + prompt improvements) |
| `results/bristol/evaluation_N1_v3.3_llm.md` | Bristol N1 evaluation of v3.3 (current best for N1) |
| `datasets/bristol/N2.txt` | Bristol N2 research interview (converted from xlsx) |
| `datasets/bristol/N2_expected.json` | Ground truth - 13 requirements |
| `results/bristol/output_N2_v3.2_llm.json` | Bristol N2 LLM v3.2 output (14 items, gpt-oss-120b + dedup) |
| `results/bristol/evaluation_N2_v3.2_llm.md` | Bristol N2 evaluation of v3.2 baseline |
| `results/bristol/output_N2_v3.3_llm.json` | Bristol N2 LLM v3.3 output (17 items, gpt-oss-120b + prompt improvements) |
| `results/bristol/evaluation_N2_v3.3_llm.md` | Bristol N2 evaluation of v3.3 (current best for N2) |

## Requirements

- Python 3.10+
- `openai` and `python-dotenv` (for LLM mode only)
- A Cerebras API key (free tier - sign up at [cloud.cerebras.ai](https://cloud.cerebras.ai))
