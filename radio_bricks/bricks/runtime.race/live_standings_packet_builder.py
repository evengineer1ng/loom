from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.race.live_standings_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.race_request.v1"],
    "outputs": ["runtime.race_response.v1"],
    "requires": [],
    "provides": ["runtime.live_standings_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "race", "standings", "pbp"],
    "description": "Normalize live standings into a renderable full-field read model with gaps and player highlights.",
}


def build_live_standings_packet(live_standings: list[dict[str, Any]] | None) -> dict[str, Any]:
    rows = []
    for index, standing in enumerate(live_standings or [], 1):
        item = dict(standing)
        gap = float(item.get("gap") or 0.0)
        status = str(item.get("status") or "racing")
        rows.append({
            "position": index,
            "driver": str(item.get("driver") or "Unknown"),
            "team": str(item.get("team") or "Unknown"),
            "gap_text": "Leader" if index == 1 else (status.upper() if status != "racing" else (f"+{gap:.1f}s" if gap > 0 else "")),
            "status": status,
            "is_player": bool(item.get("is_player", False)),
        })
    return {"rows": rows, "field_size": len(rows), "player_rows": [row for row in rows if row.get("is_player")]}


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_live_standings_packet(list(payload.get("live_standings") or []))
    output_packet = {
        "packet_type": "runtime.race_response.v1",
        "packet_version": "runtime.race_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "live-standings-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built live standings packet.",
        "refs": [],
        "data": {"field_size": value.get("field_size", 0)},
    }]
