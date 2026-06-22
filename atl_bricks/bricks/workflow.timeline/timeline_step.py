from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "workflow.timeline.timeline_step",
    "kind": "bridge",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["workflow.timeline_request.v1"],
    "outputs": ["workflow.timeline_response.v1"],
    "requires": [],
    "provides": ["workflow.timeline_step_from_dict", "workflow.timeline_step_to_dict"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["workflow", "timeline", "step"],
    "description": "Serialize and deserialize timeline steps for automation workflows.",
}


@dataclass
class TimelineStep:
    type: str
    params: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.type, "params": self.params}

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "TimelineStep":
        return TimelineStep(type=str(data.get("type", "")).strip(), params=dict(data.get("params", {}) or {}))


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = input_packet.get("payload", {})
    step = TimelineStep.from_dict(dict(payload.get("value") or {}))
    output_packet = {
        "packet_type": "workflow.timeline_response.v1",
        "packet_version": "workflow.timeline_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"value": step.to_dict()},
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "timeline-step-serialized",
        "brick_id": CONCEPT["id"],
        "kind": "conversion",
        "label": "Serialized timeline step.",
        "refs": [],
        "data": {"type": output_packet["payload"]["value"].get("type", "")},
    }]
