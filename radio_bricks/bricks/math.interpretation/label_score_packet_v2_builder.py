from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.interpretation.label_score_packet_v2_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🏷️",
    "deterministic": True,
    "inputs": ["math.interpretation_request.v1"],
    "outputs": ["math.interpretation_response.v1"],
    "requires": [],
    "provides": ["math.label_score_packet_v2"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "interpretation", "label", "score", "evidence"],
    "description": "Package a scored label with threshold, concept/variant lineage, source label, and feature evidence rather than only a scalar score.",
}


def build_label_score_packet_v2(
    label: str,
    score: float,
    distance: float,
    kind: str,
    threshold: float,
    concept_id: str,
    variant_id: str,
    source_label: str,
    feature_evidence: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    return {
        "label": str(label),
        "score": float(score),
        "distance": float(distance),
        "kind": str(kind),
        "threshold": float(threshold),
        "concept_id": str(concept_id),
        "variant_id": str(variant_id),
        "source_label": str(source_label),
        "feature_evidence": [dict(item) for item in (feature_evidence or [])],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_label_score_packet_v2(
        label=str(payload.get("label") or ""),
        score=float(payload.get("score") or 0.0),
        distance=float(payload.get("distance") or 0.0),
        kind=str(payload.get("kind") or ""),
        threshold=float(payload.get("threshold") or 0.0),
        concept_id=str(payload.get("concept_id") or ""),
        variant_id=str(payload.get("variant_id") or ""),
        source_label=str(payload.get("source_label") or ""),
        feature_evidence=list(payload.get("feature_evidence") or []),
    )
    output_packet = {
        "packet_type": "math.interpretation_response.v1",
        "packet_version": "math.interpretation_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "label-score-packet-v2",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built enriched label-score packet.",
        "refs": [],
        "data": {
            "label": value.get("label", ""),
            "kind": value.get("kind", ""),
            "evidence_count": len(value.get("feature_evidence", [])),
        },
    }]
