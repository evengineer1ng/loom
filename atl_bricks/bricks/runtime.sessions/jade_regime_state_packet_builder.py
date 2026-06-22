from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.sessions.jade_regime_state_packet_builder",
    "kind": "renderer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.session_request.v1"],
    "outputs": ["runtime.session_response.v1"],
    "requires": [],
    "provides": ["runtime.jade_regime_state_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "session", "jade", "regime", "state"],
    "description": "Build Jade regime-state packets spanning volatility, correlation, breadth, lead-lag, divergence, and cooldown state.",
}


def build_jade_regime_state_packet(vol_regime: str | None, corr_regime: str | None, breadth_regime: str | None, lead_lag_state: str | None, regime: str | None, divergence_state: str | None, cooldown_active: str | None, regime_bearish: bool, regime_long_only: bool) -> dict[str, Any]:
    return {
        "vol_regime": vol_regime,
        "corr_regime": corr_regime,
        "breadth_regime": breadth_regime,
        "lead_lag_state": lead_lag_state,
        "regime": regime,
        "divergence_state": divergence_state,
        "cooldown_active": cooldown_active,
        "regime_bearish": bool(regime_bearish),
        "regime_long_only": bool(regime_long_only),
        "state_vector": [
            vol_regime,
            corr_regime,
            breadth_regime,
            lead_lag_state,
            regime,
            divergence_state,
            cooldown_active,
        ],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_jade_regime_state_packet(
        vol_regime=payload.get("vol_regime"),
        corr_regime=payload.get("corr_regime"),
        breadth_regime=payload.get("breadth_regime"),
        lead_lag_state=payload.get("lead_lag_state"),
        regime=payload.get("regime"),
        divergence_state=payload.get("divergence_state"),
        cooldown_active=payload.get("cooldown_active"),
        regime_bearish=bool(payload.get("regime_bearish", False)),
        regime_long_only=bool(payload.get("regime_long_only", False)),
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
    return [{
        "receipt_id": "jade-regime-state-packet",
        "brick_id": CONCEPT["id"],
        "kind": "state",
        "label": "Built Jade regime-state packet.",
        "refs": [],
        "data": {"regime": value.get("regime"), "cooldown_active": value.get("cooldown_active")},
    }]
