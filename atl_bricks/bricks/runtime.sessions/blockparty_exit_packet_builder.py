from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.sessions.blockparty_exit_packet_builder",
    "kind": "renderer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.session_request.v1"],
    "outputs": ["runtime.session_response.v1"],
    "requires": [],
    "provides": ["runtime.blockparty_exit_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "session", "blockparty", "exit"],
    "description": "Build a Block Party exit packet capturing time-stop, leadership-flip, and group-reversal outcomes.",
}


def build_blockparty_exit_packet(reason: str | None, current_profit: float, duration_minutes: float, group: float | None, own_ret: float | None, gap: float | None) -> dict[str, Any]:
    return {
        "reason": reason,
        "current_profit": float(current_profit),
        "duration_minutes": float(duration_minutes),
        "group_return": group,
        "own_return": own_ret,
        "gap": gap,
        "leadership_flip": reason in {"bp_caught_up_long", "bp_caught_up_short"},
        "group_reversal": reason in {"bp_group_rev_long", "bp_group_rev_short"},
        "time_stop": reason == "bp_time_stop",
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_blockparty_exit_packet(
        reason=payload.get("reason"),
        current_profit=float(payload.get("current_profit") or 0.0),
        duration_minutes=float(payload.get("duration_minutes") or 0.0),
        group=payload.get("group"),
        own_ret=payload.get("own_ret"),
        gap=payload.get("gap"),
    )
    output_packet = {
        "packet_type": "runtime.session_response.v1",
        "packet_version": "runtime.session_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"receipt_id": "blockparty-exit-packet", "brick_id": CONCEPT["id"], "kind": "report", "label": "Built Block Party exit packet.", "refs": [], "data": {"reason": value.get("reason")}}]
