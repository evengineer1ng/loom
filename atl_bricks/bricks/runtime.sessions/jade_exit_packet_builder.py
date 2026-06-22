from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.sessions.jade_exit_packet_builder",
    "kind": "renderer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.session_request.v1"],
    "outputs": ["runtime.session_response.v1"],
    "requires": [],
    "provides": ["runtime.jade_exit_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "session", "jade", "exit"],
    "description": "Build Jade exit packets around regime shifts, correlation breakdowns, breadth extremes, and divergence exits.",
}


def build_jade_exit_packet(exit_tag: str | None, signals: dict[str, Any] | None = None, regime: str | None = None, corr_regime: str | None = None, breadth_regime: str | None = None, divergence_state: str | None = None) -> dict[str, Any]:
    flags = dict(signals or {})
    return {
        "exit_tag": exit_tag or "",
        "regime": regime,
        "corr_regime": corr_regime,
        "breadth_regime": breadth_regime,
        "divergence_state": divergence_state,
        "regime_exit": bool(flags.get("regime_shift_long", False) or flags.get("regime_shift_short", False)),
        "corr_breakdown_exit": bool(flags.get("corr_breakdown", False)),
        "breadth_exit": bool(flags.get("breadth_collapse_long", False) or flags.get("breadth_extreme_short", False)),
        "divergence_exit": bool(flags.get("divergence_revert_long", False) or flags.get("divergence_revert_short", False)),
        "rsi_extreme_exit": bool(flags.get("rsi_extreme_long", False) or flags.get("rsi_extreme_short", False)),
        "signals": flags,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_jade_exit_packet(
        exit_tag=payload.get("exit_tag"),
        signals=dict(payload.get("signals") or {}),
        regime=payload.get("regime"),
        corr_regime=payload.get("corr_regime"),
        breadth_regime=payload.get("breadth_regime"),
        divergence_state=payload.get("divergence_state"),
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
        "receipt_id": "jade-exit-packet",
        "brick_id": CONCEPT["id"],
        "kind": "report",
        "label": "Built Jade exit packet.",
        "refs": [],
        "data": {"exit_tag": value.get("exit_tag", ""), "regime_exit": value.get("regime_exit", False)},
    }]
