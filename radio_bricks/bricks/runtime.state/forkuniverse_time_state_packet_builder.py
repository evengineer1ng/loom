from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.state.forkuniverse_time_state_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🕰️",
    "deterministic": True,
    "inputs": ["runtime.state_request.v1"],
    "outputs": ["runtime.state_response.v1"],
    "requires": [],
    "provides": ["runtime.forkuniverse_time_state_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "state", "forkuniverse", "time"],
    "description": "Package the ForkUniverse time state including tick, epoch, real-to-world ratios, last computed tick, and current mode.",
}


def build_forkuniverse_time_state_packet(
    tick: int,
    epoch: int,
    world_seconds_per_real_second: float,
    real_seconds_per_tick: float,
    last_computed_tick: int,
    mode: str,
) -> dict[str, Any]:
    return {
        "tick": int(tick),
        "epoch": int(epoch),
        "world_seconds_per_real_second": float(world_seconds_per_real_second),
        "real_seconds_per_tick": float(real_seconds_per_tick),
        "last_computed_tick": int(last_computed_tick),
        "mode": mode,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_forkuniverse_time_state_packet(
        tick=int(payload.get("tick") or 0),
        epoch=int(payload.get("epoch") or 0),
        world_seconds_per_real_second=float(payload.get("world_seconds_per_real_second") or 0.0),
        real_seconds_per_tick=float(payload.get("real_seconds_per_tick") or 0.0),
        last_computed_tick=int(payload.get("last_computed_tick") or 0),
        mode=str(payload.get("mode") or ""),
    )
    output_packet = {
        "packet_type": "runtime.state_response.v1",
        "packet_version": "runtime.state_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "forkuniverse-time-state-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built ForkUniverse time-state packet.",
        "refs": [],
        "data": {"tick": value.get("tick", 0), "mode": value.get("mode", "")},
    }]
