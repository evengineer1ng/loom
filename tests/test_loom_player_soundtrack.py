from loom_player_ui import soundtrack_decl, soundtrack_fade_sec, soundtrack_path


def test_soundtrack_helpers_degrade_cleanly_when_absent():
    descriptor = {"oradio": "silent"}
    assert soundtrack_decl(descriptor) == {}
    assert soundtrack_path(descriptor) == ""
    assert soundtrack_fade_sec(descriptor) == 1.25


def test_soundtrack_helpers_read_descriptor_values():
    descriptor = {
        "oradio": "scored",
        "soundtrack": {
            "path": "assets/score.mp3",
            "fade_sec": "2.75",
            "loop": True,
        },
    }
    assert soundtrack_decl(descriptor)["loop"] is True
    assert soundtrack_path(descriptor) == "assets/score.mp3"
    assert soundtrack_fade_sec(descriptor) == 2.75
