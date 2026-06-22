from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.family_batch_sampler_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧬",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.family_batch_sampler_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "training", "family", "sampler"],
    "description": "Package family-aware batch-sampler policy with batch size, reserved family slots, drop-last mode, and eligible family counts.",
}


def build_family_batch_sampler_packet(
    batch_size: int,
    family_slots: int,
    drop_last: bool,
    family_count: int,
    labelled_window_count: int,
) -> dict[str, Any]:
    return {
        "batch_size": int(batch_size),
        "family_slots": int(family_slots),
        "drop_last": bool(drop_last),
        "family_count": int(family_count),
        "labelled_window_count": int(labelled_window_count),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_family_batch_sampler_packet(
        batch_size=int(payload.get("batch_size") or 0),
        family_slots=int(payload.get("family_slots") or 0),
        drop_last=bool(payload.get("drop_last")),
        family_count=int(payload.get("family_count") or 0),
        labelled_window_count=int(payload.get("labelled_window_count") or 0),
    )
    output_packet = {
        "packet_type": "runtime.binding_response.v1",
        "packet_version": "runtime.binding_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "family-batch-sampler-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built family-batch sampler packet.",
        "refs": [],
        "data": {
            "batch_size": value.get("batch_size", 0),
            "family_slots": value.get("family_slots", 0),
            "family_count": value.get("family_count", 0),
        },
    }]
