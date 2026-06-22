from __future__ import annotations

import hashlib
from typing import Any


RIBBON_CATS = (
    "camera_tools", "connectivity", "dash_editor", "dashes", "devices",
    "diagnostics", "drive", "extras", "head_tracking", "help", "hid_fusion",
    "input_mapper", "moonlight", "pi_desktop", "profiles", "ribbon_studio",
    "rpm_lights", "settings", "simulation_tools", "system_tools", "telemetry",
)


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.ribbon_skin_assignment_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🎞️",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.ribbon_skin_assignment_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "ribbon", "skin", "category", "deterministic"],
    "description": "Assign a deterministic ribbon skin by manifest category when valid, else by hashed station id.",
}


def build_ribbon_skin_assignment_packet(
    station_id: str,
    manifest: dict[str, Any] | None,
) -> dict[str, Any]:
    manifest_data = dict(manifest or {})
    station_block = manifest_data.get("station") if isinstance(manifest_data.get("station"), dict) else {}
    raw = str(station_block.get("ribbon") or station_block.get("category") or "").strip().lower().replace(" ", "_")
    if raw in RIBBON_CATS:
        category = raw
        assignment_mode = "manifest_category"
    else:
        digest = hashlib.md5(str(station_id).encode("utf-8")).hexdigest()
        category = RIBBON_CATS[int(digest, 16) % len(RIBBON_CATS)]
        assignment_mode = "station_hash"
    return {
        "station_id": str(station_id),
        "category": category,
        "assignment_mode": assignment_mode,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_ribbon_skin_assignment_packet(
        station_id=str(payload.get("station_id") or ""),
        manifest=dict(payload.get("manifest") or {}),
    )
    output_packet = {
        "packet_type": "runtime.binding_response.v1",
        "packet_version": "runtime.binding_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "ribbon-skin-assignment-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built ribbon skin-assignment packet.",
        "refs": [],
        "data": {
            "category": value.get("category", ""),
            "assignment_mode": value.get("assignment_mode", ""),
        },
    }]
