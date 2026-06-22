from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "config.assembly.manifest_namer",
    "kind": "bridge",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["config.request.v1"],
    "outputs": ["config.response.v1"],
    "requires": [],
    "provides": ["config.manifest_name"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["config", "manifest", "naming"],
    "description": "Build a deterministic manifest name from universe, exchange, market type, and quote currency.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    payload = input_packet.get("payload", {})
    missing = [field for field in ("universe", "exchange_id", "market_type", "quote") if not payload.get(field)]
    if missing:
        return [{"code": "missing_fields", "message": f"Missing payload fields: {', '.join(missing)}"}]
    return []


def manifest_name(universe: str, exchange_id: str, market_type: str, quote: str) -> str:
    return f"{universe}_{exchange_id}_{market_type}_{quote.lower()}"


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    payload = input_packet["payload"]
    value = manifest_name(str(payload["universe"]), str(payload["exchange_id"]), str(payload["market_type"]), str(payload["quote"]))
    output_packet = {
        "packet_type": "config.response.v1",
        "packet_version": "config.response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"manifest_name": value},
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "manifest-name-built",
        "brick_id": CONCEPT["id"],
        "kind": "config_build",
        "label": "Built deterministic manifest name.",
        "refs": [],
        "data": output_packet["payload"],
    }]
