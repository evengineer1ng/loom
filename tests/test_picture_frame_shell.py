from ribbon_os_shell import RadioShell


class _PF:
    def __init__(self):
        self.calls = []

    def assign(self, station_id, frame_id):
        self.calls.append((station_id, frame_id))


def test_set_station_frame_refreshes_cards_and_galaxy():
    shell = RadioShell.__new__(RadioShell)
    pf = _PF()
    called = {"cards": 0, "galaxy": 0}

    shell._picture_frame_brick = lambda: pf
    shell._render_cards = lambda: called.__setitem__("cards", called["cards"] + 1)
    shell._attach_galaxy_thumbs = lambda: called.__setitem__("galaxy", called["galaxy"] + 1)

    shell._set_station_frame("kernel", "gold")

    assert pf.calls == [("kernel", "gold")]
    assert called["cards"] == 1
    assert called["galaxy"] == 1
