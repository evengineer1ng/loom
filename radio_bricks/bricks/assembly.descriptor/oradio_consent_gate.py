from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "assembly.descriptor.oradio_consent_gate",
    "kind": "assembler",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["assembly.descriptor_request.v1"],
    "outputs": ["assembly.descriptor_response.v1"],
    "requires": [],
    "provides": ["assembly.oradio_consent_gate"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["assembly", "descriptor", "consent", "club"],
    "description": "Filter sensitive telemetry and dependent bindings from an .oradio open request according to consent state.",
}


def apply_oradio_consent_gate(telemetry: list[dict[str, Any]] | None, bindings: list[dict[str, Any]] | None, manifest: list[dict[str, Any]] | None, allow_sensitive: bool) -> dict[str, Any]:
    telemetry_rows = [dict(row) for row in (telemetry or [])]
    binding_rows = [dict(row) for row in (bindings or [])]
    requests = [dict(row) for row in (manifest or [])]
    allowed_names = set()
    withheld = []
    for req in requests:
        sensitive = bool(req.get("sensitive", False))
        consented = bool(req.get("consented", False))
        if not sensitive or consented or bool(allow_sensitive):
            allowed_names.add(str(req.get("name") or ""))
        else:
            withheld.append(req)
    dropped = {str(req.get("name") or "") for req in withheld}
    filtered_telemetry = [row for row in telemetry_rows if str(row.get("name") or "") in allowed_names or str(row.get("name") or "") not in dropped]
    filtered_bindings = [row for row in binding_rows if str(row.get("source") or "") not in dropped]
    return {
        "telemetry": filtered_telemetry,
        "bindings": filtered_bindings,
        "withheld": withheld,
        "dropped_sources": sorted(dropped),
        "degraded": bool(withheld),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = apply_oradio_consent_gate(
        telemetry=list(payload.get("telemetry") or []),
        bindings=list(payload.get("bindings") or []),
        manifest=list(payload.get("manifest") or []),
        allow_sensitive=bool(payload.get("allow_sensitive", False)),
    )
    output_packet = {
        "packet_type": "assembly.descriptor_response.v1",
        "packet_version": "assembly.descriptor_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "oradio-consent-gate",
        "brick_id": CONCEPT["id"],
        "kind": "assembly",
        "label": "Applied .oradio consent gate.",
        "refs": [],
        "data": {"withheld": len(value.get("withheld", [])), "degraded": value.get("degraded", False)},
    }]
