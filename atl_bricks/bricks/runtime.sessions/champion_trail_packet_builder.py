from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.sessions.champion_trail_packet_builder",
    "kind": "renderer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.session_request.v1"],
    "outputs": ["runtime.session_response.v1"],
    "requires": [],
    "provides": ["runtime.champion_trail_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "session", "champion", "trail"],
    "description": "Build a champion-trail state packet from rank, ROI thresholds, velocity, and drawdown state.",
}


def build_champion_trail_packet(rank: int, dyn_roi: float, rung_target: float | None, current_profit: float, telemetry: dict[str, Any] | None, champ_trail_activate_base: float, champ_trail_activate_step: float, champ_allowed_drawdown_base: float, champ_allowed_drawdown_step: float, velocity_weight: float) -> dict[str, Any]:
    tel = dict(telemetry or {})
    champ_index = min(max(int(rank) - 4, 0), 5)
    boosted_roi = max(float(dyn_roi), float(dyn_roi) + 0.6 * (float(rung_target) - float(dyn_roi))) if rung_target is not None else float(dyn_roi)
    activate_at = float(champ_trail_activate_base) + champ_index * float(champ_trail_activate_step)
    allowed_dd = float(champ_allowed_drawdown_base) + champ_index * float(champ_allowed_drawdown_step)
    if float(tel.get("vel", 0.0) or 0.0) < 0.0:
        tighten = min(0.75, abs(float(tel.get("vel", 0.0) or 0.0)) * float(velocity_weight))
        allowed_dd *= (1.0 - tighten)
    peak = float(tel.get("max", current_profit) or current_profit)
    return {
        "rank": int(rank),
        "boosted_roi": boosted_roi,
        "activate_at": activate_at,
        "allowed_drawdown": allowed_dd,
        "peak_profit": peak,
        "current_profit": float(current_profit),
        "drawdown_from_peak": peak - float(current_profit),
        "champ_dynamic_roi_hit": float(current_profit) >= boosted_roi,
        "champ_trail_armed": float(current_profit) >= activate_at,
        "champ_trail_hit": float(current_profit) >= activate_at and (peak - float(current_profit)) >= allowed_dd,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_champion_trail_packet(
        rank=int(payload.get("rank") or 0),
        dyn_roi=float(payload.get("dyn_roi") or 0.0),
        rung_target=payload.get("rung_target"),
        current_profit=float(payload.get("current_profit") or 0.0),
        telemetry=dict(payload.get("telemetry") or {}),
        champ_trail_activate_base=float(payload.get("champ_trail_activate_base") or 0.0),
        champ_trail_activate_step=float(payload.get("champ_trail_activate_step") or 0.0),
        champ_allowed_drawdown_base=float(payload.get("champ_allowed_drawdown_base") or 0.0),
        champ_allowed_drawdown_step=float(payload.get("champ_allowed_drawdown_step") or 0.0),
        velocity_weight=float(payload.get("velocity_weight") or 0.0),
    )
    output_packet = {
        "packet_type": "runtime.session_response.v1",
        "packet_version": "runtime.session_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"receipt_id": "champion-trail-packet", "brick_id": CONCEPT["id"], "kind": "report", "label": "Built champion trail packet.", "refs": [], "data": {"rank": value.get("rank", 0), "armed": value.get("champ_trail_armed", False)}}]
