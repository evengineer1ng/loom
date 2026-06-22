from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "registry.station.feed_toggle_reader",
    "kind": "reader",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["registry.station_request.v1"],
    "outputs": ["registry.station_response.v1"],
    "requires": [],
    "provides": ["registry.station_feed_toggles"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["registry", "station", "feeds"],
    "description": "Read enabled and disabled station feed toggles plus minimal per-feed runtime hints.",
}


def read_feed_toggles(feeds: dict[str, Any] | None) -> dict[str, Any]:
    rows = dict(feeds or {})
    enabled = []
    disabled = []
    details = {}
    for name, raw in rows.items():
        cfg = dict(raw or {}) if isinstance(raw, dict) else {}
        bucket = enabled if bool(cfg.get("enabled", False)) else disabled
        bucket.append(str(name))
        details[str(name)] = {
            "enabled": bool(cfg.get("enabled", False)),
            "plugin": cfg.get("plugin") or str(name),
            "poll_sec": cfg.get("poll_sec"),
            "priority": cfg.get("priority"),
        }
    return {"enabled": sorted(enabled), "disabled": sorted(disabled), "details": details}


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    value = read_feed_toggles(dict(input_packet.get("payload") or {}))
    output_packet = {
        "packet_type": "registry.station_response.v1",
        "packet_version": "registry.station_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "feed-toggle-reader",
        "brick_id": CONCEPT["id"],
        "kind": "read",
        "label": "Read feed toggles.",
        "refs": [],
        "data": {"enabled": len(value.get("enabled", [])), "disabled": len(value.get("disabled", []))},
    }]
