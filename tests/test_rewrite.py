"""Tests for Stage 4: Requirement Rewriting / Normalisation."""

from pipeline.rewrite import rewrite_requirements


def _make_candidate(sentence, source_turn=0, req_type="functional"):
    return {"sentence": sentence, "source_turn": source_turn, "req_type": req_type}


def test_rule1_able_to():
    candidates = [_make_candidate(
        "Users should be able to reset their password if they forget it."
    )]
    result = rewrite_requirements(candidates)
    assert result[0]["normalised"] == (
        "The system shall allow users to reset their password if they forget it."
    )


def test_rule2_should_verb():
    candidates = [_make_candidate("The system should log all events.")]
    result = rewrite_requirements(candidates)
    assert result[0]["normalised"] == "The system shall log all events."


def test_rule3_imperative_with_filler():
    candidates = [_make_candidate("Yes, send them a reset link.")]
    result = rewrite_requirements(candidates)
    assert result[0]["normalised"] == "The system shall send them a reset link."


def test_fallback():
    candidates = [_make_candidate("All data needs encryption.")]
    result = rewrite_requirements(candidates)
    assert result[0]["normalised"].startswith("The system shall")
    assert result[0]["normalised"].endswith(".")


def test_no_double_period():
    candidates = [_make_candidate("Users must log in.")]
    result = rewrite_requirements(candidates)
    assert not result[0]["normalised"].endswith("..")


def test_original_fields_preserved():
    candidates = [_make_candidate("Users must log in.", source_turn=3, req_type="functional")]
    result = rewrite_requirements(candidates)
    assert result[0]["source_turn"] == 3
    assert result[0]["req_type"] == "functional"
    assert "normalised" in result[0]
