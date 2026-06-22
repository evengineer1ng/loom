from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.decision.decision_resolution_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.decision_request.v1"],
    "outputs": ["runtime.decision_response.v1"],
    "requires": [],
    "provides": ["runtime.decision_resolution_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "decision", "history", "packet"],
    "description": "Package a resolved multi-option decision into history-ready and event-ready forms.",
}


def build_decision_resolution_packet(
    tick: int,
    season: int,
    game_day: int,
    category: str,
    prompt: str,
    options: list[dict[str, Any]] | None,
    chosen_option_id: str,
    control_mode: str,
) -> dict[str, Any]:
    option_list = [dict(option) for option in (options or [])]
    chosen = next((option for option in option_list if str(option.get("id") or "") == str(chosen_option_id)), {})
    decision_id = f"decision_{int(tick)}_{category}"
    resolved_by = "player" if str(control_mode) == "human" else "delegate"
    return {
        "decision_history_record": {
            "decision_id": decision_id,
            "tick": int(tick),
            "season": int(season),
            "game_day": int(game_day),
            "category": category,
            "decision_text": prompt,
            "options": option_list,
            "chosen_option_id": str(chosen_option_id),
            "chosen_option_label": str(chosen.get("label") or ""),
            "immediate_cost": float(chosen.get("cost") or 0.0),
            "resolved_by": resolved_by,
        },
        "resolution_event": {
            "event_type": "outcome",
            "category": f"decision_resolved_{category}",
            "priority": 85.0,
            "severity": "major",
            "data": {
                "decision_id": decision_id,
                "category": category,
                "chosen_option": str(chosen.get("label") or ""),
                "cost": float(chosen.get("cost") or 0.0),
                "message": f"Decision made: {str(chosen.get('label') or '')}",
            },
        },
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_decision_resolution_packet(
        tick=int(payload.get("tick") or 0),
        season=int(payload.get("season") or 0),
        game_day=int(payload.get("game_day") or 0),
        category=str(payload.get("category") or ""),
        prompt=str(payload.get("prompt") or ""),
        options=list(payload.get("options") or []),
        chosen_option_id=str(payload.get("chosen_option_id") or ""),
        control_mode=str(payload.get("control_mode") or "human"),
    )
    output_packet = {
        "packet_type": "runtime.decision_response.v1",
        "packet_version": "runtime.decision_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    record = dict(value.get("decision_history_record") or {})
    return [{
        "receipt_id": "decision-resolution-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built decision resolution packet.",
        "refs": [],
        "data": {"decision_id": record.get("decision_id", ""), "resolved_by": record.get("resolved_by", "")},
    }]
