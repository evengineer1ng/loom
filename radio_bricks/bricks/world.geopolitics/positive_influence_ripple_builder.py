from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "world.geopolitics.positive_influence_ripple_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🌤️",
    "deterministic": True,
    "inputs": ["world.geopolitics_request.v1"],
    "outputs": ["world.geopolitics_response.v1"],
    "requires": [],
    "provides": ["world.positive_influence_ripple_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["world", "geopolitics", "influence", "ripple", "era"],
    "description": "Package a positive-era influence ripple from a Deep Field civ to same-region neighbours.",
}


def build_positive_influence_ripple(
    source_civ_id: str,
    source_era_flag: str,
    geographic_region: int,
    radiating_eras: list[str] | None,
    stability_delta: float,
    alignment_delta: float,
) -> dict[str, Any]:
    return {
        "source_civ_id": source_civ_id,
        "source_era_flag": source_era_flag,
        "geographic_region": int(geographic_region),
        "radiating_eras": list(radiating_eras or []),
        "stability_delta": float(stability_delta),
        "alignment_delta": float(alignment_delta),
        "is_radiating": source_era_flag in set(radiating_eras or []),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_positive_influence_ripple(
        source_civ_id=str(payload.get("source_civ_id") or ""),
        source_era_flag=str(payload.get("source_era_flag") or ""),
        geographic_region=int(payload.get("geographic_region") or 0),
        radiating_eras=list(payload.get("radiating_eras") or []),
        stability_delta=float(payload.get("stability_delta") or 0.0),
        alignment_delta=float(payload.get("alignment_delta") or 0.0),
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
        "receipt_id": "positive-influence-ripple",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built positive-influence ripple packet.",
        "refs": [],
        "data": {"source_civ_id": value.get("source_civ_id", ""), "is_radiating": value.get("is_radiating", False)},
    }]
