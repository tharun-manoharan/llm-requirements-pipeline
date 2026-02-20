"""Tests for Stage 5: Structuring."""

import json

from pipeline.structure import structure_requirements


def _make_rewritten(normalised, source_turn=0, req_type="functional"):
    return {
        "sentence": "original",
        "source_turn": source_turn,
        "req_type": req_type,
        "normalised": normalised,
    }


def test_sequential_ids():
    rewritten = [
        _make_rewritten("The system shall do A."),
        _make_rewritten("The system shall do B."),
        _make_rewritten("The system shall do C."),
    ]
    turns = [{"turn_index": 0, "role": "stakeholder", "text": "..."}]
    result = structure_requirements(rewritten, turns)
    assert result[0]["id"] == "REQ-001"
    assert result[1]["id"] == "REQ-002"
    assert result[2]["id"] == "REQ-003"


def test_source_includes_role():
    rewritten = [_make_rewritten("The system shall do X.", source_turn=2)]
    turns = [
        {"turn_index": 0, "role": "stakeholder", "text": "..."},
        {"turn_index": 1, "role": "developer", "text": "..."},
        {"turn_index": 2, "role": "stakeholder", "text": "..."},
    ]
    result = structure_requirements(rewritten, turns)
    assert result[0]["source"] == "Turn 2 (stakeholder)"


def test_json_serialisable():
    rewritten = [_make_rewritten("The system shall do X.")]
    turns = [{"turn_index": 0, "role": "stakeholder", "text": "..."}]
    result = structure_requirements(rewritten, turns)
    # Should not raise
    json.dumps(result)


def test_output_schema():
    rewritten = [_make_rewritten("The system shall do X.", req_type="non-functional")]
    turns = [{"turn_index": 0, "role": "stakeholder", "text": "..."}]
    result = structure_requirements(rewritten, turns)
    req = result[0]
    assert set(req.keys()) == {"id", "type", "priority", "statement", "source"}
    assert req["type"] == "non-functional"
    assert req["statement"] == "The system shall do X."
