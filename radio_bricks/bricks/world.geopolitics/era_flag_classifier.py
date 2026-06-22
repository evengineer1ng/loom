from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "world.geopolitics.era_flag_classifier",
    "kind": "classifier",
    "version": "0.1.0",
    "emoji": "🏷️",
    "deterministic": True,
    "inputs": ["world.geopolitics_request.v1"],
    "outputs": ["world.geopolitics_response.v1"],
    "requires": [],
    "provides": ["world.era_flag_classification"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["world", "geopolitics", "era", "classifier", "deep_field"],
    "description": "Package a Deep Field era-flag decision with candidate confirmation and sustained-state metadata.",
}


def classify_era_flag(
    era_flag: str,
    era_candidate: str,
    era_candidate_ticks: int,
    momentum_sustained: int,
    stability_trend: float,
    wealth_growth_rate: float,
) -> dict[str, Any]:
    positive_eras = {"ASCENDANT", "GOLDEN_AGE", "RENAISSANCE", "TRADE_HEGEMONY", "REFORMATION_RISE"}
    crisis_eras = {"CIVIL_CRISIS", "FAMINE", "DECLINE", "MILITANT"}
    return {
        "era_flag": era_flag,
        "era_candidate": era_candidate,
        "era_candidate_ticks": int(era_candidate_ticks),
        "momentum_sustained": int(momentum_sustained),
        "stability_trend": float(stability_trend),
        "wealth_growth_rate": float(wealth_growth_rate),
        "era_family": "positive" if era_flag in positive_eras else "crisis" if era_flag in crisis_eras else "stable",
        "is_confirming_candidate": bool(era_candidate),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = classify_era_flag(
        era_flag=str(payload.get("era_flag") or ""),
        era_candidate=str(payload.get("era_candidate") or ""),
        era_candidate_ticks=int(payload.get("era_candidate_ticks") or 0),
        momentum_sustained=int(payload.get("momentum_sustained") or 0),
        stability_trend=float(payload.get("stability_trend") or 0.0),
        wealth_growth_rate=float(payload.get("wealth_growth_rate") or 0.0),
    )
    output_packet = {
        "packet_type": "world.geopolitics_response.v1",
        "packet_version": "world.geopolitics_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "era-flag-classification",
        "brick_id": CONCEPT["id"],
        "kind": "classify",
        "label": "Classified Deep Field era flag.",
        "refs": [],
        "data": {"era_flag": value.get("era_flag", ""), "era_family": value.get("era_family", "")},
    }]
