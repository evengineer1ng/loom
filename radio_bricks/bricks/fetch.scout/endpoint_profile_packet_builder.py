from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "fetch.scout.endpoint_profile_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🛰️",
    "deterministic": True,
    "inputs": ["fetch.scout_request.v1"],
    "outputs": ["fetch.scout_response.v1"],
    "requires": [],
    "provides": ["fetch.endpoint_profile_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["fetch", "scout", "endpoint", "profile", "json"],
    "description": "Package one HTTP-JSON endpoint profile with fetch status, chosen item path, item count, discovered fields, and derived bucket map.",
}


def build_endpoint_profile_packet(
    base_url: str,
    path: str,
    source: str,
    ok: bool,
    item_path: str,
    item_count: int,
    fields: dict[str, Any] | None,
    field_map: dict[str, Any] | None,
    reason: str,
) -> dict[str, Any]:
    return {
        "base_url": str(base_url),
        "path": str(path),
        "source": str(source),
        "ok": bool(ok),
        "item_path": str(item_path),
        "item_count": int(item_count),
        "fields": dict(fields or {}),
        "field_map": dict(field_map or {}),
        "reason": str(reason),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_endpoint_profile_packet(
        base_url=str(payload.get("base_url") or ""),
        path=str(payload.get("path") or ""),
        source=str(payload.get("source") or ""),
        ok=bool(payload.get("ok")),
        item_path=str(payload.get("item_path") or ""),
        item_count=int(payload.get("item_count") or 0),
        fields=dict(payload.get("fields") or {}),
        field_map=dict(payload.get("field_map") or {}),
        reason=str(payload.get("reason") or ""),
    )
    output_packet = {
        "packet_type": "fetch.scout_response.v1",
        "packet_version": "fetch.scout_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "endpoint-profile-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built endpoint-profile packet.",
        "refs": [],
        "data": {
            "source": value.get("source", ""),
            "ok": value.get("ok", False),
            "item_count": value.get("item_count", 0),
        },
    }]
