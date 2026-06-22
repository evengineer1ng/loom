from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.save.save_status_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🗄️",
    "deterministic": True,
    "inputs": ["runtime.save_request.v1"],
    "outputs": ["runtime.save_response.v1"],
    "requires": [],
    "provides": ["runtime.save_status_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "save", "status", "ticks", "metadata"],
    "description": "Package save-file existence and freshness metadata, plus saved-run summary fields when a save is present.",
}


def build_save_status_packet(
    save_exists: bool,
    last_save_tick: int,
    current_tick: int,
    ticks_since_save: int | None,
    saved_seed: int | None = None,
    saved_tick: int | None = None,
    saved_team_size: int | None = None,
    saved_location: str | None = None,
    saved_fragments: int | None = None,
) -> dict[str, Any]:
    packet: dict[str, Any] = {
        "save_exists": bool(save_exists),
        "last_save_tick": int(last_save_tick),
        "current_tick": int(current_tick),
        "ticks_since_save": ticks_since_save if ticks_since_save is None else int(ticks_since_save),
    }
    if saved_seed is not None:
        packet["saved_seed"] = int(saved_seed)
    if saved_tick is not None:
        packet["saved_tick"] = int(saved_tick)
    if saved_team_size is not None:
        packet["saved_team_size"] = int(saved_team_size)
    if saved_location is not None:
        packet["saved_location"] = saved_location
    if saved_fragments is not None:
        packet["saved_fragments"] = int(saved_fragments)
    return packet


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_save_status_packet(
        save_exists=bool(payload.get("save_exists")),
        last_save_tick=int(payload.get("last_save_tick") or 0),
        current_tick=int(payload.get("current_tick") or 0),
        ticks_since_save=payload.get("ticks_since_save"),
        saved_seed=payload.get("saved_seed"),
        saved_tick=payload.get("saved_tick"),
        saved_team_size=payload.get("saved_team_size"),
        saved_location=payload.get("saved_location"),
        saved_fragments=payload.get("saved_fragments"),
    )
    output_packet = {
        "packet_type": "runtime.save_response.v1",
        "packet_version": "runtime.save_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "save-status-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built save-status packet.",
        "refs": [],
        "data": {"save_exists": value.get("save_exists", False), "current_tick": value.get("current_tick", 0)},
    }]
