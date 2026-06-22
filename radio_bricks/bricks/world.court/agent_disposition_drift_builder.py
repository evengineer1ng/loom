from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "world.court.agent_disposition_drift_builder",
    "kind": "builder",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["world.court_request.v1"],
    "outputs": ["world.court_response.v1"],
    "requires": [],
    "provides": ["world.agent_disposition_drift_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["world", "court", "agent", "disposition"],
    "description": "Package court-agent disposition drift under awake or sleeping conditions.",
}


def build_agent_disposition_drift_packet(
    sleeping: bool,
    trust: float,
    admiration: float,
    fear: float,
    resentment: float,
    consecutive_silence_ticks: int,
    petitions_ignored: int,
    times_rewarded: int,
) -> dict[str, Any]:
    updates: dict[str, float] = {}
    if sleeping:
        updates["resentment_delta"] = -0.005
        updates["trust_bias_toward_neutral"] = 50.0
    else:
        if petitions_ignored > times_rewarded:
            updates["resentment_delta"] = 0.01
        if consecutive_silence_ticks > 10:
            pressure = consecutive_silence_ticks * 0.002
            if trust < 40:
                updates["resentment_delta"] = updates.get("resentment_delta", 0.0) + pressure
                updates["decisiveness_delta"] = -pressure * 2
            else:
                updates["admiration_delta"] = -pressure * 0.5
    return {
        "sleeping": bool(sleeping),
        "current": {"trust": float(trust), "admiration": float(admiration), "fear": float(fear), "resentment": float(resentment)},
        "updates": updates,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_agent_disposition_drift_packet(
        sleeping=bool(payload.get("sleeping", False)),
        trust=float(payload.get("trust") or 0.0),
        admiration=float(payload.get("admiration") or 0.0),
        fear=float(payload.get("fear") or 0.0),
        resentment=float(payload.get("resentment") or 0.0),
        consecutive_silence_ticks=int(payload.get("consecutive_silence_ticks") or 0),
        petitions_ignored=int(payload.get("petitions_ignored") or 0),
        times_rewarded=int(payload.get("times_rewarded") or 0),
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
        "receipt_id": "agent-disposition-drift-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built agent disposition drift packet.",
        "refs": [],
        "data": {"sleeping": value.get("sleeping", False)},
    }]
