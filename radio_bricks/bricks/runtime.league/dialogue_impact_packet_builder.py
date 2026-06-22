from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.league.dialogue_impact_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🗣️",
    "deterministic": True,
    "inputs": ["runtime.league_request.v1"],
    "outputs": ["runtime.league_response.v1"],
    "requires": [],
    "provides": ["runtime.dialogue_impact_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "league", "dialogue", "ideology", "credibility"],
    "description": "Package a credibility-weighted dialogue ideology delta across competition, preservation, industrialization, research, and anomaly curiosity.",
}


def build_dialogue_impact_packet(
    competition: float,
    preservation: float,
    industrialization: float,
    research_priority: float,
    anomaly_curiosity: float,
    credibility_multiplier: float,
) -> dict[str, Any]:
    return {
        "competition": float(competition),
        "preservation": float(preservation),
        "industrialization": float(industrialization),
        "research_priority": float(research_priority),
        "anomaly_curiosity": float(anomaly_curiosity),
        "credibility_multiplier": float(credibility_multiplier),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_dialogue_impact_packet(
        competition=float(payload.get("competition") or 0.0),
        preservation=float(payload.get("preservation") or 0.0),
        industrialization=float(payload.get("industrialization") or 0.0),
        research_priority=float(payload.get("research_priority") or 0.0),
        anomaly_curiosity=float(payload.get("anomaly_curiosity") or 0.0),
        credibility_multiplier=float(payload.get("credibility_multiplier") or 1.0),
    )
    output_packet = {
        "packet_type": "runtime.league_response.v1",
        "packet_version": "runtime.league_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "dialogue-impact-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built dialogue-impact packet.",
        "refs": [],
        "data": {"credibility_multiplier": value.get("credibility_multiplier", 1.0)},
    }]
