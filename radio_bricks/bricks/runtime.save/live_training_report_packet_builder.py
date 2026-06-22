from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.save.live_training_report_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📋",
    "deterministic": True,
    "inputs": ["runtime.save_request.v1"],
    "outputs": ["runtime.save_response.v1"],
    "requires": [],
    "provides": ["runtime.live_training_report_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "save", "training", "report", "center"],
    "description": "Package a live floor-training report with profile identity, captured center, and recommendation count.",
}


def build_live_training_report_packet(
    profile: str,
    center_ls_x: float,
    center_ls_y: float,
    recommendation_count: int,
) -> dict[str, Any]:
    return {
        "profile": str(profile),
        "center_ls_x": float(center_ls_x),
        "center_ls_y": float(center_ls_y),
        "recommendation_count": int(recommendation_count),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_live_training_report_packet(
        profile=str(payload.get("profile") or ""),
        center_ls_x=float(payload.get("center_ls_x") or 0.0),
        center_ls_y=float(payload.get("center_ls_y") or 0.0),
        recommendation_count=int(payload.get("recommendation_count") or 0),
    )
    output_packet = {
        "packet_type": "runtime.save_response.v1",
        "packet_version": "runtime.save_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "live-training-report-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built live-training report packet.",
        "refs": [],
        "data": {
            "profile": value.get("profile", ""),
            "recommendation_count": value.get("recommendation_count", 0),
        },
    }]
