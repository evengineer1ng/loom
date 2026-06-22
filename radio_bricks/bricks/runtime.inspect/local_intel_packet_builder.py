from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.inspect.local_intel_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🔎",
    "deterministic": True,
    "inputs": ["runtime.inspect_request.v1"],
    "outputs": ["runtime.inspect_response.v1"],
    "requires": [],
    "provides": ["runtime.local_intel_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "inspect", "local", "intel", "planning"],
    "description": "Package current-node planning intel with biome summary, encounter availability, neighbor gates, and narrator-facing summary text.",
}


def build_local_intel_packet(
    node_id: str,
    node_name: str,
    node_type: str,
    region: str,
    is_relay_node: bool,
    is_start: bool,
    biome: dict[str, float] | None,
    neighbors: list[str] | None,
    can_encounter: bool,
    encounter_table: dict[str, Any] | None,
    neighbor_gates: list[dict[str, Any]] | None,
    summary: str,
    tick: int,
) -> dict[str, Any]:
    return {
        "node_id": node_id,
        "node_name": node_name,
        "node_type": node_type,
        "region": region,
        "is_relay_node": bool(is_relay_node),
        "is_start": bool(is_start),
        "biome": {str(key): float(value) for key, value in (biome or {}).items()},
        "neighbors": list(neighbors or []),
        "can_encounter": bool(can_encounter),
        "encounter_table": dict(encounter_table or {}) if encounter_table is not None else None,
        "neighbor_gates": [dict(item) for item in (neighbor_gates or [])],
        "summary": summary,
        "tick": int(tick),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_local_intel_packet(
        node_id=str(payload.get("node_id") or ""),
        node_name=str(payload.get("node_name") or ""),
        node_type=str(payload.get("node_type") or ""),
        region=str(payload.get("region") or ""),
        is_relay_node=bool(payload.get("is_relay_node")),
        is_start=bool(payload.get("is_start")),
        biome=dict(payload.get("biome") or {}),
        neighbors=list(payload.get("neighbors") or []),
        can_encounter=bool(payload.get("can_encounter")),
        encounter_table=payload.get("encounter_table"),
        neighbor_gates=list(payload.get("neighbor_gates") or []),
        summary=str(payload.get("summary") or ""),
        tick=int(payload.get("tick") or 0),
    )
    output_packet = {
        "packet_type": "runtime.inspect_response.v1",
        "packet_version": "runtime.inspect_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "local-intel-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built local-intel packet.",
        "refs": [],
        "data": {"node_id": value.get("node_id", ""), "neighbor_gate_count": len(value.get("neighbor_gates", []))},
    }]
