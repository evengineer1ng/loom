"""launch_shortcut — open an .oradio AS a launcher for an external target.

The realization (2026-06-21): if an oradio can carry a "shortcut" (a Steam game, an .exe, a .lnk,
a URL, a steam:// URI, any shell command) and RUN it on double-click, then RibbonOS becomes a
**visual museum / launcher**: host your entire Steam library as a wall of living loops, each tile a
game that boots when you open it.

This is wired through the oradio manifest's existing `open` field:

    "open": {"kind": "shortcut", "target": "steam://rungameid/440", "launch": "auto",
             "args": "", "cwd": ""}

The shell honors `open.kind == "shortcut"` by calling this brick's `launch()` instead of spawning
the oradio runtime. `launch` is the brick's job (the only place that knows how to resolve a target
across Steam URIs / files / URLs / shell commands and start it cross-platform).

Contract: loom.concept.v1 (in-file CONCEPT + inspect/validate/run/receipts), like the other
mined bricks. The single side effect is spawning the target process.
"""

from __future__ import annotations

import os
import re
import shlex
import subprocess
import sys
from typing import Any, Dict, List, Optional

CONCEPT: Dict[str, Any] = {
    "api_version": "loom.concept.v1",
    "id": "ui.shortcut.launch_shortcut",
    "kind": "launcher",
    "version": "0.1.0",
    "deterministic": False,            # it starts an external process
    "inputs": ["ui.shortcut_request.v1"],
    "outputs": ["ui.shortcut_launched.v1"],
    "requires": [],
    "provides": ["shortcut", "launcher", "open_with"],
    "side_effects": ["process_spawn"],
    "ui_slots": ["oradio.open"],
    "params": [
        {"name": "target", "label": "Target", "type": "string", "default": "",
         "hint": "steam://rungameid/<AppID>, a .exe/.lnk path, a URL, or a shell command"},
        {"name": "launch", "label": "Kind", "type": "enum",
         "options": ["auto", "steam", "file", "url", "shell"], "default": "auto"},
        {"name": "args", "label": "Arguments", "type": "string", "default": ""},
        {"name": "cwd", "label": "Working dir", "type": "string", "default": ""},
    ],
    "tags": ["ui", "launcher", "shortcut", "steam", "museum", "open_with"],
    "emoji": "🕹️",
    "description": "Open an oradio AS a launcher: run a Steam game / .exe / .lnk / URL / shell "
                   "command on double-click. Turns RibbonOS into a visual museum of your library.",
}

# scheme://  prefix (steam:// , http:// , https:// , com.epicgames.launcher:// , ...)
_SCHEME = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.\-]*://")
_FILE_SUFFIXES = (".lnk", ".exe", ".bat", ".cmd", ".com", ".msi", ".app", ".desktop", ".sh")


def steam_uri(app_id: str | int) -> str:
    """A Steam launch URI for an AppID. `steam://rungameid/<id>` boots the game directly."""
    return f"steam://rungameid/{str(app_id).strip()}"


def _expand(path: str) -> str:
    return os.path.expandvars(os.path.expanduser(path))


def resolve_kind(target: str) -> str:
    """Infer how to launch `target`: 'url' (http/https), 'uri' (steam:// & other schemes),
    'file' (existing path or known executable suffix), else 'shell'."""
    t = (target or "").strip().strip('"')
    if not t:
        return "shell"
    m = _SCHEME.match(t)
    if m:
        return "url" if m.group(0).lower() in ("http://", "https://") else "uri"
    if os.path.exists(_expand(t)) or t.lower().endswith(_FILE_SUFFIXES):
        return "file"
    return "shell"


def launch(target: str, *, kind: str = "auto", args: Any = None,
           cwd: Optional[str] = None) -> Dict[str, Any]:
    """Start `target`. `kind` in {auto, steam, file, url, shell}; 'steam' treats `target` as an
    AppID (or a full steam:// URI). Returns a small launch receipt. Cross-platform."""
    target = (target or "").strip().strip('"')
    if not target:
        raise ValueError("launch_shortcut: empty target")

    if kind == "steam":
        if not _SCHEME.match(target):
            target = steam_uri(target)
        kind = "uri"
    if kind in (None, "", "auto"):
        kind = resolve_kind(target)

    if isinstance(args, str):
        arglist: List[str] = shlex.split(args, posix=(os.name != "nt"))
    else:
        arglist = list(args or [])
    cwd = _expand(cwd) if cwd else None

    pid = None
    if kind in ("url", "uri"):
        # OS URI handlers (steam://, http://, custom launchers) — args don't apply.
        if os.name == "nt":
            os.startfile(target)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            pid = subprocess.Popen(["open", target]).pid
        else:
            pid = subprocess.Popen(["xdg-open", target]).pid
    elif kind == "file":
        p = _expand(target)
        if os.name == "nt":
            if arglist:
                pid = subprocess.Popen([p, *arglist], cwd=cwd, close_fds=True).pid
            else:
                os.startfile(p)  # type: ignore[attr-defined]  # respects .lnk / file association
        elif sys.platform == "darwin":
            extra = (["--args", *arglist] if arglist else [])
            pid = subprocess.Popen(["open", p, *extra], cwd=cwd).pid
        else:
            pid = subprocess.Popen([p, *arglist], cwd=cwd, close_fds=True).pid
    else:  # shell command
        parts = shlex.split(target, posix=(os.name != "nt")) + arglist
        pid = subprocess.Popen(parts, cwd=cwd, close_fds=True).pid

    return {"target": target, "kind": kind, "args": arglist, "cwd": cwd, "pid": pid}


# ---------------------------------------------------------------------------
# loom.concept.v1 contract
# ---------------------------------------------------------------------------

def inspect() -> Dict[str, Any]:
    return CONCEPT


def validate(input_packet: Dict[str, Any], context=None) -> List[Dict[str, str]]:
    issues: List[Dict[str, str]] = []
    payload = (input_packet or {}).get("payload", {})
    if not str(payload.get("target", "")).strip():
        issues.append({"code": "missing_target", "message": "payload.target is required"})
    k = payload.get("launch", "auto")
    if k not in ("auto", "steam", "file", "url", "shell"):
        issues.append({"code": "bad_kind", "message": f"unknown launch kind {k!r}"})
    return issues


def run(input_packet: Dict[str, Any], context=None) -> Dict[str, Any]:
    payload = (input_packet or {}).get("payload", {})
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": None, "receipts": [], "issues": issues, "meta": {}}
    info = launch(payload.get("target", ""), kind=payload.get("launch", "auto"),
                  args=payload.get("args"), cwd=payload.get("cwd"))
    output = {"packet_type": "ui.shortcut_launched.v1", "payload": info}
    return {"ok": True, "output_packet": output, "receipts": receipts(output),
            "issues": [], "meta": {}}


def receipts(output_packet: Dict[str, Any]) -> List[Dict[str, Any]]:
    p = (output_packet or {}).get("payload", {})
    return [{
        "receipt_id": f"shortcut:{p.get('target', '')}",
        "brick_id": CONCEPT["id"],
        "kind": "launch",
        "label": f"launched {p.get('kind', '?')}: {p.get('target', '')}",
        "refs": [],
        "data": {"pid": p.get("pid"), "kind": p.get("kind")},
    }]
