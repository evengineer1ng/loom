from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.economy.market_symbol_state_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📉",
    "deterministic": True,
    "inputs": ["runtime.economy_request.v1"],
    "outputs": ["runtime.economy_response.v1"],
    "requires": [],
    "provides": ["runtime.market_symbol_state_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "economy", "market", "symbol", "state"],
    "description": "Package rolling market symbol state with prices, returns, volatility history, last price, and per-event cooldown memory.",
}


def build_market_symbol_state_packet(
    symbol: str,
    prices: list[float] | None,
    returns: list[float] | None,
    vol_history: list[float] | None,
    last_price: float | None,
    last_emit_minute: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "symbol": str(symbol),
        "prices": [float(item) for item in (prices or [])],
        "returns": [float(item) for item in (returns or [])],
        "vol_history": [float(item) for item in (vol_history or [])],
        "last_price": None if last_price is None else float(last_price),
        "last_emit_minute": dict(last_emit_minute or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_market_symbol_state_packet(
        symbol=str(payload.get("symbol") or ""),
        prices=list(payload.get("prices") or []),
        returns=list(payload.get("returns") or []),
        vol_history=list(payload.get("vol_history") or []),
        last_price=payload.get("last_price"),
        last_emit_minute=dict(payload.get("last_emit_minute") or {}),
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
        "receipt_id": "market-symbol-state-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built market-symbol state packet.",
        "refs": [],
        "data": {
            "symbol": value.get("symbol", ""),
            "price_points": len(value.get("prices", [])),
            "return_points": len(value.get("returns", [])),
        },
    }]
