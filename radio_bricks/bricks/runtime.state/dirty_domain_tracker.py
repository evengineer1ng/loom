from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.state.dirty_domain_tracker",
    "kind": "builder",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.state_request.v1"],
    "outputs": ["runtime.state_response.v1"],
    "requires": [],
    "provides": ["runtime.dirty_domain_state"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "state", "dirty", "ui"],
    "description": "Track domain-level dirty flags for selective UI refresh or background sync.",
}


DOMAINS = [
    "contracts",
    "stats",
    "team",
    "finance",
    "development",
    "sponsors",
    "car",
    "manager_career",
    "audio_settings",
]


def build_dirty_domain_state(current: dict[str, Any] | None, mark_domain: str | None = None, clear: bool = False) -> dict[str, Any]:
    flags = {domain: bool(dict(current or {}).get(domain, False)) for domain in DOMAINS}
    if clear:
        flags = {domain: False for domain in DOMAINS}
    elif mark_domain == "all":
        flags = {domain: True for domain in DOMAINS}
    elif mark_domain in flags:
        flags[str(mark_domain)] = True
    return {"flags": flags, "is_dirty": any(flags.values())}


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_dirty_domain_state(
        current=dict(payload.get("current") or {}),
        mark_domain=payload.get("mark_domain"),
        clear=bool(payload.get("clear", False)),
    )
    output_packet = {
        "packet_type": "runtime.state_response.v1",
        "packet_version": "runtime.state_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "dirty-domain-state",
        "brick_id": CONCEPT["id"],
        "kind": "state",
        "label": "Built dirty-domain state.",
        "refs": [],
        "data": {"dirty_count": sum(1 for flag in dict(value.get('flags') or {}).values() if flag)},
    }]
