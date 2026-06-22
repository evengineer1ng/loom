from __future__ import annotations

from copy import deepcopy
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "config.assembly.market_order_price_side_reconciler",
    "kind": "bridge",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["config.request.v1"],
    "outputs": ["config.response.v1"],
    "requires": [],
    "provides": ["config.reconcile_market_order_price_side"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["config", "freqtrade", "order-type"],
    "description": "Reconcile entry and exit pricing price_side when market order types are declared.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def reconcile_market_order_price_side(config: dict[str, Any], entry_order_type: str = "", exit_order_type: str = "") -> dict[str, Any]:
    cfg = deepcopy(config)
    if entry_order_type == "market":
        cfg.setdefault("entry_pricing", {})["price_side"] = "other"
    if exit_order_type == "market":
        cfg.setdefault("exit_pricing", {})["price_side"] = "other"
    return cfg


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = input_packet.get("payload", {})
    config = dict(payload.get("config") or {})
    reconciled = reconcile_market_order_price_side(
        config,
        entry_order_type=str(payload.get("entry_order_type") or ""),
        exit_order_type=str(payload.get("exit_order_type") or ""),
    )
    output_packet = {
        "packet_type": "config.response.v1",
        "packet_version": "config.response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"config": reconciled},
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    cfg = output_packet["payload"]["config"]
    return [{
        "receipt_id": "market-order-price-side-reconciled",
        "brick_id": CONCEPT["id"],
        "kind": "config_build",
        "label": "Reconciled price_side for market orders.",
        "refs": [],
        "data": {
            "entry_price_side": (cfg.get("entry_pricing") or {}).get("price_side"),
            "exit_price_side": (cfg.get("exit_pricing") or {}).get("price_side"),
        },
    }]
