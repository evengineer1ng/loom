from bookmark.brick_kernel import Brick
from bookmark.canvas import _placement_payload, _validate_placement
from bookmark.draft import PlacedBrick


class _Module:
    @staticmethod
    def validate(input_packet, context=None):
        payload = (input_packet or {}).get("payload", {})
        issues = []
        if not payload.get("target"):
            issues.append({"code": "missing_target", "message": "payload.target is required"})
        return issues


def test_placement_payload_merges_params_into_payload():
    brick = Brick(
        id="ui.shortcut.launch_shortcut",
        path=__file__,
        inputs=("ui.shortcut_request.v1",),
        outputs=("ui.shortcut_launched.v1",),
        concept={"params": [{"name": "target", "type": "string"}, {"name": "launch", "type": "string"}]},
        module=_Module(),
        available=True,
    )
    placed = PlacedBrick(
        instance_id="ui.shortcut.launch_shortcut#0",
        brick=brick,
        config={"target": "steam://rungameid/440"},
        payload={"cwd": "C:/Games"},
    )

    payload = _placement_payload(placed)
    assert payload["target"] == "steam://rungameid/440"
    assert payload["cwd"] == "C:/Games"


def test_validate_placement_uses_effective_payload():
    brick = Brick(
        id="ui.shortcut.launch_shortcut",
        path=__file__,
        inputs=("ui.shortcut_request.v1",),
        outputs=("ui.shortcut_launched.v1",),
        concept={"params": [{"name": "target", "type": "string"}]},
        module=_Module(),
        available=True,
    )
    placed = PlacedBrick(
        instance_id="ui.shortcut.launch_shortcut#0",
        brick=brick,
        config={},
        payload={},
    )

    issues = _validate_placement(placed)
    assert issues and issues[0]["code"] == "missing_target"

    placed.config["target"] = "steam://rungameid/440"
    assert _validate_placement(placed) == []


def test_blank_param_does_not_erase_payload_value():
    brick = Brick(
        id="ui.shortcut.launch_shortcut",
        path=__file__,
        inputs=("ui.shortcut_request.v1",),
        outputs=("ui.shortcut_launched.v1",),
        concept={"params": [{"name": "target", "type": "string"}]},
        module=_Module(),
        available=True,
    )
    placed = PlacedBrick(
        instance_id="ui.shortcut.launch_shortcut#0",
        brick=brick,
        config={"target": ""},
        payload={"target": r"C:\Games\iRacing UI.lnk"},
    )

    payload = _placement_payload(placed)
    assert payload["target"] == r"C:\Games\iRacing UI.lnk"
    assert _validate_placement(placed) == []
