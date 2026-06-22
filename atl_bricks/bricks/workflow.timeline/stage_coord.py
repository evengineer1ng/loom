from __future__ import annotations

from dataclasses import dataclass
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "workflow.timeline.stage_coord",
    "kind": "bridge",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["workflow.timeline_request.v1"],
    "outputs": ["workflow.timeline_response.v1"],
    "requires": [],
    "provides": ["workflow.stage_coord_from_dict", "workflow.stage_coord_to_dict"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["workflow", "timeline", "coordinate"],
    "description": "Serialize and deserialize stage coordinates for timeline-driven automation.",
}


@dataclass
class StageCoord:
    x: int = 0
    y: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {"x": int(self.x), "y": int(self.y)}

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "StageCoord":
        return StageCoord(x=safe_int(data.get("x", 0)), y=safe_int(data.get("y", 0)))


def inspect() -> dict[str, Any]:
    return CONCEPT


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = input_packet.get("payload", {})
    coord = StageCoord.from_dict(dict(payload.get("value") or {}))
    output_packet = {
        "packet_type": "workflow.timeline_response.v1",
        "packet_version": "workflow.timeline_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"value": coord.to_dict()},
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "stage-coord-serialized",
        "brick_id": CONCEPT["id"],
        "kind": "conversion",
        "label": "Serialized timeline stage coordinate.",
        "refs": [],
        "data": output_packet["payload"]["value"],
    }]
