from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.narration.deterministic_narration_packet_builder",
    "kind": "renderer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.narration_request.v1"],
    "outputs": ["runtime.narration_response.v1"],
    "requires": [],
    "provides": ["runtime.deterministic_narration_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "narration", "deterministic"],
    "description": "Build a deterministic narration packet from a candidate, a source lens, and an optional transition line.",
}


def build_deterministic_narration_packet(candidate: dict[str, Any] | None, source_lens: str | None, transition_line: str | None = None) -> dict[str, Any]:
    cand = dict(candidate or {})
    title = str(cand.get("title") or "").strip()
    body = str(cand.get("body") or "").strip()
    lens = str(source_lens or "an update").strip()
    intro = f"Here's {lens}: {title}." if title else f"Here's {lens}."
    if transition_line:
        intro = f"{transition_line} {intro}"
    summary = body
    if len(summary) > 400:
        cut = summary[:400]
        summary = cut[: cut.rfind('. ') + 1] if '. ' in cut else cut + "..."
    return {
        "host_intro": intro,
        "summary": summary,
        "panel": [],
        "host_takeaway": "",
        "source": cand.get("source"),
        "type": cand.get("type"),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_deterministic_narration_packet(
        candidate=dict(payload.get("candidate") or {}),
        source_lens=payload.get("source_lens"),
        transition_line=payload.get("transition_line"),
    )
    output_packet = {
        "packet_type": "runtime.narration_response.v1",
        "packet_version": "runtime.narration_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "deterministic-narration-packet",
        "brick_id": CONCEPT["id"],
        "kind": "render",
        "label": "Built deterministic narration packet.",
        "refs": [],
        "data": {"has_summary": bool(value.get("summary"))},
    }]
