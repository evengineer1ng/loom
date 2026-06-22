from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "assembly.loom.trade_route_plan_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🗺️",
    "deterministic": True,
    "inputs": ["assembly.loom_request.v1"],
    "outputs": ["assembly.loom_response.v1"],
    "requires": [],
    "provides": ["assembly.trade_route_plan_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["assembly", "loom", "trade", "route", "plan"],
    "description": "Package a trade-route plan with route identity, repeat behavior, global buy list, and ordered leg definitions.",
}


def build_trade_route_plan_packet(
    name: str,
    repeat: bool,
    global_buy_commodities: dict[str, Any] | None,
    legs: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    return {
        "name": str(name),
        "repeat": bool(repeat),
        "global_buy_commodities": dict(global_buy_commodities or {}),
        "legs": [dict(item) for item in (legs or [])],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_trade_route_plan_packet(
        name=str(payload.get("name") or ""),
        repeat=bool(payload.get("repeat")),
        global_buy_commodities=dict(payload.get("global_buy_commodities") or {}),
        legs=list(payload.get("legs") or []),
    )
    output_packet = {
        "packet_type": "assembly.loom_response.v1",
        "packet_version": "assembly.loom_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "trade-route-plan-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built trade-route plan packet.",
        "refs": [],
        "data": {
            "name": value.get("name", ""),
            "leg_count": len(value.get("legs", [])),
            "repeat": value.get("repeat", False),
        },
    }]
