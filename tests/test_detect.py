"""Tests for Stage 3: Candidate Requirement Detection."""

from pipeline.detect import detect_candidates


def _make_segmented(text, is_candidate=True, index=0, role="stakeholder"):
    return {
        "turn_index": index,
        "role": role,
        "text": text,
        "is_candidate": is_candidate,
    }


def test_questions_discarded():
    turns = [_make_segmented("Should that be via email?")]
    result = detect_candidates(turns)
    assert len(result) == 0


def test_functional_classification():
    turns = [_make_segmented("Users should be able to reset their password.")]
    result = detect_candidates(turns)
    assert len(result) == 1
    assert result[0]["req_type"] == "functional"


def test_non_functional_classification():
    turns = [_make_segmented("The system must encrypt all data at rest.")]
    result = detect_candidates(turns)
    assert len(result) == 1
    assert result[0]["req_type"] == "non-functional"


def test_non_candidate_turns_skipped():
    turns = [_make_segmented("Ok.", is_candidate=False)]
    result = detect_candidates(turns)
    assert len(result) == 0


def test_multi_sentence_turn():
    turns = [_make_segmented(
        "The system should log all events. This is important for auditing."
    )]
    result = detect_candidates(turns)
    # First sentence has "should" + "log"; second has "audit" (NF keyword check)
    assert len(result) >= 1
    assert result[0]["sentence"] == "The system should log all events."


def test_source_turn_preserved():
    turns = [_make_segmented("Users must authenticate.", index=5)]
    result = detect_candidates(turns)
    assert result[0]["source_turn"] == 5
