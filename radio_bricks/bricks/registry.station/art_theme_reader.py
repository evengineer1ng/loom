from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "registry.station.art_theme_reader",
    "kind": "reader",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["registry.station_request.v1"],
    "outputs": ["registry.station_response.v1"],
    "requires": [],
    "provides": ["registry.station_art_theme"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["registry", "station", "art", "theme"],
    "description": "Read station art and panel theme seams including background mode, panel treatments, accent, and subtitle wave state.",
}


def read_art_theme(manifest: dict[str, Any] | None) -> dict[str, Any]:
    art = dict(dict(manifest or {}).get("art") or {})
    panels = dict(art.get("panels") or {})
    return {
        "global_bg": dict(art.get("global_bg") or {}),
        "panels": {name: dict(cfg or {}) for name, cfg in panels.items()},
        "accent": art.get("accent") or "",
        "subtitle_wave": bool(art.get("subtitle_wave", False)),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    value = read_art_theme(dict(input_packet.get("payload") or {}))
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
        "receipt_id": "art-theme-reader",
        "brick_id": CONCEPT["id"],
        "kind": "read",
        "label": "Read station art theme.",
        "refs": [],
        "data": {"panel_count": len(value.get("panels", {})), "subtitle_wave": value.get("subtitle_wave", False)},
    }]
