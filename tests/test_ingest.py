"""Tests for Stage 1: Input Ingestion."""

from pipeline.ingest import parse_conversation


def test_basic_three_turn_conversation():
    raw = (
        "Stakeholder: Users should be able to reset their password.\n"
        "Developer: Should that be via email?\n"
        "Stakeholder: Yes, send them a reset link."
    )
    turns = parse_conversation(raw)
    assert len(turns) == 3
    assert turns[0]["turn_index"] == 0
    assert turns[0]["role"] == "stakeholder"
    assert turns[0]["text"] == "Users should be able to reset their password."
    assert turns[1]["role"] == "developer"
    assert turns[2]["turn_index"] == 2


def test_empty_input():
    assert parse_conversation("") == []
    assert parse_conversation("   \n\n  ") == []


def test_case_insensitive_roles():
    raw = "STAKEHOLDER: Must encrypt data.\nDEVELOPER: OK."
    turns = parse_conversation(raw)
    assert len(turns) == 2
    assert turns[0]["role"] == "stakeholder"
    assert turns[1]["role"] == "developer"


def test_multiline_turn():
    raw = (
        "Stakeholder: The system must log all access attempts.\n"
        "Including failed ones.\n"
        "Developer: Got it."
    )
    turns = parse_conversation(raw)
    assert len(turns) == 2
    assert "Including failed ones." in turns[0]["text"]
    assert turns[1]["text"] == "Got it."


def test_blank_lines_ignored():
    raw = (
        "Stakeholder: First requirement.\n"
        "\n"
        "\n"
        "Developer: Understood."
    )
    turns = parse_conversation(raw)
    assert len(turns) == 2


def test_timestamped_format():
    raw = (
        "[0:00:00] spk_0: We are here for the IFA system.\n"
        "[0:01:17] spk_1: The budget consists of income and expenses.\n"
        "[0:02:15] spk_2: Okay, so the IFA is an association?"
    )
    turns = parse_conversation(raw)
    assert len(turns) == 3
    assert turns[0]["role"] == "spk_0"
    assert turns[0]["text"] == "We are here for the IFA system."
    assert turns[1]["role"] == "spk_1"
    assert turns[2]["turn_index"] == 2


def test_timestamped_format_auto_detected():
    raw_simple = "Stakeholder: Must encrypt data."
    raw_ts = "[0:00:00] spk_0: Must encrypt data."
    t1 = parse_conversation(raw_simple)
    t2 = parse_conversation(raw_ts)
    assert t1[0]["role"] == "stakeholder"
    assert t2[0]["role"] == "spk_0"
    assert t1[0]["text"] == t2[0]["text"]
