# LLM Requirements Pipeline

A 5-stage NLP pipeline that extracts structured software requirements from raw
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
       |            naive: regex rules  |  llm: Llama 3.3 70B via Groq
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

| Stage | Module | Naive | LLM |
|-------|--------|-------|-----|
| 1. Ingest | `pipeline/ingest.py` | Regex parser | - |
| 2+3. Extract | `pipeline/extract.py` | - | Llama 3.3 70B (Groq) |
| 2. Segment | `pipeline/segment.py` | Keyword matching | (replaced by extract) |
| 3. Detect | `pipeline/detect.py` | Sentence split + classify | (replaced by extract) |
| 4. Rewrite | `pipeline/rewrite.py` | Regex rules | Llama 3.3 70B (Groq) |
| 5. Structure | `pipeline/structure.py` | ID assignment | - |
| Shared | `pipeline/llm_client.py` | - | Groq client factory |

## Progress and Results

Evaluated against **41 manually curated ground-truth requirements** from a real stakeholder interview transcript
(`examples/conversation_02.txt`).

### Comparison across versions

| Metric | v1.0 Naive | v1.1 LLM 7B | v1.2 LLM 7B+Ctx | v2.0 LLM 70B |
|---|---|---|---|---|
| Model | - | Qwen 7B (HF) | Qwen 7B (HF) | **Llama 3.3 70B (Groq)** |
| LLM stages | - | Stage 4 only | Stage 4 only | **Stage 4 only** |
| Output count | 67 | 41 | 31 | **23** |
| **Precision** | 40.3% | 75.6% | 80.6% | **91.3%** |
| **Recall** | 65.9% | **70.7%** | 61.0% | 53.7% |
| **F1 Score** | 0.500 | **0.731** | 0.694 | 0.676 |
| Usable outputs | 0% | 61% | 81% | **91%** |
| Priority accuracy | - | - | 34% | **57%** |
| False positives | 40 | 10 | 6 | **2** |
| False negatives | 14 | 12 | 16 | 19 |
| Speed (67 candidates) | instant | ~3-5 min | ~3-5 min | **~10 sec** |

### v3.0 - LLM Stages 2+3 (in progress)

The latest version upgrades stages 2-3 from keyword matching to LLM-based
semantic extraction. Instead of matching 24 keywords, the LLM reads the full
conversation and identifies requirements by meaning - catching business rules
stated as facts, implicit permissions, procedural language, and other patterns
that keyword matching misses.

**What changed:**
- New `pipeline/extract.py` - single LLM call replaces stages 2+3 in `--llm` mode
- New `pipeline/llm_client.py` - shared Groq client used by both extract and rewrite
- `pipeline/run.py` - branches to LLM extraction when `--llm` flag is set
- Recall-biased extraction prompt (include borderline items; Stage 4 filters)
- Robust error handling: per-minute rate limit retries, daily token limit
  detection, automatic fallback to naive mode
- 8 new unit tests for the extraction JSON parser (40 total, all passing)

**Preliminary results** (from initial run before rate limiting):
- Extraction found **115 candidates** vs 67 from keyword matching (+72%)
- Many previously missed ground-truth requirements were caught
- Full evaluation pending (Groq free tier daily token limit reached)

### Key findings

- **v1.0 (Naive baseline)**: Keyword matching finds many candidates but has
  extremely high noise (40 false positives) and 0% of outputs are usable
  requirements - the regex rewriter just prepends "The system shall" to raw
  conversational text.

- **v1.1 (LLM rewrite - Qwen 7B)**: Adding a 7B LLM to Stage 4 nearly doubled
  precision (40% -> 76%) and took usable output from 0% to 61%. The LLM serves
  dual purpose: rewriting and filtering non-requirements. **Best F1 (0.731).**

- **v1.2 (LLM + context window - Qwen 7B)**: Passing 2 surrounding turns as
  context improved precision further (81%) and output quality (81% usable), but
  the 7B model became too aggressive at filtering, dropping recall to 61%.
  Priority classification non-functional (34% accuracy, model defaults to
  "preferred").

- **v2.0 (Groq / Llama 3.3 70B)**: Upgrading to a 10x larger model dramatically
  improved output quality - **91% precision, 91% usable, zero poor rewrites, and
  57% priority accuracy**. The 70B model is a much better rewriter and filter,
  but it is also more aggressive, dropping recall to 54%. Speed improved from
  minutes to seconds thanks to Groq's hardware-accelerated inference.

- **v3.0 (LLM Stages 2+3)**: Addresses the #1 recall bottleneck - 8+ false
  negatives caused by keyword matching never finding certain requirements.
  Replaces keyword matching with semantic LLM extraction. Initial run shows 72%
  more candidates extracted. Full evaluation pending.

### What's next

1. **Complete v3.0 evaluation** - run full pipeline and evaluate against ground
   truth once Groq daily token budget resets.
2. **Fix type classification** - functional vs non-functional labels still have
   ~24% error rate across all versions.
3. **Improve priority** - the 70B model never uses "preferred" (treats everything
   as essential or optional). Few-shot examples could fix this.

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
pip install groq python-dotenv
```

Create a `.env` file in the project root:
```
GROQ_API_KEY=your_groq_api_key_here
```

### Running the pipeline

**1. Naive mode (no API needed, instant):**
```bash
python -m pipeline.run examples/conversation_01.txt
```

**2. Naive mode with trace (shows all 5 stages):**
```bash
python -m pipeline.run --trace examples/conversation_01.txt
```

**3. LLM mode (requires Groq API key):**
```bash
python -m pipeline.run --llm examples/conversation_02.txt
```

**4. LLM mode with trace:**
```bash
python -m pipeline.run --llm --trace examples/conversation_02.txt
```

### Quick demo sequence

For a demo, run these in order:

```bash
# Step 1: Show naive baseline (instant, no API)
python -m pipeline.run --trace examples/conversation_01.txt

# Step 2: Show naive on the real IFA conversation (instant)
python -m pipeline.run examples/conversation_02.txt

# Step 3: Show LLM improvement (~2-3 min with Groq)
python -m pipeline.run --llm examples/conversation_02.txt

# Step 4: Compare outputs side by side
#   examples/naive_output_02.json    - 67 items, 0% usable   (v1.0)
#   examples/llm_output_02.json      - 41 items, 61% usable  (v1.1)
#   examples/llm_output_02_v2.json   - 31 items, 81% usable  (v1.2)
#   examples/llm_output_02_v3.json   - 23 items, 91% usable  (v2.0)
#   examples/expected_output_02.json - 41 items ground truth

# Step 5: Run the test suite
python -m pytest tests/ -v
```

### Pre-generated outputs (no API needed)

If the Groq API is unavailable during the demo, all outputs are already saved:

| File | Description |
|---|---|
| `examples/conversation_01.txt` | Simple 3-line test conversation |
| `examples/conversation_02.txt` | Real IFA stakeholder interview (~40 min) |
| `examples/expected_output_01.json` | Ground truth for conversation 01 (2 reqs) |
| `examples/expected_output_02.json` | Ground truth for conversation 02 (41 reqs) |
| `examples/naive_output_02.json` | Naive pipeline output (67 items) |
| `examples/llm_output_02.json` | LLM v1.1 output (41 items, Qwen 7B) |
| `examples/llm_output_02_v2.json` | LLM v1.2 output (31 items, Qwen 7B + context) |
| `examples/llm_output_02_v3.json` | LLM v2.0 output (23 items, Llama 70B) |
| `examples/evaluation_v1.0_naive.md` | Detailed evaluation of naive baseline |
| `examples/evaluation_v1.1_llm_rewrite.md` | Evaluation of Qwen 7B rewrite |
| `examples/evaluation_v1.2_llm_context.md` | Evaluation of Qwen 7B + context |
| `examples/evaluation_v2.0_groq.md` | Evaluation of Llama 70B via Groq |

### Running tests

```bash
python -m pytest tests/ -v
```

## Requirements

- Python 3.10+
- `groq` and `python-dotenv` (for LLM mode only)
- A Groq API key (free tier works - sign up at console.groq.com)
