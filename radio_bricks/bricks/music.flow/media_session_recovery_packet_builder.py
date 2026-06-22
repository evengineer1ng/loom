from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "music.flow.media_session_recovery_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🔄",
    "deterministic": True,
    "inputs": ["music.flow_request.v1"],
    "outputs": ["music.flow_response.v1"],
    "requires": [],
    "provides": ["music.media_session_recovery_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["music", "flow", "session", "recovery", "backend"],
    "description": "Package media-session recovery with current-session fallback ranking, handler rebinding, and full refresh after session swap.",
}


def build_media_session_recovery_packet(
    backend: str,
    had_active_session: bool,
    recovered_session: bool,
    selected_source_app: str,
    candidate_sessions: list[dict[str, Any]] | None,
    rebound_handlers: list[str] | None,
) -> dict[str, Any]:
    return {
        "backend": str(backend),
        "had_active_session": bool(had_active_session),
        "recovered_session": bool(recovered_session),
        "selected_source_app": str(selected_source_app),
        "candidate_sessions": [dict(item) for item in (candidate_sessions or [])],
        "rebound_handlers": [str(item) for item in (rebound_handlers or [])],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_media_session_recovery_packet(
        backend=str(payload.get("backend") or ""),
        had_active_session=bool(payload.get("had_active_session")),
        recovered_session=bool(payload.get("recovered_session")),
        selected_source_app=str(payload.get("selected_source_app") or ""),
        candidate_sessions=list(payload.get("candidate_sessions") or []),
        rebound_handlers=list(payload.get("rebound_handlers") or []),
    )
    output_packet = {
        "packet_type": "music.flow_response.v1",
        "packet_version": "music.flow_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "media-session-recovery-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built media-session recovery packet.",
        "refs": [],
        "data": {
            "backend": value.get("backend", ""),
            "recovered_session": value.get("recovered_session", False),
            "candidate_count": len(value.get("candidate_sessions", [])),
        },
    }]
