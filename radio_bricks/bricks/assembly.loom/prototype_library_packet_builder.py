from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "assembly.loom.prototype_library_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧬",
    "deterministic": True,
    "inputs": ["assembly.loom_request.v1"],
    "outputs": ["assembly.loom_response.v1"],
    "requires": [],
    "provides": ["assembly.prototype_library_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["assembly", "loom", "prototype", "library", "latent"],
    "description": "Package a phase-anchored prototype library entry with label, per-phase thresholds, within-take similarity, and take count.",
}


def build_prototype_library_packet(
    label: str,
    thresholds: list[float] | None,
    within_sim: float,
    n_takes: int,
) -> dict[str, Any]:
    return {
        "label": str(label),
        "thresholds": [float(item) for item in (thresholds or [])],
        "within_sim": float(within_sim),
        "n_takes": int(n_takes),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_prototype_library_packet(
        label=str(payload.get("label") or ""),
        thresholds=list(payload.get("thresholds") or []),
        within_sim=float(payload.get("within_sim") or 0.0),
        n_takes=int(payload.get("n_takes") or 0),
    )
    output_packet = {
        "packet_type": "assembly.loom_response.v1",
        "packet_version": "assembly.loom_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "prototype-library-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built prototype-library packet.",
        "refs": [],
        "data": {
            "label": value.get("label", ""),
            "n_takes": value.get("n_takes", 0),
            "within_sim": value.get("within_sim", 0.0),
        },
    }]
