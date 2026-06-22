from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "backtest.calibration.universe_membership_gate",
    "kind": "world_operator",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["backtest.sim_request.v1"],
    "outputs": ["backtest.sim_response.v1"],
    "requires": [],
    "provides": ["backtest.membership_gate_allow"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["backtest", "universe", "gate"],
    "description": "Allow an entry only when the pair belongs to the universe membership set for the requested date.",
}


def membership_gate_allow(pair: str, members: list[str] | None) -> bool:
    if members is None:
        return True
    return str(pair or "") in set(str(item) for item in (members or []))


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    allowed = membership_gate_allow(str(payload.get("pair") or ""), payload.get("members"))
    output_packet = {
        "packet_type": "backtest.sim_response.v1",
        "packet_version": "backtest.sim_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"allowed": allowed},
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(allowed), "issues": [], "meta": {}}


def receipts(allowed: bool) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "universe-membership-gate",
        "brick_id": CONCEPT["id"],
        "kind": "gate",
        "label": "Evaluated universe membership gate.",
        "refs": [],
        "data": {"allowed": allowed},
    }]
