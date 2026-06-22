from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "registry.station.ui_layout_reader",
    "kind": "reader",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["registry.station_request.v1"],
    "outputs": ["registry.station_response.v1"],
    "requires": [],
    "provides": ["registry.station_ui_layout"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["registry", "station", "ui", "layout"],
    "description": "Read station UI layout seams including windows, panes, widget tabs, and minimized state.",
}


def read_ui_layout(manifest: dict[str, Any] | None) -> dict[str, Any]:
    layout = dict(dict(manifest or {}).get("ui_layout") or {})
    windows = dict(layout.get("windows") or {})
    panes = dict(layout.get("panes") or {})
    return {
        "windows": {name: dict(cfg or {}) for name, cfg in windows.items()},
        "panes": {name: dict(cfg or {}) for name, cfg in panes.items()},
        "window_count": len(windows),
        "pane_count": len(panes),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    value = read_ui_layout(dict(input_packet.get("payload") or {}))
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
        "receipt_id": "ui-layout-reader",
        "brick_id": CONCEPT["id"],
        "kind": "read",
        "label": "Read UI layout.",
        "refs": [],
        "data": {"window_count": value.get("window_count", 0), "pane_count": value.get("pane_count", 0)},
    }]
