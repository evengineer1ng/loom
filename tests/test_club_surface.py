from pathlib import Path


def test_club_surface_has_graceful_offline_fallback():
    path = Path(r"C:\Users\evana\OneDrive\Documents\oracle-radio\html_bricks\bricks\club.surface\club.html")
    text = path.read_text(encoding="utf-8")
    assert "Offline Club preview" in text
    assert "backend unavailable" not in text
    assert "club.offline.requests" in text
    assert "Open the doors" in text
    assert "/api/launch-backend" in text
    assert "How would you like to open oradios here?" in text
    assert "How many bricks should we bring along?" in text
    assert "Anything heavier for the road?" in text
    assert "Machine readiness" in text
    assert "/api/readiness" in text
