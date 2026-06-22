from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "narrative.profile.active_arc_selection_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🪡",
    "deterministic": True,
    "inputs": ["narrative.profile_request.v1"],
    "outputs": ["narrative.profile_response.v1"],
    "requires": [],
    "provides": ["narrative.active_arc_selection_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["narrative", "profile", "arc", "selection", "forced"],
    "description": "Package deterministic active-arc and minor-role selection, including forced insertion of the Hidden Knower arc.",
}


def build_active_arc_selection_packet(
    shuffled_arc_codes: list[str] | None,
    active_arc_codes: list[str] | None,
    minor_role_codes: list[str] | None,
    forced_arc_code: str,
    forced_arc_inserted: bool,
) -> dict[str, Any]:
    return {
        "shuffled_arc_codes": list(shuffled_arc_codes or []),
        "active_arc_codes": list(active_arc_codes or []),
        "minor_role_codes": list(minor_role_codes or []),
        "forced_arc_code": forced_arc_code,
        "forced_arc_inserted": bool(forced_arc_inserted),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_active_arc_selection_packet(
        shuffled_arc_codes=list(payload.get("shuffled_arc_codes") or []),
        active_arc_codes=list(payload.get("active_arc_codes") or []),
        minor_role_codes=list(payload.get("minor_role_codes") or []),
        forced_arc_code=str(payload.get("forced_arc_code") or "CA3"),
        forced_arc_inserted=bool(payload.get("forced_arc_inserted")),
    )
    output_packet = {
        "packet_type": "narrative.profile_response.v1",
        "packet_version": "narrative.profile_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "active-arc-selection-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built active-arc selection packet.",
        "refs": [],
        "data": {"forced_arc_code": value.get("forced_arc_code", ""), "forced_arc_inserted": value.get("forced_arc_inserted", False)},
    }]
