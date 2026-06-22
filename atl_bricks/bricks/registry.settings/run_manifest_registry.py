from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "registry.settings.run_manifest_registry",
    "kind": "bridge",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["registry.settings_request.v1"],
    "outputs": ["registry.settings_response.v1"],
    "requires": [],
    "provides": ["registry.run_manifest_upsert", "registry.run_manifest_get"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["registry", "manifest", "runs"],
    "description": "Store and update run-cell results keyed by a stable composite manifest key.",
}


def manifest_key(strategy: str, universe: str, variant: str) -> str:
    return f"{strategy}|{universe}|{variant}"


def upsert_manifest_entry(manifest: dict[str, Any] | None, strategy: str, universe: str, variant: str, result: dict[str, Any]) -> dict[str, Any]:
    updated = dict(manifest or {})
    updated[manifest_key(strategy, universe, variant)] = dict(result)
    return updated


def get_manifest_entry(manifest: dict[str, Any] | None, strategy: str, universe: str, variant: str) -> dict[str, Any] | None:
    value = dict(manifest or {}).get(manifest_key(strategy, universe, variant))
    return dict(value) if isinstance(value, dict) else None


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    action = str(payload.get("action") or "get").strip().lower()
    manifest = dict(payload.get("manifest") or {})
    strategy = str(payload.get("strategy") or "")
    universe = str(payload.get("universe") or "")
    variant = str(payload.get("variant") or "")
    if action == "upsert":
        value = {
            "manifest": upsert_manifest_entry(manifest, strategy, universe, variant, dict(payload.get("result") or {})),
            "key": manifest_key(strategy, universe, variant),
        }
    else:
        value = {
            "entry": get_manifest_entry(manifest, strategy, universe, variant),
            "key": manifest_key(strategy, universe, variant),
        }
    output_packet = {
        "packet_type": "registry.settings_response.v1",
        "packet_version": "registry.settings_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(action, output_packet), "issues": [], "meta": {}}


def receipts(action: str, output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    payload = output_packet.get("payload") or {}
    return [{
        "receipt_id": f"run-manifest-{action}",
        "brick_id": CONCEPT["id"],
        "kind": "state",
        "label": f"Run manifest action: {action}.",
        "refs": [],
        "data": {"key": payload.get("key", "")},
    }]
