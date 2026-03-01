"""Tests for Stage 4b: Deduplication."""

from unittest.mock import MagicMock, patch

from pipeline.deduplicate import deduplicate_requirements, _parse_indices


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _req(normalised, source_turn=0, req_type="functional", priority="preferred"):
    return {
        "sentence": "original text",
        "source_turn": source_turn,
        "req_type": req_type,
        "priority": priority,
        "normalised": normalised,
    }


# ---------------------------------------------------------------------------
# _parse_indices unit tests
# ---------------------------------------------------------------------------

def test_parse_indices_empty_array():
    assert _parse_indices("[]", max_index=5) == set()


def test_parse_indices_normal():
    assert _parse_indices("[1, 3]", max_index=5) == {1, 3}


def test_parse_indices_out_of_range_dropped():
    assert _parse_indices("[0, 9]", max_index=5) == {0}


def test_parse_indices_markdown_fenced():
    raw = "```json\n[2, 4]\n```"
    assert _parse_indices(raw, max_index=10) == {2, 4}


def test_parse_indices_invalid_json():
    assert _parse_indices("not json", max_index=5) == set()


def test_parse_indices_non_list_json():
    assert _parse_indices('{"remove": [1]}', max_index=5) == set()


# ---------------------------------------------------------------------------
# deduplicate_requirements - naive mode (passthrough)
# ---------------------------------------------------------------------------

def test_naive_mode_returns_unchanged():
    reqs = [_req("The system shall do A."), _req("The system shall do B.")]
    result = deduplicate_requirements(reqs, mode="naive")
    assert result == reqs


def test_naive_mode_empty_list():
    assert deduplicate_requirements([], mode="naive") == []


def test_single_item_skips_llm():
    reqs = [_req("The system shall do A.")]
    # Should return without any LLM call regardless of mode
    result = deduplicate_requirements(reqs, mode="llm")
    assert result == reqs


# ---------------------------------------------------------------------------
# deduplicate_requirements - LLM mode (mocked)
# ---------------------------------------------------------------------------

def _make_mock_response(content: str):
    msg = MagicMock()
    msg.content = content
    choice = MagicMock()
    choice.message = msg
    resp = MagicMock()
    resp.choices = [choice]
    return resp


@patch("pipeline.llm_client.get_llm_client")
def test_llm_mode_removes_duplicate(mock_get_client):
    client = MagicMock()
    mock_get_client.return_value = client
    # LLM says remove index 1 (the duplicate)
    client.chat.completions.create.return_value = _make_mock_response("[1]")

    reqs = [
        _req("The system shall allow only teams to insert budget transactions.", source_turn=29),
        _req("The system shall restrict each team to access only its own financial data.", source_turn=29),
    ]
    result = deduplicate_requirements(reqs, mode="llm")
    assert len(result) == 1
    assert result[0] == reqs[0]


@patch("pipeline.llm_client.get_llm_client")
def test_llm_mode_no_duplicates(mock_get_client):
    client = MagicMock()
    mock_get_client.return_value = client
    client.chat.completions.create.return_value = _make_mock_response("[]")

    reqs = [
        _req("The system shall prevent movement into no-go zones.", source_turn=84),
        _req("The system shall sound an audible alarm near no-go zones.", source_turn=86),
    ]
    result = deduplicate_requirements(reqs, mode="llm")
    assert len(result) == 2


@patch("pipeline.llm_client.get_llm_client")
def test_llm_mode_preserves_order_after_removal(mock_get_client):
    client = MagicMock()
    mock_get_client.return_value = client
    # Remove indices 1 and 3
    client.chat.completions.create.return_value = _make_mock_response("[1, 3]")

    reqs = [
        _req("The system shall do A.", source_turn=1),
        _req("The system shall do A duplicate.", source_turn=2),
        _req("The system shall do B.", source_turn=5),
        _req("The system shall do B duplicate.", source_turn=6),
    ]
    result = deduplicate_requirements(reqs, mode="llm")
    assert len(result) == 2
    assert result[0]["normalised"] == "The system shall do A."
    assert result[1]["normalised"] == "The system shall do B."


@patch("pipeline.llm_client.get_llm_client")
def test_llm_mode_falls_back_on_token_limit(mock_get_client):
    client = MagicMock()
    mock_get_client.return_value = client
    client.chat.completions.create.side_effect = Exception("Daily tokens per day limit exceeded")

    reqs = [
        _req("The system shall do A."),
        _req("The system shall do B."),
    ]
    result = deduplicate_requirements(reqs, mode="llm")
    # Should return original list unchanged
    assert result == reqs
