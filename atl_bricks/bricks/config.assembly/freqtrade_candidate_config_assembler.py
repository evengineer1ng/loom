from __future__ import annotations

from copy import deepcopy
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "config.assembly.freqtrade_candidate_config_assembler",
    "kind": "planner",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["config.request.v1"],
    "outputs": ["config.response.v1"],
    "requires": [],
    "provides": ["config.assemble_freqtrade_candidate_config"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["config", "freqtrade", "assembly"],
    "description": "Assemble a fuller deterministic Freqtrade candidate config from precomputed pieces.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def assemble_freqtrade_candidate_config(
    base_config: dict[str, Any],
    exchange_profile: dict[str, Any],
    timeframe: str,
    max_open_trades: int,
    bot_name: str,
    pair_whitelist: list[str] | None = None,
    pair_blacklist: list[str] | None = None,
    entry_order_type: str = "",
    exit_order_type: str = "",
) -> dict[str, Any]:
    config = deepcopy(base_config) if isinstance(base_config, dict) else {}
    profile = exchange_profile or {}
    config["bot_name"] = bot_name
    config["dry_run"] = True
    config["initial_state"] = "running"
    config["fiat_display_currency"] = ""
    config["timeframe"] = timeframe or str(config.get("timeframe") or "5m")
    config["trading_mode"] = str(profile.get("trading_mode") or config.get("trading_mode") or "futures")
    config["margin_mode"] = str(profile.get("margin_mode") or config.get("margin_mode") or "isolated")
    config["stake_currency"] = str(profile.get("stake_currency") or config.get("stake_currency") or "USDT")
    config["max_open_trades"] = int(max_open_trades)
    config["exchange"] = {
        "name": str(profile.get("name") or "binance"),
        "ccxt_config": {
            "enableRateLimit": True,
            "options": deepcopy(profile.get("ccxt_options") or {}),
        },
        "pair_whitelist": list(pair_whitelist or []),
        "pair_blacklist": list(pair_blacklist or []),
    }
    if exit_order_type == "market":
        config.setdefault("exit_pricing", {})["price_side"] = "other"
    if entry_order_type == "market":
        config.setdefault("entry_pricing", {})["price_side"] = "other"
    config.setdefault("pairlists", [])
    return config


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = input_packet.get("payload", {})
    config = assemble_freqtrade_candidate_config(
        base_config=dict(payload.get("base_config") or {}),
        exchange_profile=dict(payload.get("exchange_profile") or {}),
        timeframe=str(payload.get("timeframe") or ""),
        max_open_trades=int(payload.get("max_open_trades") or 0),
        bot_name=str(payload.get("bot_name") or ""),
        pair_whitelist=list(payload.get("pair_whitelist") or []),
        pair_blacklist=list(payload.get("pair_blacklist") or []),
        entry_order_type=str(payload.get("entry_order_type") or ""),
        exit_order_type=str(payload.get("exit_order_type") or ""),
    )
    output_packet = {
        "packet_type": "config.response.v1",
        "packet_version": "config.response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"config": config},
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    cfg = output_packet["payload"]["config"]
    return [{
        "receipt_id": "freqtrade-candidate-config-assembled",
        "brick_id": CONCEPT["id"],
        "kind": "config_build",
        "label": "Assembled deterministic Freqtrade candidate config.",
        "refs": [],
        "data": {
            "bot_name": cfg.get("bot_name"),
            "exchange": (cfg.get("exchange") or {}).get("name"),
            "timeframe": cfg.get("timeframe"),
        },
    }]
