"""Tests for Stage 2: Conversation Segmentation."""

from pipeline.segment import segment_turns


def _make_turn(text, index=0, role="stakeholder"):
    return {"turn_index": index, "role": role, "text": text}


def test_keyword_match():
    turns = [_make_turn("Users should be able to reset their password.")]
    result = segment_turns(turns)
    assert result[0]["is_candidate"] is True


def test_bare_filler_excluded():
    for filler in ["Ok.", "yes", "Got it", "Sure!", "Thanks.", "Right"]:
        turns = [_make_turn(filler)]
        result = segment_turns(turns)
        assert result[0]["is_candidate"] is False, f"Expected False for: {filler}"


def test_filler_with_content_not_excluded():
    turns = [_make_turn("Yes, send them a reset link.")]
    result = segment_turns(turns)
    assert result[0]["is_candidate"] is True


def test_no_keywords():
    turns = [_make_turn("I think we discussed this last week.")]
    result = segment_turns(turns)
    assert result[0]["is_candidate"] is False


def test_multiple_turns():
    turns = [
        _make_turn("Users should log in.", 0),
        _make_turn("Ok.", 1, "developer"),
        _make_turn("The system must encrypt data.", 2),
    ]
    result = segment_turns(turns)
    assert result[0]["is_candidate"] is True
    assert result[1]["is_candidate"] is False
    assert result[2]["is_candidate"] is True
