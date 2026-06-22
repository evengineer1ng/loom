from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.narration.ftb_event_batch_tagger",
    "kind": "builder",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.narration_request.v1"],
    "outputs": ["runtime.narration_response.v1"],
    "requires": [],
    "provides": ["runtime.ftb_event_batch_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "narration", "ftb", "events", "batch"],
    "description": "Tag FTB events with narrator-facing batch metadata for aggregation and routing.",
}


def build_ftb_event_batch_packet(
    events: list[dict[str, Any]] | None,
    batch_mode: bool = False,
    tick_range: list[int] | tuple[int, int] | None = None,
) -> dict[str, Any]:
    tagged = []
    start_tick = int((tick_range or [0, 0])[0]) if tick_range else 0
    end_tick = int((tick_range or [0, 0])[1]) if tick_range else 0
    for event in events or []:
        item = dict(event)
        data = dict(item.get("data") or {})
        data["_ftb"] = True
        if batch_mode and tick_range:
            data["_batch_mode"] = True
            data["_batch_start_tick"] = start_tick
            data["_batch_end_tick"] = end_tick
        item["data"] = data
        tagged.append(item)
    return {
        "events": tagged,
        "batch_mode": bool(batch_mode),
        "tick_range": [start_tick, end_tick] if tick_range else None,
        "event_count": len(tagged),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_ftb_event_batch_packet(
        events=list(payload.get("events") or []),
        batch_mode=bool(payload.get("batch_mode", False)),
        tick_range=payload.get("tick_range"),
    )
    output_packet = {
        "packet_type": "runtime.narration_response.v1",
        "packet_version": "runtime.narration_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "ftb-event-batch-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built FTB narrator event batch packet.",
        "refs": [],
        "data": {"event_count": value.get("event_count", 0), "batch_mode": value.get("batch_mode", False)},
    }]
