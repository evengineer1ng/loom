from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.decision.club_ask_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "❓",
    "deterministic": True,
    "inputs": ["runtime.decision_request.v1"],
    "outputs": ["runtime.decision_response.v1"],
    "requires": [],
    "provides": ["runtime.club_ask_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "decision", "club", "ask", "dependency", "prompt"],
    "description": "Package a Club ask for a dependency that is new, changed, or vanished on this machine.",
}


def build_club_ask_packet(
    capability: str,
    kind: str,
    reason: str,
    prompt: str,
) -> dict[str, Any]:
    return {
        "capability": str(capability),
        "kind": str(kind),
        "reason": str(reason),
        "prompt": str(prompt),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_club_ask_packet(
        capability=str(payload.get("capability") or ""),
        kind=str(payload.get("kind") or ""),
        reason=str(payload.get("reason") or ""),
        prompt=str(payload.get("prompt") or ""),
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
        "receipt_id": "club-ask-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built Club ask packet.",
        "refs": [],
        "data": {
            "capability": value.get("capability", ""),
            "reason": value.get("reason", ""),
        },
    }]
