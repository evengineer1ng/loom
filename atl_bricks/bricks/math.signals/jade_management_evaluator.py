from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.signals.jade_management_evaluator",
    "kind": "classifier",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["math.series_request.v1"],
    "outputs": ["math.series_response.v1"],
    "requires": [],
    "provides": ["math.jade_exit_or_add"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "signals", "jade", "management"],
    "description": "Evaluate Jade-style time-stop exits and proven-winner adds.",
}


def jade_exit_or_add(current_profit: float, duration_minutes: float, current_rate: float, min_rate: float, nr_of_successful_entries: int, stake_amount: float) -> dict[str, Any]:
    exit_label = None
    add_stake = None
    if current_profit < -0.01 and duration_minutes > 45 and current_rate <= min_rate * 1.001:
        exit_label = "time_stop_loss_confirmed"
    elif 0 < current_profit < 0.003 and duration_minutes > 90:
        exit_label = "time_stop_flat"
    if current_profit > 0.015 and nr_of_successful_entries <= 1 and duration_minutes >= 20:
        add_stake = float(stake_amount) * 0.30
    return {"exit_label": exit_label, "add_stake": add_stake}


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = jade_exit_or_add(
        current_profit=float(payload.get("current_profit") or 0.0),
        duration_minutes=float(payload.get("duration_minutes") or 0.0),
        current_rate=float(payload.get("current_rate") or 0.0),
        min_rate=float(payload.get("min_rate") or 0.0),
        nr_of_successful_entries=int(payload.get("nr_of_successful_entries") or 0),
        stake_amount=float(payload.get("stake_amount") or 0.0),
    )
    output_packet = {
        "packet_type": "math.series_response.v1",
        "packet_version": "math.series_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"receipt_id": "jade-management", "brick_id": CONCEPT["id"], "kind": "classification", "label": "Evaluated Jade management logic.", "refs": [], "data": value}]
