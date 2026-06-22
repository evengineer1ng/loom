from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.arbitration_policy_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧭",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.arbitration_policy_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "arbitration", "policy", "recognition"],
    "description": "Package runtime arbitration policy with thresholds, ambiguity/null margins, confirmation dwell, cooldown, and release-below-threshold timing.",
}


def build_arbitration_policy_packet(
    threshold: float,
    ambiguity_margin: float,
    null_margin: float,
    confirmation_seconds: float,
    cooldown_seconds: float,
    release_below_threshold_seconds: float,
) -> dict[str, Any]:
    return {
        "threshold": float(threshold),
        "ambiguity_margin": float(ambiguity_margin),
        "null_margin": float(null_margin),
        "confirmation_seconds": float(confirmation_seconds),
        "cooldown_seconds": float(cooldown_seconds),
        "release_below_threshold_seconds": float(release_below_threshold_seconds),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_arbitration_policy_packet(
        threshold=float(payload.get("threshold") or 0.0),
        ambiguity_margin=float(payload.get("ambiguity_margin") or 0.0),
        null_margin=float(payload.get("null_margin") or 0.0),
        confirmation_seconds=float(payload.get("confirmation_seconds") or 0.0),
        cooldown_seconds=float(payload.get("cooldown_seconds") or 0.0),
        release_below_threshold_seconds=float(payload.get("release_below_threshold_seconds") or 0.0),
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
        "receipt_id": "arbitration-policy-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built arbitration-policy packet.",
        "refs": [],
        "data": {
            "threshold": value.get("threshold", 0.0),
            "ambiguity_margin": value.get("ambiguity_margin", 0.0),
            "cooldown_seconds": value.get("cooldown_seconds", 0.0),
        },
    }]
