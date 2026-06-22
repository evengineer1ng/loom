from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "workflow.timeline.bot_config_state",
    "kind": "bridge",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["workflow.timeline_request.v1"],
    "outputs": ["workflow.timeline_response.v1"],
    "requires": [],
    "provides": ["workflow.bot_config_from_dict", "workflow.bot_config_to_dict"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["workflow", "timeline", "config"],
    "description": "Serialize and deserialize timeline bot configuration state.",
}


@dataclass
class StageCoord:
    x: int = 0
    y: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {"x": int(self.x), "y": int(self.y)}

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "StageCoord":
        return StageCoord(x=safe_int(data.get("x", 0)), y=safe_int(data.get("y", 0)))


@dataclass
class TimelineStep:
    type: str
    params: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.type, "params": self.params}

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "TimelineStep":
        return TimelineStep(type=str(data.get("type", "")).strip(), params=dict(data.get("params", {}) or {}))


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


DEFAULT_WINDOW_FILTER = "cleo"


@dataclass
class BotConfig:
    window_title: str = ""
    window_filter: str = DEFAULT_WINDOW_FILTER
    use_ocr: bool = True
    ocr_langs: tuple[str, ...] = ("en",)
    ocr_gpu: bool = False
    ocr_conf_threshold: float = 0.5
    click_move_duration: float = 0.05
    after_activate_sleep: float = 0.30
    after_type_symbol_sleep: float = 0.30
    after_click_side_sleep: float = 0.20
    after_type_qty_sleep: float = 0.20
    coords: dict[str, StageCoord] = field(default_factory=lambda: {
        "symbol_input": StageCoord(100, 50),
        "buy_button": StageCoord(200, 300),
        "sell_button": StageCoord(300, 300),
        "qty_input": StageCoord(150, 400),
        "confirm": StageCoord(250, 500),
    })
    timeline: list[TimelineStep] = field(default_factory=list)
    timelines: dict[str, list[TimelineStep]] = field(default_factory=dict)
    active_timeline_name: str = "default"

    def to_dict(self) -> dict[str, Any]:
        return {
            "window_title": self.window_title,
            "window_filter": self.window_filter,
            "use_ocr": bool(self.use_ocr),
            "ocr_langs": list(self.ocr_langs),
            "ocr_gpu": bool(self.ocr_gpu),
            "ocr_conf_threshold": float(self.ocr_conf_threshold),
            "click_move_duration": float(self.click_move_duration),
            "after_activate_sleep": float(self.after_activate_sleep),
            "after_type_symbol_sleep": float(self.after_type_symbol_sleep),
            "after_click_side_sleep": float(self.after_click_side_sleep),
            "after_type_qty_sleep": float(self.after_type_qty_sleep),
            "coords": {k: v.to_dict() for k, v in self.coords.items()},
            "timeline": [s.to_dict() for s in self.timeline],
            "timelines": {name: [s.to_dict() for s in steps] for name, steps in self.timelines.items()},
            "active_timeline_name": self.active_timeline_name,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "BotConfig":
        cfg = BotConfig()
        cfg.window_title = str(data.get("window_title", cfg.window_title) or "")
        cfg.window_filter = str(data.get("window_filter", cfg.window_filter) or DEFAULT_WINDOW_FILTER)
        cfg.use_ocr = bool(data.get("use_ocr", cfg.use_ocr))
        cfg.ocr_langs = tuple(data.get("ocr_langs", list(cfg.ocr_langs)) or list(cfg.ocr_langs))
        cfg.ocr_gpu = bool(data.get("ocr_gpu", cfg.ocr_gpu))
        cfg.ocr_conf_threshold = safe_float(data.get("ocr_conf_threshold", cfg.ocr_conf_threshold), cfg.ocr_conf_threshold)
        cfg.click_move_duration = safe_float(data.get("click_move_duration", cfg.click_move_duration), cfg.click_move_duration)
        cfg.after_activate_sleep = safe_float(data.get("after_activate_sleep", cfg.after_activate_sleep), cfg.after_activate_sleep)
        cfg.after_type_symbol_sleep = safe_float(data.get("after_type_symbol_sleep", cfg.after_type_symbol_sleep), cfg.after_type_symbol_sleep)
        cfg.after_click_side_sleep = safe_float(data.get("after_click_side_sleep", cfg.after_click_side_sleep), cfg.after_click_side_sleep)
        cfg.after_type_qty_sleep = safe_float(data.get("after_type_qty_sleep", cfg.after_type_qty_sleep), cfg.after_type_qty_sleep)
        coords_in = data.get("coords", {}) or {}
        for key in list(cfg.coords.keys()):
            if key in coords_in and isinstance(coords_in[key], dict):
                cfg.coords[key] = StageCoord.from_dict(coords_in[key])
        tl_in = data.get("timeline", None)
        if isinstance(tl_in, list) and tl_in:
            cfg.timeline = [TimelineStep.from_dict(x) for x in tl_in if isinstance(x, dict)]
        cfg.timelines = {}
        tls = data.get("timelines", {}) or {}
        if isinstance(tls, dict):
            for name, steps in tls.items():
                if isinstance(steps, list):
                    cfg.timelines[name] = [TimelineStep.from_dict(x) for x in steps if isinstance(x, dict)]
        cfg.active_timeline_name = str(data.get("active_timeline_name", "default") or "default")
        return cfg


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = input_packet.get("payload", {})
    cfg = BotConfig.from_dict(dict(payload.get("value") or {}))
    output_packet = {
        "packet_type": "workflow.timeline_response.v1",
        "packet_version": "workflow.timeline_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"value": cfg.to_dict()},
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    value = output_packet["payload"]["value"]
    return [{
        "receipt_id": "bot-config-serialized",
        "brick_id": CONCEPT["id"],
        "kind": "conversion",
        "label": "Serialized bot config state.",
        "refs": [],
        "data": {"timeline_steps": len(value.get("timeline") or []), "saved_timelines": len(value.get("timelines") or {})},
    }]
