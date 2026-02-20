"""Stage 5: Structuring — assign IDs and emit final JSON-ready list."""


def structure_requirements(
    rewritten: list[dict],
    turns: list[dict],
) -> list[dict]:
    """Produce the final structured requirements list.

    Each requirement has: id, type, priority, statement, source.
    The 'turns' list is used to look up the speaker role for the source field.
    """
    # Build a quick lookup: turn_index -> role
    role_lookup = {t["turn_index"]: t["role"] for t in turns}

    result = []
    for i, req in enumerate(rewritten, start=1):
        source_turn = req["source_turn"]
        role = role_lookup.get(source_turn, "unknown")
        result.append({
            "id": f"REQ-{i:03d}",
            "type": req["req_type"],
            "priority": req.get("priority", "preferred"),
            "statement": req["normalised"],
            "source": f"Turn {source_turn} ({role})",
        })

    return result
