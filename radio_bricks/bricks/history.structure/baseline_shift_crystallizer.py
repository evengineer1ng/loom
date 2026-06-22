from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "history.structure.baseline_shift_crystallizer",
    "kind": "builder",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["history.structure_request.v1"],
    "outputs": ["history.structure_response.v1"],
    "requires": [],
    "provides": ["history.baseline_shift_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["history", "structure", "baseline", "shift"],
    "description": "Crystallize a structural baseline shift from a sustained trigger and one target effect.",
}


def build_baseline_shift_packet(
    tick: int,
    trigger_variable: str,
    trigger_threshold: float,
    trigger_direction: str,
    years_sustained: int,
    target_variable: str,
    delta: float,
    description: str,
    era_tag: str = "",
) -> dict[str, Any]:
    shift_id = f"bshift_{int(tick)}_{trigger_variable}_{target_variable}"
    return {
        "shift_id": shift_id,
        "trigger_variable": trigger_variable,
        "trigger_threshold": float(trigger_threshold),
        "trigger_direction": trigger_direction,
        "years_sustained": int(years_sustained),
        "tick_applied": int(tick),
        "target_variable": target_variable,
        "delta": float(delta),
        "description": description,
        "era_tag": era_tag,
        "causal_metadata": {
            "trigger": trigger_variable,
            "direction": trigger_direction,
            "threshold": float(trigger_threshold),
            "years_sustained": int(years_sustained),
            "description": description,
        },
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_baseline_shift_packet(
        tick=int(payload.get("tick") or 0),
        trigger_variable=str(payload.get("trigger_variable") or ""),
        trigger_threshold=float(payload.get("trigger_threshold") or 0.0),
        trigger_direction=str(payload.get("trigger_direction") or ""),
        years_sustained=int(payload.get("years_sustained") or 0),
        target_variable=str(payload.get("target_variable") or ""),
        delta=float(payload.get("delta") or 0.0),
        description=str(payload.get("description") or ""),
        era_tag=str(payload.get("era_tag") or ""),
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
        "receipt_id": "baseline-shift-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built baseline shift packet.",
        "refs": [],
        "data": {"shift_id": value.get("shift_id", ""), "target_variable": value.get("target_variable", "")},
    }]
