from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "history.structure.institutional_scar_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["history.structure_request.v1"],
    "outputs": ["history.structure_response.v1"],
    "requires": [],
    "provides": ["history.institutional_scar_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["history", "structure", "scar", "institutional"],
    "description": "Package a permanent institutional scar left by a resolved crisis event.",
}


def build_institutional_scar_packet(
    tick: int,
    event_id: str,
    event_kind: str,
    event_description: str,
    variable: str,
    delta: float,
    description: str,
    adaptive: bool = False,
) -> dict[str, Any]:
    prefix = "scar_adapt" if adaptive else "scar"
    return {
        "scar_id": f"{prefix}_{int(tick)}_{event_id[:12]}_{variable}",
        "source_event_id": event_id,
        "source_event_kind": f"{event_kind}_ADAPTIVE" if adaptive else event_kind,
        "source_event_description": event_description[:100],
        "tick_formed": int(tick),
        "variable": variable,
        "delta": round(float(delta), 3),
        "description": description,
        "adaptive": bool(adaptive),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_institutional_scar_packet(
        tick=int(payload.get("tick") or 0),
        event_id=str(payload.get("event_id") or ""),
        event_kind=str(payload.get("event_kind") or ""),
        event_description=str(payload.get("event_description") or ""),
        variable=str(payload.get("variable") or ""),
        delta=float(payload.get("delta") or 0.0),
        description=str(payload.get("description") or ""),
        adaptive=bool(payload.get("adaptive", False)),
    )
    output_packet = {
        "packet_type": "history.structure_response.v1",
        "packet_version": "history.structure_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "institutional-scar-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built institutional scar packet.",
        "refs": [],
        "data": {"scar_id": value.get("scar_id", ""), "adaptive": value.get("adaptive", False)},
    }]
