"""Bake a finished F1 race into a thin-wire event tape (JSON), using the deterministic
event-detector. FastF1 (heavy) lives ONLY here — run once; the engine then replays the JSON
through the generic `tape_replay` source with no FastF1 at runtime. Tape philosophy, literal.

    python -m tools.bake_f1 --round 7 --out data/f1_barcelona_2026.json

Prints a non-spoiler summary only (counts + event types), never positions or the result.
"""
from __future__ import annotations

import argparse
import json
import os
import warnings
from collections import Counter


def _row(text: str, priority: float, tags: list) -> dict:
    return {"title": text, "body": text, "type": "f1", "priority": priority, "tags": tags}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, default=2026)
    ap.add_argument("--round", type=int, required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    warnings.filterwarnings("ignore")
    import fastf1
    from oradio_engine.detect import overtakes, running_extrema

    os.makedirs("data/f1_cache", exist_ok=True)
    fastf1.Cache.enable_cache("data/f1_cache")
    session = fastf1.get_session(args.year, args.round, "R")
    session.load(laps=True, telemetry=False, weather=False, messages=False)
    laps = session.laps

    # abbreviation/number -> last name, for readable narration
    names: dict = {}
    try:
        for _, r in session.results.iterrows():
            names[str(r.get("Abbreviation"))] = r.get("LastName") or r.get("Abbreviation")
            names[str(r.get("DriverNumber"))] = r.get("LastName") or r.get("Abbreviation")
    except Exception:
        pass

    def nm(code) -> str:
        return str(names.get(str(code), code))

    max_lap = int(laps["LapNumber"].max())

    # per-lap position frames -> overtakes (relational events)
    frames = []
    for lap_no in range(1, max_lap + 1):
        lap_rows = laps[laps["LapNumber"] == lap_no]
        frame = {}
        for _, row in lap_rows.iterrows():
            pos = row["Position"]
            if pos == pos:  # not NaN
                frame[row["Driver"]] = int(pos)
        frames.append(frame)

    events = []  # (lap, priority, row)
    for step, gainer, loser in overtakes(frames):
        lap = step + 1
        events.append((lap, 0.7, _row(
            f"{nm(gainer)} passes {nm(loser)}", 0.7,
            ["f1", f"lap:{lap}", "actor:" + nm(gainer), "action:overtake", "object:" + nm(loser), "valence:hype"],
        )))

    # fastest laps, chronologically -> each new race-fastest
    valid = laps[laps["LapTime"].notna() & laps["Time"].notna()].sort_values("Time")
    samples = [{"t": row["LapTime"].total_seconds(), "drv": row["Driver"], "lap": int(row["LapNumber"])}
               for _, row in valid.iterrows()]
    for _, s in running_extrema(samples, "t", mode="min"):
        lap = s["lap"]
        events.append((lap, 0.85, _row(
            f"{nm(s['drv'])} sets the fastest lap", 0.85,
            ["f1", f"lap:{lap}", "actor:" + nm(s["drv"]), "action:clock", "object:fastest_lap", "definite:1", "valence:hype"],
        )))

    # pit stops
    for _, row in laps[laps["PitInTime"].notna()].iterrows():
        lap = int(row["LapNumber"])
        events.append((lap, 0.5, _row(
            f"{nm(row['Driver'])} pits", 0.5,
            ["f1", f"lap:{lap}", "actor:" + nm(row["Driver"]), "action:pit"],
        )))

    events.sort(key=lambda e: (e[0], -e[1]))
    rows = [e[2] for e in events]

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False)

    kinds = Counter(t.split(":", 1)[1] for r in rows for t in r["tags"] if t.startswith("action:"))
    print(f"baked {len(rows)} events -> {args.out}")
    print("event types:", dict(kinds))
    print("laps:", max_lap, "| drivers:", laps["Driver"].nunique())


if __name__ == "__main__":
    main()
