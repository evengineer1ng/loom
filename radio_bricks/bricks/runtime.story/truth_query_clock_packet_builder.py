from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.story.truth_query_clock_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🕰️",
    "deterministic": True,
    "inputs": ["runtime.story_request.v1"],
    "outputs": ["runtime.story_response.v1"],
    "requires": [],
    "provides": ["runtime.truth_query_clock_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "story", "query", "clock", "time"],
    "description": "Package truth-query clock math that derives elapsed real seconds, simulated seconds, formatted universe time, and formatted elapsed simulation time.",
}


def build_truth_query_clock_packet(
    since_mode: str,
    since_timestamp: str,
    now_timestamp: str,
    elapsed_real_seconds: float,
    simulated_seconds: float,
    universe_time: str,
    elapsed_sim_time: str,
) -> dict[str, Any]:
    return {
        "since_mode": str(since_mode),
        "since_timestamp": str(since_timestamp),
        "now_timestamp": str(now_timestamp),
        "elapsed_real_seconds": float(elapsed_real_seconds),
        "simulated_seconds": float(simulated_seconds),
        "universe_time": str(universe_time),
        "elapsed_sim_time": str(elapsed_sim_time),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_truth_query_clock_packet(
        since_mode=str(payload.get("since_mode") or ""),
        since_timestamp=str(payload.get("since_timestamp") or ""),
        now_timestamp=str(payload.get("now_timestamp") or ""),
        elapsed_real_seconds=float(payload.get("elapsed_real_seconds") or 0.0),
        simulated_seconds=float(payload.get("simulated_seconds") or 0.0),
        universe_time=str(payload.get("universe_time") or ""),
        elapsed_sim_time=str(payload.get("elapsed_sim_time") or ""),
    )
    output_packet = {
        "packet_type": "runtime.story_response.v1",
        "packet_version": "runtime.story_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "truth-query-clock-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built truth-query clock packet.",
        "refs": [],
        "data": {
            "since_mode": value.get("since_mode", ""),
            "elapsed_real_seconds": value.get("elapsed_real_seconds", 0.0),
            "universe_time": value.get("universe_time", ""),
        },
    }]
