from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.trace.oradio_open_result_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧭",
    "deterministic": True,
    "inputs": ["runtime.trace_request.v1"],
    "outputs": ["runtime.trace_response.v1"],
    "requires": [],
    "provides": ["runtime.oradio_open_result_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "trace", "open", "manifest", "withheld", "plugins"],
    "description": "Package the power-on result of opening an oradio, including readiness, manifest withholding, and plugin withholding.",
}


def build_oradio_open_result_packet(
    name: str,
    ok: bool,
    engine_built: bool,
    manifest: list[dict[str, Any]] | None,
    withheld: list[dict[str, Any]] | None,
    plugins: list[dict[str, Any]] | None,
    plugins_withheld: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    return {
        "name": str(name),
        "ok": bool(ok),
        "engine_built": bool(engine_built),
        "manifest": [dict(item) for item in (manifest or [])],
        "withheld": [dict(item) for item in (withheld or [])],
        "plugins": [dict(item) for item in (plugins or [])],
        "plugins_withheld": [dict(item) for item in (plugins_withheld or [])],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_oradio_open_result_packet(
        name=str(payload.get("name") or ""),
        ok=bool(payload.get("ok")),
        engine_built=bool(payload.get("engine_built")),
        manifest=list(payload.get("manifest") or []),
        withheld=list(payload.get("withheld") or []),
        plugins=list(payload.get("plugins") or []),
        plugins_withheld=list(payload.get("plugins_withheld") or []),
    )
    output_packet = {
        "packet_type": "runtime.trace_response.v1",
        "packet_version": "runtime.trace_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "oradio-open-result-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built oradio open result packet.",
        "refs": [],
        "data": {
            "name": value.get("name", ""),
            "ok": value.get("ok", False),
            "withheld_count": len(value.get("withheld", [])),
            "plugins_withheld_count": len(value.get("plugins_withheld", [])),
        },
    }]
