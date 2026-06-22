"""Speed-of-light traversal (ribbon_os_shell): clicking a station 2+ jumps away plays EVERY
crossover clip along the real soulmate path, sped up on a gradient by path length, never skipping a
clip. Covers the pure path/speed helpers + the traversal sequencing (with a fake video surface)."""

from __future__ import annotations

import types

from ribbon_os_shell import RadioShell, SPEED_OF_LIGHT_MAX, SPEED_OF_LIGHT_GAIN


def _station(sid, soulmates):
    return types.SimpleNamespace(station_id=sid, soulmates=list(soulmates),
                                 soulmate=(soulmates[0] if soulmates else ""))


def _shell(stations):
    sh = RadioShell.__new__(RadioShell)
    sh.stations = stations
    return sh


def test_path_through_hub():
    sh = _shell([_station("kernel", []), _station("iracing", ["kernel"]),
                 _station("cyberpunk", ["kernel"])])
    # the real route, not a direct dissolve
    assert sh._loom_path("iracing", "cyberpunk") == ["iracing", "kernel", "cyberpunk"]
    assert sh._loom_path("iracing", "kernel") == ["iracing", "kernel"]
    assert sh._loom_path("iracing", "iracing") is None      # same node
    assert sh._loom_path("iracing", "ghost") is None        # not in graph


def test_path_shortest_in_chain():
    sh = _shell([_station("a", ["b"]), _station("b", ["a", "c"]), _station("c", ["b", "d"]),
                 _station("d", ["c", "e"]), _station("e", ["d"])])
    assert sh._loom_path("a", "e") == ["a", "b", "c", "d", "e"]


def test_speed_gradient_and_cap():
    sh = _shell([])
    assert sh._speed_of_light(1) == 1.0                       # single hop = native
    assert sh._speed_of_light(2) == 1.0 + SPEED_OF_LIGHT_GAIN
    assert sh._speed_of_light(3) == 1.0 + 2 * SPEED_OF_LIGHT_GAIN
    assert sh._speed_of_light(1000) == SPEED_OF_LIGHT_MAX     # never beyond the maximum
    # monotonic up to the cap
    seq = [sh._speed_of_light(n) for n in range(1, 12)]
    assert seq == sorted(seq)


class _FakeVideo:
    enabled = True

    def __init__(self):
        self.played = []        # (path, loop, fade_ms)
        self.speeds = []

    def set_speed(self, mult):
        self.speeds.append(mult)

    def play(self, path, loop=False, on_finished=None, fade_ms=0):
        self.played.append((path, loop, fade_ms))
        if on_finished is not None:
            on_finished()        # run the chain synchronously for the test
        return True


def _traversal_shell():
    sh = RadioShell.__new__(RadioShell)
    sh.stations = []
    sh._path_token = 0
    sh._current_oradio_id = "iracing"
    sh.ribbon_media_phase = "ORADIO_LOOP"
    sh.ribbon_video = _FakeVideo()
    return sh


def test_traverse_plays_every_leg_then_loop():
    sh = _traversal_shell()
    station = types.SimpleNamespace(station_id="cyberpunk")
    legs = [("iracing", "kernel", "c0.mp4"), ("kernel", "cyberpunk", "c1.mp4")]
    sh._path_token += 1
    sh._traverse_path(legs, station, "cyberpunk_loop.mp4")

    paths = [p for (p, _loop, _f) in sh.ribbon_video.played]
    assert paths == ["c0.mp4", "c1.mp4", "cyberpunk_loop.mp4"]  # every clip, in order, then the loop
    assert sh.ribbon_video.played[-1][1] is True               # final = looping
    assert sh._current_oradio_id == "cyberpunk"                # landed on target
    assert sh.ribbon_video.speeds[0] == sh._speed_of_light(2)  # sped up for the traversal
    assert sh.ribbon_video.speeds[-1] == 1.0                   # back to native on arrival


def test_missing_leg_clip_never_strands():
    sh = _traversal_shell()
    station = types.SimpleNamespace(station_id="cyberpunk")
    legs = [("iracing", "kernel", None), ("kernel", "cyberpunk", "c1.mp4")]  # first clip missing
    sh._path_token += 1
    sh._traverse_path(legs, station, "loop.mp4")
    paths = [p for (p, _loop, _f) in sh.ribbon_video.played]
    assert paths == ["c1.mp4", "loop.mp4"]            # skips only the absent clip, still arrives
    assert sh._current_oradio_id == "cyberpunk"


def test_stale_traversal_aborts_on_new_token():
    sh = _traversal_shell()
    station = types.SimpleNamespace(station_id="cyberpunk")
    legs = [("iracing", "kernel", "c0.mp4"), ("kernel", "cyberpunk", "c1.mp4")]
    # simulate a newer click landing between legs by bumping the token inside play
    real_play = sh.ribbon_video.play
    def play_then_supersede(path, loop=False, on_finished=None, fade_ms=0):
        sh._path_token += 1     # a fresh traversal started
        return real_play(path, loop=loop, on_finished=on_finished, fade_ms=fade_ms)
    sh.ribbon_video.play = play_then_supersede
    token = sh._path_token + 1
    sh._path_token = token
    sh._traverse_path(legs, station, "loop.mp4")
    # only the first leg plays; the chain aborts instead of fighting the newer one
    paths = [p for (p, _loop, _f) in sh.ribbon_video.played]
    assert paths == ["c0.mp4"]
