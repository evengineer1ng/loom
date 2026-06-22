from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.organ_identity_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🫀",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.organ_identity_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "organ", "identity", "determinism", "seed"],
    "description": "Package an organ identity with determinism class, seed, and future-computability permission.",
}


def build_organ_identity_packet(
    name: str,
    determinism: str,
    seed: Any,
    can_compute_future: bool,
) -> dict[str, Any]:
    return {
        "name": str(name),
        "determinism": str(determinism),
        "seed": seed,
        "can_compute_future": bool(can_compute_future),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_organ_identity_packet(
        name=str(payload.get("name") or ""),
        determinism=str(payload.get("determinism") or ""),
        seed=payload.get("seed"),
        can_compute_future=bool(payload.get("can_compute_future")),
    )
    output_packet = {
        "packet_type": "runtime.binding_response.v1",
        "packet_version": "runtime.binding_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "organ-identity-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built organ identity packet.",
        "refs": [],
        "data": {
            "name": value.get("name", ""),
            "determinism": value.get("determinism", ""),
            "can_compute_future": value.get("can_compute_future", False),
        },
    }]
