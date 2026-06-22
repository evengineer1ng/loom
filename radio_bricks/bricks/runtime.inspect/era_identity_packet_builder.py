from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.inspect.era_identity_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "👑",
    "deterministic": True,
    "inputs": ["runtime.inspect_request.v1"],
    "outputs": ["runtime.inspect_response.v1"],
    "requires": [],
    "provides": ["runtime.era_identity_packet"],
    "side_effects": [],
    "ui_slots": ["inspection.era"],
    "tags": ["runtime", "inspect", "era", "history", "read_model"],
    "description": "Package the current era, active modifiers, and era history into a portable inspection packet.",
}


def build_era_identity_packet(
    current_era: str,
    modifiers: dict[str, float] | None,
    era_history: list[dict[str, Any]] | None,
    total_baseline_shifts: int | None = None,
    total_scars: int | None = None,
) -> dict[str, Any]:
    return {
        "current_era": current_era,
        "modifiers": {str(key): float(value) for key, value in (modifiers or {}).items()},
        "era_history": list(era_history or []),
        "total_baseline_shifts": None if total_baseline_shifts is None else int(total_baseline_shifts),
        "total_scars": None if total_scars is None else int(total_scars),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_era_identity_packet(
        current_era=str(payload.get("current_era") or ""),
        modifiers=dict(payload.get("modifiers") or {}),
        era_history=list(payload.get("era_history") or []),
        total_baseline_shifts=payload.get("total_baseline_shifts"),
        total_scars=payload.get("total_scars"),
    )
    output_packet = {
        "packet_type": "runtime.inspect_response.v1",
        "packet_version": "runtime.inspect_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "era-identity-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built era-identity inspection packet.",
        "refs": [],
        "data": {"current_era": value.get("current_era", "")},
    }]
