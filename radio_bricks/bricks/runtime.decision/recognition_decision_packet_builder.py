from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.decision.recognition_decision_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🎯",
    "deterministic": True,
    "inputs": ["runtime.decision_request.v1"],
    "outputs": ["runtime.decision_response.v1"],
    "requires": [],
    "provides": ["runtime.recognition_decision_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "decision", "recognition", "gesture", "commit"],
    "description": "Package an explicit recognition runtime decision with decision kind, commit/hold/release labels, variants, and matched gestures.",
}


def build_recognition_decision_packet(
    kind: str,
    commit_label: str,
    commit_variant: str,
    hold_label: str,
    hold_variant: str,
    release_label: str,
    gesture_matches: list[str] | None,
) -> dict[str, Any]:
    return {
        "kind": str(kind),
        "commit_label": str(commit_label),
        "commit_variant": str(commit_variant),
        "hold_label": str(hold_label),
        "hold_variant": str(hold_variant),
        "release_label": str(release_label),
        "gesture_matches": [str(item) for item in (gesture_matches or [])],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_recognition_decision_packet(
        kind=str(payload.get("kind") or ""),
        commit_label=str(payload.get("commit_label") or ""),
        commit_variant=str(payload.get("commit_variant") or ""),
        hold_label=str(payload.get("hold_label") or ""),
        hold_variant=str(payload.get("hold_variant") or ""),
        release_label=str(payload.get("release_label") or ""),
        gesture_matches=list(payload.get("gesture_matches") or []),
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
        "receipt_id": "recognition-decision-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built recognition-decision packet.",
        "refs": [],
        "data": {
            "kind": value.get("kind", ""),
            "commit_label": value.get("commit_label", ""),
            "hold_label": value.get("hold_label", ""),
        },
    }]
