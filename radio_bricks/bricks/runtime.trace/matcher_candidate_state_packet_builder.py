from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.trace.matcher_candidate_state_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧭",
    "deterministic": True,
    "inputs": ["runtime.trace_request.v1"],
    "outputs": ["runtime.trace_response.v1"],
    "requires": [],
    "provides": ["runtime.matcher_candidate_state_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "trace", "matcher", "candidate", "phase"],
    "description": "Package matcher candidate state with label index, phase, dwell, peak confidence, and remaining cooldown.",
}


def build_matcher_candidate_state_packet(
    label_index: int,
    phase: str,
    dwell: int,
    peak_confidence: float,
    cooldown_frames_remaining: int,
) -> dict[str, Any]:
    return {
        "label_index": int(label_index),
        "phase": str(phase),
        "dwell": int(dwell),
        "peak_confidence": float(peak_confidence),
        "cooldown_frames_remaining": int(cooldown_frames_remaining),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_matcher_candidate_state_packet(
        label_index=int(payload.get("label_index") or 0),
        phase=str(payload.get("phase") or ""),
        dwell=int(payload.get("dwell") or 0),
        peak_confidence=float(payload.get("peak_confidence") or 0.0),
        cooldown_frames_remaining=int(payload.get("cooldown_frames_remaining") or 0),
    )
    output_packet = {
        "packet_type": "runtime.trace_response.v1",
        "packet_version": "runtime.trace_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "matcher-candidate-state-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built matcher candidate-state packet.",
        "refs": [],
        "data": {
            "label_index": value.get("label_index", 0),
            "phase": value.get("phase", ""),
            "dwell": value.get("dwell", 0),
        },
    }]
