from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "world.coherence.coherence_correction_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["world.coherence_request.v1"],
    "outputs": ["world.coherence_response.v1"],
    "requires": [],
    "provides": ["world.coherence_correction_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["world", "coherence", "correction", "packet"],
    "description": "Package a single cross-domain coherence correction with reason, delta, and material-state context.",
}


def build_coherence_correction_packet(layer_name: str, variable: str, delta: float, reason: str, material_state: str, kingdom_id: str, tick: int) -> dict[str, Any]:
    return {
        "source_type": "coherence",
        "source_id": reason,
        "target_type": "layer",
        "target_id": kingdom_id,
        "variable": variable,
        "delta": float(delta),
        "tick": int(tick),
        "metadata": {"material_state": material_state, "reason": reason, "layer_name": layer_name},
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_coherence_correction_packet(
        layer_name=str(payload.get("layer_name") or ""),
        variable=str(payload.get("variable") or ""),
        delta=float(payload.get("delta") or 0.0),
        reason=str(payload.get("reason") or ""),
        material_state=str(payload.get("material_state") or ""),
        kingdom_id=str(payload.get("kingdom_id") or ""),
        tick=int(payload.get("tick") or 0),
    )
    output_packet = {
        "packet_type": "world.coherence_response.v1",
        "packet_version": "world.coherence_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "coherence-correction-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built coherence correction packet.",
        "refs": [],
        "data": {"variable": value.get("variable", ""), "reason": value.get("source_id", "")},
    }]
