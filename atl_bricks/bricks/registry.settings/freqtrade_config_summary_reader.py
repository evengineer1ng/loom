from __future__ import annotations

import json
from pathlib import Path
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "registry.settings.freqtrade_config_summary_reader",
    "kind": "bridge",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["registry.request.v1"],
    "outputs": ["registry.response.v1"],
    "requires": [],
    "provides": ["registry.read_freqtrade_config_summary"],
    "side_effects": ["file_read"],
    "ui_slots": [],
    "tags": ["freqtrade", "config", "summary"],
    "description": "Read a compact summary view from a freqtrade config file.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    payload = input_packet.get("payload", {})
    if not payload.get("config_path"):
        return [{"code": "missing_config_path", "message": "payload.config_path is required."}]
    return []


def load_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def read_config_summary(config_path: Path) -> dict[str, Any]:
    if not config_path.exists():
        return {}
    raw = load_json(config_path, {})
    exchange = raw.get("exchange", {}) if isinstance(raw.get("exchange"), dict) else {}
    pairlists = raw.get("pairlists") or [{}]
    pair_whitelist = exchange.get("pair_whitelist") or []
    first_pairlist = pairlists[0] if isinstance(pairlists, list) and pairlists else {}
    return {
        "exchange": exchange.get("name"),
        "stake_currency": raw.get("stake_currency"),
        "dry_run_wallet": raw.get("dry_run_wallet"),
        "max_open_trades": raw.get("max_open_trades"),
        "timeframe": raw.get("timeframe"),
        "pairlist_method": first_pairlist.get("method") if isinstance(first_pairlist, dict) else None,
        "pair_count": len(pair_whitelist),
        "pair_whitelist_preview": pair_whitelist[:8],
    }


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    config_path = Path(str(input_packet["payload"]["config_path"]))
    summary = read_config_summary(config_path)
    output_packet = {
        "packet_type": "registry.response.v1",
        "packet_version": "registry.response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"config_path": str(config_path), "summary": summary},
        "refs": [str(config_path)],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {
        "ok": True,
        "output_packet": output_packet,
        "receipts": receipts(output_packet),
        "issues": [],
        "meta": {},
    }


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "receipt_id": "freqtrade-config-summary-read",
            "brick_id": CONCEPT["id"],
            "kind": "file_read",
            "label": "Read freqtrade config summary.",
            "refs": output_packet["refs"],
            "data": {"fields": sorted(output_packet["payload"]["summary"].keys())},
        }
    ]
