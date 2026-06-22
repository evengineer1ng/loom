from __future__ import annotations

import base64
from typing import Any

import httpx


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "fetch.freqtrade_api.closed_trades_pager",
    "kind": "bridge",
    "version": "0.1.0",
    "deterministic": False,
    "inputs": ["fetch.http_request.v1"],
    "outputs": ["fetch.http_response.v1"],
    "requires": [],
    "provides": ["fetch.freqtrade_closed_trades"],
    "side_effects": ["network_read"],
    "ui_slots": [],
    "tags": ["freqtrade", "trades", "pagination"],
    "description": "Fetch all closed trades from a Freqtrade REST API using paginated /api/v1/trades reads.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    payload = input_packet.get("payload", {})
    missing = [field for field in ("api_url", "username", "password") if field not in payload]
    if missing:
        return [{"code": "missing_fields", "message": f"Missing payload fields: {', '.join(missing)}"}]
    return []


def build_auth_header(username: str, password: str) -> dict[str, str]:
    raw = f"{username}:{password}"
    token = base64.b64encode(raw.encode("ascii")).decode("ascii")
    return {"Authorization": f"Basic {token}"}


def first_present_value(*values: Any) -> Any:
    for value in values:
        if value is not None and value != "":
            return value
    return None


def fetch_closed_trades(api_url: str, username: str, password: str, limit: int = 250) -> list[dict[str, Any]] | None:
    headers = build_auth_header(username, password)
    records: list[dict[str, Any]] = []
    try:
        with httpx.Client() as client:
            offset = 0
            while True:
                response = client.get(
                    f"{api_url.rstrip('/')}/api/v1/trades?limit={limit}&offset={offset}",
                    headers=headers,
                    timeout=8.0,
                )
                response.raise_for_status()
                payload = response.json()
                page = payload.get("trades", []) if isinstance(payload, dict) else []
                if not page:
                    break
                for trade in page:
                    if bool(trade.get("is_open")):
                        continue
                    records.append(
                        {
                            "trade_id": trade.get("trade_id"),
                            "pair": trade.get("pair"),
                            "exit_reason": str(trade.get("exit_reason") or ""),
                            "enter_tag": str(trade.get("enter_tag") or ""),
                            "close_profit": first_present_value(trade.get("close_profit"), trade.get("profit_ratio")),
                            "close_profit_abs": first_present_value(trade.get("close_profit_abs"), trade.get("profit_abs")),
                            "realized_profit": trade.get("realized_profit"),
                            "open_date": trade.get("open_date"),
                            "close_date": trade.get("close_date"),
                            "is_short": bool(trade.get("is_short")),
                        }
                    )
                total = int(payload.get("total_trades") or len(page))
                offset += len(page)
                if offset >= total:
                    break
    except Exception:
        return None
    return records


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    payload = input_packet["payload"]
    api_url = str(payload.get("api_url") or "")
    username = str(payload.get("username") or "")
    password = str(payload.get("password") or "")
    limit = int(payload.get("limit") or 250)
    trades = fetch_closed_trades(api_url, username, password, limit=limit)
    output_packet = {
        "packet_type": "fetch.http_response.v1",
        "packet_version": "fetch.http_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"api_url": api_url, "trades": trades, "count": len(trades) if trades is not None else 0},
        "refs": [f"{api_url.rstrip('/')}/api/v1/trades"],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {
        "ok": trades is not None,
        "output_packet": output_packet,
        "receipts": receipts(output_packet),
        "issues": [] if trades is not None else [{"code": "fetch_failed", "message": "Could not fetch closed trades."}],
        "meta": {},
    }


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "receipt_id": "freqtrade-closed-trades-fetched",
            "brick_id": CONCEPT["id"],
            "kind": "network_read",
            "label": "Fetched paginated closed trades from Freqtrade API.",
            "refs": output_packet["refs"],
            "data": {"count": output_packet["payload"]["count"]},
        }
    ]
