from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.sessions.observation_snapshot",
    "kind": "record",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.session_request.v1"],
    "outputs": ["runtime.session_response.v1"],
    "requires": [],
    "provides": ["runtime.observation_snapshot_from_dict", "runtime.observation_snapshot_to_dict"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "session", "observation", "ocr"],
    "description": "Represent a captured observation with bounds, artifact path, and cleaned OCR lines.",
}


@dataclass
class ObservationSnapshot:
    timestamp: str
    window_title: str
    artifact_path: str
    bounds: dict[str, int]
    ocr: list[dict[str, Any]] = field(default_factory=list)

    @property
    def ocr_lines(self) -> list[str]:
        return [str(item.get("text", "")).strip() for item in self.ocr if str(item.get("text", "")).strip()]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["ocr_lines"] = self.ocr_lines
        return data

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "ObservationSnapshot":
        bounds = {str(key): int(value) for key, value in dict(data.get("bounds") or {}).items()}
        return ObservationSnapshot(
            timestamp=str(data.get("timestamp", "")).strip(),
            window_title=str(data.get("window_title", "")).strip(),
            artifact_path=str(data.get("artifact_path", "")).strip(),
            bounds=bounds,
            ocr=[dict(item) for item in (data.get("ocr") or []) if isinstance(item, dict)],
        )


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    snapshot = ObservationSnapshot.from_dict(dict(input_packet.get("payload") or {}))
    output_packet = {
        "packet_type": "runtime.session_response.v1",
        "packet_version": "runtime.session_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": snapshot.to_dict(),
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    payload = output_packet.get("payload") or {}
    return [{
        "receipt_id": "observation-snapshot-normalized",
        "brick_id": CONCEPT["id"],
        "kind": "record",
        "label": "Normalized observation snapshot.",
        "refs": [],
        "data": {"ocr_lines": len(payload.get("ocr_lines") or []), "has_artifact": bool(payload.get("artifact_path"))},
    }]
