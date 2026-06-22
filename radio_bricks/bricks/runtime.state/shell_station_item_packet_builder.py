from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.state.shell_station_item_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🪐",
    "deterministic": True,
    "inputs": ["runtime.state_request.v1"],
    "outputs": ["runtime.state_response.v1"],
    "requires": [],
    "provides": ["runtime.shell_station_item_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "state", "shell", "station", "oradio", "soulmate"],
    "description": "Package a shell station item with source kind, manifest payload, path, and soulmate linkage.",
}


def build_shell_station_item_packet(
    station_id: str,
    path: str,
    manifest: dict[str, Any] | None,
    source_kind: str,
    soulmate: str,
) -> dict[str, Any]:
    return {
        "station_id": str(station_id),
        "path": str(path),
        "manifest": dict(manifest or {}),
        "source_kind": str(source_kind),
        "soulmate": str(soulmate),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_shell_station_item_packet(
        station_id=str(payload.get("station_id") or ""),
        path=str(payload.get("path") or ""),
        manifest=dict(payload.get("manifest") or {}),
        source_kind=str(payload.get("source_kind") or ""),
        soulmate=str(payload.get("soulmate") or ""),
    )
    output_packet = {
        "packet_type": "runtime.state_response.v1",
        "packet_version": "runtime.state_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "shell-station-item-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built shell station-item packet.",
        "refs": [],
        "data": {
            "station_id": value.get("station_id", ""),
            "source_kind": value.get("source_kind", ""),
            "soulmate": value.get("soulmate", ""),
        },
    }]
