from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.terminal.terminal_condition_snapshot_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🩻",
    "deterministic": True,
    "inputs": ["runtime.terminal_request.v1"],
    "outputs": ["runtime.terminal_response.v1"],
    "requires": [],
    "provides": ["runtime.terminal_condition_snapshot"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "terminal", "collapse", "snapshot", "conditions"],
    "description": "Build a collapse-condition snapshot packet capturing the variables a terminal-resolution engine evaluates and records.",
}


def build_terminal_condition_snapshot(
    health_composite: float,
    food_stores: float,
    labor_pool: float,
    resource_pressure: float,
    infrastructure: float,
    trade_volume: float,
    treasury: float,
    cohesion: float,
    hope_level: float,
    class_tension: float,
    fear_level: float,
    cultural_confidence: float,
    legitimacy: float,
    enforcement_capacity: float,
    institutional_strength: float,
    external_threat: float,
    corruption: float,
    public_faith: float,
    collapse_duration: int,
) -> dict[str, Any]:
    return {
        "health_composite": float(health_composite),
        "food_stores": float(food_stores),
        "labor_pool": float(labor_pool),
        "resource_pressure": float(resource_pressure),
        "infrastructure": float(infrastructure),
        "trade_volume": float(trade_volume),
        "treasury": float(treasury),
        "cohesion": float(cohesion),
        "hope_level": float(hope_level),
        "class_tension": float(class_tension),
        "fear_level": float(fear_level),
        "cultural_confidence": float(cultural_confidence),
        "legitimacy": float(legitimacy),
        "enforcement_capacity": float(enforcement_capacity),
        "institutional_strength": float(institutional_strength),
        "external_threat": float(external_threat),
        "corruption": float(corruption),
        "public_faith": float(public_faith),
        "collapse_duration": int(collapse_duration),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_terminal_condition_snapshot(
        health_composite=float(payload.get("health_composite") or 0.0),
        food_stores=float(payload.get("food_stores") or 0.0),
        labor_pool=float(payload.get("labor_pool") or 0.0),
        resource_pressure=float(payload.get("resource_pressure") or 0.0),
        infrastructure=float(payload.get("infrastructure") or 0.0),
        trade_volume=float(payload.get("trade_volume") or 0.0),
        treasury=float(payload.get("treasury") or 0.0),
        cohesion=float(payload.get("cohesion") or 0.0),
        hope_level=float(payload.get("hope_level") or 0.0),
        class_tension=float(payload.get("class_tension") or 0.0),
        fear_level=float(payload.get("fear_level") or 0.0),
        cultural_confidence=float(payload.get("cultural_confidence") or 0.0),
        legitimacy=float(payload.get("legitimacy") or 0.0),
        enforcement_capacity=float(payload.get("enforcement_capacity") or 0.0),
        institutional_strength=float(payload.get("institutional_strength") or 0.0),
        external_threat=float(payload.get("external_threat") or 0.0),
        corruption=float(payload.get("corruption") or 0.0),
        public_faith=float(payload.get("public_faith") or 0.0),
        collapse_duration=int(payload.get("collapse_duration") or 0),
    )
    output_packet = {
        "packet_type": "runtime.terminal_response.v1",
        "packet_version": "runtime.terminal_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "terminal-condition-snapshot",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built terminal-condition snapshot.",
        "refs": [],
        "data": {"health_composite": value.get("health_composite", 0.0), "collapse_duration": value.get("collapse_duration", 0)},
    }]
