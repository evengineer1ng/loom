from __future__ import annotations

from typing import Any


DEFAULT_EXCHANGE_PROFILES = (
    {"name": "binance", "stake_currency": "USDC", "trading_mode": "futures", "margin_mode": "isolated", "rotation_bias": 0, "ccxt_options": {"defaultType": "swap", "defaultSettle": "USDC"}},
    {"name": "bitget", "stake_currency": "USDT", "trading_mode": "futures", "margin_mode": "isolated", "rotation_bias": 0, "ccxt_options": {"defaultType": "swap", "defaultSettle": "USDT"}},
    {"name": "bybit", "stake_currency": "USDT", "trading_mode": "futures", "margin_mode": "isolated", "rotation_bias": 0, "ccxt_options": {"defaultType": "swap", "defaultSettle": "USDT"}},
    {"name": "okx", "stake_currency": "USDT", "trading_mode": "futures", "margin_mode": "isolated", "rotation_bias": 0, "ccxt_options": {"defaultType": "swap", "defaultSettle": "USDT", "fetchMarkets": ["swap"]}},
    {"name": "hyperliquid", "stake_currency": "USDC", "trading_mode": "futures", "margin_mode": "isolated", "rotation_bias": 3, "ccxt_options": {"fetchMarkets": {"types": ["swap"]}, "defaultType": "swap", "defaultSettle": "USDC", "hip3TokensByName": {}, "cachedCurrenciesById": {}}},
)

CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "config.assembly.exchange_profile_picker",
    "kind": "planner",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["config.request.v1"],
    "outputs": ["config.response.v1"],
    "requires": [],
    "provides": ["config.pick_exchange_profile"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["config", "exchange", "rotation"],
    "description": "Pick an exchange profile from an existing exchange name or a deterministic rotation order snapshot.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def pick_exchange_profile(existing_exchange: str = "", rotation_order: list[str] | None = None, profiles: tuple[dict[str, Any], ...] = DEFAULT_EXCHANGE_PROFILES) -> dict[str, Any]:
    indexed = {str(profile["name"]): profile for profile in profiles}
    if existing_exchange in indexed:
        return dict(indexed[existing_exchange])
    for exchange_name in rotation_order or []:
        if exchange_name in indexed:
            return dict(indexed[exchange_name])
    return dict(profiles[0])


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = input_packet.get("payload", {})
    profile = pick_exchange_profile(
        existing_exchange=str(payload.get("existing_exchange") or ""),
        rotation_order=list(payload.get("rotation_order") or []),
    )
    output_packet = {
        "packet_type": "config.response.v1",
        "packet_version": "config.response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"profile": profile},
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "exchange-profile-picked",
        "brick_id": CONCEPT["id"],
        "kind": "planning",
        "label": "Picked deterministic exchange profile.",
        "refs": [],
        "data": {"exchange_name": (output_packet["payload"]["profile"] or {}).get("name")},
    }]
