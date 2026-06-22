from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.save.trajectory_restore_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧭",
    "deterministic": True,
    "inputs": ["runtime.save_request.v1"],
    "outputs": ["runtime.save_response.v1"],
    "requires": [],
    "provides": ["runtime.trajectory_restore_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "save", "trajectory", "restore", "ideology"],
    "description": "Package the restored player trajectory snapshot including behavioral counters and ideology vector.",
}


def build_trajectory_restore_packet(
    competitive_focus: float,
    exploration_depth: float,
    research_investment: float,
    breeding_intensity: float,
    anomaly_exposure: float,
    risk_appetite: float,
    battles_won: int,
    battles_lost: int,
    nodes_explored: int,
    species_discovered: int,
    breeds_completed: int,
    relics_found: int,
    anomaly_events: int,
    creatures_captured: int,
    ideology: dict[str, float] | None,
) -> dict[str, Any]:
    return {
        "competitive_focus": float(competitive_focus),
        "exploration_depth": float(exploration_depth),
        "research_investment": float(research_investment),
        "breeding_intensity": float(breeding_intensity),
        "anomaly_exposure": float(anomaly_exposure),
        "risk_appetite": float(risk_appetite),
        "battles_won": int(battles_won),
        "battles_lost": int(battles_lost),
        "nodes_explored": int(nodes_explored),
        "species_discovered": int(species_discovered),
        "breeds_completed": int(breeds_completed),
        "relics_found": int(relics_found),
        "anomaly_events": int(anomaly_events),
        "creatures_captured": int(creatures_captured),
        "ideology": {str(key): float(value) for key, value in (ideology or {}).items()},
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_trajectory_restore_packet(
        competitive_focus=float(payload.get("competitive_focus") or 0.0),
        exploration_depth=float(payload.get("exploration_depth") or 0.0),
        research_investment=float(payload.get("research_investment") or 0.0),
        breeding_intensity=float(payload.get("breeding_intensity") or 0.0),
        anomaly_exposure=float(payload.get("anomaly_exposure") or 0.0),
        risk_appetite=float(payload.get("risk_appetite") or 0.0),
        battles_won=int(payload.get("battles_won") or 0),
        battles_lost=int(payload.get("battles_lost") or 0),
        nodes_explored=int(payload.get("nodes_explored") or 0),
        species_discovered=int(payload.get("species_discovered") or 0),
        breeds_completed=int(payload.get("breeds_completed") or 0),
        relics_found=int(payload.get("relics_found") or 0),
        anomaly_events=int(payload.get("anomaly_events") or 0),
        creatures_captured=int(payload.get("creatures_captured") or 0),
        ideology=dict(payload.get("ideology") or {}),
    )
    output_packet = {
        "packet_type": "runtime.save_response.v1",
        "packet_version": "runtime.save_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "trajectory-restore-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built trajectory-restore packet.",
        "refs": [],
        "data": {"nodes_explored": value.get("nodes_explored", 0), "anomaly_events": value.get("anomaly_events", 0)},
    }]
