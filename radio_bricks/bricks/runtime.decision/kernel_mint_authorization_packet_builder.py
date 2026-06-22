from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.decision.kernel_mint_authorization_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "👑",
    "deterministic": True,
    "inputs": ["runtime.decision_request.v1"],
    "outputs": ["runtime.decision_response.v1"],
    "requires": [],
    "provides": ["runtime.kernel_mint_authorization_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "decision", "kernel", "mint", "authorization", "lineage"],
    "description": "Decide whether a requested mint may produce a kernel, based on whether the issuer descends from a kernel.",
}


def build_kernel_mint_authorization_packet(
    requested_kernel: bool,
    issuer_manifest: dict[str, Any] | None,
    requested_oradio_id: str,
) -> dict[str, Any]:
    manifest = dict(issuer_manifest or {})
    issuer_is_kernel = bool(manifest.get("kernel"))
    issuer_id = str(manifest.get("id") or manifest.get("oradio_id") or "")
    issuer_lineage = dict(manifest.get("kernel_lineage") or {})
    if requested_kernel:
        authorized = issuer_is_kernel
        if authorized:
            reason = "issuer is already a kernel, so kernel minting is allowed"
        else:
            reason = "only a kernel may mint another kernel"
    else:
        authorized = True
        reason = "non-kernel oradios may be minted without kernel ancestry"
    return {
        "requested_oradio_id": str(requested_oradio_id),
        "requested_kernel": bool(requested_kernel),
        "issuer_oradio_id": issuer_id,
        "issuer_is_kernel": issuer_is_kernel,
        "issuer_lineage": issuer_lineage,
        "authorized": authorized,
        "reason": reason,
        "required_lineage_fields": [
            "root_kernel_id",
            "parent_kernel_id",
            "issuer_oradio_id",
            "generation",
            "mint_scope",
        ],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_kernel_mint_authorization_packet(
        requested_kernel=bool(payload.get("requested_kernel")),
        issuer_manifest=dict(payload.get("issuer_manifest") or {}),
        requested_oradio_id=str(payload.get("requested_oradio_id") or ""),
    )
    output_packet = {
        "packet_type": "runtime.decision_response.v1",
        "packet_version": "runtime.decision_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "kernel-mint-authorization-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built kernel mint-authorization packet.",
        "refs": [],
        "data": {
            "requested_kernel": value.get("requested_kernel", False),
            "authorized": value.get("authorized", False),
        },
    }]
