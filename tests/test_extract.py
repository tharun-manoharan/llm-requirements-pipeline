"""Tests for the LLM extraction module (stages 2+3 combined)."""

import json

from pipeline.extract import _parse_extraction_response


def test_parse_valid_json():
    response = json.dumps({
        "requirements": [
            {"sentence": "Each team manages its own budget.", "source_turn": 3, "req_type": "functional"},
            {"sentence": "Data must be encrypted.", "source_turn": 10, "req_type": "non-functional"},
        ]
    })
    result = _parse_extraction_response(response, max_turn_index=130)
    assert len(result) == 2
    assert result[0]["sentence"] == "Each team manages its own budget."
    assert result[0]["source_turn"] == 3
    assert result[0]["req_type"] == "functional"
    assert result[1]["req_type"] == "non-functional"


def test_parse_bare_array():
    response = json.dumps([
        {"sentence": "Test requirement.", "source_turn": 0, "req_type": "functional"}
    ])
    result = _parse_extraction_response(response, max_turn_index=10)
    assert len(result) == 1
    assert result[0]["sentence"] == "Test requirement."


def test_parse_missing_sentence_skipped():
    response = json.dumps({
        "requirements": [
            {"source_turn": 3, "req_type": "functional"},
            {"sentence": "Valid.", "source_turn": 3, "req_type": "functional"},
        ]
    })
    result = _parse_extraction_response(response, max_turn_index=10)
    assert len(result) == 1
    assert result[0]["sentence"] == "Valid."


def test_parse_invalid_turn_index_skipped():
    response = json.dumps({
        "requirements": [
            {"sentence": "Bad turn.", "source_turn": 999, "req_type": "functional"},
            {"sentence": "Negative.", "source_turn": -1, "req_type": "functional"},
            {"sentence": "Good turn.", "source_turn": 5, "req_type": "functional"},
        ]
    })
    result = _parse_extraction_response(response, max_turn_index=10)
    assert len(result) == 1
    assert result[0]["source_turn"] == 5


def test_parse_bad_req_type_defaults_to_functional():
    response = json.dumps({
        "requirements": [
            {"sentence": "Test.", "source_turn": 0, "req_type": "banana"},
        ]
    })
    result = _parse_extraction_response(response, max_turn_index=10)
    assert result[0]["req_type"] == "functional"


def test_parse_empty_requirements():
    response = json.dumps({"requirements": []})
    result = _parse_extraction_response(response, max_turn_index=10)
    assert result == []


def test_output_contract_matches_stage4_input():
    """Verify output has exactly the keys Stage 4 expects."""
    response = json.dumps({
        "requirements": [
            {"sentence": "Budget management per team.", "source_turn": 3, "req_type": "functional"}
        ]
    })
    result = _parse_extraction_response(response, max_turn_index=130)
    assert set(result[0].keys()) == {"sentence", "source_turn", "req_type"}


def test_parse_whitespace_sentence_skipped():
    response = json.dumps({
        "requirements": [
            {"sentence": "   ", "source_turn": 0, "req_type": "functional"},
            {"sentence": "Real requirement.", "source_turn": 1, "req_type": "functional"},
        ]
    })
    result = _parse_extraction_response(response, max_turn_index=10)
    assert len(result) == 1
    assert result[0]["sentence"] == "Real requirement."
