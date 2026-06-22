from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "config.assembly.pairlist_manifest_reader",
    "kind": "bridge",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["config.request.v1"],
    "outputs": ["config.response.v1"],
    "requires": [],
    "provides": ["config.pairlist_manifest_base_url", "config.get_pairlist_manifest"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["config", "manifest", "pairlist"],
    "description": "Read pairlist manifest settings and look up cached manifest payloads by deterministic key.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def pairlist_manifest_base_url(settings: dict[str, Any] | None = None) -> str:
    settings = settings or {}
    return str(settings.get("pairlist_manifest_base_url") or "http://host.docker.internal:8000").rstrip("/")


def get_pairlist_manifest(name: str, generated_json: dict[str, Any] | None = None) -> dict[str, Any] | None:
    generated_json = generated_json or {}
    payload = generated_json.get(f"pairlist_manifest:{name}")
    return payload if isinstance(payload, dict) else None


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = input_packet.get("payload", {})
    name = str(payload.get("name") or "")
    settings = payload.get("settings") if isinstance(payload.get("settings"), dict) else {}
    generated_json = payload.get("generated_json") if isinstance(payload.get("generated_json"), dict) else {}
    output_packet = {
        "packet_type": "config.response.v1",
        "packet_version": "config.response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {
            "base_url": pairlist_manifest_base_url(settings),
            "manifest": get_pairlist_manifest(name, generated_json) if name else None,
        },
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "pairlist-manifest-read",
        "brick_id": CONCEPT["id"],
        "kind": "config_read",
        "label": "Read pairlist manifest settings and cache lookup.",
        "refs": [],
        "data": {"has_manifest": bool(output_packet["payload"]["manifest"])},
    }]
