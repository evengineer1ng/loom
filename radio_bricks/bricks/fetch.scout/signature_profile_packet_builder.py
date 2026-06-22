from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "fetch.scout.signature_profile_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧾",
    "deterministic": True,
    "inputs": ["fetch.scout_request.v1"],
    "outputs": ["fetch.scout_response.v1"],
    "requires": [],
    "provides": ["fetch.signature_profile_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["fetch", "scout", "signature", "profile", "endpoint"],
    "description": "Package the full antenna signature profile across profiled endpoints, per-source profiles, and signature write intent.",
}


def build_signature_profile_packet(
    base_url: str,
    profiled_at: float,
    endpoints: dict[str, Any] | None,
    write_signature: bool,
) -> dict[str, Any]:
    return {
        "base_url": str(base_url),
        "profiled_at": float(profiled_at),
        "endpoints": dict(endpoints or {}),
        "write_signature": bool(write_signature),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_signature_profile_packet(
        base_url=str(payload.get("base_url") or ""),
        profiled_at=float(payload.get("profiled_at") or 0.0),
        endpoints=dict(payload.get("endpoints") or {}),
        write_signature=bool(payload.get("write_signature")),
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
        "receipt_id": "signature-profile-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built signature-profile packet.",
        "refs": [],
        "data": {
            "base_url": value.get("base_url", ""),
            "endpoint_count": len(value.get("endpoints", {})),
            "write_signature": value.get("write_signature", False),
        },
    }]
