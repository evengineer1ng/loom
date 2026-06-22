from __future__ import annotations

from dataclasses import dataclass
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "workflow.timeline.window_binding_state",
    "kind": "bridge",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["workflow.timeline_request.v1"],
    "outputs": ["workflow.timeline_response.v1"],
    "requires": [],
    "provides": ["workflow.window_binding_apply", "workflow.window_binding_serialize"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["workflow", "window", "binding", "state"],
    "description": "Track the selected target window and a preview-locked copy of that selection as portable automation state.",
}


@dataclass
class WindowBindingState:
    window_title: str = ""
    locked_window_title: str = ""
    window_filter: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "window_title": self.window_title,
            "locked_window_title": self.locked_window_title,
            "window_filter": self.window_filter,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "WindowBindingState":
        return WindowBindingState(
            window_title=str(data.get("window_title", "") or "").strip(),
            locked_window_title=str(data.get("locked_window_title", "") or "").strip(),
            window_filter=str(data.get("window_filter", "") or "").strip(),
        )


def apply_window_selection(state: WindowBindingState, title: str, lock_preview: bool = True) -> WindowBindingState:
    selected = str(title or "").strip()
    return WindowBindingState(
        window_title=selected,
        locked_window_title=selected if lock_preview else state.locked_window_title,
        window_filter=state.window_filter,
    )


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    state = WindowBindingState.from_dict(dict(payload.get("state") or {}))
    next_state = apply_window_selection(
        state,
        title=str(payload.get("window_title") or state.window_title),
        lock_preview=bool(payload.get("lock_preview", True)),
    )
    output_packet = {
        "packet_type": "workflow.timeline_response.v1",
        "packet_version": "workflow.timeline_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": next_state.to_dict(),
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    payload = output_packet.get("payload") or {}
    return [{
        "receipt_id": "window-binding-updated",
        "brick_id": CONCEPT["id"],
        "kind": "state",
        "label": "Updated locked target-window binding state.",
        "refs": [],
        "data": {
            "window_title": payload.get("window_title", ""),
            "locked_window_title": payload.get("locked_window_title", ""),
        },
    }]
