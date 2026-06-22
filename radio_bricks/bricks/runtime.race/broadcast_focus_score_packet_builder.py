from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.race.broadcast_focus_score_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🎥",
    "deterministic": True,
    "inputs": ["runtime.race_request.v1"],
    "outputs": ["runtime.race_response.v1"],
    "requires": [],
    "provides": ["runtime.broadcast_focus_score_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "race", "broadcast", "focus", "score"],
    "description": "Package broadcast director scoring over drivers with leader bonus, battle bonus, incident decay, lock focus, and selected camera target.",
}


def build_broadcast_focus_score_packet(
    mode: str,
    locked_car: int | None,
    battles: list[dict[str, Any]] | None,
    scored_drivers: list[dict[str, Any]] | None,
    selected_car: int | None,
    camera_group: int,
) -> dict[str, Any]:
    return {
        "mode": str(mode),
        "locked_car": None if locked_car is None else int(locked_car),
        "battles": [dict(item) for item in (battles or [])],
        "scored_drivers": [dict(item) for item in (scored_drivers or [])],
        "selected_car": None if selected_car is None else int(selected_car),
        "camera_group": int(camera_group),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_broadcast_focus_score_packet(
        mode=str(payload.get("mode") or ""),
        locked_car=payload.get("locked_car"),
        battles=list(payload.get("battles") or []),
        scored_drivers=list(payload.get("scored_drivers") or []),
        selected_car=payload.get("selected_car"),
        camera_group=int(payload.get("camera_group") or 0),
    )
    output_packet = {
        "packet_type": "runtime.race_response.v1",
        "packet_version": "runtime.race_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "broadcast-focus-score-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built broadcast-focus score packet.",
        "refs": [],
        "data": {
            "mode": value.get("mode", ""),
            "selected_car": value.get("selected_car", None),
            "driver_count": len(value.get("scored_drivers", [])),
        },
    }]
