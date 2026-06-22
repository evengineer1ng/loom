from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "config.assembly.exchange_profile_reader",
    "kind": "bridge",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["config.request.v1"],
    "outputs": ["config.response.v1"],
    "requires": [],
    "provides": ["config.exchange_profile_by_id", "config.exchange_quote_currency"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["config", "exchange", "profile"],
    "description": "Read exchange profiles and derive quote currency from settle/stake settings.",
}


DEFAULT_EXCHANGE_PROFILES = (
    {"name": "binance", "stake_currency": "USDC", "trading_mode": "futures", "margin_mode": "isolated", "rotation_bias": 0, "ccxt_options": {"defaultType": "swap", "defaultSettle": "USDC"}},
    {"name": "bitget", "stake_currency": "USDT", "trading_mode": "futures", "margin_mode": "isolated", "rotation_bias": 0, "ccxt_options": {"defaultType": "swap", "defaultSettle": "USDT"}},
    {"name": "bybit", "stake_currency": "USDT", "trading_mode": "futures", "margin_mode": "isolated", "rotation_bias": 0, "ccxt_options": {"defaultType": "swap", "defaultSettle": "USDT"}},
    {"name": "okx", "stake_currency": "USDT", "trading_mode": "futures", "margin_mode": "isolated", "rotation_bias": 0, "ccxt_options": {"defaultType": "swap", "defaultSettle": "USDT", "fetchMarkets": ["swap"]}},
    {"name": "hyperliquid", "stake_currency": "USDC", "trading_mode": "futures", "margin_mode": "isolated", "rotation_bias": 3, "ccxt_options": {"fetchMarkets": {"types": ["swap"]}, "defaultType": "swap", "defaultSettle": "USDC", "hip3TokensByName": {}, "cachedCurrenciesById": {}}},
)


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    if "exchange_id" not in input_packet.get("payload", {}):
        return [{"code": "missing_exchange_id", "message": "payload.exchange_id is required."}]
    return []


def exchange_profile_by_id(exchange_id: str, profiles: tuple[dict[str, Any], ...] = DEFAULT_EXCHANGE_PROFILES) -> dict[str, Any] | None:
    for profile in profiles:
        if str(profile.get("name")) == exchange_id:
            return dict(profile)
    return None


def exchange_quote_currency(profile: dict[str, Any]) -> str:
    options = profile.get("ccxt_options") or {}
    return str(options.get("defaultSettle") or profile.get("stake_currency") or "USDT").upper()


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    exchange_id = str(input_packet["payload"]["exchange_id"])
    profile = exchange_profile_by_id(exchange_id)
    output_packet = {
        "packet_type": "config.response.v1",
        "packet_version": "config.response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"profile": profile, "quote_currency": exchange_quote_currency(profile) if profile else ""},
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "exchange-profile-read",
        "brick_id": CONCEPT["id"],
        "kind": "config_read",
        "label": "Read exchange profile and quote currency.",
        "refs": [],
        "data": {"has_profile": bool(output_packet["payload"]["profile"])},
    }]
