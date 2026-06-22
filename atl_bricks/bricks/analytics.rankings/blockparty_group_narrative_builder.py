from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "analytics.rankings.blockparty_group_narrative_builder",
    "kind": "analyzer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["analytics.rankings_request.v1"],
    "outputs": ["analytics.rankings_response.v1"],
    "requires": [],
    "provides": ["analytics.blockparty_group_narrative"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["analytics", "rankings", "blockparty", "group", "narrative"],
    "description": "Build group-state narratives from Block Party group move, breadth, speed, and laggard-gap state.",
}


def build_blockparty_group_narrative(group: float, breadth: float, member_count: int, group_fast: float | None, breadth_fast: float | None, own_return: float | None, min_breadth: float, group_move_min: float, group_move_fast_min: float, group_move_strong: float) -> dict[str, Any]:
    lit_up = float(group) >= float(group_move_min) or (group_fast is not None and float(group_fast) >= float(group_move_fast_min))
    lit_down = float(group) <= -float(group_move_min) or (group_fast is not None and float(group_fast) <= -float(group_move_fast_min))
    strong_up = float(group) >= float(group_move_strong) or (group_fast is not None and float(group_fast) >= float(group_move_strong))
    strong_down = float(group) <= -float(group_move_strong) or (group_fast is not None and float(group_fast) <= -float(group_move_strong))
    breadth_ok = float(breadth) >= float(min_breadth) or (breadth_fast is not None and float(breadth_fast) >= float(min_breadth))
    gap = None if own_return is None else float(own_return) - float(group)
    if strong_up:
        state = "strong_up"
    elif strong_down:
        state = "strong_down"
    elif lit_up:
        state = "lit_up"
    elif lit_down:
        state = "lit_down"
    else:
        state = "neutral"
    return {
        "state": state,
        "group": float(group),
        "group_fast": None if group_fast is None else float(group_fast),
        "breadth": float(breadth),
        "breadth_fast": None if breadth_fast is None else float(breadth_fast),
        "member_count": int(member_count),
        "breadth_ok": breadth_ok,
        "lit_up": lit_up,
        "lit_down": lit_down,
        "strong_up": strong_up,
        "strong_down": strong_down,
        "own_return": own_return,
        "gap": gap,
        "narrative": f"{state}|group={float(group):+.2f}|group_fast={'na' if group_fast is None else f'{float(group_fast):+.2f}'}|breadth={float(breadth):.2f}|members={int(member_count)}",
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_blockparty_group_narrative(
        group=float(payload.get("group") or 0.0),
        breadth=float(payload.get("breadth") or 0.0),
        member_count=int(payload.get("member_count") or 0),
        group_fast=payload.get("group_fast"),
        breadth_fast=payload.get("breadth_fast"),
        own_return=payload.get("own_return"),
        min_breadth=float(payload.get("min_breadth") or 0.0),
        group_move_min=float(payload.get("group_move_min") or 0.0),
        group_move_fast_min=float(payload.get("group_move_fast_min") or 0.0),
        group_move_strong=float(payload.get("group_move_strong") or 0.0),
    )
    output_packet = {
        "packet_type": "analytics.rankings_response.v1",
        "packet_version": "analytics.rankings_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "blockparty-group-narrative",
        "brick_id": CONCEPT["id"],
        "kind": "analysis",
        "label": "Built Block Party group narrative.",
        "refs": [],
        "data": {"state": value.get("state", "neutral"), "breadth_ok": value.get("breadth_ok", False)},
    }]
