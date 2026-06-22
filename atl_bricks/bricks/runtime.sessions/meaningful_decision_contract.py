from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.sessions.meaningful_decision_contract",
    "kind": "record",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.session_request.v1"],
    "outputs": ["runtime.session_response.v1"],
    "requires": [],
    "provides": ["runtime.meaningful_decision_from_dict", "runtime.meaningful_decision_to_dict"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "session", "decision", "actions"],
    "description": "Represent a non-filler decision artifact with explicit actions and optional user-input gate.",
}


@dataclass
class ActionStep:
    kind: str
    params: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "ActionStep":
        return ActionStep(kind=str(data.get("kind", "")).strip(), params=dict(data.get("params", {}) or {}))

    def to_dict(self) -> dict[str, Any]:
        return {"kind": self.kind, "params": dict(self.params)}


@dataclass
class MeaningfulDecision:
    persona_line: str
    summary: str
    reasoning: str
    actions: list[ActionStep] = field(default_factory=list)
    requires_user_input: bool = False
    question_for_user: str = ""

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "MeaningfulDecision":
        actions: list[ActionStep] = []
        for item in (data.get("actions") or []):
            if not isinstance(item, dict):
                continue
            if "kind" in item and "params" in item:
                actions.append(ActionStep.from_dict(item))
                continue
            params = {key: value for key, value in item.items() if key != "kind"}
            actions.append(ActionStep(kind=str(item.get("kind", "")).strip(), params=params))
        return MeaningfulDecision(
            persona_line=str(data.get("persona_line", "")).strip(),
            summary=str(data.get("summary", "")).strip(),
            reasoning=str(data.get("reasoning", "")).strip(),
            actions=actions,
            requires_user_input=bool(data.get("requires_user_input", False)),
            question_for_user=str(data.get("question_for_user", "")).strip(),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "persona_line": self.persona_line,
            "summary": self.summary,
            "reasoning": self.reasoning,
            "requires_user_input": self.requires_user_input,
            "question_for_user": self.question_for_user,
            "actions": [action.to_dict() for action in self.actions],
        }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    decision = MeaningfulDecision.from_dict(dict(input_packet.get("payload") or {}))
    output_packet = {
        "packet_type": "runtime.session_response.v1",
        "packet_version": "runtime.session_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": decision.to_dict(),
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    payload = output_packet.get("payload") or {}
    return [{
        "receipt_id": "meaningful-decision-normalized",
        "brick_id": CONCEPT["id"],
        "kind": "record",
        "label": "Normalized meaningful decision artifact.",
        "refs": [],
        "data": {"actions": len(payload.get("actions") or []), "requires_user_input": bool(payload.get("requires_user_input"))},
    }]
