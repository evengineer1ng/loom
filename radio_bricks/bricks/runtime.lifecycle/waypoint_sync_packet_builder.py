from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.lifecycle.waypoint_sync_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧭",
    "deterministic": True,
    "inputs": ["runtime.lifecycle_request.v1"],
    "outputs": ["runtime.lifecycle_response.v1"],
    "requires": [],
    "provides": ["runtime.waypoint_sync_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "lifecycle", "waypoint", "sync", "route"],
    "description": "Package waypoint-sync lifecycle with route signature change detection, waypoint output writing, and optional assist push to EDAP.",
}


def build_waypoint_sync_packet(
    route_signature: str,
    prior_route_signature: str,
    waypoint_output: str,
    auto_sync: bool,
    pushed_to_edap: bool,
    start_assist: bool,
) -> dict[str, Any]:
    return {
        "route_signature": str(route_signature),
        "prior_route_signature": str(prior_route_signature),
        "waypoint_output": str(waypoint_output),
        "auto_sync": bool(auto_sync),
        "pushed_to_edap": bool(pushed_to_edap),
        "start_assist": bool(start_assist),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_waypoint_sync_packet(
        route_signature=str(payload.get("route_signature") or ""),
        prior_route_signature=str(payload.get("prior_route_signature") or ""),
        waypoint_output=str(payload.get("waypoint_output") or ""),
        auto_sync=bool(payload.get("auto_sync")),
        pushed_to_edap=bool(payload.get("pushed_to_edap")),
        start_assist=bool(payload.get("start_assist")),
    )
    output_packet = {
        "packet_type": "runtime.lifecycle_response.v1",
        "packet_version": "runtime.lifecycle_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "waypoint-sync-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built waypoint-sync packet.",
        "refs": [],
        "data": {
            "route_signature": value.get("route_signature", ""),
            "pushed_to_edap": value.get("pushed_to_edap", False),
            "start_assist": value.get("start_assist", False),
        },
    }]
