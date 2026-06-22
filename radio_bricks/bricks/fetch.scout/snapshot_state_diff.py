from __future__ import annotations

import json
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "fetch.scout.snapshot_state_diff",
    "kind": "analyzer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["fetch.scout_request.v1"],
    "outputs": ["fetch.scout_response.v1"],
    "requires": [],
    "provides": ["fetch.scout_state_diff_candidates"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["fetch", "scout", "snapshot", "diff"],
    "description": "Diff a current scout snapshot against a previous one and emit raw field-added or field-changed observations.",
}


def diff_scout_snapshot(prev: dict[str, Any] | None, curr: dict[str, Any] | None, source: str, default_priority: float, ignore_keys: list[str] | None = None) -> list[dict[str, Any]]:
    current = dict(curr or {})
    previous = dict(prev or {})
    ignore = set(str(item) for item in (ignore_keys or []))
    out = []
    for key, value in current.items():
        if key in ignore:
            continue
        if key not in previous:
            out.append(_candidate(source, "field_added", f"{key} appeared", _short(value), default_priority, f"{key}={_short(value)}"))
        elif previous.get(key) != value:
            out.append(_candidate(source, "field_changed", f"{key} changed", f"{_short(previous.get(key))} -> {_short(value)}", default_priority, f"{key}={_short(value)}"))
    return out


def _candidate(source: str, otype: str, title: str, body: str, priority: float, raw_id: str) -> dict[str, Any]:
    return {
        "post_id": f"{source}:{raw_id}",
        "source": source,
        "title": title,
        "body": body,
        "priority": float(priority),
        "type": otype,
        "tags": [source, otype],
    }


def _short(value: Any, limit: int = 120) -> str:
    try:
        text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    except Exception:
        text = str(value)
    return text if len(text) <= limit else text[: limit - 1] + "..."


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = diff_scout_snapshot(
        prev=dict(payload.get("prev") or {}),
        curr=dict(payload.get("curr") or {}),
        source=str(payload.get("source") or "scout"),
        default_priority=float(payload.get("default_priority") or 60.0),
        ignore_keys=list(payload.get("ignore_keys") or []),
    )
    output_packet = {
        "packet_type": "fetch.scout_response.v1",
        "packet_version": "fetch.scout_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "snapshot-state-diff",
        "brick_id": CONCEPT["id"],
        "kind": "analysis",
        "label": "Built snapshot diff observations.",
        "refs": [],
        "data": {"count": len(value)},
    }]
