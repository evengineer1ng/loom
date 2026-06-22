from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.economy.transaction_ledger_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.economy_request.v1"],
    "outputs": ["runtime.economy_response.v1"],
    "requires": [],
    "provides": ["runtime.transaction_ledger_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "economy", "ledger", "finance"],
    "description": "Normalize financial transactions into a portable ledger packet with income and expense totals.",
}


def build_transaction_ledger_packet(transactions: list[dict[str, Any]] | None) -> dict[str, Any]:
    entries = [dict(item) for item in (transactions or [])]
    income_total = sum(float(item.get("amount") or 0.0) for item in entries if str(item.get("type") or "") == "income")
    expense_total = sum(float(item.get("amount") or 0.0) for item in entries if str(item.get("type") or "") == "expense")
    categories = sorted({str(item.get("category") or "") for item in entries if item.get("category")})
    latest_balance = entries[0].get("balance_after") if entries else None
    return {
        "entries": entries,
        "entry_count": len(entries),
        "income_total": income_total,
        "expense_total": expense_total,
        "net_flow": income_total - expense_total,
        "categories": categories,
        "latest_balance": latest_balance,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_transaction_ledger_packet(list(payload.get("transactions") or []))
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
        "receipt_id": "transaction-ledger-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built transaction ledger packet.",
        "refs": [],
        "data": {"entry_count": value.get("entry_count", 0), "net_flow": value.get("net_flow", 0.0)},
    }]
