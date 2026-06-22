from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.decision.audio_fade_policy_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🎚️",
    "deterministic": True,
    "inputs": ["runtime.decision_request.v1"],
    "outputs": ["runtime.decision_response.v1"],
    "requires": [],
    "provides": ["runtime.audio_fade_policy_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "decision", "audio", "fade", "entry", "exit"],
    "description": "Package the fade policy that governs how a Loom soundtrack enters and exits a session.",
}


def build_audio_fade_policy_packet(
    entry_fade_sec: float,
    exit_fade_sec: float,
    restart_from_head: bool,
) -> dict[str, Any]:
    return {
        "entry_fade_sec": float(entry_fade_sec),
        "exit_fade_sec": float(exit_fade_sec),
        "restart_from_head": bool(restart_from_head),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_audio_fade_policy_packet(
        entry_fade_sec=float(payload.get("entry_fade_sec") or 0.0),
        exit_fade_sec=float(payload.get("exit_fade_sec") or 0.0),
        restart_from_head=bool(payload.get("restart_from_head", True)),
    )
    output_packet = {
        "packet_type": "runtime.decision_response.v1",
        "packet_version": "runtime.decision_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "audio-fade-policy-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built audio fade policy packet.",
        "refs": [],
        "data": {
            "entry_fade_sec": value.get("entry_fade_sec", 0.0),
            "exit_fade_sec": value.get("exit_fade_sec", 0.0),
        },
    }]
