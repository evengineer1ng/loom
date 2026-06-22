from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "registry.station.source_quota_reader",
    "kind": "reader",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["registry.station_request.v1"],
    "outputs": ["registry.station_response.v1"],
    "requires": [],
    "provides": ["registry.station_source_quotas"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["registry", "station", "quota"],
    "description": "Read station scheduler source quotas into a normalized allocation packet.",
}


def read_source_quotas(source_quotas: dict[str, Any] | None) -> dict[str, Any]:
    rows = {str(k): int(v) for k, v in dict(source_quotas or {}).items()}
    total = sum(rows.values())
    return {
        "quotas": rows,
        "total": total,
        "shares": {name: (value / total if total else 0.0) for name, value in rows.items()},
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    value = read_source_quotas(dict(input_packet.get("payload") or {}))
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
        "receipt_id": "source-quota-reader",
        "brick_id": CONCEPT["id"],
        "kind": "read",
        "label": "Read source quotas.",
        "refs": [],
        "data": {"sources": len(value.get("quotas", {})), "total": value.get("total", 0)},
    }]
