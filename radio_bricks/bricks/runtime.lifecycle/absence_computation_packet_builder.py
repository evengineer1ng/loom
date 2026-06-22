from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.lifecycle.absence_computation_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🌘",
    "deterministic": True,
    "inputs": ["runtime.lifecycle_request.v1"],
    "outputs": ["runtime.lifecycle_response.v1"],
    "requires": [],
    "provides": ["runtime.absence_computation_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "lifecycle", "absence", "ticks", "delta"],
    "description": "Package the while-you-were-gone absence computation with elapsed real seconds, owed ticks, mode transitions, and emitted truth delta.",
}


def build_absence_computation_packet(
    elapsed_real_seconds: float,
    from_tick: int,
    owed_ticks: int,
    to_tick: int,
    entered_deep_sleep: bool,
    truth_delta: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "elapsed_real_seconds": float(elapsed_real_seconds),
        "from_tick": int(from_tick),
        "owed_ticks": int(owed_ticks),
        "to_tick": int(to_tick),
        "entered_deep_sleep": bool(entered_deep_sleep),
        "truth_delta": dict(truth_delta or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_absence_computation_packet(
        elapsed_real_seconds=float(payload.get("elapsed_real_seconds") or 0.0),
        from_tick=int(payload.get("from_tick") or 0),
        owed_ticks=int(payload.get("owed_ticks") or 0),
        to_tick=int(payload.get("to_tick") or 0),
        entered_deep_sleep=bool(payload.get("entered_deep_sleep")),
        truth_delta=dict(payload.get("truth_delta") or {}),
    )
    output_packet = {
        "packet_type": "runtime.lifecycle_response.v1",
        "packet_version": "runtime.lifecycle_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "absence-computation-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built absence-computation packet.",
        "refs": [],
        "data": {"owed_ticks": value.get("owed_ticks", 0), "entered_deep_sleep": value.get("entered_deep_sleep", False)},
    }]
