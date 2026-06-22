from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.inspect.coherence_diagnostic_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🪢",
    "deterministic": True,
    "inputs": ["runtime.inspect_request.v1"],
    "outputs": ["runtime.inspect_response.v1"],
    "requires": [],
    "provides": ["runtime.coherence_diagnostic_packet"],
    "side_effects": [],
    "ui_slots": ["inspection.coherence"],
    "tags": ["runtime", "inspect", "coherence", "tensions", "diagnostic"],
    "description": "Package material-state coherence diagnostics, justification score, and cross-domain tension summaries.",
}


def build_coherence_diagnostic_packet(
    material_state: str,
    justification_score: float,
    tensions: dict[str, float] | None,
    health_composite: float,
) -> dict[str, Any]:
    return {
        "material_state": material_state,
        "justification_score": float(justification_score),
        "tensions": {str(key): float(value) for key, value in (tensions or {}).items()},
        "health_composite": float(health_composite),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_coherence_diagnostic_packet(
        material_state=str(payload.get("material_state") or ""),
        justification_score=float(payload.get("justification_score") or 0.0),
        tensions=dict(payload.get("tensions") or {}),
        health_composite=float(payload.get("health_composite") or 0.0),
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
        "receipt_id": "coherence-diagnostic-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built coherence diagnostic packet.",
        "refs": [],
        "data": {"material_state": value.get("material_state", "")},
    }]
