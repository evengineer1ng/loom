from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.economy.portfolio_position_snapshot_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "💼",
    "deterministic": True,
    "inputs": ["runtime.economy_request.v1"],
    "outputs": ["runtime.economy_response.v1"],
    "requires": [],
    "provides": ["runtime.portfolio_position_snapshot_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "economy", "portfolio", "positions", "equity"],
    "description": "Package extracted portfolio equity and open positions with coin, size, entry, unrealized PnL, leverage, and derived notional value.",
}


def build_portfolio_position_snapshot_packet(
    equity: float | None,
    positions: list[dict[str, Any]] | None,
    user_address: str,
    provider: str,
) -> dict[str, Any]:
    return {
        "equity": None if equity is None else float(equity),
        "positions": [dict(item) for item in (positions or [])],
        "user_address": str(user_address),
        "provider": str(provider),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_portfolio_position_snapshot_packet(
        equity=payload.get("equity"),
        positions=list(payload.get("positions") or []),
        user_address=str(payload.get("user_address") or ""),
        provider=str(payload.get("provider") or ""),
    )
    output_packet = {
        "packet_type": "runtime.economy_response.v1",
        "packet_version": "runtime.economy_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "portfolio-position-snapshot-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built portfolio-position snapshot packet.",
        "refs": [],
        "data": {
            "provider": value.get("provider", ""),
            "equity_present": value.get("equity") is not None,
            "position_count": len(value.get("positions", [])),
        },
    }]
