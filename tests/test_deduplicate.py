"""Tests for Stage 4b: Deduplication."""

from unittest.mock import MagicMock, patch

from pipeline.deduplicate import deduplicate_requirements, _parse_decisions


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


def _decision(index, duplicate_of, confidence="high", reason="same behaviour"):
    return (
        f'[{{"index": {index}, "duplicate_of": {duplicate_of}, '
        f'"confidence": "{confidence}", "reason": "{reason}"}}]'
    )


# ---------------------------------------------------------------------------
# _parse_decisions unit tests
# ---------------------------------------------------------------------------

def test_parse_decisions_empty_array():
    assert _parse_decisions("[]", max_index=5) == []


def test_parse_decisions_single_high_confidence():
    raw = '[{"index": 1, "duplicate_of": 0, "confidence": "high", "reason": "same behaviour"}]'
    result = _parse_decisions(raw, max_index=5)
    assert len(result) == 1
    assert result[0]["index"] == 1
    assert result[0]["duplicate_of"] == 0
    assert result[0]["confidence"] == "high"
    assert result[0]["reason"] == "same behaviour"


def test_parse_decisions_multiple():
    raw = (
        '[{"index": 1, "duplicate_of": 0, "confidence": "high", "reason": "r1"},'
        ' {"index": 3, "duplicate_of": 2, "confidence": "medium", "reason": "r2"}]'
    )
    result = _parse_decisions(raw, max_index=5)
    assert len(result) == 2
    assert {d["index"] for d in result} == {1, 3}


def test_parse_decisions_out_of_range_dropped():
    raw = '[{"index": 9, "duplicate_of": 0, "confidence": "high", "reason": "r"}]'
    assert _parse_decisions(raw, max_index=5) == []


def test_parse_decisions_self_reference_dropped():
    raw = '[{"index": 1, "duplicate_of": 1, "confidence": "high", "reason": "r"}]'
    assert _parse_decisions(raw, max_index=5) == []


def test_parse_decisions_invalid_confidence_defaults_to_low():
    raw = '[{"index": 1, "duplicate_of": 0, "confidence": "maybe", "reason": "r"}]'
    result = _parse_decisions(raw, max_index=5)
    assert result[0]["confidence"] == "low"


def test_parse_decisions_markdown_fenced():
    raw = '```json\n[{"index": 2, "duplicate_of": 0, "confidence": "medium", "reason": "r"}]\n```'
    result = _parse_decisions(raw, max_index=10)
    assert len(result) == 1
    assert result[0]["index"] == 2


def test_parse_decisions_invalid_json():
    assert _parse_decisions("not json", max_index=5) == []


def test_parse_decisions_non_list_json():
    assert _parse_decisions('{"remove": [1]}', max_index=5) == []


def test_parse_decisions_missing_fields_skipped():
    raw = '[{"index": 1, "confidence": "high"}]'  # missing duplicate_of
    assert _parse_decisions(raw, max_index=5) == []


# ---------------------------------------------------------------------------
# deduplicate_requirements - naive mode (passthrough)
# ---------------------------------------------------------------------------

def test_naive_mode_returns_unchanged():
    reqs = [_req("The system shall do A."), _req("The system shall do B.")]
    result, decisions = deduplicate_requirements(reqs, mode="naive")
    assert result == reqs
    assert decisions == []


def test_naive_mode_empty_list():
    result, decisions = deduplicate_requirements([], mode="naive")
    assert result == []
    assert decisions == []


def test_single_item_skips_llm():
    reqs = [_req("The system shall do A.")]
    result, decisions = deduplicate_requirements(reqs, mode="llm")
    assert result == reqs
    assert decisions == []


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
def test_llm_mode_removes_exact_synonym(mock_get_client):
    """Clear synonym: 'send a notification' vs 'notify the user' — same behaviour."""
    client = MagicMock()
    mock_get_client.return_value = client
    llm_resp = _decision(1, 0, confidence="high", reason="same notification behaviour, different phrasing")
    client.chat.completions.create.return_value = _make_mock_response(llm_resp)

    reqs = [
        _req("The system shall send a notification when a budget limit is exceeded.", source_turn=5),
        _req("The system shall notify the user when the budget limit is reached.", source_turn=7),
    ]
    result, decisions = deduplicate_requirements(reqs, mode="llm")
    assert len(result) == 1
    assert result[0] == reqs[0]
    assert len(decisions) == 1
    assert decisions[0]["confidence"] == "high"
    assert decisions[0]["removed"] == reqs[1]["normalised"]
    assert decisions[0]["duplicate_of"] == reqs[0]["normalised"]


@patch("pipeline.llm_client.get_llm_client")
def test_llm_mode_removes_near_duplicate_with_medium_confidence(mock_get_client):
    """Near-duplicate: same core behaviour, one slightly more specific."""
    client = MagicMock()
    mock_get_client.return_value = client
    llm_resp = _decision(1, 0, confidence="medium", reason="both describe access control for budget data")
    client.chat.completions.create.return_value = _make_mock_response(llm_resp)

    reqs = [
        _req("The system shall allow only IFA administrative personnel and teams to access the budgeting system.", source_turn=13),
        _req("The system shall restrict access to financial records to authorised users only.", source_turn=15),
    ]
    result, decisions = deduplicate_requirements(reqs, mode="llm")
    assert len(result) == 1
    assert decisions[0]["confidence"] == "medium"


@patch("pipeline.llm_client.get_llm_client")
def test_llm_mode_keeps_distinct_related_requirements(mock_get_client):
    """Distinct but related: prevent movement vs sound alarm — different system actions."""
    client = MagicMock()
    mock_get_client.return_value = client
    client.chat.completions.create.return_value = _make_mock_response("[]")

    reqs = [
        _req("The system shall prevent movement into no-go zones.", source_turn=84),
        _req("The system shall sound an audible alarm when approaching a no-go zone.", source_turn=86),
    ]
    result, decisions = deduplicate_requirements(reqs, mode="llm")
    assert len(result) == 2
    assert decisions == []


@patch("pipeline.llm_client.get_llm_client")
def test_llm_mode_keeps_distinct_view_vs_export(mock_get_client):
    """Distinct: viewing data vs exporting data — different system actions."""
    client = MagicMock()
    mock_get_client.return_value = client
    client.chat.completions.create.return_value = _make_mock_response("[]")

    reqs = [
        _req("The system shall allow administrative users to view all transaction records.", source_turn=7),
        _req("The system shall allow export of data to journalists or press.", source_turn=22),
    ]
    result, decisions = deduplicate_requirements(reqs, mode="llm")
    assert len(result) == 2
    assert decisions == []


@patch("pipeline.llm_client.get_llm_client")
def test_llm_mode_preserves_order_after_removal(mock_get_client):
    client = MagicMock()
    mock_get_client.return_value = client
    raw = (
        '[{"index": 1, "duplicate_of": 0, "confidence": "high", "reason": "r1"},'
        ' {"index": 3, "duplicate_of": 2, "confidence": "high", "reason": "r2"}]'
    )
    client.chat.completions.create.return_value = _make_mock_response(raw)

    reqs = [
        _req("The system shall do A.", source_turn=1),
        _req("The system shall do A duplicate.", source_turn=2),
        _req("The system shall do B.", source_turn=5),
        _req("The system shall do B duplicate.", source_turn=6),
    ]
    result, decisions = deduplicate_requirements(reqs, mode="llm")
    assert len(result) == 2
    assert result[0]["normalised"] == "The system shall do A."
    assert result[1]["normalised"] == "The system shall do B."
    assert len(decisions) == 2


@patch("pipeline.llm_client.get_llm_client")
def test_llm_mode_decisions_log_content(mock_get_client):
    """decisions log entries have correct removed/duplicate_of/confidence/reason."""
    client = MagicMock()
    mock_get_client.return_value = client
    llm_resp = _decision(1, 0, confidence="high", reason="identical requirement")
    client.chat.completions.create.return_value = _make_mock_response(llm_resp)

    reqs = [
        _req("The system shall allow referees to insert game events in real time.", source_turn=17),
        _req("The system shall enable referees to log game events in real time.", source_turn=18),
    ]
    result, decisions = deduplicate_requirements(reqs, mode="llm")
    assert decisions[0]["removed"] == reqs[1]["normalised"]
    assert decisions[0]["duplicate_of"] == reqs[0]["normalised"]
    assert decisions[0]["confidence"] == "high"
    assert decisions[0]["reason"] == "identical requirement"


@patch("pipeline.llm_client.get_llm_client")
def test_llm_mode_falls_back_on_token_limit(mock_get_client):
    client = MagicMock()
    mock_get_client.return_value = client
    client.chat.completions.create.side_effect = Exception("Daily tokens per day limit exceeded")

    reqs = [
        _req("The system shall do A."),
        _req("The system shall do B."),
    ]
    result, decisions = deduplicate_requirements(reqs, mode="llm")
    assert result == reqs
    assert decisions == []
