from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.signals.climate_temperature_signal",
    "kind": "calculator",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["math.series_request.v1"],
    "outputs": ["math.series_response.v1"],
    "requires": [],
    "provides": ["math.climate_temperature_signal"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "signals", "rolling", "climate"],
    "description": "Compute a rolling climate temperature as hot-gain share minus hot-loss share, clipped to [-1, 1].",
}


def climate_temperature_signal(fan_gain: list[float] | None, fan_loss: list[float] | None, gain_threshold: float, loss_threshold: float, window: int) -> list[float | None]:
    gains = list(fan_gain or [])
    losses = list(fan_loss or [])
    size = min(len(gains), len(losses))
    if size == 0 or window <= 0:
        return []
    values: list[float | None] = []
    for index in range(size):
        start = max(0, index - window + 1)
        gain_window = gains[start:index + 1]
        loss_window = losses[start:index + 1]
        if len(gain_window) < window or len(loss_window) < window:
            values.append(None)
            continue
        gain_hot = sum(1 for value in gain_window if float(value) > gain_threshold) / window
        loss_hot = sum(1 for value in loss_window if float(value) > loss_threshold) / window
        values.append(max(-1.0, min(1.0, gain_hot - loss_hot)))
    return values


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    series = climate_temperature_signal(
        fan_gain=[float(item) for item in (payload.get("fan_gain") or [])],
        fan_loss=[float(item) for item in (payload.get("fan_loss") or [])],
        gain_threshold=float(payload.get("gain_threshold") or 0.0),
        loss_threshold=float(payload.get("loss_threshold") or 0.0),
        window=int(payload.get("window") or 0),
    )
    output_packet = {
        "packet_type": "math.series_response.v1",
        "packet_version": "math.series_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"values": series},
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(series), "issues": [], "meta": {}}


def receipts(series: list[float | None]) -> list[dict[str, Any]]:
    populated = [value for value in series if value is not None]
    return [{
        "receipt_id": "climate-temperature-computed",
        "brick_id": CONCEPT["id"],
        "kind": "calculation",
        "label": "Computed climate temperature signal.",
        "refs": [],
        "data": {"points": len(populated), "min": min(populated) if populated else None, "max": max(populated) if populated else None},
    }]
