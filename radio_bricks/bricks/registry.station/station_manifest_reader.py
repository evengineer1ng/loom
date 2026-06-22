from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "registry.station.station_manifest_reader",
    "kind": "reader",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["registry.station_request.v1"],
    "outputs": ["registry.station_response.v1"],
    "requires": [],
    "provides": ["registry.station_manifest_summary"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["registry", "station", "manifest"],
    "description": "Read stable station manifest seams including station identity, meta plugin, model stack, path refs, and feed list.",
}


def read_station_manifest(manifest: dict[str, Any] | None) -> dict[str, Any]:
    data = dict(manifest or {})
    station = dict(data.get("station") or {})
    feeds = dict(data.get("feeds") or {})
    scheduler = dict(data.get("scheduler") or {})
    source_quotas = dict(scheduler.get("source_quotas") or {})
    return {
        "station_id": station.get("id") or station.get("name") or "",
        "station_name": station.get("name") or "",
        "host": station.get("host") or "",
        "category": station.get("category") or "",
        "meta_plugin": data.get("meta_plugin") or station.get("meta_plugin") or "",
        "llm_provider": dict(data.get("llm") or {}).get("provider") or "",
        "models": dict(data.get("models") or {}),
        "paths": dict(data.get("paths") or {}),
        "feed_names": sorted(feeds.keys()),
        "source_quotas": source_quotas,
        "mix_weights": dict(dict(data.get("mix") or {}).get("weights") or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    value = read_station_manifest(dict(input_packet.get("payload") or {}))
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
        "receipt_id": "station-manifest-reader",
        "brick_id": CONCEPT["id"],
        "kind": "read",
        "label": "Read station manifest summary.",
        "refs": [],
        "data": {"station_name": value.get("station_name", ""), "feeds": len(value.get("feed_names", []))},
    }]
