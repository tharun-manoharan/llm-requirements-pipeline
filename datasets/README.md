# Datasets

Raw input conversations and their hand-annotated ground-truth requirements.
Each sub-folder is one dataset source.

## Structure

```
datasets/
  test/                      # Minimal synthetic conversation used by unit tests
    conversation.txt
    expected.json

  ifa/                       # Real IFA stakeholder requirements-elicitation session
    conversation.txt
    expected.json            # 41 ground-truth requirements

  bristol/                   # Semi-structured interviews — trust in space teleoperation
    N1.txt                   # Interview N1 (nuclear/industrial arm operator)
    N1_expected.json         # 16 ground-truth requirements
    N2.txt                   # (to be added)
    ...
```

## Conversation format

All files use the simple two-role format parsed by `pipeline/ingest.py`:

```
SpeakerLabel: turn text here
SpeakerLabel: next turn
```

Common role labels: `Stakeholder`, `Developer`, `Interviewer`, `Participant`.
Lines with no matching label are treated as continuations of the previous turn.

## Ground-truth schema

`*_expected.json` / `*expected.json` files follow this schema:

```json
[
  {
    "id": "GT-001",
    "type": "functional" | "non-functional",
    "priority": "essential" | "preferred" | "optional",
    "statement": "The system shall ...",
    "source": "Turn N (role)"
  }
]
```

Annotation is manual: read the conversation, identify statements that express
a genuine system need, and write a clean "The system shall …" statement for each.

## Dataset sources

| Folder | Description | Size |
|---|---|---|
| `test/` | Synthetic toy example (password reset) | 3 turns, 2 GT reqs |
| `ifa/` | IFA sports system — requirements elicitation session | ~90 turns, 41 GT reqs |
| `bristol/` | Bristol PhD thesis — trust in space teleoperation interviews | 13 interviews (N1–N4, S1–S3, U1–U3, O1–O3) |

**Bristol source**: *"The Importance of Trust in Space Teleoperation"* — University of
Bristol PhD thesis. Data: <https://data.bristol.ac.uk/data/dataset/suauncyhoc1c2ahjpro04fwmy>

## Pipeline outputs and evaluations

Pipeline outputs (JSON) and evaluation reports (Markdown) live in `results/`,
not here. See `results/README.md`.
