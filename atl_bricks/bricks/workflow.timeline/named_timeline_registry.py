from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "workflow.timeline.named_timeline_registry",
    "kind": "bridge",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["workflow.timeline_request.v1"],
    "outputs": ["workflow.timeline_response.v1"],
    "requires": [],
    "provides": ["workflow.timeline_registry_save", "workflow.timeline_registry_load", "workflow.timeline_registry_delete"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["workflow", "timeline", "macro", "registry"],
    "description": "Manage named timeline macros as portable state without coupling to any GUI shell.",
}


@dataclass
class TimelineStep:
    type: str
    params: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.type, "params": dict(self.params)}

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "TimelineStep":
        return TimelineStep(type=str(data.get("type", "")).strip(), params=dict(data.get("params", {}) or {}))


def clone_steps(steps: list[TimelineStep] | None) -> list[TimelineStep]:
    return [TimelineStep(step.type, dict(step.params)) for step in (steps or [])]


def save_named_timeline(registry: dict[str, list[TimelineStep]] | None, name: str, steps: list[TimelineStep] | None) -> dict[str, list[TimelineStep]]:
    result = {str(key): clone_steps(value) for key, value in dict(registry or {}).items()}
    key = str(name or "").strip()
    if not key:
        return result
    result[key] = clone_steps(steps)
    return result


def load_named_timeline(registry: dict[str, list[TimelineStep]] | None, name: str) -> list[TimelineStep]:
    key = str(name or "").strip()
    if not key:
        return []
    return clone_steps(dict(registry or {}).get(key) or [])


def delete_named_timeline(registry: dict[str, list[TimelineStep]] | None, name: str) -> dict[str, list[TimelineStep]]:
    result = {str(key): clone_steps(value) for key, value in dict(registry or {}).items()}
    key = str(name or "").strip()
    if key:
        result.pop(key, None)
    return result


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    action = str(payload.get("action") or "load").strip().lower()
    name = str(payload.get("name") or "").strip()
    raw_registry = dict(payload.get("registry") or {})
    registry = {
        str(key): [TimelineStep.from_dict(item) for item in value if isinstance(item, dict)]
        for key, value in raw_registry.items()
        if isinstance(value, list)
    }
    value: Any = None
    if action == "save":
        steps = [TimelineStep.from_dict(item) for item in (payload.get("steps") or []) if isinstance(item, dict)]
        value = {
            "registry": {
                key: [step.to_dict() for step in steps_list]
                for key, steps_list in save_named_timeline(registry, name, steps).items()
            },
            "active_timeline_name": name,
        }
    elif action == "delete":
        value = {
            "registry": {
                key: [step.to_dict() for step in steps_list]
                for key, steps_list in delete_named_timeline(registry, name).items()
            },
            "active_timeline_name": str(payload.get("active_timeline_name") or ""),
        }
    else:
        value = {
            "steps": [step.to_dict() for step in load_named_timeline(registry, name)],
            "active_timeline_name": name,
        }
    output_packet = {
        "packet_type": "workflow.timeline_response.v1",
        "packet_version": "workflow.timeline_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(action, output_packet), "issues": [], "meta": {}}


def receipts(action: str, output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    payload = output_packet.get("payload") or {}
    return [{
        "receipt_id": f"named-timeline-{action}",
        "brick_id": CONCEPT["id"],
        "kind": "state",
        "label": f"Named timeline registry action: {action}.",
        "refs": [],
        "data": {"active_timeline_name": payload.get("active_timeline_name", "")},
    }]
