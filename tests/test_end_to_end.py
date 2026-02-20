"""End-to-end pipeline test."""

import json
import os

from pipeline.run import run_pipeline


EXAMPLE_CONVERSATION = """\
Stakeholder: Users should be able to reset their password if they forget it.
Developer: Should that be via email?
Stakeholder: Yes, send them a reset link."""


def test_full_pipeline():
    result = run_pipeline(EXAMPLE_CONVERSATION)
    assert len(result) == 2

    assert result[0]["id"] == "REQ-001"
    assert result[0]["type"] == "functional"
    assert "reset their password" in result[0]["statement"]
    assert result[0]["source"] == "Turn 0 (stakeholder)"

    assert result[1]["id"] == "REQ-002"
    assert result[1]["type"] == "functional"
    assert "send" in result[1]["statement"].lower()
    assert result[1]["source"] == "Turn 2 (stakeholder)"


def test_golden_file():
    examples_dir = os.path.join(os.path.dirname(__file__), "..", "examples")
    conversation_path = os.path.join(examples_dir, "conversation_01.txt")
    expected_path = os.path.join(examples_dir, "expected_output_01.json")

    with open(conversation_path, "r") as f:
        raw = f.read()
    with open(expected_path, "r") as f:
        expected = json.load(f)

    result = run_pipeline(raw)
    # Compare id, type, statement, source (priority depends on mode)
    assert len(result) == len(expected)
    for r, e in zip(result, expected):
        assert r["id"] == e["id"]
        assert r["type"] == e["type"]
        assert r["statement"] == e["statement"]
        assert r["source"] == e["source"]


def test_empty_input():
    result = run_pipeline("")
    assert result == []


def test_no_requirements():
    raw = "Developer: Let's discuss the timeline.\nStakeholder: Sure, sounds good."
    result = run_pipeline(raw)
    assert result == []
