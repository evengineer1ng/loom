from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.sessions.professor_advice_contract",
    "kind": "record",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.session_request.v1"],
    "outputs": ["runtime.session_response.v1"],
    "requires": [],
    "provides": ["runtime.professor_advice_from_dict", "runtime.professor_advice_to_dict"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "session", "advice", "overlay"],
    "description": "Represent a compact advisory artifact with observations, suggested inputs, and user-facing question state.",
}


@dataclass
class ProfessorAdvice:
    persona_line: str
    summary: str
    guidance: str
    key_observations: list[str] = field(default_factory=list)
    suggested_inputs: list[str] = field(default_factory=list)
    question_for_user: str = ""

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "ProfessorAdvice":
        return ProfessorAdvice(
            persona_line=str(data.get("persona_line", "")).strip(),
            summary=str(data.get("summary", "")).strip(),
            guidance=str(data.get("guidance", "")).strip(),
            key_observations=[str(item).strip() for item in (data.get("key_observations") or []) if str(item).strip()],
            suggested_inputs=[str(item).strip() for item in (data.get("suggested_inputs") or []) if str(item).strip()],
            question_for_user=str(data.get("question_for_user", "")).strip(),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "persona_line": self.persona_line,
            "summary": self.summary,
            "guidance": self.guidance,
            "key_observations": list(self.key_observations),
            "suggested_inputs": list(self.suggested_inputs),
            "question_for_user": self.question_for_user,
        }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    advice = ProfessorAdvice.from_dict(dict(input_packet.get("payload") or {}))
    output_packet = {
        "packet_type": "runtime.session_response.v1",
        "packet_version": "runtime.session_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": advice.to_dict(),
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    payload = output_packet.get("payload") or {}
    return [{
        "receipt_id": "professor-advice-normalized",
        "brick_id": CONCEPT["id"],
        "kind": "record",
        "label": "Normalized professor-style advisory artifact.",
        "refs": [],
        "data": {
            "observations": len(payload.get("key_observations") or []),
            "suggested_inputs": len(payload.get("suggested_inputs") or []),
        },
    }]
