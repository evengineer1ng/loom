from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.narration.trade_route_status_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🚚",
    "deterministic": True,
    "inputs": ["runtime.narration_request.v1"],
    "outputs": ["runtime.narration_response.v1"],
    "requires": [],
    "provides": ["runtime.trade_route_status_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "narration", "trade", "route", "status"],
    "description": "Package narrator-facing trade-route status with crew identity, progress percentage, next leg description, and emitted status copy.",
}


def build_trade_route_status_packet(
    crew_name: str,
    ship_name: str,
    progress_percent: float,
    next_leg: dict[str, Any] | None,
    title: str,
    body: str,
) -> dict[str, Any]:
    return {
        "crew_name": str(crew_name),
        "ship_name": str(ship_name),
        "progress_percent": float(progress_percent),
        "next_leg": dict(next_leg or {}),
        "title": str(title),
        "body": str(body),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_trade_route_status_packet(
        crew_name=str(payload.get("crew_name") or ""),
        ship_name=str(payload.get("ship_name") or ""),
        progress_percent=float(payload.get("progress_percent") or 0.0),
        next_leg=dict(payload.get("next_leg") or {}),
        title=str(payload.get("title") or ""),
        body=str(payload.get("body") or ""),
    )
    output_packet = {
        "packet_type": "runtime.narration_response.v1",
        "packet_version": "runtime.narration_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "trade-route-status-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built trade-route status packet.",
        "refs": [],
        "data": {
            "crew_name": value.get("crew_name", ""),
            "progress_percent": value.get("progress_percent", 0.0),
            "title": value.get("title", ""),
        },
    }]
