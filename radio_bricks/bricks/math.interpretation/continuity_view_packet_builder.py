from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.interpretation.continuity_view_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧷",
    "deterministic": True,
    "inputs": ["math.interpretation_request.v1"],
    "outputs": ["math.interpretation_response.v1"],
    "requires": [],
    "provides": ["math.continuity_view_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "interpretation", "continuity", "thread", "event", "ordinal"],
    "description": "Project an event through the continuity fader by stripping carried ordinal state when continuity is off.",
}


def build_continuity_view_packet(event: dict[str, Any] | None, continuity: bool) -> dict[str, Any]:
    view = dict(event or {})
    if not continuity:
        view.pop("ordinal", None)
    return {
        "event": view,
        "continuity": bool(continuity),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_continuity_view_packet(
        event=dict(payload.get("event") or {}),
        continuity=bool(payload.get("continuity")),
    )
    output_packet = {
        "packet_type": "math.interpretation_response.v1",
        "packet_version": "math.interpretation_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "continuity-view-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built continuity-view packet.",
        "refs": [],
        "data": {
            "continuity": value.get("continuity", False),
            "has_ordinal": "ordinal" in (value.get("event") or {}),
        },
    }]
