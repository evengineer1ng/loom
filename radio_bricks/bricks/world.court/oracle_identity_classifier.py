from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "world.court.oracle_identity_classifier",
    "kind": "evaluator",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["world.court_request.v1"],
    "outputs": ["world.court_response.v1"],
    "requires": [],
    "provides": ["world.oracle_identity_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["world", "court", "oracle", "identity"],
    "description": "Classify the emergent Oracle archetype from decree usage, silence, and volatility.",
}


def classify_oracle_identity(
    decree_count: int,
    silence_count: int,
    volatility: float,
    dominant_axis: str | None = None,
) -> dict[str, Any]:
    if decree_count <= 0:
        archetype = "UNKNOWN"
    elif silence_count > decree_count:
        archetype = "THE_SILENT"
    elif volatility > 0.75:
        archetype = "THE_ERRATIC"
    else:
        axis = str(dominant_axis or "").lower()
        if axis in {"war", "security", "military"}:
            archetype = "THE_HAWK"
        elif axis in {"trade", "treasury", "commerce"}:
            archetype = "THE_MERCHANT"
        elif axis in {"reform", "law", "institution"}:
            archetype = "THE_REFORMIST"
        elif axis in {"faith", "temple", "belief"}:
            archetype = "THE_PIOUS"
        elif axis in {"commons", "people", "populace"}:
            archetype = "THE_POPULIST"
        else:
            archetype = "UNKNOWN"
    return {
        "archetype": archetype,
        "decree_count": int(decree_count),
        "silence_count": int(silence_count),
        "volatility": float(volatility),
        "dominant_axis": str(dominant_axis or ""),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = classify_oracle_identity(
        decree_count=int(payload.get("decree_count") or 0),
        silence_count=int(payload.get("silence_count") or 0),
        volatility=float(payload.get("volatility") or 0.0),
        dominant_axis=payload.get("dominant_axis"),
    )
    output_packet = {
        "packet_type": "world.court_response.v1",
        "packet_version": "world.court_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "oracle-identity-packet",
        "brick_id": CONCEPT["id"],
        "kind": "evaluate",
        "label": "Classified oracle identity.",
        "refs": [],
        "data": {"archetype": value.get("archetype", "UNKNOWN")},
    }]
