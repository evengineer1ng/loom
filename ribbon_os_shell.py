#!/usr/bin/env python3
from __future__ import annotations

# Radio OS Version
__version__ = "1.06"
RADIO_OS_VERSION = "1.06"
RADIO_OS_RELEASE_DATE = "2026-02-13"

import importlib.util
import sys
import os
import json
import time
import yaml
import shutil
import subprocess
import hashlib
import math
import zipfile
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path

from oradio_engine.loom_graph import LoomGraph, load_declaration_text
from oradio_engine.loom_runtime import write_active_loom_state
try:
    from PIL import Image, ImageTk, ImageOps, ImageDraw
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
try:
    import cv2  # type: ignore
    import numpy as np  # type: ignore
    HAS_CV2 = True
except ImportError:
    cv2 = None  # type: ignore
    np = None  # type: ignore
    HAS_CV2 = False

# --- Detect boot mode early (before importing tkinter) ---
import argparse as _argparse
_boot_parser = _argparse.ArgumentParser(add_help=False)
_boot_parser.add_argument("--desktop", action="store_true")
_boot_parser.add_argument("--web", action="store_true")
_boot_parser.add_argument("--settings", action="store_true")
_boot_args, _ = _boot_parser.parse_known_args()

# --settings opens only the settings window, but it's a windowed mode → needs real tkinter.
BOOT_MODE = "desktop" if (_boot_args.desktop or _boot_args.settings) else ("web" if _boot_args.web else "headless")

# Only import tkinter when running in desktop mode
if BOOT_MODE == "desktop":
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog

    # --- Cross-platform Button Shim ---
    if sys.platform == "darwin":
        class StyledButton(tk.Label):
            def __init__(self, parent, *args, **kwargs):
                self.command = kwargs.pop("command", None)
                self.disabled = False
                if "padx" not in kwargs: kwargs["padx"] = 10
                if "pady" not in kwargs: kwargs["pady"] = 5
                if "cursor" not in kwargs: kwargs["cursor"] = "hand2"
                state = kwargs.pop("state", "normal")
                super().__init__(parent, *args, **kwargs)
                if state == "disabled": self.configure(state="disabled")
                self.bind("<Button-1>", self._on_click)
                self.bind("<Enter>", self._on_hover)
                self.bind("<Leave>", self._on_leave)
                self._orig_bg = kwargs.get("bg", kwargs.get("background", "SystemButtonFace"))
                self._hover_bg = self._adjust_color(self._orig_bg, 20)
            def _adjust_color(self, hex_color, amount=20):
                if not isinstance(hex_color, str) or not hex_color.startswith("#") or len(hex_color) != 7: return hex_color 
                try:
                    r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
                    return f"#{min(255, max(0, r+amount)):02x}{min(255, max(0, g+amount)):02x}{min(255, max(0, b+amount)):02x}"
                except: return hex_color
            def _on_click(self, event):
                if self.command and not self.disabled: self.after(5, self.command)
            def _on_hover(self, event):
                if not self.disabled: self.config(bg=self._hover_bg)
            def _on_leave(self, event):
                if not self.disabled: self.config(bg=self._orig_bg)
            def configure(self, **kwargs):
                if "command" in kwargs: self.command = kwargs.pop("command")
                if "state" in kwargs:
                    self.disabled = (kwargs.pop("state") == "disabled")
                    self.config(cursor="arrow" if self.disabled else "hand2", fg="#666666" if self.disabled else kwargs.get("fg", "#ffffff"))
                super().configure(**kwargs)
            config = configure
        tk.Button = StyledButton
else:
    # Headless / web mode — provide lightweight stubs so the rest of the
    # module can be parsed without a display server.
    tk = None   # type: ignore
    ttk = None  # type: ignore
    messagebox = None  # type: ignore
    filedialog = None  # type: ignore

BASE = os.path.dirname(__file__)

# ── OLED soul-display event helper (non-fatal if daemon not running) ─────────
def _oled(event_type: str, **extra):
    """Send a fire-and-forget UDP event to the OLED daemon.

    Silently no-ops if the daemon is not running or the tools module
    is unavailable — OLED is enhancement-only, never blocking.
    """
    try:
        import sys as _sys
        _tools = os.path.join(BASE, "tools")
        if _tools not in _sys.path:
            _sys.path.insert(0, _tools)
        from oled_event_client import send_oled_event  # type: ignore
        payload = {"type": event_type}
        payload.update(extra)
        send_oled_event(payload)
    except Exception:
        pass
STATIONS_DIR = os.path.join(BASE, "stations")
RUNTIME_PATH = os.path.join(BASE, "bookmark.py")  # legacy station runtime (unchanged)
PLUGINS_DIR = os.path.join(BASE, "plugins")
ORADIO_PLAYER_PATH = os.path.join(BASE, "oradio_player.py")
# The Club holds loom-specific artifacts: crossovers and the boot "door" transitions + index.
# (bookmark/door.py manages doors here; bookmark/mint.py stores crossovers here.)
CLUB_DIR = os.path.join(BASE, "club")
DEFAULT_LOOM_ID = "default"   # LEGACY door key (pre loom-switching); migrated by _door_loom_id

# Speed-of-light traversal: clicking a station 2+ jumps away plays EVERY crossover clip along the
# real soulmate path (never skipping one), sped up on a gradient by how many legs the path has — so
# a big loom is traversable edge-to-edge faster than a small one, up to a hard cap (past which a
# very large loom just takes longer; bookmarks let you leave and resume). speed = 1 + (legs-1)*GAIN,
# clamped to [1, MAX]. legs==1 (a direct neighbour) stays native.
SPEED_OF_LIGHT_MAX = 6.0
SPEED_OF_LIGHT_GAIN = 0.9

# The reskinned ribbon-os Bookmark — the .oradio authoring surface — lives in the oracle-radio
# project. It MUST run with that directory as cwd so its `bookmark/` brick package imports.
ORADIO_BOOKMARK_DIR = r"C:\Users\evana\OneDrive\Documents\oracle-radio"
ORADIO_BOOKMARK = os.path.join(ORADIO_BOOKMARK_DIR, "bookmark.py")
RIBBON_OS_MEDIA_ROOT = r"C:\Users\evana\OneDrive\Documents\ribbon-os-(4.5)\videos"
RIBBON_OS_RIBBON_ROOT = os.path.join(RIBBON_OS_MEDIA_ROOT, "ribbon")

# The fixed ribbon-skin vocabulary: the folders under videos/ribbon/, each holding
# {entry,loop,exit}.ogv. We have ~21 skins, NOT one per station, so every .oradio
# station is ASSIGNED one of these as its visual look (the ribbon is the look; the
# .oradio is the content). Assignment is deterministic: by manifest category if it
# names a real ribbon folder, else hash(station_id) so the same station always
# resolves to the same ribbon and never flickers between runs.
RIBBON_CATS = [
    "camera_tools", "connectivity", "dash_editor", "dashes", "devices",
    "diagnostics", "drive", "extras", "head_tracking", "help", "hid_fusion",
    "input_mapper", "moonlight", "pi_desktop", "profiles", "ribbon_studio",
    "rpm_lights", "settings", "simulation_tools", "system_tools", "telemetry",
]

def ribbon_cat_for_station(station: "StationInfo") -> str:
    """Resolve a station to one of the fixed RIBBON_CATS skins (deterministic)."""
    cfg = getattr(station, "manifest", None) or {}
    st_meta = cfg.get("station", {}) if isinstance(cfg.get("station", {}), dict) else {}
    raw = str(st_meta.get("ribbon") or st_meta.get("category") or "").strip().lower().replace(" ", "_")
    if raw in RIBBON_CATS:
        return raw
    digest = hashlib.md5(station.station_id.encode("utf-8")).hexdigest()
    return RIBBON_CATS[int(digest, 16) % len(RIBBON_CATS)]

def ribbon_dir_for_cat(cat: str) -> str:
    return os.path.join(RIBBON_OS_RIBBON_ROOT, cat)

def ribbon_clip_for_station(station: "StationInfo", kind: str) -> str:
    """kind in {'entry','loop','exit'}; returns the assigned ribbon SKIN clip path.

    NB: this is the generic backdrop pack (~21 skins). A minted .oradio carries its OWN authored
    loop.mp4 — prefer `oradio_baked_loop(station)` for an .oradio so the loop the author baked is
    what shows, with the ribbon pack only as the home/boot backdrop & last-resort fallback."""
    return os.path.join(ribbon_dir_for_cat(ribbon_cat_for_station(station)), f"{kind}.ogv")


def _read_oradio_descriptor(path: str) -> Dict[str, Any]:
    """Read an .oradio's descriptor. A MINTED .oradio is a zip (manifest.json + loop.mp4); the
    legacy spec examples are plain YAML descriptors. This returns a descriptor dict the shell can
    consume in both cases — for a minted bundle it synthesizes the station/theme keys from the
    manifest and stashes the zip path under `_oradio_zip` so the baked loop can be extracted."""
    if zipfile.is_zipfile(path):
        try:
            with zipfile.ZipFile(path) as zf:
                m = json.loads(zf.read("manifest.json").decode("utf-8"))
            vsig = m.get("visual_signature") or {}
            family = str(vsig.get("family") or "")
            return {
                "oradio": m.get("id") or Path(path).stem,
                "title": m.get("title", ""),
                "station": {"name": m.get("title") or m.get("id") or Path(path).stem,
                            "category": family},
                "theme": family,
                "kernel": bool(m.get("kernel", False)),
                "soulmates": m.get("soulmates", {}),
                "bricks": m.get("bricks", []),
                "declaration": m.get("declaration", ""),
                "loop": m.get("loop", "loop.mp4"),
                "thumbnail": m.get("thumbnail"),
                "audio": m.get("audio"),
                "visual_signature": vsig,
                "author": m.get("author"),
                "open": m.get("open"),
                "visual": {},
                "_oradio_zip": str(path),
            }
        except Exception:
            return {}
    return _read_yaml_like(path)


# Extracted baked loops are cached here so we play the .oradio's OWN loop without re-unzipping.
_ORADIO_LOOP_CACHE = os.path.join(CLUB_DIR, "cache", "loops")
# Extracted bundled thumbnail.png (the card / galaxy-node icon the author attached at Edit time).
_ORADIO_THUMB_CACHE = os.path.join(CLUB_DIR, "cache", "thumbs")


def oradio_baked_loop(station: "StationInfo") -> Optional[str]:
    """Return a playable path to the .oradio's authored loop.mp4 (extracted + cached), or None.

    The loop is baked INTO the .oradio zip at mint; we extract it once into club/cache/loops keyed
    by id + the zip's mtime, so a re-mint refreshes the cache."""
    desc = getattr(station, "descriptor", None) or {}
    zip_path = desc.get("_oradio_zip") or (
        station.launch_path if str(getattr(station, "launch_path", "")).lower().endswith(".oradio")
        and zipfile.is_zipfile(getattr(station, "launch_path", "")) else None
    )
    if not zip_path or not os.path.exists(zip_path):
        return None
    loop_name = desc.get("loop", "loop.mp4")
    try:
        sig = int(os.path.getmtime(zip_path))
    except Exception:
        sig = 0
    out = os.path.join(_ORADIO_LOOP_CACHE, f"{station.station_id}.{sig}.mp4")
    if os.path.exists(out) and os.path.getsize(out) > 0:
        return out
    try:
        os.makedirs(_ORADIO_LOOP_CACHE, exist_ok=True)
        with zipfile.ZipFile(zip_path) as zf:
            data = zf.read(loop_name)
        with open(out, "wb") as f:
            f.write(data)
        return out
    except Exception:
        return None

def oradio_thumbnail(station: "StationInfo") -> Optional[str]:
    """Return a path to the .oradio's bundled thumbnail.png (extracted + cached), or None if the
    author never attached one. Keyed by id + zip mtime, so an Edit refreshes it. Mirrors
    oradio_baked_loop; used as the carousel card art + galaxy node icon when present."""
    desc = getattr(station, "descriptor", None) or {}
    zip_path = desc.get("_oradio_zip") or (
        station.launch_path if str(getattr(station, "launch_path", "")).lower().endswith(".oradio")
        and zipfile.is_zipfile(getattr(station, "launch_path", "")) else None
    )
    if not zip_path or not os.path.exists(zip_path):
        return None
    thumb_name = str(desc.get("thumbnail") or "thumbnail.png")
    try:
        sig = int(os.path.getmtime(zip_path))
    except Exception:
        sig = 0
    out = os.path.join(_ORADIO_THUMB_CACHE, f"{station.station_id}.{sig}.png")
    if os.path.exists(out) and os.path.getsize(out) > 0:
        return out
    try:
        with zipfile.ZipFile(zip_path) as zf:
            if thumb_name not in zf.namelist():
                return None
            data = zf.read(thumb_name)
        os.makedirs(_ORADIO_THUMB_CACHE, exist_ok=True)
        with open(out, "wb") as f:
            f.write(data)
        return out
    except Exception:
        return None


def station_recency(station: "StationInfo") -> float:
    """Most-recent-first ordering key. No manifest timestamp exists, so use the
    station directory mtime; prefer manifest 'last_opened' if a build adds one."""
    cfg = getattr(station, "manifest", None) or {}
    st_meta = cfg.get("station", {}) if isinstance(cfg.get("station", {}), dict) else {}
    lo = st_meta.get("last_opened")
    if isinstance(lo, (int, float)):
        return float(lo)
    try:
        return os.path.getmtime(station.path)
    except Exception:
        return 0.0

# -----------------------------
# Config Helpers (Moved Up)
# -----------------------------
def get_global_config_path() -> str:
    """Return path to global RadioOS settings file."""
    if os.name == "nt":
        # Windows: %APPDATA%\RadioOS\config.json
        appdata = os.getenv("APPDATA", os.path.expanduser("~"))
        cfg_dir = os.path.join(appdata, "RadioOS")
    else:
        # Mac/Linux: ~/.radioOS/config.json
        cfg_dir = os.path.expanduser("~/.radioOS")
    
    os.makedirs(cfg_dir, exist_ok=True)
    return os.path.join(cfg_dir, "config.json")

def get_global_config() -> Dict[str, Any]:
    """Load global settings (creates empty dict if not exists)."""
    path = get_global_config_path()
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_global_config(cfg: Dict[str, Any]) -> None:
    """Save global settings."""
    path = get_global_config_path()
    tmp = path + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
        os.replace(tmp, path)
    except Exception as e:
        print(f"Failed to save global config: {e}")

# -----------------------------
# Init Config & Scale
# -----------------------------
_G_CFG = get_global_config()
_G_GEN = _G_CFG.get("general", {})

UI_SCALE = float(_G_GEN.get("ui_scale", 1.0))
# Attempt high-dpi awareness on Windows if scale > 1.0 or user requests
# (Often better to just do it if possible, but let's stick to safe defaults)
if os.name == "nt":
    try:
        from ctypes import windll
        # If scale is default 1.0, user might rely on OS scaling.
        # But if they set custom scale, they likely want us to handle it.
        # For now, we enforce DPI awareness aggressively to avoid "squished" buttons.
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass


# -----------------------------
# UI Theme
# -----------------------------
UI = {
    "bg": "#0e0e0e",
    "panel": "#121212",
    "card": "#181818",
    "card_hover": "#222222",
    "surface": "#0a0a0a",
    "text": "#e8e8e8",
    "muted": "#9a9a9a",
    "accent": "#4cc9f0",
    "danger": "#ff4d6d",
    "good": "#2ee59d",
}

# Color theme presets
COLOR_THEMES = {
    "dark": {
        "bg": "#0e0e0e",
        "panel": "#121212",
        "card": "#181818",
        "card_hover": "#222222",
        "surface": "#0a0a0a",
        "text": "#e8e8e8",
        "muted": "#9a9a9a",
        "accent": "#4cc9f0",
        "danger": "#ff4d6d",
        "good": "#2ee59d",
    },
    "light": {
        "bg": "#ffffff",
        "panel": "#f5f5f5",
        "card": "#fafafa",
        "card_hover": "#e8e8e8",
        "surface": "#f0f0f0",
        "text": "#1a1a1a",
        "muted": "#666666",
        "accent": "#0891b2",
        "danger": "#dc2626",
        "good": "#16a34a",
    },
    "nord": {
        "bg": "#2e3440",
        "panel": "#3b4252",
        "card": "#434c5e",
        "card_hover": "#4c566a",
        "surface": "#2e3440",
        "text": "#eceff4",
        "muted": "#d8dee9",
        "accent": "#88c0d0",
        "danger": "#bf616a",
        "good": "#a3be8c",
    },
    "dracula": {
        "bg": "#282a36",
        "panel": "#343746",
        "card": "#44475a",
        "card_hover": "#6272a4",
        "surface": "#21222c",
        "text": "#f8f8f2",
        "muted": "#6272a4",
        "accent": "#bd93f9",
        "danger": "#ff5555",
        "good": "#50fa7b",
    },
    "monokai": {
        "bg": "#272822",
        "panel": "#2d2e27",
        "card": "#3e3d32",
        "card_hover": "#49483e",
        "surface": "#1e1f1c",
        "text": "#f8f8f2",
        "muted": "#75715e",
        "accent": "#66d9ef",
        "danger": "#f92672",
        "good": "#a6e22e",
    },
}

RIBBON_SHELL_THEMES = {
    "midnight": {"bg": "#081018", "overlay": "#13202d", "accent": "#6ce3ff"},
    "sunset": {"bg": "#160d12", "overlay": "#24161d", "accent": "#ffb067"},
    "silver": {"bg": "#101214", "overlay": "#1d232a", "accent": "#7fd1ff"},
}


def blend_hex(hex_a: str, hex_b: str, amount: float) -> str:
    amount = max(0.0, min(1.0, amount))
    try:
        a = tuple(int(hex_a[idx:idx + 2], 16) for idx in (1, 3, 5))
        b = tuple(int(hex_b[idx:idx + 2], 16) for idx in (1, 3, 5))
    except Exception:
        return hex_a
    rgb = [round((1.0 - amount) * left + amount * right) for left, right in zip(a, b)]
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


class RibbonShellStateMachine:
    def __init__(self, theme_name: str = "midnight"):
        self.phase = "BOOT"
        self.theme_name = theme_name if theme_name in RIBBON_SHELL_THEMES else "midnight"
        self.boot_started = time.time()
        self.last_activity = time.time()
        self.launch_flash_until = 0.0

    def theme(self) -> Dict[str, str]:
        return RIBBON_SHELL_THEMES[self.theme_name]

    def note_activity(self) -> None:
        self.last_activity = time.time()
        if self.phase != "BOOT":
            self.phase = "ACTIVE"

    def note_launch(self) -> None:
        self.launch_flash_until = time.time() + 1.2
        self.phase = "LAUNCH"

    def tick(self) -> None:
        now = time.time()
        if self.phase == "BOOT" and now - self.boot_started > 1.4:
            self.phase = "ACTIVE"
            return
        if self.phase == "LAUNCH" and now >= self.launch_flash_until:
            self.phase = "ACTIVE"
            return
        if self.phase != "BOOT" and now - self.last_activity > 30.0:
            self.phase = "DIM"

    def overlay_alpha_hint(self) -> float:
        if self.phase == "BOOT":
            return 0.92
        if self.phase == "LAUNCH":
            return 1.0
        if self.phase == "DIM":
            return 0.22
        return 0.84


class RibbonVideoSurface:
    def __init__(self, root: "tk.Tk", parent: "tk.Widget", host_label=None):
        self.root = root
        self.parent = parent
        self.enabled = bool(HAS_PIL and HAS_CV2)
        self.label = host_label or tk.Label(parent, bd=0, highlightthickness=0, bg="#000000")
        if host_label is None:
            self.label.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._current: Optional[Dict[str, Any]] = None
        self._transition: Optional[Dict[str, Any]] = None
        self._image = None
        self._running = False
        self._frame_ms = 33
        self._last_frame = None
        self._speed = 1.0   # speed-of-light playback multiplier (1.0 = native 30fps)
        self._frame_accum = 0.0   # fractional-frame carry so non-integer speeds are smooth
        # Optional per-frame overlay drawer: called with the final RGB numpy frame
        # (HxWx3, uint8) to draw on IN PLACE before display. Used by the galaxy map to
        # composite the node graph onto the video — keeps it in the no-blink pipeline.
        self.overlay_cb = None
        if self.enabled:
            self._running = True
            self.root.after(self._frame_ms, self._pump)

    def _open_stream(self, path: str, loop: bool, on_finished=None) -> Optional[Dict[str, Any]]:
        if not self.enabled or not os.path.exists(path):
            return None
        cap = cv2.VideoCapture(path)
        if not cap or not cap.isOpened():
            try:
                cap.release()
            except Exception:
                pass
            return None
        return {
            "cap": cap,
            "path": path,
            "loop": loop,
            "on_finished": on_finished,
            "finished_called": False,
            "last_frame": None,
        }

    def _close_stream(self, stream: Optional[Dict[str, Any]]) -> None:
        if not stream:
            return
        cap = stream.get("cap")
        if cap is not None:
            try:
                cap.release()
            except Exception:
                pass

    def play(self, path: str, *, loop: bool = False, on_finished=None, fade_ms: int = 0) -> bool:
        stream = self._open_stream(path, loop, on_finished=on_finished)
        if not stream:
            return False
        if self._current and fade_ms > 0:
            self._transition = {
                "old": self._current,
                "new": stream,
                "started": time.time(),
                "duration": max(0.05, fade_ms / 1000.0),
            }
        else:
            self._close_stream(self._current)
            self._close_stream(self._transition["new"] if self._transition else None)
            self._close_stream(self._transition["old"] if self._transition else None)
            self._transition = None
            self._current = stream
        return True

    def stop(self) -> None:
        self._running = False
        self._close_stream(self._current)
        self._current = None
        if self._transition:
            self._close_stream(self._transition.get("old"))
            self._close_stream(self._transition.get("new"))
            self._transition = None

    def set_speed(self, mult: float) -> None:
        """Speed-of-light: play the active clip faster by advancing extra frames per tick (cap
        safe). Used so traversing a far node doesn't crawl — the longer the path, the quicker.
        Fractional speeds are honored via a frame accumulator; resetting to 1.0 clears the carry."""
        self._speed = max(1.0, min(float(mult), SPEED_OF_LIGHT_MAX))
        if self._speed <= 1.0:
            self._frame_accum = 0.0

    def _read_frame(self, stream: Dict[str, Any]):
        cap = stream["cap"]
        ok, frame = cap.read()
        if not ok or frame is None:
            if stream["loop"]:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ok, frame = cap.read()
            if not ok or frame is None:
                if not stream["finished_called"]:
                    stream["finished_called"] = True
                    callback = stream.get("on_finished")
                    if callback is not None:
                        self.root.after(0, callback)
                return stream.get("last_frame")
        # speed-of-light: advance extra frames per tick (display only the latest). A fractional
        # accumulator carries the remainder so e.g. 1.5x skips one extra frame every other tick.
        self._frame_accum += max(0.0, getattr(self, "_speed", 1.0) - 1.0)
        skips = int(self._frame_accum)
        self._frame_accum -= skips
        for _ in range(skips):
            ok2, f2 = cap.read()
            if not ok2 or f2 is None:
                break
            frame = f2
        stream["last_frame"] = frame
        return frame

    def _render_frame(self, frame) -> None:
        if frame is None or not HAS_PIL:
            return
        width = max(2, self.label.winfo_width())
        height = max(2, self.label.winfo_height())
        if width <= 2 or height <= 2:
            width = max(2, self.parent.winfo_width())
            height = max(2, self.parent.winfo_height())
        if width <= 2 or height <= 2:
            return
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # INTER_AREA only wins when shrinking; for the usual upscale (720p -> window)
        # it softens. Use INTER_CUBIC upscaling for a sharper background.
        src_h, src_w = frame.shape[:2]
        interp = cv2.INTER_AREA if (width * height) < (src_w * src_h) else cv2.INTER_CUBIC
        frame = cv2.resize(frame, (width, height), interpolation=interp)
        if self.overlay_cb is not None:
            try:
                frame = np.ascontiguousarray(frame)
                self.overlay_cb(frame)  # draws the galaxy graph onto the frame in place
            except Exception:
                pass
        image = Image.fromarray(frame)
        self._image = ImageTk.PhotoImage(image=image)
        self.label.configure(image=self._image)

    def _pump(self) -> None:
        if not self._running or not self.enabled:
            return

        _t0 = time.time()
        output = None
        if self._transition:
            old_stream = self._transition["old"]
            new_stream = self._transition["new"]
            old_frame = self._read_frame(old_stream)
            new_frame = self._read_frame(new_stream)
            if old_frame is None:
                old_frame = new_frame
            if new_frame is None:
                new_frame = old_frame
            if old_frame is not None and new_frame is not None:
                if old_frame.shape[:2] != new_frame.shape[:2]:
                    new_frame = cv2.resize(new_frame, (old_frame.shape[1], old_frame.shape[0]), interpolation=cv2.INTER_AREA)
                t = (time.time() - self._transition["started"]) / self._transition["duration"]
                t = max(0.0, min(1.0, t))
                output = cv2.addWeighted(old_frame, 1.0 - t, new_frame, t, 0.0)
                if t >= 1.0:
                    self._close_stream(old_stream)
                    self._current = new_stream
                    self._transition = None
        elif self._current:
            output = self._read_frame(self._current)

        if output is not None:
            self._last_frame = output
            self._render_frame(output)
        elif self._last_frame is not None:
            self._render_frame(self._last_frame)

        # Compensate the next tick for the time decode+resize+blit just took, so the
        # cadence stays near the clip's 30fps instead of (33ms + work) per frame.
        work_ms = (time.time() - _t0) * 1000.0
        delay = int(self._frame_ms - work_ms)
        if delay < 1:
            delay = 1
        self.root.after(delay, self._pump)


class GalaxyMap:
    """Lightweight spatial carousel: oradios are NODES, authored crossovers are EDGES
    (Elite-Dangerous galaxy-map style). Pure point/line projection — no GL. The graph
    is composited onto the flat video frames; you orbit (yaw/pitch/roll) + zoom it.
    Nodes are real now; edges only appear once a crossover bond is authored."""

    def __init__(self):
        self.nodes = []          # [{id, label, pos(np3), station, thumb(RGBA np)}]
        self.edges = []          # [(i, j)] — authored crossover bonds (empty until baked)
        self.edge_keys = {}      # {(i, j): "a__b"}
        self.edge_textures = {}  # {"a__b": rgba numpy texture}
        # The "home loop" SUN is RETIRED (older-engine artifact). Under the current canon an
        # oradio is the unit of simulation — nodes stand ALONE, and edges only appear from
        # authored crossover bonds. pos=None disables every sun draw + the genesis bonds below.
        self.sun = {"pos": None, "label": "home loop", "thumb": None}
        self.yaw = 0.6
        self.pitch = 0.35
        self.roll = 0.0
        self.dist = 3.4
        self.focus = 0
        self.accent = (120, 220, 160)
        self._proj = []          # per-node (sx, sy, depth) or None, set each draw
        self._sun_proj = None

    @staticmethod
    def _pos_for(key: str):
        h = hashlib.md5(key.encode("utf-8")).hexdigest()
        a = int(h[0:8], 16) / 0xFFFFFFFF
        b = int(h[8:16], 16) / 0xFFFFFFFF
        c = int(h[16:24], 16) / 0xFFFFFFFF
        theta = a * 2 * math.pi
        phi = math.acos(2 * b - 1)
        r = 0.7 + 0.55 * c
        return np.array([r * math.sin(phi) * math.cos(theta),
                         r * math.sin(phi) * math.sin(theta),
                         r * math.cos(phi)], dtype=float)

    def set_nodes(self, stations):
        self.nodes = []
        station_index: Dict[str, int] = {}
        for st in stations:
            cfg = getattr(st, "manifest", None) or {}
            meta = cfg.get("station", {}) if isinstance(cfg.get("station", {}), dict) else {}
            # Show the Title set at mint (manifest.title), not the slug id / loom-node label.
            desc = getattr(st, "descriptor", None) or {}
            label = str(desc.get("title") or "").strip() or str(meta.get("name") or st.station_id)
            self.nodes.append({"id": st.station_id, "label": str(label),
                               "pos": self._pos_for(st.station_id), "station": st})
            station_index[st.station_id] = len(self.nodes) - 1
        self.edges = []
        self.edge_keys = {}
        seen_edges = set()
        for st in stations:
            left = station_index.get(st.station_id)
            if left is None:
                continue
            soulmates = list(getattr(st, "soulmates", []) or [])
            if not soulmates:
                soulmate = getattr(st, "soulmate", "") or ""
                soulmates = [soulmate] if soulmate else []
            for soulmate_id in soulmates:
                right = station_index.get(soulmate_id)
                if right is None or left == right:
                    continue
                edge = tuple(sorted((left, right)))
                if edge in seen_edges:
                    continue
                seen_edges.add(edge)
                self.edges.append(edge)
                ids = sorted((st.station_id, soulmate_id))
                self.edge_keys[edge] = f"{ids[0]}__{ids[1]}"
        if self.nodes:
            self.focus = int(clamp(self.focus, 0, len(self.nodes) - 1))

    def set_edge_textures(self, textures):
        self.edge_textures = dict(textures or {})

    def _rot(self):
        cy, sy = math.cos(self.yaw), math.sin(self.yaw)
        cp, sp = math.cos(self.pitch), math.sin(self.pitch)
        cr, sr = math.cos(self.roll), math.sin(self.roll)
        Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
        Rx = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]])
        Rz = np.array([[cr, -sr, 0], [sr, cr, 0], [0, 0, 1]])
        return Rz @ Rx @ Ry

    def bond_distance(self, a, b):
        """Jumps between two node indices along AUTHORED crossover edges only.

        The genesis bond — every oradio bonded to the source/keyframe oradio (the
        node we draw as the 'sun') — is NOT a shortcut here: routing through it is
        the map's default, not real distance. So two oradios with no authored
        crossover between them are 'unmapped' (None), not 'far'. Returns the hop
        count along authored edges, 0 if a == b, or None if no authored path exists."""
        if a == b:
            return 0
        if not self.edges:
            return None
        adj = {}
        for i, j in self.edges:
            adj.setdefault(i, []).append(j)
            adj.setdefault(j, []).append(i)
        seen = {a}
        frontier = [a]
        dist = 0
        while frontier:
            dist += 1
            nxt = []
            for u in frontier:
                for v in adj.get(u, ()):
                    if v == b:
                        return dist
                    if v not in seen:
                        seen.add(v)
                        nxt.append(v)
            frontier = nxt
        return None

    def orbit(self, dyaw, dpitch):
        self.yaw += dyaw
        self.pitch = clamp(self.pitch + dpitch, -1.5, 1.5)

    def roll_by(self, d):
        self.roll += d

    def zoom(self, factor):
        self.dist = clamp(self.dist * factor, 1.6, 8.0)

    def hit_test(self, x, y, tol=34):
        best, bestd = None, float("inf")
        for i, p in enumerate(self._proj):
            if p is None:
                continue
            d = (p[0] - x) ** 2 + (p[1] - y) ** 2
            if d < bestd:
                bestd, best = d, i
        return best if (best is not None and bestd <= tol * tol) else None

    def hit_test_edge(self, x, y, tol=14):
        best = None
        bestd = float("inf")
        for edge in self.edges:
            i, j = edge
            if i >= len(self._proj) or j >= len(self._proj):
                continue
            pi, pj = self._proj[i], self._proj[j]
            if pi is None or pj is None:
                continue
            d = self._point_segment_distance(x, y, pi[0], pi[1], pj[0], pj[1])
            if d < bestd:
                bestd = d
                best = edge
        return best if (best is not None and bestd <= tol) else None

    @staticmethod
    def _point_segment_distance(px, py, ax, ay, bx, by):
        abx, aby = (bx - ax), (by - ay)
        denom = (abx * abx) + (aby * aby)
        if denom <= 1e-6:
            return math.hypot(px - ax, py - ay)
        t = ((px - ax) * abx + (py - ay) * aby) / denom
        t = clamp(t, 0.0, 1.0)
        qx = ax + (abx * t)
        qy = ay + (aby * t)
        return math.hypot(px - qx, py - qy)

    def _project(self, pos, R, cx, cy, f):
        pc = R @ pos
        depth = self.dist - pc[2]
        if depth < 0.25:
            return None
        return (cx + f * pc[0] / depth, cy - f * pc[1] / depth, depth)

    def _blit_thumb(self, frame, thumb, sx, sy, sz):
        """Alpha-composite a circular RGBA thumbnail centered at (sx, sy), size sz."""
        if thumb is None or sz < 4:
            return False
        th = cv2.resize(thumb, (sz, sz), interpolation=cv2.INTER_AREA)
        h, w = frame.shape[:2]
        x0, y0 = int(sx - sz / 2), int(sy - sz / 2)
        x1, y1 = x0 + sz, y0 + sz
        fx0, fy0 = max(0, x0), max(0, y0)
        fx1, fy1 = min(w, x1), min(h, y1)
        if fx0 >= fx1 or fy0 >= fy1:
            return True
        tx0, ty0 = fx0 - x0, fy0 - y0
        sub = th[ty0:ty0 + (fy1 - fy0), tx0:tx0 + (fx1 - fx0)]
        a = sub[:, :, 3:4].astype(float) / 255.0
        roi = frame[fy0:fy1, fx0:fx1]
        roi[:] = (sub[:, :, :3].astype(float) * a + roi.astype(float) * (1 - a)).astype(frame.dtype)
        return True

    def _blit_rgba(self, frame, rgba, sx, sy):
        if rgba is None:
            return
        h, w = frame.shape[:2]
        th, tw = rgba.shape[:2]
        x0, y0 = int(sx - tw / 2), int(sy - th / 2)
        x1, y1 = x0 + tw, y0 + th
        fx0, fy0 = max(0, x0), max(0, y0)
        fx1, fy1 = min(w, x1), min(h, y1)
        if fx0 >= fx1 or fy0 >= fy1:
            return
        tx0, ty0 = fx0 - x0, fy0 - y0
        sub = rgba[ty0:ty0 + (fy1 - fy0), tx0:tx0 + (fx1 - fx0)]
        if sub.shape[2] < 4:
            return
        a = sub[:, :, 3:4].astype(float) / 255.0
        roi = frame[fy0:fy1, fx0:fx1]
        roi[:] = (sub[:, :, :3].astype(float) * a + roi.astype(float) * (1 - a)).astype(frame.dtype)

    def _draw_textured_edge(self, frame, pi, pj, texture):
        x0, y0 = float(pi[0]), float(pi[1])
        x1, y1 = float(pj[0]), float(pj[1])
        dx, dy = (x1 - x0), (y1 - y0)
        length = math.hypot(dx, dy)
        if length < 4:
            return False
        angle = math.degrees(math.atan2(dy, dx))
        tex_h, tex_w = texture.shape[:2]
        scale = clamp(18.0 / max(1.0, float(tex_h)), 0.45, 1.6)
        sw = max(10, int(tex_w * scale))
        sh = max(8, int(tex_h * scale))
        tile = cv2.resize(texture, (sw, sh), interpolation=cv2.INTER_AREA)
        center = (sw / 2.0, sh / 2.0)
        M = cv2.getRotationMatrix2D(center, -angle, 1.0)
        cos_v = abs(M[0, 0]); sin_v = abs(M[0, 1])
        bound_w = max(1, int((sh * sin_v) + (sw * cos_v)))
        bound_h = max(1, int((sh * cos_v) + (sw * sin_v)))
        M[0, 2] += (bound_w / 2.0) - center[0]
        M[1, 2] += (bound_h / 2.0) - center[1]
        rot = cv2.warpAffine(tile, M, (bound_w, bound_h), flags=cv2.INTER_LINEAR,
                             borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
        spacing = max(8, int(sw * 0.72))
        margin = max(bound_w, bound_h) * 0.5
        usable = length - (margin * 2.0)
        if usable <= 1.0:
            return False
        count = max(1, int(usable // spacing) + 1)
        start = margin
        end = length - margin
        for idx in range(count):
            tlen = start if count == 1 else (start + ((end - start) * (idx / max(1, count - 1))))
            t = tlen / length
            sx = x0 + dx * t
            sy = y0 + dy * t
            self._blit_rgba(frame, rot, sx, sy)
        return True

    def draw(self, frame, accent=None):
        if np is None or cv2 is None or not self.nodes:
            return
        if accent is not None:
            self.accent = accent
        h, w = frame.shape[:2]
        cx, cy = w / 2.0, h / 2.0
        f = 0.9 * min(w, h)
        R = self._rot()
        proj = [self._project(n["pos"], R, cx, cy, f) for n in self.nodes]
        self._proj = proj
        sun_p = self._project(self.sun["pos"], R, cx, cy, f) if self.sun.get("pos") is not None else None
        self._sun_proj = sun_p

        # Genesis bonds: a clear line from every oradio to the sun (the home loop).
        if sun_p is not None:
            for i, p in enumerate(proj):
                if p is None:
                    continue
                t = clamp((self.dist + 1.3 - p[2]) / 2.4, 0.3, 1.0)
                col = tuple(int(c * (0.45 + 0.4 * t)) for c in self.accent)
                cv2.line(frame, (int(p[0]), int(p[1])), (int(sun_p[0]), int(sun_p[1])),
                         col, max(1, int(2 * t)), cv2.LINE_AA)

        # Authored crossover bonds (brighter) — empty until baked, renderer-ready.
        for (i, j) in self.edges:
            if i >= len(proj) or j >= len(proj):
                continue
            pi, pj = proj[i], proj[j]
            if pi is None or pj is None:
                continue
            key = self.edge_keys.get((i, j))
            tex = self.edge_textures.get(key) if key else None
            if tex is not None:
                shadow = tuple(int(c * 0.28) for c in self.accent)
                cv2.line(frame, (int(pi[0]), int(pi[1])), (int(pj[0]), int(pj[1])),
                         shadow, 2, cv2.LINE_AA)
                self._draw_textured_edge(frame, pi, pj, tex)
                continue
            cv2.line(frame, (int(pi[0]), int(pi[1])), (int(pj[0]), int(pj[1])),
                     (245, 245, 255), 2, cv2.LINE_AA)

        # The sun (home loop) at center.
        if sun_p is not None:
            sscale = f / sun_p[2]
            srad = max(10, int(sscale * 0.045))
            if not self._blit_thumb(frame, self.sun.get("thumb"), sun_p[0], sun_p[1], srad * 2):
                cv2.circle(frame, (int(sun_p[0]), int(sun_p[1])), srad, (255, 236, 170), -1, cv2.LINE_AA)
            cv2.circle(frame, (int(sun_p[0]), int(sun_p[1])), srad + 3, (255, 244, 200), 2, cv2.LINE_AA)

        # Nodes = the oradios themselves (circular thumbnails), back-to-front.
        order = sorted(range(len(proj)), key=lambda i: -(proj[i][2] if proj[i] else 1e9))
        for i in order:
            p = proj[i]
            if p is None:
                continue
            sx, sy, depth = p
            focused = (i == self.focus)
            scale = f / depth
            sz = int(clamp(scale * 0.085, 26, 150))
            ring = self.accent if focused else (235, 240, 250)
            cv2.circle(frame, (int(sx), int(sy)), sz // 2 + (5 if focused else 2), ring,
                       3 if focused else 1, cv2.LINE_AA)
            if not self._blit_thumb(frame, self.nodes[i].get("thumb"), sx, sy, sz):
                cv2.circle(frame, (int(sx), int(sy)), sz // 2, (90, 100, 120), -1, cv2.LINE_AA)
            lbl = self.nodes[i]["label"]
            fs = clamp(0.0016 * scale, 0.38, 0.62)
            lcol = self.accent if focused else (235, 240, 250)
            (tw, _), _ = cv2.getTextSize(lbl, cv2.FONT_HERSHEY_SIMPLEX, fs, 1)
            cv2.putText(frame, lbl, (int(sx - tw / 2), int(sy + sz / 2 + 18)),
                        cv2.FONT_HERSHEY_SIMPLEX, fs, lcol, 1, cv2.LINE_AA)


# Apply theme from config if present
_theme_name = _G_GEN.get("theme", "dark")
if _theme_name in COLOR_THEMES:
    UI.update(COLOR_THEMES[_theme_name])

# -----------------------------
# Fonts (Scaled)
# -----------------------------
def _scale_font(size: int) -> int:
    return int(size * UI_SCALE)

FONT_H1 = ("Segoe UI", _scale_font(20), "bold")
FONT_H2 = ("Segoe UI", _scale_font(16), "bold")
FONT_BODY = ("Segoe UI", _scale_font(11))
FONT_SMALL = ("Segoe UI", _scale_font(10))

# -----------------------------
# Helpers
# -----------------------------
def scaled_geometry(w: int, h: int) -> str:
    return f"{int(w * UI_SCALE)}x{int(h * UI_SCALE)}"



def discover_plugins() -> Dict[str, Dict[str, Any]]:
    plugins: Dict[str, Dict[str, Any]] = {}
    if not os.path.exists(PLUGINS_DIR):
        return plugins

    for fn in sorted(os.listdir(PLUGINS_DIR)):
        if not fn.endswith(".py"):
            continue

        name = os.path.splitext(fn)[0]
        path = os.path.join(PLUGINS_DIR, fn)

        info: Dict[str, Any] = {
            "name": name,
            "display": name,
            "desc": "",
            "path": path,
            "is_feed": True,      # default
            "defaults": None,     # optional dict
        }

        try:
            spec = importlib.util.spec_from_file_location(name, path)
            mod = importlib.util.module_from_spec(spec)
            assert spec and spec.loader
            spec.loader.exec_module(mod)

            info["display"] = getattr(mod, "PLUGIN_NAME", name)
            info["desc"]    = getattr(mod, "PLUGIN_DESC", "")
            info["is_feed"] = bool(getattr(mod, "IS_FEED", True))

            # Plugin-provided defaults (any of these names are acceptable)
            # Keep it flexible so plugin authors have options.
            d = (
                getattr(mod, "FEED_DEFAULTS", None)
                or getattr(mod, "DEFAULT_FEED_CFG", None)
                or getattr(mod, "DEFAULT_CONFIG", None)
            )
            if isinstance(d, dict):
                info["defaults"] = d

        except Exception:
            # tolerate import failure; keep minimal info
            pass

        plugins[name] = info

    return plugins


def discover_meta_plugins() -> List[str]:
    """Discover available meta plugins from plugins/meta/ directory."""
    meta_dir = os.path.join(PLUGINS_DIR, "meta")
    plugins = []
    
    if not os.path.exists(meta_dir):
        return ["radio_station"]  # default fallback
    
    for fn in sorted(os.listdir(meta_dir)):
        if fn.endswith(".py") and not fn.startswith("__"):
            name = os.path.splitext(fn)[0]
            plugins.append(name)
    
    return plugins if plugins else ["radio_station"]


def safe_read_yaml(path: str) -> Dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}

def safe_write_yaml(path: str, obj: Dict[str, Any]) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        yaml.safe_dump(obj, f, sort_keys=False, allow_unicode=True)
    os.replace(tmp, path)

def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def now_ts() -> int:
    return int(time.time())

def station_manifest_path(station_dir: str) -> str:
    return os.path.join(station_dir, "manifest.yaml")

def station_status_path(station_dir: str) -> str:
    return os.path.join(station_dir, "status.json")

def station_db_path(station_dir: str) -> str:
    return os.path.join(station_dir, "station.sqlite")

def station_memory_path(station_dir: str) -> str:
    return os.path.join(station_dir, "station_memory.json")

def parse_list_field(s: str) -> List[Any]:
    """
    Accepts:
      - JSON list: ["a","b"]
      - YAML-ish list: [a, b]
      - comma list: a,b
      - empty
    Returns list.
    """
    s = (s or "").strip()
    if not s:
        return []
    # Try JSON first
    try:
        v = json.loads(s)
        if isinstance(v, list):
            return v
    except Exception:
        pass
    # Try YAML list
    try:
        v = yaml.safe_load(s)
        if isinstance(v, list):
            return v
    except Exception:
        pass
    # Comma fallback
    return [x.strip() for x in s.split(",") if x.strip()]

def parse_scalar_field(s: str) -> Any:
    """
    Parses an entry field into bool/int/float/list/str as appropriate.
    - If it looks like JSON/YAML list -> list
    - If it is 'true/false' -> bool
    - If numeric -> int/float
    - Else string
    """
    raw = (s or "").strip()
    if raw == "":
        return ""

    low = raw.lower()
    if low in ("true", "false"):
        return low == "true"

    # list-ish
    if (raw.startswith("[") and raw.endswith("]")) or "," in raw:
        # but don't blindly convert every comma string into list for keys that are clearly scalars
        # (we'll only use this in dynamic editor where list values started as list)
        pass

    # number
    try:
        if "." in raw:
            return float(raw)
        return int(raw)
    except Exception:
        return raw

def resolve_cfg_path(station_dir: str, p: str) -> str:
    """
    Resolve relative paths against:
      1) station_dir
      2) RADIO_OS_ROOT (BASE)
    """
    p = (p or "").strip()
    if not p:
        return ""
    if os.path.isabs(p):
        return p

    # Try station dir first
    cand = os.path.join(station_dir, p)
    if os.path.exists(cand):
        return cand

    # Try BASE
    cand = os.path.join(BASE, p)
    if os.path.exists(cand):
        return cand

    # Fall back to station relative join even if not exists
    return os.path.join(station_dir, p)


# -----------------------------
# Station discovery
# -----------------------------
@dataclass
class StationInfo:
    station_id: str
    path: str
    manifest: Dict[str, Any]
    source_kind: str = "legacy_station"
    soulmate: str = ""
    soulmates: List[str] = field(default_factory=list)
    descriptor: Optional[Dict[str, Any]] = None
    launch_path: str = ""


def _read_yaml_like(path: str) -> Dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}
    except Exception:
        return {}


def _shell_manifest_from_oradio(oradio_path: str, descriptor: Dict[str, Any], label: str = "") -> Dict[str, Any]:
    visual = descriptor.get("visual") if isinstance(descriptor.get("visual"), dict) else {}
    base = visual.get("base") if isinstance(visual.get("base"), dict) else {}
    station_block = descriptor.get("station") if isinstance(descriptor.get("station"), dict) else {}
    derived_name = label or str(station_block.get("name") or descriptor.get("oradio") or Path(oradio_path).stem)
    derived_category = str(
        station_block.get("category")
        or descriptor.get("theme")
        or base.get("theme")
        or ""
    ).strip()
    derived_logo = str(station_block.get("logo") or descriptor.get("logo") or "").strip()
    return {
        "station": {
            "name": derived_name,
            "category": derived_category,
            "logo": derived_logo,
            "ribbon": derived_category,
        },
        "theme": str(descriptor.get("theme") or base.get("theme") or "").strip(),
        "visual": visual,
    }


def _discover_oradio_candidates() -> List[Path]:
    seen: Dict[str, Path] = {}
    for pattern in ("*.oradio", "exports/*.oradio", "spec/examples/*.oradio"):
        for path in Path(BASE).glob(pattern):
            seen[str(path.resolve())] = path
    return list(seen.values())


def _discover_primary_loom() -> Optional[Path]:
    candidates: List[Path] = []
    for pattern in ("*.loom", "exports/*.loom", "spec/examples/*.loom"):
        candidates.extend(Path(BASE).glob(pattern))
    for path in sorted(candidates):
        try:
            universe, nodes = load_declaration_text(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if universe or nodes:
            if nodes:
                return path
    return None


def _discover_all_looms() -> List[Tuple[Path, str, str]]:
    """Every authored .loom on disk -> (loom_path, loom_id, label). Sibling of
    _discover_primary_loom; populates the right-click "Go to loom ▸" switch menu. loom_id is
    the loom's universe (falling back to the file stem) so it matches the door/crossover keys."""
    out: List[Tuple[Path, str, str]] = []
    seen_path: set = set()
    seen_id: set = set()
    candidates: List[Path] = []
    for pattern in ("*.loom", "exports/*.loom", "spec/examples/*.loom"):
        candidates.extend(Path(BASE).glob(pattern))
    for path in sorted(candidates):
        rp = str(path.resolve())
        if rp in seen_path:
            continue
        try:
            universe, nodes = load_declaration_text(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not (universe or nodes):
            continue
        loom_id = str(universe) if universe else path.stem
        if loom_id in seen_id:        # same universe authored twice on disk -> one menu entry
            continue
        seen_path.add(rp)
        seen_id.add(loom_id)
        # The universe can be a long descriptive sentence; the file stem is the readable label.
        out.append((path, loom_id, path.stem))
    return out


def load_oradio_shell_items_for(loom_path: Optional[Path]) -> List[StationInfo]:
    """Build the carousel's StationInfo list from a specific .loom (or the standalone-oradio
    fallback when `loom_path` is None / empty). Parametrized form of load_oradio_shell_items so
    loom-switching can reload the shell from another loom."""
    if loom_path is not None:
        try:
            graph = LoomGraph.from_dict(_read_yaml_like(str(loom_path)))
        except Exception:
            graph = LoomGraph(universe="", oradios=())
        items: List[StationInfo] = []
        for node in graph.oradios:
            candidate = Path(node.oradio)
            if not candidate.is_absolute():
                candidate = (loom_path.parent / candidate).resolve()
            descriptor = _read_oradio_descriptor(str(candidate))
            items.append(
                StationInfo(
                    station_id=node.id,
                    path=str(candidate.parent),
                    manifest=_shell_manifest_from_oradio(str(candidate), descriptor, label=node.label),
                    source_kind="oradio",
                    soulmate=node.soulmate,
                    soulmates=list(getattr(node, "soulmates", ()) or ([] if not node.soulmate else [node.soulmate])),
                    descriptor=descriptor,
                    launch_path=str(candidate),
                )
            )
        if items:
            return items

    items: List[StationInfo] = []
    for path in _discover_oradio_candidates():
        descriptor = _read_oradio_descriptor(str(path))
        station_id = str(descriptor.get("oradio") or path.stem)
        items.append(
            StationInfo(
                station_id=station_id,
                path=str(path.resolve().parent),
                manifest=_shell_manifest_from_oradio(str(path), descriptor),
                source_kind="oradio",
                descriptor=descriptor,
                launch_path=str(path.resolve()),
            )
        )
    return items


def load_oradio_shell_items() -> List[StationInfo]:
    """Carousel items for the PRIMARY loom (boot default). See load_oradio_shell_items_for."""
    return load_oradio_shell_items_for(_discover_primary_loom())


def load_stations() -> List[StationInfo]:
    oradio_items = load_oradio_shell_items()
    if oradio_items:
        return oradio_items

    out: List[StationInfo] = []
    if not os.path.exists(STATIONS_DIR):
        return out

    for name in sorted(os.listdir(STATIONS_DIR)):
        path = os.path.join(STATIONS_DIR, name)
        if not os.path.isdir(path):
            continue
        mp = station_manifest_path(path)
        if not os.path.exists(mp):
            continue
        cfg = safe_read_yaml(mp)
        out.append(StationInfo(station_id=name, path=path, manifest=cfg, launch_path=path))
    return out

# -----------------------------
# Runtime process management
# -----------------------------
class StationProcess:
    def __init__(self):
        self.proc: Optional[subprocess.Popen] = None
        self.station: Optional[StationInfo] = None
        self._log_file = None  # keep handle alive on Windows
        self._log_thread = None  # background thread for log capture

    def is_alive(self) -> bool:
        return self.proc is not None and self.proc.poll() is None

    def launch(self, station: StationInfo) -> None:
        print(f"DEBUG: StationProcess.launch() called")
        self.stop()

        env = os.environ.copy()
        env["STATION_DIR"] = station.path
        env["STATION_DB_PATH"] = station_db_path(station.path)
        env["STATION_MEMORY_PATH"] = station_memory_path(station.path)

        env.setdefault("RADIO_OS_ROOT", BASE)
        env.setdefault("RADIO_OS_PLUGINS", os.path.join(BASE, "plugins"))
        env.setdefault("RADIO_OS_VOICES", os.path.join(BASE, "voices"))
        
        # Inject Visual Model configuration from manifest > global config
        # 1. Start with global config
        global_cfg = get_global_config()
        
        # Apply environment variables from global config
        env_vars = global_cfg.get("environment", {})
        for var_name, var_value in env_vars.items():
            if var_value.strip():  # Only set non-empty values
                env[var_name] = var_value
        
        # Inject global API keys (OpenAI, etc) if not already in env
        default_models = global_cfg.get("default_models", {})
        openai_key = default_models.get("openai_api_key", "").strip()
        if openai_key and "OPENAI_API_KEY" not in env:
            env["OPENAI_API_KEY"] = openai_key

        visual_cfg = global_cfg.get("visual_models", {})
        
        # 2. Override with station manifest
        manifest = station.manifest or {}
        if "visual_models" in manifest:
            visual_cfg.update(manifest["visual_models"])
            
        if visual_cfg:
            env["VISUAL_MODEL_TYPE"] = str(visual_cfg.get("model_type", "local"))
            env["VISUAL_MODEL_LOCAL"] = str(visual_cfg.get("local_model", "llava:latest"))
            env["VISUAL_MODEL_API_PROVIDER"] = str(visual_cfg.get("api_provider", ""))
            env["VISUAL_MODEL_API_MODEL"] = str(visual_cfg.get("api_model", ""))
            env["VISUAL_MODEL_API_KEY"] = str(visual_cfg.get("api_key", ""))
            env["VISUAL_MODEL_API_ENDPOINT"] = str(visual_cfg.get("api_endpoint", ""))
            env["VISUAL_MODEL_MAX_IMAGE_SIZE"] = str(visual_cfg.get("max_image_size", "1024"))
            env["VISUAL_MODEL_IMAGE_QUALITY"] = str(visual_cfg.get("image_quality", "85"))

        # Ensure unbuffered UTF-8 output so logs are captured correctly
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUNBUFFERED"] = "1"

        log_dir = station.path if os.path.isdir(station.path) else os.path.dirname(station.path)
        log_path = os.path.join(log_dir, "runtime.log")
        lf = None
        try:
            lf = open(log_path, "a", encoding="utf-8", errors="ignore")
            lf.write("\n\n===== LAUNCH {} =====\n".format(time.strftime("%Y-%m-%d %H:%M:%S")))
            lf.flush()
        except Exception:
            lf = None

        if station.source_kind == "oradio":
            target = station.launch_path or station.path
            cmd = [sys.executable, "-u", ORADIO_PLAYER_PATH, target]
        else:
            cmd = [sys.executable, "-u", RUNTIME_PATH]
        print(f"DEBUG: Command: {cmd}")
        print(f"DEBUG: CWD: {BASE}")
        print(f"DEBUG: RUNTIME_PATH: {RUNTIME_PATH}")

        # Fix: Use subprocess.PIPE for stdout/stderr to avoid file descriptor issues
        # CRITICAL: Set encoding='utf-8' explicitly on Windows to handle emoji in output
        kwargs = {"cwd": BASE, "env": env, "stdout": subprocess.PIPE, "stderr": subprocess.STDOUT, "text": True, "encoding": "utf-8", "errors": "replace"}
        if sys.platform == "win32":
            # hide console window for runtime (Windows only)
            # NOTE: CREATE_NO_WINDOW can prevent win32gui.EnumWindows() from working correctly.
            # Set RADIO_OS_SHOW_CONSOLE=1 to disable this for window enumeration/debugging.
            if not os.environ.get("RADIO_OS_SHOW_CONSOLE"):
                try:
                    kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
                except Exception:
                    pass

        self._log_file = lf
        print(f"DEBUG: About to spawn subprocess...")
        try:
            self.proc = subprocess.Popen(cmd, **kwargs)
            print(f"DEBUG: Subprocess spawned, PID: {self.proc.pid}")
        except Exception as e:
            print(f"DEBUG ERROR: Failed to spawn subprocess: {e}")
            raise
        self.station = station
        _oled("enter_station", station_id=station.station_id)
        
        # Start a thread to capture and log output
        if self.proc and lf:
            import threading
            
            def log_output():
                try:
                    # Platform-specific handling for encoding edge cases
                    is_windows = sys.platform == "win32"
                    
                    while self.proc and self.proc.poll() is None:
                        line = self.proc.stdout.readline()
                        if line:
                            if is_windows:
                                # Windows: Extra error handling for charmap codec issues
                                try:
                                    # If line is bytes, decode with error handling
                                    if isinstance(line, bytes):
                                        line = line.decode('utf-8', errors='replace')
                                    lf.write(line)
                                    lf.flush()
                                except UnicodeDecodeError as ude:
                                    # Fallback: write sanitized version
                                    lf.write(f"[decode error in output: {ude}]\n")
                                    lf.flush()
                            else:
                                # Mac/Linux: Direct write (subprocess handles encoding)
                                lf.write(line)
                                lf.flush()
                        else:
                            break
                    # Get any remaining output
                    if self.proc and self.proc.stdout:
                        remaining = self.proc.stdout.read()
                        if remaining:
                            if is_windows:
                                try:
                                    if isinstance(remaining, bytes):
                                        remaining = remaining.decode('utf-8', errors='replace')
                                    lf.write(remaining)
                                    lf.flush()
                                except UnicodeDecodeError:
                                    pass  # Skip corrupted trailing output
                            else:
                                lf.write(remaining)
                                lf.flush()
                except Exception as e:
                    print(f"Log capture error: {e}")
            
            self._log_thread = threading.Thread(target=log_output, daemon=True)
            self._log_thread.start()

    def stop(self) -> None:
        if self.proc:
            try:
                self.proc.terminate()
            except Exception:
                pass
        _oled("exit_station")
        
        # Wait for log thread to finish
        if hasattr(self, '_log_thread') and self._log_thread and self._log_thread.is_alive():
            try:
                self._log_thread.join(timeout=2)
            except Exception:
                pass
        
        self.proc = None
        self.station = None
        self._log_thread = None
        
        try:
            if self._log_file:
                self._log_file.flush()
                self._log_file.close()
        except Exception:
            pass
        self._log_file = None

# -----------------------------
# Shell UI
# -----------------------------
class RadioShell:
    def __init__(self):
        # Load theme before creating UI
        cfg = get_global_config()
        theme_name = cfg.get("general", {}).get("theme", "dark")
        if theme_name in COLOR_THEMES:
            UI.update(COLOR_THEMES[theme_name])
        
        self.root = tk.Tk()
        self.root.title("Ribbon OS")
        self.root.geometry(scaled_geometry(1440, 860))
        self.root.configure(bg=UI["bg"])
        ribbon_theme_name = cfg.get("general", {}).get("ribbon_shell_theme", "midnight")
        self.ribbon_state = RibbonShellStateMachine(ribbon_theme_name)
        self.clock_var = tk.StringVar(value="")
        self._last_overlay_alpha = None
        self.ribbon_video = None
        self.ribbon_media_phase = "BOOT_SPLASH"
        self.ribbon_media_started = False
        self.ribbon_media_root = RIBBON_OS_MEDIA_ROOT
        # Per-tile ribbon state machine (port of main.gd's per-object machine):
        # the focused carousel tile's assigned ribbon becomes the background.
        self._ribbon_focus_cat = None       # ribbon folder currently shown
        self._pending_focus_station = None  # station to morph to once current segment ends
        self._current_oradio_id = None      # which .oradio's authored loop is on-screen (for carrier)
        self._path_token = 0                # bumps each traversal so a stale speed-of-light chain aborts

        self.proc = StationProcess()
        # The active loom drives doors/crossovers/attract keys + which loom the carousel shows.
        # Boot honors the last loom you were in (.active_loom.json), falling back to the primary;
        # right-click "Go to loom ▸" or the Loom app's "load into RibbonOS" swaps it (_switch_to_loom).
        self._active_loom_path: Optional[Path] = self._boot_active_loom()
        self._active_loom_id: str = self._loom_id_for(self._active_loom_path)
        try:
            write_active_loom_state(Path(BASE), self._active_loom_path)
        except Exception:
            pass
        # Load the carousel from the ACTIVE loom (not whatever _discover_primary_loom sorts first —
        # that picks alphabetically, so a newer loom like 'hoh' would otherwise shadow the loom you
        # were actually in). Matches refresh_stations.
        self.stations: List[StationInfo] = (
            load_oradio_shell_items_for(self._active_loom_path)
            if self._active_loom_path is not None else None
        ) or load_stations()
        # The Switch-style home is built from `home_tiles` (recency-ordered boxes +
        # an "All .oradios" overflow box). `selected_idx` indexes the TILES/cards,
        # not `self.stations`; use `_focused_station()` to get the focused station.
        self.home_tiles: List[Dict[str, Any]] = []
        self.selected_idx = 0

        # Spatial nav: the carousel can flip to a 3D galaxy map of oradio nodes.
        self.galaxy = GalaxyMap()
        self._nav_mode = "carousel"   # or "galaxy"
        self._gx_last = None
        self._gx_moved = False
        self._gx_press_node = None

        self._view = "home"  # or "runtime"
        self._transitioning = False

        self._build_styles()
        self._build_top_bar()
        self._build_home_view()
        self._build_runtime_view()
        self._init_ribbon_media()

        self._status_poll_ms = 450
        self._tick()

        self.show_home(instant=True)
        self._bind_shell_state_events()
        self._apply_ribbon_shell_state(force=True)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        _oled("boot")

    def _bind_shell_state_events(self):
        self.root.bind("<Motion>", lambda _e: self._note_shell_activity())
        self.root.bind("<Button-1>", lambda _e: self._note_shell_activity())
        self.root.bind("<MouseWheel>", lambda _e: self._note_shell_activity())
        self.root.bind("<Key>", lambda _e: self._note_shell_activity())
        self.root.bind("<F11>", lambda _e: self._toggle_fullscreen())

    def _note_shell_activity(self):
        self.ribbon_state.note_activity()
        self._start_ribbon_entry_if_needed()
        self._apply_ribbon_shell_state()

    def _toggle_fullscreen(self):
        try:
            current = bool(self.root.attributes("-fullscreen"))
            self.root.attributes("-fullscreen", not current)
        except Exception:
            pass
        self._note_shell_activity()

    def _init_ribbon_media(self):
        self.ribbon_video = RibbonVideoSurface(self.root, self.home, host_label=self.home_bg)
        self._start_ribbon_boot_sequence()

    def _ribbon_media_path(self, name: str) -> str:
        return os.path.join(self.ribbon_media_root, name)

    def _set_home_overlay(self, visible: bool):
        # Tiles float directly on the ribbon (no opaque field). "Hiding the overlay"
        # now means place_forget the tiles + hint so the bare ribbon shows full-screen
        # (boot splash/attract, and the 30s idle reveal); showing re-lays them out.
        # Any mouse move/key fires _note_shell_activity -> reveal, so tiles never strand.
        self._home_tiles_visible = visible
        try:
            if visible:
                self.home_hint.place(x=18, y=14)
                self._relayout(self.selected_idx, animate=False)
            else:
                self.home_hint.place_forget()
                for c in self.cards:
                    for key in ("frame", "title"):
                        w = c.get(key)
                        if w is not None:
                            try: w.place_forget()
                            except Exception: pass
        except Exception:
            pass

    def _start_ribbon_boot_sequence(self):
        if not self.ribbon_video or not self.ribbon_video.enabled:
            self.ribbon_media_phase = "HOME_LOOP"
            self.ribbon_media_started = True
            self._set_home_overlay(True)   # no ribbon video -> show the carousel
            return
        # Boot is a DISTINCT clip (seen once), NOT a loop. Play it full, then bridge its end into
        # the attract via our pts ENTRY ("boot exit -> pts entry"), then the pts loop.
        # boot.mp4 is the GENERAL-PURPOSE boot (cut from splash_screen_ribbon.ogv before its baked-in
        # old-pts-entry tail); its last frame is the exact continuation of boot_carrier_src.mp4, so
        # the pts entry carrier morphs out of it seamlessly. Falls back to the legacy splash clip.
        splash = self._ribbon_media_path("boot.mp4")
        if not os.path.exists(splash):
            splash = self._ribbon_media_path("splash_screen_ribbon.ogv")
        if self.ribbon_video.play(splash, loop=False, on_finished=self._on_boot_clip_finished):
            self.ribbon_media_phase = "BOOT_SPLASH"
            self._set_home_overlay(False)  # let the boot clip show full-screen
            return
        self._set_home_overlay(True)
        self._on_boot_clip_finished()

    def _on_boot_clip_finished(self):
        """The boot clip has played once. Bridge its end into the attract with our pts ENTRY (the
        boot-exit -> pts-entry transition). Falls straight to the pts loop if no entry was built."""
        pts_entry = self._resolve_attract_entry()
        if pts_entry and self.ribbon_video and self.ribbon_video.play(
                pts_entry, loop=False, on_finished=self._on_ribbon_splash_finished, fade_ms=200):
            self.ribbon_media_phase = "BOOT_EXIT"
            return
        self._on_ribbon_splash_finished()

    def _on_ribbon_splash_finished(self):
        self.ribbon_media_phase = "ATTRACT"
        self._play_ribbon_attract()

    def _resolve_attract_clip(self) -> Optional[str]:
        """The current loom-bookmark's generated push-to-start loop, if one was built. None falls
        back to the shipped ptsloop.ogv (e.g. an author's own Sora attract). See bookmark/door.py."""
        return self._resolve_attract_part("loop")

    def _resolve_attract_entry(self) -> Optional[str]:
        """boot -> pts: our generated transition INTO the attract loop (replaces the old splash)."""
        return self._resolve_attract_part("entry")

    def _resolve_attract_exit(self) -> Optional[str]:
        """pts -> bookmark: our generated transition OUT of attract (replaces the old entry.ogv)."""
        return self._resolve_attract_part("exit")

    def _boot_carrier_src(self) -> str:
        """The clip the boot->pts (and boot->bookmark door) carrier morphs OUT of. This is
        boot_carrier_src.mp4 = the 1s continuation of boot.mp4's last frame, so the carrier's first
        frame == the boot clip's last frame (no hardcut). Falls back to loop.ogv if not present."""
        cand = self._ribbon_media_path("boot_carrier_src.mp4")
        return cand if os.path.exists(cand) else self._ribbon_media_path("loop.ogv")

    def _boot_active_loom(self) -> Optional[Path]:
        """The loom to open on boot: the last one you were in (.active_loom.json, written whenever
        the active loom changes), falling back to the primary loom on disk."""
        try:
            from oradio_engine.loom_runtime import read_active_loom_state
            raw = str(read_active_loom_state(Path(BASE)).get("loom_path", "")).strip()
            if raw and os.path.exists(raw):
                return Path(raw)
        except Exception:
            pass
        return _discover_primary_loom()

    def _loom_id_for(self, loom_path: Optional[Path]) -> str:
        """The door/crossover key for a .loom: its universe id (fallback = file stem). Falls back
        to the legacy DEFAULT_LOOM_ID when there is no loom on disk at all."""
        if loom_path is None:
            return DEFAULT_LOOM_ID
        try:
            universe, _ = load_declaration_text(loom_path.read_text(encoding="utf-8"))
            if universe:
                return str(universe)
        except Exception:
            pass
        return loom_path.stem

    def _door_loom_id(self, loom_id: str) -> str:
        """Door/attract storage key for a loom, with legacy migration. Before looms were tracked
        the single door set was stored under DEFAULT_LOOM_ID ('default'); if `loom_id` has no
        door of its own yet but that legacy set exists, the ACTIVE loom inherits it so the
        existing boot/attract clips keep playing (no regression)."""
        try:
            from bookmark import door
            idx = door._load_index(CLUB_DIR)
        except Exception:
            idx = {}
        if loom_id in idx:
            return loom_id
        legacy = os.path.join(CLUB_DIR, "doors", DEFAULT_LOOM_ID)
        if loom_id == self._active_loom_id and os.path.isdir(legacy):
            return DEFAULT_LOOM_ID
        return loom_id

    def _resolve_attract_part(self, part: str) -> Optional[str]:
        try:
            from bookmark import door
            fn = {"loop": door.attract_clip_path, "entry": door.attract_entry_path,
                  "exit": door.attract_exit_path}[part]
            # Try the active loom's door key, then the legacy 'default' set. This matters because
            # once a loom enters the door index its key stops migrating to 'default' — but the pts
            # triptych may still live under 'default' (built before the loom had its own door). Fall
            # back so the themed pts keeps playing instead of dropping to the shipped ptsloop.ogv.
            seen = []
            for lid in (self._door_loom_id(self._active_loom_id), self._active_loom_id, DEFAULT_LOOM_ID):
                if not lid or lid in seen:
                    continue
                seen.append(lid)
                bm_id = door.get_bookmark(CLUB_DIR, lid)
                cand = str(fn(CLUB_DIR, lid, bm_id))
                if os.path.exists(cand):
                    return cand
            return None
        except Exception:
            return None

    def _play_ribbon_attract(self):
        if not self.ribbon_video:
            return
        # Prefer the loom's generated PTS (themed to its bookmark door); else the shipped attract.
        pts = self._resolve_attract_clip() or self._ribbon_media_path("ptsloop.ogv")
        if not self.ribbon_video.play(pts, loop=True, fade_ms=180):
            self._enter_ribbon_home_loop()

    def _start_ribbon_entry_if_needed(self):
        if self._view != "home":
            return
        if self.ribbon_media_started:
            return
        if self.ribbon_media_phase != "ATTRACT":
            return
        self.ribbon_media_started = True
        self.ribbon_media_phase = "ENTRY"
        if not self.ribbon_video:
            self.ribbon_media_phase = "HOME_LOOP"
            return
        # Prefer OUR generated pts EXIT (pts -> bookmark loop); it lands on the bookmark's first
        # frame, so _enter_ribbon_home_loop then settles into the authored loop seamlessly. Fall
        # back to the legacy entry.ogv when no pts exit was built.
        entry = self._resolve_attract_exit() or self._ribbon_media_path("entry.ogv")
        if not self.ribbon_video.play(entry, loop=False, on_finished=self._enter_ribbon_home_loop, fade_ms=260):
            self._enter_ribbon_home_loop()

    def _enter_ribbon_home_loop(self):
        self.ribbon_media_phase = "HOME_LOOP"
        self.ribbon_media_started = True
        self._set_home_overlay(True)   # reveal the carousel (ribbon keeps looping behind it)
        if not self.ribbon_video:
            return
        # Switch behavior: the background is the FOCUSED tile's ribbon. If a station
        # is focused, morph straight into its entry; otherwise the generic home loop.
        st = self._focused_station()
        if st is not None:
            if self._play_oradio_loop(st):   # a minted .oradio -> its authored loop
                return
            self._start_category_entry(st)
            return
        # DOOR: if this loom's bookmark door clip exists, transition THROUGH it into the bookmark
        # (boot screen -> door entry -> bookmark's loop). Fully guarded: a missing clip / failed
        # play() falls straight through to the generic home loop (no regression).
        door_info = self._resolve_boot_door()
        if door_info is not None:
            entry_clip, bm_station = door_info

            def _land_on_bookmark():
                target = None
                if bm_station is not None:
                    target = oradio_baked_loop(bm_station)   # the bookmark's authored loop
                    if target:
                        self._current_oradio_id = bm_station.station_id
                        self.ribbon_media_phase = "ORADIO_LOOP"
                    else:
                        target = ribbon_clip_for_station(bm_station, "loop")
                if not target:
                    target = self._ribbon_media_path("loop.ogv")
                self.ribbon_video.play(target, loop=True, fade_ms=240)

            if self.ribbon_video.play(entry_clip, loop=False,
                                      on_finished=_land_on_bookmark, fade_ms=240):
                return
        loop_path = self._ribbon_media_path("loop.ogv")
        self.ribbon_video.play(loop_path, loop=True, fade_ms=240)

    # -----------------------------
    # Per-tile ribbon state machine (port of main.gd per-object machine).
    # Drives the SINGLE existing RibbonVideoSurface (no compositor): the focused
    # carousel tile's assigned ribbon plays entry -> loop as the background, and
    # exit -> (next entry | home loop) when focus moves. Crossfade/REVERSING_ENTRY
    # are deliberately omitted per the locked spec.
    # -----------------------------
    def _loom_adjacency(self) -> Dict[str, List[str]]:
        """Undirected soulmate-bond graph over the current stations — the set of playable crossover
        edges (a bond is exactly where a crossover clip gets baked). Deterministic."""
        ids = {s.station_id for s in self.stations}
        adj: Dict[str, List[str]] = {}
        for s in self.stations:
            sm = list(getattr(s, "soulmates", []) or [])
            if not sm:
                one = getattr(s, "soulmate", "") or ""
                sm = [one] if one else []
            for m in sm:
                if m not in ids or m == s.station_id:
                    continue
                adj.setdefault(s.station_id, [])
                adj.setdefault(m, [])
                if m not in adj[s.station_id]:
                    adj[s.station_id].append(m)
                if s.station_id not in adj[m]:
                    adj[m].append(s.station_id)
        return adj

    def _loom_path(self, from_id: Optional[str], to_id: str) -> Optional[List[str]]:
        """Shortest soulmate-bond path [from_id, ..., to_id] via BFS (neighbours in sorted order =
        deterministic), or None if the two oradios aren't connected by authored bonds. The real
        route the speed-of-light traversal follows — never a direct dissolve across the graph."""
        if not from_id or from_id == to_id:
            return None
        adj = self._loom_adjacency()
        if from_id not in adj or to_id not in adj:
            return None
        from collections import deque
        prev: Dict[str, Optional[str]] = {from_id: None}
        q = deque([from_id])
        while q:
            u = q.popleft()
            if u == to_id:
                path: List[str] = []
                cur: Optional[str] = u
                while cur is not None:
                    path.append(cur)
                    cur = prev[cur]
                return list(reversed(path))
            for v in sorted(adj.get(u, ())):
                if v not in prev:
                    prev[v] = u
                    q.append(v)
        return None

    def _speed_of_light(self, legs: int) -> float:
        """Playback multiplier for a `legs`-long traversal: longer path -> quicker, capped. A
        single hop stays native (the transition plays at normal speed)."""
        if legs <= 1:
            return 1.0
        return clamp(1.0 + (legs - 1) * SPEED_OF_LIGHT_GAIN, 1.0, SPEED_OF_LIGHT_MAX)

    def _custom_crossover_path(self, from_id: str, to_id: str, loom_id: Optional[str] = None) -> str:
        """Where an AUTHOR's own crossover clip for from->to lives (durable; regen never wipes it).
        'Hard mode': the author owns making it seamless to the loops, in exchange for full freedom.
        Presence here overrides the generated carrier clip."""
        lid = loom_id or self._active_loom_id
        return os.path.join(CLUB_DIR, "crossovers", lid, "custom", f"{from_id}__{to_id}.entry.mp4")

    def _oradio_crossover_clip(self, from_id: Optional[str], to_id: str) -> Optional[str]:
        """The crossover clip from->to: an author's CUSTOM clip if present (wins), else the
        generated carrier clip baked Club-side. Checks the active loom id and the legacy default.
        Returns None for a standalone/unbonded oradio (caller dissolves)."""
        if not from_id or from_id == to_id:
            return None
        loom_ids = [self._active_loom_id, DEFAULT_LOOM_ID]
        rel = f"{from_id}__{to_id}.entry.mp4"
        # custom (author-provided, hard-mode) wins over the generated engine clip, in both looms
        for lid in loom_ids:
            cand = os.path.join(CLUB_DIR, "crossovers", lid, "custom", rel)
            if os.path.exists(cand):
                return cand
        for lid in loom_ids:
            cand = os.path.join(CLUB_DIR, "crossovers", lid, rel)
            if os.path.exists(cand):
                return cand
        return None

    def _play_oradio_loop(self, station: Optional["StationInfo"]) -> bool:
        """Show a minted .oradio's authored loop.mp4 as the background. If the target is 2+ soulmate
        jumps from the currently-shown oradio, TRAVERSE the real path — playing every crossover clip
        along it in sequence (never skipping one), sped up on a gradient by path length (speed of
        light) — then settle on the loop. A direct neighbour plays its single crossover at native
        speed. Returns False for non-oradio/legacy stations or if no loop."""
        if station is None or getattr(station, "source_kind", "") != "oradio":
            return False
        if not self.ribbon_video or not getattr(self.ribbon_video, "enabled", False):
            return False
        loop_path = oradio_baked_loop(station)
        if not loop_path:
            return False
        self._ribbon_focus_cat = None
        self._pending_focus_station = None
        self._path_token += 1   # supersede any in-flight traversal

        # The real route through the loom (iracing -> kernel -> cyberpunk), not a direct dissolve.
        path = self._loom_path(self._current_oradio_id, station.station_id)
        if path and len(path) >= 3:
            legs = [(a, b, self._oradio_crossover_clip(a, b)) for a, b in zip(path, path[1:])]
            if any(clip for _a, _b, clip in legs):
                return self._traverse_path(legs, station, loop_path)

        # Direct neighbour / unmapped: a single crossover (or a plain dissolve) at native speed.
        cross = self._oradio_crossover_clip(self._current_oradio_id, station.station_id)
        self._current_oradio_id = station.station_id
        self.ribbon_media_phase = "ORADIO_LOOP"
        self.ribbon_video.set_speed(1.0)
        if cross:
            self.ribbon_video.play(
                cross, loop=False,
                on_finished=lambda lp=loop_path: self.ribbon_video and self.ribbon_video.play(
                    lp, loop=True, fade_ms=200),
                fade_ms=200,
            )
        else:
            self.ribbon_video.play(loop_path, loop=True, fade_ms=220)
        return True

    def _traverse_path(self, legs, station: "StationInfo", loop_path: str) -> bool:
        """Speed-of-light: play each crossover clip along `legs` back-to-back (they splice through
        the shared boundary frames of the passed-through nodes), at a gradient speed set by path
        length, then land on the target loop. Guarded by a token so a fresh click aborts this run."""
        token = self._path_token
        self.ribbon_media_phase = "ORADIO_PATH"
        self.ribbon_video.set_speed(self._speed_of_light(len(legs)))

        def play_leg(i: int):
            if token != self._path_token:
                return   # superseded by a newer traversal/focus
            if i >= len(legs):
                # arrived: settle on the target loop and drop back to native speed
                self._current_oradio_id = station.station_id
                self.ribbon_media_phase = "ORADIO_LOOP"
                if self.ribbon_video:
                    self.ribbon_video.set_speed(1.0)
                    self.ribbon_video.play(loop_path, loop=True, fade_ms=200)
                return
            a, b, clip = legs[i]
            self._current_oradio_id = b   # we've passed through to b
            # First leg eases in from the current loop; mid-chain legs hard-splice (frames match).
            fade = 160 if i == 0 else 0
            if clip and self.ribbon_video and self.ribbon_video.play(
                    clip, loop=False, on_finished=lambda: play_leg(i + 1), fade_ms=fade):
                return
            play_leg(i + 1)   # a missing leg clip never strands the traversal

        play_leg(0)
        return True

    def _focus_station_ribbon(self, station: Optional["StationInfo"]):
        if station is None:
            return
        if not self.ribbon_video or not getattr(self.ribbon_video, "enabled", False):
            return
        # Don't hijack the boot chain or a loom door-swap; remember the target and let the
        # settling step (HOME_LOOP / _switch_to_loom._land) pick it up.
        if self.ribbon_media_phase in ("BOOT_SPLASH", "BOOT_EXIT", "ATTRACT", "ENTRY",
                                       "LOOM_EXIT", "LOOM_ENTRY"):
            self._pending_focus_station = station
            return
        # A minted .oradio shows its OWN authored loop (with a carrier crossover between oradios),
        # NOT the generic ribbon skin pack. Only legacy/skin stations fall through to the category
        # state machine below.
        if self._play_oradio_loop(station):
            return
        cat = ribbon_cat_for_station(station)
        if self._ribbon_focus_cat == cat and self.ribbon_media_phase in ("CATEGORY_ENTERING", "CATEGORY_LOOPING"):
            return  # already showing this skin
        self._pending_focus_station = station
        if self.ribbon_media_phase in ("CATEGORY_ENTERING", "CATEGORY_LOOPING"):
            self._start_category_exit()
        elif self.ribbon_media_phase == "CATEGORY_EXITING":
            return  # exit in flight; its on_finished consumes _pending_focus_station
        else:
            self._start_category_entry(station)

    def _start_category_entry(self, station: "StationInfo"):
        self._ribbon_focus_cat = ribbon_cat_for_station(station)
        self._pending_focus_station = None
        self.ribbon_media_phase = "CATEGORY_ENTERING"
        entry = ribbon_clip_for_station(station, "entry")
        if not self.ribbon_video.play(entry, loop=False, on_finished=self._on_category_entry_finished, fade_ms=160):
            self._on_category_entry_finished()

    def _on_category_entry_finished(self):
        if self.ribbon_media_phase != "CATEGORY_ENTERING":
            return
        # focus changed mid-entry -> exit toward the newest target
        nxt = self._pending_focus_station
        if nxt is not None and ribbon_cat_for_station(nxt) != self._ribbon_focus_cat:
            self._start_category_exit()
            return
        self._start_category_loop()

    def _start_category_loop(self):
        self.ribbon_media_phase = "CATEGORY_LOOPING"
        # Arrived: the transition is over, so drop speed-of-light back to native.
        if self.ribbon_video:
            self.ribbon_video.set_speed(1.0)
        if not self._ribbon_focus_cat:
            return
        loop_path = os.path.join(ribbon_dir_for_cat(self._ribbon_focus_cat), "loop.ogv")
        self.ribbon_video.play(loop_path, loop=True, fade_ms=200)

    def _start_category_exit(self):
        if not self._ribbon_focus_cat:
            self._return_home_ribbon()
            return
        self.ribbon_media_phase = "CATEGORY_EXITING"
        exit_path = os.path.join(ribbon_dir_for_cat(self._ribbon_focus_cat), "exit.ogv")
        if not self.ribbon_video.play(exit_path, loop=False, on_finished=self._on_category_exit_finished, fade_ms=140):
            self._on_category_exit_finished()

    def _on_category_exit_finished(self):
        if self.ribbon_media_phase != "CATEGORY_EXITING":
            return
        nxt = self._pending_focus_station
        if nxt is not None:
            self._start_category_entry(nxt)
        else:
            self._return_home_ribbon()

    def _return_home_ribbon(self):
        self._ribbon_focus_cat = None
        self.ribbon_media_phase = "HOME_LOOP"
        if not self.ribbon_video:
            return
        loop_path = self._ribbon_media_path("loop.ogv")
        self.ribbon_video.play(loop_path, loop=True, fade_ms=200)

    def _refresh_ui_colors(self):
        """Refresh all UI elements with current theme colors."""
        # Update window background
        self.root.configure(bg=UI["bg"])
        
        # Update all frames and widgets recursively
        def update_widget_colors(widget):
            try:
                # Try common color options
                if hasattr(widget, 'configure'):
                    try:
                        widget.configure(bg=UI["bg"])
                    except:
                        pass
                    try:
                        widget.configure(fg=UI["text"])
                    except:
                        pass
            except:
                pass
            
            # Recurse on children
            for child in widget.winfo_children():
                update_widget_colors(child)
        
        # Update theme styles
        self._build_styles()
        
        # Update main widget tree
        update_widget_colors(self.root)
        
        # Force redraw
        self.root.update()

    def _restart_app(self):
        """Restart the application by closing and reopening."""
        import subprocess
        import sys
        
        # Save the current script path
        script_path = sys.argv[0]
        
        # Close the current app
        self.root.quit()
        self.root.destroy()
        
        # Restart the app in a new process
        subprocess.Popen([sys.executable, script_path])
        
        # Exit cleanly
        sys.exit(0)

    def _build_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure("TNotebook", background=UI["bg"], borderwidth=0)
        style.configure("TNotebook.Tab", background=UI["panel"], foreground=UI["text"], padding=(12, 8))
        style.map("TNotebook.Tab", background=[("selected", UI["card_hover"])])
        style.configure("TSeparator", background=UI["panel"])
    def delete_station(self, station_id: str):
        # Find station object
        st = None
        for s in self.stations:
            if s.station_id == station_id:
                st = s
                break

        if not st:
            return

        # Confirm
        if not messagebox.askyesno(
            "Delete Station",
            f"Delete station '{st.station_id}'?\n\nThis cannot be undone."
        ):
            return

        # If it's currently running → stop it cleanly
        if self.proc.station and self.proc.station.station_id == station_id:
            self.proc.stop()

        # Delete folder
        try:
            shutil.rmtree(st.path)
        except Exception as e:
            messagebox.showerror("Delete failed", str(e))
            return

        # Refresh UI list
        self.refresh_stations()


    def on_station_right_click(self, event, station_id):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(
            label="Set as bookmark (loom door)",
            command=lambda: self._set_station_as_bookmark(station_id)
        )
        # Picture frame submenu — distinct decorative frames for this oradio's carousel icon.
        try:
            frame_menu = tk.Menu(menu, tearoff=0)
            current = self._picture_frame_brick().get_assignment(station_id)
            for fid in ("none", "gold", "neon", "double", "embers", "glass"):
                frame_menu.add_command(
                    label=("● " if fid == current else "   ") + fid,
                    command=lambda f=fid, s=station_id: self._set_station_frame(s, f),
                )
            menu.add_cascade(label="Picture frame", menu=frame_menu)
        except Exception:
            pass
        # Go to loom — "you take your door to their door": swap the active loom via the carrier
        # door (exit this loom's door -> enter the next loom's door). Lists every OTHER loom.
        try:
            others = [(lp, lid, lbl) for (lp, lid, lbl) in _discover_all_looms()
                      if lid != self._active_loom_id]
            if others:
                loom_menu = tk.Menu(menu, tearoff=0)
                for lp, lid, lbl in others:
                    loom_menu.add_command(
                        label=lbl,
                        command=lambda p=lp, i=lid: self._switch_to_loom(i, p),
                    )
                menu.add_separator()
                menu.add_cascade(label="Go to loom ▸", menu=loom_menu)
        except Exception:
            pass
        menu.add_separator()
        menu.add_command(
            label="Edit .oradio…",
            command=lambda: self._edit_oradio(station_id)
        )
        menu.add_command(
            label="Edit crossover…",
            command=lambda: self._edit_crossover(station_id)
        )
        menu.add_separator()
        menu.add_command(
            label="Delete Station",
            command=lambda: self.delete_station(station_id)
        )
        menu.tk_popup(event.x_root, event.y_root)

    def _edit_oradio(self, station_id: str):
        """Inspect + basic edits for a minted .oradio: see its title / declaration / bricks, and
        attach (or replace / remove) a PNG thumbnail (the card + galaxy icon) or an MP3 soundtrack.
        Edits patch the bundle in place via bookmark.mint.set_bundle_asset — no re-mint."""
        station = next((s for s in self.stations if s.station_id == station_id), None)
        path = str(getattr(station, "launch_path", "") or "") if station else ""
        if station is None or not (path.lower().endswith(".oradio") and zipfile.is_zipfile(path)):
            messagebox.showinfo("Edit .oradio", "Only minted .oradio bundles can be edited.")
            return
        desc = getattr(station, "descriptor", None) or {}

        def _bundle_names():
            try:
                with zipfile.ZipFile(path) as zf:
                    return set(zf.namelist())
            except Exception:
                return set()

        win = tk.Toplevel(self.root)
        win.title(f"Edit .oradio — {self._station_title(station)}")
        win.configure(bg=UI["bg"]); win.geometry("600x580"); win.transient(self.root); win.grab_set()

        tk.Label(win, text=self._station_title(station), bg=UI["bg"], fg=UI["accent"],
                 font=FONT_H1).pack(anchor="w", padx=18, pady=(16, 2))
        tk.Label(win, text=os.path.basename(path), bg=UI["bg"], fg=UI["muted"],
                 font=FONT_SMALL).pack(anchor="w", padx=18)

        # ---- Inspect (read-only) ----
        insp = tk.Frame(win, bg=UI["card"]); insp.pack(fill="x", padx=18, pady=(14, 8))
        tk.Label(insp, text="Inspect", bg=UI["card"], fg=UI["accent"], font=FONT_BODY).pack(
            anchor="w", padx=12, pady=(10, 4))

        def _irow(k, v):
            r = tk.Frame(insp, bg=UI["card"]); r.pack(fill="x", padx=12, pady=3)
            tk.Label(r, text=k, bg=UI["card"], fg=UI["muted"], font=FONT_SMALL, width=12,
                     anchor="nw").pack(side="left")
            tk.Label(r, text=v, bg=UI["card"], fg=UI["text"], font=FONT_SMALL, anchor="w",
                     justify="left", wraplength=420).pack(side="left", fill="x", expand=True)

        bricks = list(desc.get("bricks") or [])
        _irow("id", str(desc.get("oradio") or station_id))
        _irow("title", str(desc.get("title") or "—"))
        _irow("declaration", str(desc.get("declaration") or "—"))
        _irow("bricks", "\n".join(bricks) if bricks else "— none —")
        _irow("kernel", "yes" if desc.get("kernel") else "no")
        tk.Frame(insp, bg=UI["card"], height=8).pack()

        status = tk.Label(win, text="", bg=UI["bg"], fg=UI["muted"], font=FONT_SMALL)
        pres = {"thumbnail.png": None, "audio.mp3": None}

        def _refresh_presence():
            names = _bundle_names()
            if pres["thumbnail.png"] is not None:
                pres["thumbnail.png"].config(
                    text=("✓ thumbnail.png attached" if "thumbnail.png" in names else "no thumbnail yet"))
            if pres["audio.mp3"] is not None:
                pres["audio.mp3"].config(
                    text=("✓ audio.mp3 attached" if "audio.mp3" in names else "no soundtrack yet"))

        def _after_change(msg):
            # The zip mtime changed -> the loop/thumb caches (keyed by mtime) refresh on reload.
            try:
                self.refresh_stations(select_id=station_id)
            except Exception:
                pass
            _refresh_presence()
            status.config(text=msg, fg=UI["accent"])

        def _set_asset(bundle_name, manifest_key, filetypes, title):
            p = filedialog.askopenfilename(title=title, filetypes=filetypes)
            if not p:
                return
            try:
                from bookmark.mint import set_bundle_asset
                set_bundle_asset(path, src=p, bundle_name=bundle_name, manifest_key=manifest_key)
                _after_change(f"{manifest_key} set ✓")
            except Exception as e:
                status.config(text=f"could not set {manifest_key}: {e}", fg="#b85c5c")

        def _remove_asset(bundle_name, manifest_key):
            try:
                from bookmark.mint import set_bundle_asset
                set_bundle_asset(path, src=None, bundle_name=bundle_name, manifest_key=manifest_key)
                _after_change(f"{manifest_key} removed")
            except Exception as e:
                status.config(text=f"could not remove {manifest_key}: {e}", fg="#b85c5c")

        ed = tk.Frame(win, bg=UI["bg"]); ed.pack(fill="x", padx=18, pady=(6, 4))

        tk.Label(ed, text="Thumbnail (PNG) — the card & galaxy icon", bg=UI["bg"], fg=UI["text"],
                 font=FONT_BODY).pack(anchor="w", pady=(8, 2))
        trow = tk.Frame(ed, bg=UI["bg"]); trow.pack(fill="x")
        pres["thumbnail.png"] = tk.Label(trow, text="", bg=UI["bg"], fg=UI["muted"], font=FONT_SMALL)
        pres["thumbnail.png"].pack(side="left")
        tk.Button(trow, text="Set PNG…", cursor="hand2", relief="flat", bd=0, padx=12, pady=5,
                  bg=UI["card"], fg=UI["text"],
                  command=lambda: _set_asset("thumbnail.png", "thumbnail",
                                             [("PNG image", "*.png"), ("Images", "*.png *.jpg *.jpeg *.webp"), ("All", "*.*")],
                                             "Choose a PNG thumbnail")).pack(side="right")
        tk.Button(trow, text="Remove", cursor="hand2", relief="flat", bd=0, padx=10, pady=5,
                  bg=UI["card"], fg=UI["muted"],
                  command=lambda: _remove_asset("thumbnail.png", "thumbnail")).pack(side="right", padx=(0, 8))

        tk.Label(ed, text="Soundtrack (MP3)", bg=UI["bg"], fg=UI["text"], font=FONT_BODY).pack(
            anchor="w", pady=(14, 2))
        arow = tk.Frame(ed, bg=UI["bg"]); arow.pack(fill="x")
        pres["audio.mp3"] = tk.Label(arow, text="", bg=UI["bg"], fg=UI["muted"], font=FONT_SMALL)
        pres["audio.mp3"].pack(side="left")
        tk.Button(arow, text="Set MP3…", cursor="hand2", relief="flat", bd=0, padx=12, pady=5,
                  bg=UI["card"], fg=UI["text"],
                  command=lambda: _set_asset("audio.mp3", "audio",
                                             [("MP3 audio", "*.mp3"), ("Audio", "*.mp3 *.wav *.ogg *.m4a"), ("All", "*.*")],
                                             "Choose an MP3 soundtrack")).pack(side="right")
        tk.Button(arow, text="Remove", cursor="hand2", relief="flat", bd=0, padx=10, pady=5,
                  bg=UI["card"], fg=UI["muted"],
                  command=lambda: _remove_asset("audio.mp3", "audio")).pack(side="right", padx=(0, 8))

        status.pack(anchor="w", padx=18, pady=(12, 0))
        tk.Button(win, text="Done", command=win.destroy, bg="#3a6b4a", fg="#ffffff", relief="flat",
                  bd=0, padx=16, pady=7, font=FONT_BODY, cursor="hand2").pack(side="bottom", pady=14)
        _refresh_presence()

    def _edit_crossover(self, station_id: str):
        """Manage this node's CUSTOM crossover clips — 'hard mode' for editors who want to drop in
        their own (e.g. Sora) transitions instead of the carrier default. Lists the node's bonded
        edges, BOTH directions; a custom clip present overrides the engine, removing it reverts.
        The author owns seamlessness (the clip should start on the from-loop's last frame and end
        on the to-loop's first). Stored durably in club/crossovers/<loom>/custom (regen never wipes
        it); see _oradio_crossover_clip / _custom_crossover_path."""
        node = next((s for s in self.stations if s.station_id == station_id), None)
        if node is None:
            return
        neighbors = self._loom_adjacency().get(station_id, [])
        title_of = {s.station_id: self._station_title(s) for s in self.stations}
        try:
            from oradio_engine.loom_runtime import load_edge_styles, edge_style_key
            from bookmark.transitions import CARRIER_PROFILES
            styles = load_edge_styles(CLUB_DIR, self._active_loom_id)
            profile_names = list(CARRIER_PROFILES.keys())
        except Exception:
            styles, profile_names, edge_style_key = {}, ["ribbon_drift"], (lambda a, b: f"{a}__{b}")

        win = tk.Toplevel(self.root)
        win.title(f"Edit crossover — {self._station_title(node)}")
        win.configure(bg=UI["bg"]); win.geometry("660x560"); win.transient(self.root); win.grab_set()
        tk.Label(win, text=f"Crossovers · {self._station_title(node)}", bg=UI["bg"], fg=UI["accent"],
                 font=FONT_H1).pack(anchor="w", padx=18, pady=(16, 2))
        tk.Label(win, text="Each edge has a STYLE (transition personality, default ribbon_drift) — "
                           "regenerated on change.\nOr go hard mode: drop your OWN clip per direction "
                           "(you own seamlessness); a custom clip overrides the style.",
                 bg=UI["bg"], fg=UI["muted"], font=FONT_SMALL, justify="left").pack(anchor="w", padx=18)

        status = tk.Label(win, text="", bg=UI["bg"], fg=UI["muted"], font=FONT_SMALL)

        body = tk.Frame(win, bg=UI["bg"]); body.pack(fill="both", expand=True, padx=18, pady=(12, 4))
        if not neighbors:
            tk.Label(body, text="This oradio has no soulmate bonds yet — bond it in Loom to add a "
                                "crossover edge.", bg=UI["bg"], fg=UI["muted"], font=FONT_BODY,
                     wraplength=580, justify="left").pack(anchor="w", pady=10)

        def _dir_row(parent, from_id, to_id):
            rowf = tk.Frame(parent, bg=UI["card"]); rowf.pack(fill="x", pady=3)
            tk.Label(rowf, text=f"{title_of.get(from_id, from_id)}  →  {title_of.get(to_id, to_id)}",
                     bg=UI["card"], fg=UI["text"], font=FONT_SMALL, anchor="w").pack(side="left", padx=12, pady=7)
            st_lbl = tk.Label(rowf, text="", bg=UI["card"], fg=UI["muted"], font=FONT_SMALL)
            st_lbl.pack(side="left", padx=8)

            def refresh():
                custom = os.path.exists(self._custom_crossover_path(from_id, to_id))
                st_lbl.config(text=("● custom clip" if custom else "○ carrier default"),
                              fg=(UI["accent"] if custom else UI["muted"]))
                rm_btn.config(state=("normal" if custom else "disabled"))

            def use_clip():
                p = filedialog.askopenfilename(title="Choose a crossover clip",
                                               filetypes=[("Video", "*.mp4 *.mov *.webm *.mkv"), ("All", "*.*")])
                if not p:
                    return
                try:
                    dst = self._custom_crossover_path(from_id, to_id)
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copyfile(p, dst)
                    status.config(text=f"custom set · {title_of.get(from_id, from_id)} → "
                                       f"{title_of.get(to_id, to_id)}", fg=UI["accent"])
                    refresh()
                except Exception as e:
                    status.config(text=f"could not set clip: {e}", fg="#b85c5c")

            def remove():
                try:
                    dst = self._custom_crossover_path(from_id, to_id)
                    if os.path.exists(dst):
                        os.remove(dst)
                    status.config(text="reverted to carrier default", fg=UI["muted"])
                    refresh()
                except Exception as e:
                    status.config(text=f"could not remove: {e}", fg="#b85c5c")

            rm_btn = tk.Button(rowf, text="Remove", command=remove, bg=UI["card"], fg=UI["muted"],
                               relief="flat", bd=0, padx=10, pady=5, cursor="hand2")
            rm_btn.pack(side="right", padx=(0, 8))
            tk.Button(rowf, text="Use my clip…", command=use_clip, bg=UI["card"], fg=UI["text"],
                      relief="flat", bd=0, padx=12, pady=5, cursor="hand2").pack(side="right", padx=(0, 8))
            refresh()

        for n in neighbors:
            edge = tk.Frame(body, bg=UI["bg"]); edge.pack(fill="x", pady=(10, 2))
            hdr = tk.Frame(edge, bg=UI["bg"]); hdr.pack(fill="x")
            tk.Label(hdr, text=f"↔ {title_of.get(n, n)}", bg=UI["bg"], fg=UI["accent"],
                     font=FONT_BODY).pack(side="left")
            # the edge's transition PERSONALITY (style) — both directions share it; regen on change.
            cur = styles.get(edge_style_key(station_id, n), "ribbon_drift")
            var = tk.StringVar(value=cur)
            combo = ttk.Combobox(hdr, textvariable=var, values=profile_names, width=14, state="readonly")
            combo.pack(side="right")
            tk.Label(hdr, text="style:", bg=UI["bg"], fg=UI["muted"], font=FONT_SMALL).pack(
                side="right", padx=(0, 6))
            combo.bind("<<ComboboxSelected>>",
                       lambda _e, nn=n, v=var: self._apply_edge_style(station_id, nn, v.get(), status))
            _dir_row(edge, station_id, n)   # this node -> neighbour
            _dir_row(edge, n, station_id)   # neighbour -> this node

        status.pack(anchor="w", padx=18, pady=(8, 0))
        tk.Button(win, text="Done", command=win.destroy, bg="#3a6b4a", fg="#ffffff", relief="flat",
                  bd=0, padx=16, pady=7, font=FONT_BODY, cursor="hand2").pack(side="bottom", pady=14)

    def _apply_edge_style(self, a: str, b: str, profile: str, status_lbl):
        """Set an edge's transition personality (styles.json) and rebake JUST that edge in the
        background (carrier render ~tens of seconds), streaming progress into status_lbl. A custom
        clip, if present, still wins at playback — this only changes the generated style underneath."""
        try:
            from oradio_engine.loom_runtime import set_edge_style, sync_crossovers
            from oradio_engine.loom_graph import load_declaration_text
        except Exception as e:
            status_lbl.config(text=f"style engine unavailable: {e}", fg="#b85c5c")
            return
        try:
            set_edge_style(CLUB_DIR, self._active_loom_id, a, b, profile)
        except Exception as e:
            status_lbl.config(text=f"could not set style: {e}", fg="#b85c5c")
            return
        loom_path = getattr(self, "_active_loom_path", None)
        if not loom_path or not os.path.exists(str(loom_path)):
            status_lbl.config(text=f"style set: {profile} (no loom on disk to rebake)", fg=UI["accent"])
            return
        try:
            universe, nodes = load_declaration_text(Path(loom_path).read_text(encoding="utf-8"))
        except Exception as e:
            status_lbl.config(text=f"style set; couldn't read loom to rebake: {e}", fg="#b85c5c")
            return
        status_lbl.config(text=f"baking {profile} · {a} ↔ {b}…", fg=UI["muted"])

        def on_prog(done, total, _label):
            self.root.after(0, lambda: status_lbl.config(
                text=f"baking {profile} · {a} ↔ {b} · {min(done + 1, total)}/{total}…"))

        def worker():
            try:
                sync_crossovers(Path(BASE), Path(loom_path), universe, nodes,
                                only_edge=(a, b), on_progress=on_prog)
                self.root.after(0, lambda: status_lbl.config(
                    text=f"✓ {profile} · {a} ↔ {b}", fg=UI["accent"]))
            except Exception as e:
                self.root.after(0, lambda: status_lbl.config(text=f"rebake failed: {e}", fg="#b85c5c"))

        import threading
        threading.Thread(target=worker, daemon=True).start()

    def _set_station_as_bookmark(self, station_id: str):
        """Make this oradio the current loom's bookmark (the boot 'door'). Records the flag, then
        builds the deterministic boot<->bookmark door clips in the background (best-effort, so the
        UI never blocks on the render). See bookmark/door.py."""
        station = next((s for s in self.stations if s.station_id == station_id), None)
        if station is None:
            return
        lid = self._active_loom_id
        try:
            from bookmark import door
            door.set_bookmark(CLUB_DIR, lid, station_id)
        except Exception:
            return
        try:
            self.mode_lbl.config(text=f"Bookmark set: {station_id} (building door…)")
        except Exception:
            pass
        boot_loop = self._boot_carrier_src()
        # Build the door INTO the oradio's authored loop (fall back to the skin if not minted yet).
        bm_loop = oradio_baked_loop(station) or ribbon_clip_for_station(station, "loop")

        def _build():
            ok = False
            try:
                from bookmark import door
                door.build_boot_door(boot_loop, bm_loop, loom_id=lid,
                                     bookmark_id=station_id, club_dir=CLUB_DIR)
                ok = True
            except Exception:
                ok = False
            try:
                msg = (f"Bookmark door ready: {station_id}" if ok
                       else f"Bookmark set: {station_id} (door build skipped)")
                self.root.after(0, lambda: self.mode_lbl.config(text=msg))
            except Exception:
                pass

        import threading
        threading.Thread(target=_build, daemon=True).start()

    def _resolve_boot_door(self):
        """Return (entry_clip_path, bookmark_station|None) if the current loom's boot door clip
        exists, else None. Used by the boot chain to transition into the bookmark."""
        try:
            from bookmark import door
            seen = []
            for lid in (self._door_loom_id(self._active_loom_id), self._active_loom_id, DEFAULT_LOOM_ID):
                if not lid or lid in seen:
                    continue
                seen.append(lid)
                bm_id = door.get_bookmark(CLUB_DIR, lid)
                entry = os.path.join(CLUB_DIR, "doors", lid, f"boot__{bm_id}.entry.mp4")
                if os.path.exists(entry):
                    bm_station = next((s for s in self.stations if s.station_id == bm_id), None)
                    return (entry, bm_station)
            return None
        except Exception:
            return None

    def _switch_to_loom(self, target_id: str, target_path: Path):
        """Carrier door swap ("you take your door to their door"): play the ACTIVE loom's door
        EXIT (bmA -> boot), then the TARGET loom's door ENTRY (boot -> bmB) — the two splice
        through the shared boot frame, so the boot clip itself is optional between them — then
        land on bmB's authored loop and reload the carousel from loom B. Fully guarded: any
        missing clip or failed play() falls through to a plain reload + fade (never a black
        screen). See memory loom-switching-brief / bookmark/door.py."""
        if target_id == self._active_loom_id:
            return
        try:
            from bookmark import door
            active_door = self._door_loom_id(self._active_loom_id)
            target_door = self._door_loom_id(target_id)
            bmA = door.get_bookmark(CLUB_DIR, active_door)
            bmB = door.get_bookmark(CLUB_DIR, target_door)
        except Exception:
            active_door = self._active_loom_id
            target_door = target_id
            bmA = bmB = None
        exit_clip = (os.path.join(CLUB_DIR, "doors", active_door, f"boot__{bmA}.exit.mp4")
                     if bmA else "")
        entry_clip = (os.path.join(CLUB_DIR, "doors", target_door, f"boot__{bmB}.entry.mp4")
                      if bmB else "")

        def _land():
            # Arrived on loom B: adopt it, reload the carousel/galaxy, settle into bmB's loop.
            self._active_loom_id = target_id
            self._active_loom_path = target_path
            try:
                write_active_loom_state(Path(BASE), target_path)
            except Exception:
                pass
            self.stations = load_oradio_shell_items_for(target_path) or []
            self._current_oradio_id = None
            self._ribbon_focus_cat = None
            self._pending_focus_station = None
            self.selected_idx = 0
            try:
                self._render_cards()
                if self._nav_mode == "galaxy":
                    self.galaxy.set_nodes(self.stations)
                    self._attach_galaxy_thumbs()
                self._relayout(self.selected_idx, animate=False)
            except Exception:
                pass
            self._set_home_overlay(True)
            self.ribbon_media_phase = "HOME_LOOP"
            st = (next((s for s in self.stations if s.station_id == bmB), None)
                  or self._focused_station())
            if st is not None and self._play_oradio_loop(st):
                return
            if self.ribbon_video:
                self.ribbon_video.play(self._ribbon_media_path("loop.ogv"), loop=True, fade_ms=240)

        def _enter():
            if (entry_clip and os.path.exists(entry_clip) and self.ribbon_video
                    and self.ribbon_video.play(entry_clip, loop=False,
                                               on_finished=_land, fade_ms=240)):
                self.ribbon_media_phase = "LOOM_ENTRY"
                return
            _land()

        try:
            self.mode_lbl.config(text=f"Going to loom: {target_id}…")
        except Exception:
            pass
        if (exit_clip and os.path.exists(exit_clip) and self.ribbon_video
                and self.ribbon_video.play(exit_clip, loop=False,
                                           on_finished=_enter, fade_ms=240)):
            self.ribbon_media_phase = "LOOM_EXIT"
            return
        _enter()

    def _refresh_via_door(self):
        """Refresh the current loom as a real traversal: current station -> bookmark door -> boot
        -> back through the same door entry. No prompt, no PTS, just the visual route."""
        target_path = self._active_loom_path or _discover_primary_loom()
        if target_path is None:
            self.refresh_stations()
            return
        loom_id = self._active_loom_id or self._loom_id_for(target_path)
        try:
            from bookmark import door
            door_id = self._door_loom_id(loom_id)
            bookmark_id = door.get_bookmark(CLUB_DIR, door_id)
        except Exception:
            door_id = loom_id
            bookmark_id = ""
        if not bookmark_id:
            self.refresh_stations()
            return

        bookmark_station = next((s for s in self.stations if s.station_id == bookmark_id), None)
        exit_clip = os.path.join(CLUB_DIR, "doors", door_id, f"boot__{bookmark_id}.exit.mp4")
        entry_clip = os.path.join(CLUB_DIR, "doors", door_id, f"boot__{bookmark_id}.entry.mp4")
        bridge_clip = self._oradio_crossover_clip(self._current_oradio_id, bookmark_id)

        def _land():
            self._active_loom_path = target_path
            self._active_loom_id = loom_id
            try:
                write_active_loom_state(Path(BASE), target_path)
            except Exception:
                pass
            self.refresh_stations(select_id=bookmark_id)
            self._set_home_overlay(True)
            self.ribbon_media_phase = "HOME_LOOP"
            st = next((s for s in self.stations if s.station_id == bookmark_id), None) or bookmark_station
            if st is not None and self._play_oradio_loop(st):
                return
            if self.ribbon_video:
                self.ribbon_video.play(self._ribbon_media_path("loop.ogv"), loop=True, fade_ms=240)

        def _enter():
            if (entry_clip and os.path.exists(entry_clip) and self.ribbon_video
                    and self.ribbon_video.play(entry_clip, loop=False, on_finished=_land, fade_ms=220)):
                self.ribbon_media_phase = "LOOM_ENTRY"
                return
            _land()

        def _exit():
            if (exit_clip and os.path.exists(exit_clip) and self.ribbon_video
                    and self.ribbon_video.play(exit_clip, loop=False, on_finished=_enter, fade_ms=220)):
                self.ribbon_media_phase = "LOOM_EXIT"
                return
            _enter()

        try:
            self.mode_lbl.config(text=f"Refreshing loom: {loom_id}…")
        except Exception:
            pass

        if (bridge_clip and os.path.exists(bridge_clip) and self.ribbon_video
                and self.ribbon_video.play(bridge_clip, loop=False, on_finished=_exit, fade_ms=180)):
            self.ribbon_media_phase = "ORADIO_LOOP"
            self._current_oradio_id = bookmark_id
            return
        _exit()

    def _build_plugin_manager(self, parent):

        plugins = discover_plugins()

        tk.Label(
            parent,
            text="Installed Plugins",
            font=FONT_H2,
            fg=UI["text"],
            bg=UI["bg"]
        ).pack(anchor="w", padx=14, pady=(14, 10))

        if not plugins:
            tk.Label(
                parent,
                text="No plugins found in /plugins folder.",
                font=FONT_BODY,
                fg=UI["muted"],
                bg=UI["bg"]
            ).pack(anchor="w", padx=14)
            return

        # ============================
        # Scroll container
        # ============================

        scrollbar = tk.Scrollbar(parent, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        canvas = tk.Canvas(parent, bg=UI["bg"], highlightthickness=0, yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar.configure(command=canvas.yview)

        frame = tk.Frame(canvas, bg=UI["bg"])
        canvas.create_window((0, 0), window=frame, anchor="nw")

        frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        # ============================
        # Current station feeds
        # ============================

        st = self.proc.station or self._focused_station() or (self.stations[0] if self.stations else None)

        feeds = {}
        if st:
            feeds = st.manifest.get("feeds", {})
            if not isinstance(feeds, dict):
                feeds = {}

        # ============================
        # Build rows
        # ============================

        for name, info in plugins.items():

            # 👉 Skip widget-only plugins
            if not info.get("is_feed", True):
                continue

            row = tk.Frame(frame, bg=UI["panel"])
            row.pack(fill="x", padx=14, pady=6)

            left = tk.Frame(row, bg=UI["panel"])
            left.pack(side="left", fill="x", expand=True)

            tk.Label(
                left,
                text=info["display"],
                font=("Segoe UI", 12, "bold"),
                fg=UI["text"],
                bg=UI["panel"]
            ).pack(anchor="w", padx=10, pady=(6, 0))

            if info.get("desc"):
                tk.Label(
                    left,
                    text=info["desc"],
                    font=FONT_SMALL,
                    fg=UI["muted"],
                    bg=UI["panel"]
                ).pack(anchor="w", padx=10, pady=(0, 6))

            # ----------------------------
            # Enabled toggle
            # ----------------------------

            enabled = bool(feeds.get(name, {}).get("enabled", False))
            v_en = tk.BooleanVar(value=enabled)

            def toggle(n=name, var=v_en):

                st2 = self.proc.station or self._focused_station() or (
                    self.stations[0] if self.stations else None
                )

                if not st2:
                    return

                mp = station_manifest_path(st2.path)
                cfg = safe_read_yaml(mp)

                cfg.setdefault("feeds", {})

                if n not in cfg["feeds"] or not isinstance(cfg["feeds"].get(n), dict):
                    cfg["feeds"][n] = {}

                cfg["feeds"][n]["enabled"] = bool(var.get())

                safe_write_yaml(mp, cfg)

                # Update in-memory station
                st2.manifest = cfg

                # Refresh UI
                self.refresh_stations(select_id=st2.station_id)

            chk = tk.Checkbutton(
                row,
                variable=v_en,
                command=toggle,
                bg=UI["panel"],
                fg=UI["text"],
                selectcolor=UI["panel"],
                activebackground=UI["panel"]
            )

            chk.pack(side="right", padx=14)
    # -----------------------------
    # Top bar
    # -----------------------------
    def _build_top_bar(self):
        self.top_bar = tk.Frame(self.root, bg=UI["bg"], height=64)
        self.top_bar.pack(fill="x", side="top")

        # Brand wordmark in the top-left: the RibbonOS logo image (transparent PNG), falling
        # back to plain text if PIL / the asset isn't available.
        self.title_lbl = None
        self._logo_img = None
        logo_path = Path(__file__).resolve().parent / "assets" / "ribbonos_logo.png"
        if HAS_PIL and logo_path.exists():
            try:
                img = Image.open(logo_path).convert("RGBA")
                bbox = img.getbbox()            # trim transparent margins
                if bbox:
                    img = img.crop(bbox)
                target_h = 50          # proud, not loud — a touch larger than the nav buttons
                target_w = max(1, int(img.width * (target_h / img.height)))
                img = img.resize((target_w, target_h), Image.LANCZOS)
                self._logo_img = ImageTk.PhotoImage(img)
                self.title_lbl = tk.Label(self.top_bar, image=self._logo_img, bg=UI["bg"])
            except Exception:
                self._logo_img = None
        if self.title_lbl is None:
            self.title_lbl = tk.Label(self.top_bar, text="Ribbon OS", font=FONT_H1,
                                      fg=UI["text"], bg=UI["bg"])
        self.title_lbl.pack(side="left", padx=(16, 0))

        self.mode_lbl = tk.Label(self.top_bar, text="Station Browser", font=FONT_SMALL, fg=UI["muted"], bg=UI["bg"])
        self.mode_lbl.pack(side="left", padx=10)

        # Which loom you're in (the active universe) — so authoring/switching is never ambiguous.
        self.loom_lbl = tk.Label(self.top_bar, text="", font=FONT_SMALL, fg=UI["accent"], bg=UI["bg"])
        self.loom_lbl.pack(side="left", padx=(0, 10))
        self._update_loom_label()

        self.top_clock_lbl = tk.Label(self.top_bar, textvariable=self.clock_var, font=FONT_SMALL, fg=UI["muted"], bg=UI["bg"])
        self.top_clock_lbl.pack(side="right", padx=(8, 16))

        self.top_right = tk.Frame(self.top_bar, bg=UI["bg"])
        self.top_right.pack(side="right", padx=12)
        right = self.top_right

        # New Oradio opens Bookmark — the .oradio authoring surface (no longer a runtime).
        # The old new-station wizard is retired; oradios are authored in Bookmark.
        self.btn_new = tk.Label(
            right, text="＋ New Oradio", font=FONT_BODY,
            bg=UI["panel"], fg=UI["text"], padx=8, pady=4, cursor="hand2"
        )
        self.btn_new.bind("<Button-1>", lambda e: self.open_bookmark_builder())
        self.btn_new.pack(side="left", padx=6)

        # Loom — the .loom universe surface (loom/app2.py). A top-toolbar BRICK beside New Oradio:
        # the toolbar is becoming brick-hosted, and Loom is the first non-core one we ship.
        self.btn_loom = tk.Label(
            right, text="✦ Loom", font=FONT_BODY,
            bg=UI["panel"], fg=UI["text"], padx=8, pady=4, cursor="hand2"
        )
        self.btn_loom.bind("<Button-1>", lambda e: self.open_loom())
        self.btn_loom.pack(side="left", padx=6)

        # Placeholder for the Club (dependency hub for consuming .oradios) — no UI yet.
        self.btn_club = tk.Label(
            right, text="◎ Club", font=FONT_BODY,
            bg=UI["panel"], fg=UI["text"], padx=8, pady=4, cursor="hand2"
        )
        self.btn_club.bind("<Button-1>", lambda e: self.open_club())
        self.btn_club.pack(side="left", padx=6)

        # Toggle the home nav between the linear carousel and the 3D galaxy map.
        self.btn_map = tk.Label(
            right, text="◆ Galaxy", font=FONT_BODY,
            bg=UI["panel"], fg=UI["text"], padx=8, pady=4, cursor="hand2"
        )
        self.btn_map.bind("<Button-1>", lambda e: self.toggle_nav_mode())
        self.btn_map.pack(side="left", padx=6)

        self.btn_refresh = tk.Label(
            right, text="↻ Refresh", font=FONT_BODY,
            bg=UI["panel"], fg=UI["text"], padx=8, pady=4, cursor="hand2"
        )
        self.btn_refresh.bind("<Button-1>", lambda e: self._refresh_via_door())
        self.btn_refresh.pack(side="left", padx=6)

        self.btn_settings = tk.Label(
            right, text="⚙ Settings", font=FONT_BODY,
            bg=UI["panel"], fg=UI["text"], padx=8, pady=4, cursor="hand2"
        )
        self.btn_settings.bind("<Button-1>", lambda e: self.open_settings())
        self.btn_settings.pack(side="left", padx=6)

        # Web server + Audio CLI no longer have top-bar buttons (shell stays lean):
        # the server re-homes into the Club, Audio CLI into the kernel. The capabilities
        # remain, driven by global settings (auto-launch below) and reachable from those
        # surfaces. btn_server / btn_mic are kept as None so the toggle/theme code that
        # references them no-ops gracefully.
        self._web_server_thread = None
        self._web_server_stop = None
        self._web_server_url = None
        self.btn_server = None

        self._audio_cli_session = None
        self.btn_mic = None

        # Auto-launch server if global setting is enabled
        cfg = get_global_config()
        if cfg.get("general", {}).get("always_launch_server", False):
            self.root.after(500, self._auto_launch_server)

        # Auto-start Audio CLI listener if enabled in settings
        if cfg.get("general", {}).get("audio_cli_enabled", False):
            self.root.after(1000, self._auto_start_audio_cli)

    # -----------------------------
    # Web Server Management
    # -----------------------------
    def _auto_launch_server(self):
        """Auto-launch web server from global setting."""
        if self._web_server_thread is None:
            self._start_web_server()

    def toggle_web_server(self):
        """Toggle the Radio OS web shell server on/off."""
        if self._web_server_thread and self._web_server_thread.is_alive():
            self._stop_web_server()
        else:
            self._start_web_server()

    def _start_web_server(self):
        """Start the web shell server in a daemon thread."""
        import threading
        try:
            from web_server import start_web_shell, WEB_SHELL_PORT
        except ImportError as e:
            messagebox.showerror("Web Server Error", 
                f"Could not import web_server module:\n{e}\n\n"
                "Make sure web_server.py exists in the Radio OS root directory.")
            return

        self._web_server_stop = threading.Event()

        def _on_start(url):
            self._web_server_url = url

        cfg = get_global_config()
        port = int(cfg.get("general", {}).get("web_server_port", WEB_SHELL_PORT))

        self._web_server_thread = threading.Thread(
            target=start_web_shell,
            kwargs={
                "port": port,
                "stop_event": self._web_server_stop,
                "callback_on_start": _on_start,
            },
            daemon=True,
        )
        self._web_server_thread.start()

        if self.btn_server:
            self.btn_server.config(text="🌐 Server ON", bg=UI["good"], fg="#000")

        # Show info after a short delay for the server to bind
        def _show_info():
            url = self._web_server_url or f"http://127.0.0.1:{port}"
            messagebox.showinfo("Web Server Started", 
                f"Radio OS web shell is running!\n\n"
                f"Local:       http://127.0.0.1:{port}\n"
                f"Network:   {url}\n"
                f"Tailscale:  Use your Tailscale IP + :{port}\n\n"
                f"Open this URL in any browser to manage stations remotely.")
        self.root.after(1200, _show_info)

    def _stop_web_server(self):
        """Stop the web shell server."""
        if self._web_server_stop:
            self._web_server_stop.set()
        self._web_server_thread = None
        self._web_server_stop = None
        self._web_server_url = None
        if self.btn_server:
            self.btn_server.config(text="🌐 Launch Server", bg=UI["panel"], fg=UI["text"])

    # -----------------------------
    # Audio CLI Management
    # -----------------------------
    def _auto_start_audio_cli(self):
        """Auto-start Audio CLI listener from global setting."""
        if self._audio_cli_session is None:
            self._init_audio_cli()
        if self._audio_cli_session and not self._audio_cli_session.is_running:
            self._audio_cli_session.start_listener()
            if self.btn_mic:
                self.btn_mic.config(text="🎤 Audio CLI (ON)", bg="#1a3a1a", fg=UI["good"])

    def _toggle_audio_cli(self):
        """Toggle Audio CLI listener on/off."""
        if self._audio_cli_session is None:
            self._init_audio_cli()

        if self._audio_cli_session is None:
            messagebox.showerror("Audio CLI", 
                "Audio CLI could not be initialized.\n\n"
                "Make sure sounddevice is installed and a microphone is available.")
            return

        if self._audio_cli_session.is_running:
            self._audio_cli_session.stop_listener()
            if self.btn_mic:
                self.btn_mic.config(text="🎤 Audio CLI", bg=UI["panel"], fg=UI["text"])
        else:
            self._audio_cli_session.start_listener()
            if self.btn_mic:
                self.btn_mic.config(text="🎤 Audio CLI (ON)", bg="#1a3a1a", fg=UI["good"])

    def _init_audio_cli(self):
        """Initialize the Audio CLI session object."""
        try:
            from audio_cli import AudioCLISession

            # Read default mode from global config
            acli_cfg = get_global_config().get("audio_cli", {})
            default_mode = acli_cfg.get("default_mode", "tkinter")
            web_url = acli_cfg.get("web_url", "http://127.0.0.1:7800")

            if default_mode == "web":
                self._audio_cli_session = AudioCLISession(shell=None, web_url=web_url)
            else:
                self._audio_cli_session = AudioCLISession(self)

            # Wire up session callbacks
            def on_start():
                if self.btn_mic:
                    self.root.after(0, lambda: self.btn_mic.config(
                        text="🎤 ACTIVE", bg="#3a1a1a", fg=UI["danger"]))

            def on_end():
                if self.btn_mic:
                    self.root.after(0, lambda: self.btn_mic.config(
                        text="🎤 Audio CLI (ON)", bg="#1a3a1a", fg=UI["good"]))

            def on_status(text):
                self.root.after(0, lambda t=text: self.mode_lbl.config(
                    text=f"Audio CLI: {t}"))

            self._audio_cli_session.on_session_start = on_start
            self._audio_cli_session.on_session_end = on_end
            self._audio_cli_session.on_status_change = on_status

        except Exception as e:
            print(f"[AudioCLI] Init failed: {e}")
            self._audio_cli_session = None

    # -----------------------------
    # Home view
    # -----------------------------
    def _build_home_view(self):
        self.home = tk.Frame(self.root, bg=UI["bg"])
        # The ribbon video is the literal full-screen background.
        self.home_bg = tk.Label(self.home, bd=0, highlightthickness=0, bg="#000000")
        self.home_bg.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Tiles are placed DIRECTLY over the video (no opaque field/canvas), so the
        # ribbon shows through the gaps -> tiles float on the live ribbon. The hint
        # floats at the top; both vanish on idle to reveal the bare ribbon.
        self.home_hint = tk.Label(
            self.home,
            text="Scroll / drag / arrows to browse  •  double-click or hold a tile to launch",
            font=FONT_BODY, fg=UI["muted"], bg=UI["bg"]
        )
        self.home_hint.place(x=18, y=14)

        self.cards: List[Dict[str, Any]] = []
        self._sel_pos = 0.0           # animated carousel position (float index)
        self._tile_anim = None
        self._home_tiles_visible = True
        self._drag_last_x = None
        self._drag_moved = False

        for w in (self.home, self.home_bg):
            w.bind("<MouseWheel>", self._on_mousewheel)
            w.bind("<ButtonPress-1>", self._drag_start)
            w.bind("<B1-Motion>", self._drag_move)
            w.bind("<ButtonRelease-1>", self._drag_end)
            w.bind("<Double-Button-1>", self._home_double_click)
            w.bind("<Button-3>", self._home_right_click)
        self.root.bind("<Left>", lambda e: self._nav(-1))
        self.root.bind("<Right>", lambda e: self._nav(1))
        self.root.bind("<Return>", lambda e: self._play_selected())
        self.root.bind("<q>", lambda e: self._galaxy_roll(-0.08))
        self.root.bind("<e>", lambda e: self._galaxy_roll(0.08))
        self.home.bind("<Configure>", lambda e: self._relayout(self.selected_idx, animate=False))

        self._render_cards()
        self.root.after(150, lambda: self._relayout(self.selected_idx, animate=False))

    def _tile_step_px(self) -> int:
        # horizontal spacing between tile centers
        return int((self.ART + 56) * UI_SCALE)

    def _relayout(self, sel_pos: float, animate: bool = False):
        """Place every tile relative to the animated carousel position so the
        focused tile sits dead-center and the ribbon shows between tiles."""
        if not self.cards or not self._home_tiles_visible:
            return
        if animate:
            self._animate_to(sel_pos)
            return
        self._sel_pos = float(sel_pos)
        self.root.update_idletasks()
        w = max(self.home.winfo_width(), 1)
        h = max(self.home.winfo_height(), 1)
        cx = w / 2
        step = self._tile_step_px()
        # Pin the TOP of every tile (the art) to a fixed y so a long, wrapping title
        # grows DOWNWARD and never nudges the card/art upward. anchor="n" = top-center.
        art = int(self.ART * UI_SCALE)
        y_top = int(h * 0.5 - art / 2)
        title_y = y_top + art + int(10 * UI_SCALE)
        for i, c in enumerate(self.cards):
            f = c.get("frame")
            if f is None:
                continue
            x = int(cx + (i - self._sel_pos) * step)
            f.place(in_=self.home, x=x, y=y_top, anchor="n")
            t = c.get("title")
            if t is not None:
                # title is its own placed widget directly below the card, so a long
                # wrapping title grows downward and never affects the card geometry.
                t.place(in_=self.home, x=x, y=title_y, anchor="n")

    def _animate_to(self, target: float):
        if self._tile_anim is not None:
            try: self.root.after_cancel(self._tile_anim)
            except Exception: pass
            self._tile_anim = None
        start = self._sel_pos
        t0 = time.time()
        dur = 0.22
        def step():
            t = (time.time() - t0) / dur
            if t >= 1.0:
                self._relayout(target, animate=False)
                self._tile_anim = None
                return
            k = 1 - (1 - clamp(t, 0.0, 1.0)) ** 3
            self._relayout(start + (target - start) * k, animate=False)
            self._tile_anim = self.root.after(16, step)
        step()

    # Nintendo-Switch home layout: ~20 boxes, filled most-recent-first, last box
    # is the "All .oradios" overflow door.
    HOME_MAX_BOXES = 19

    def _recent_stations(self) -> List["StationInfo"]:
        """Stations ordered most-recent-first (recency = dir mtime, see station_recency)."""
        return sorted(self.stations, key=station_recency, reverse=True)

    def _focused_tile(self) -> Optional[Dict[str, Any]]:
        if 0 <= self.selected_idx < len(self.home_tiles):
            return self.home_tiles[self.selected_idx]
        return None

    def _focused_station(self) -> Optional["StationInfo"]:
        tile = self._focused_tile()
        if tile and tile.get("kind") == "station":
            return tile.get("station")
        return None

    def _render_cards(self):
        for c in self.cards:
            for key in ("frame", "title"):
                w = c.get(key)
                if w is not None:
                    try: w.destroy()
                    except Exception: pass
        self.cards.clear()
        self.home_tiles = []
        if getattr(self, "_empty_lbl", None) is not None:
            try: self._empty_lbl.destroy()
            except Exception: pass
            self._empty_lbl = None

        if not self.stations:
            self._empty_lbl = tk.Label(self.home, text="No stations found. Create one.",
                                       font=FONT_H2, fg=UI["muted"], bg=UI["bg"])
            self._empty_lbl.place(relx=0.5, rely=0.5, anchor="center")
            return

        ordered = self._recent_stations()
        visible = ordered[: self.HOME_MAX_BOXES]
        overflow = ordered[self.HOME_MAX_BOXES :]
        for st in visible:
            self.home_tiles.append({"kind": "station", "station": st})
        # Last box is always the overflow door to the full grid/list.
        self.home_tiles.append({"kind": "all", "station": None, "overflow": overflow})

        for i, tile in enumerate(self.home_tiles):
            if tile["kind"] == "station":
                card = self._create_station_card(self.home, tile["station"], i)
            else:
                card = self._create_all_oradios_card(self.home, i, len(self.stations))
            self.cards.append({"frame": card, "title": getattr(card, "_titlewidget", None),
                               "station": tile.get("station"), "tile": tile})

        self.selected_idx = int(clamp(self.selected_idx, 0, max(0, len(self.cards) - 1)))
        self._relayout(self.selected_idx, animate=False)
        self._highlight_selected()
        self._focus_station_ribbon(self._focused_station())

    def _create_all_oradios_card(self, parent, idx: int, total: int):
        size = int(self.ART * UI_SCALE)
        base = Image.new("RGBA", (size, size), self._hex_rgb(UI["panel"]) + (255,)) if HAS_PIL else None
        if base is not None:
            d = ImageDraw.Draw(base)
            try:
                from PIL import ImageFont
                try:
                    font = ImageFont.truetype("seguisym.ttf", int(size * 0.5))
                except Exception:
                    font = ImageFont.truetype("segoeui.ttf", int(size * 0.5))
            except Exception:
                font = None
            try:
                bbox = d.textbbox((0, 0), "▦", font=font)
                tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
                d.text(((size - tw) / 2 - bbox[0], (size - th) / 2 - bbox[1]), "▦",
                       fill=self._hex_rgb(UI["accent"]) + (255,), font=font)
            except Exception:
                pass
        return self._make_tile(parent, base, f"All .oradios ({total})", idx, self._open_all_oradios)

    def _open_all_oradios(self):
        """Overflow view: the full station grid/list (every .oradio, recency-ordered)."""
        win = tk.Toplevel(self.root)
        win.title("All .oradios")
        win.configure(bg=UI["bg"])
        win.geometry(scaled_geometry(720, 560))

        tk.Label(win, text="All .oradios", font=FONT_H1, fg=UI["text"], bg=UI["bg"]).pack(anchor="w", padx=16, pady=(14, 8))

        canvas = tk.Canvas(win, bg=UI["bg"], highlightthickness=0)
        scroll = tk.Scrollbar(win, orient="vertical", command=canvas.yview)
        body = tk.Frame(canvas, bg=UI["bg"])
        body.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=body, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True, padx=(16, 0), pady=(0, 14))
        scroll.pack(side="right", fill="y", pady=(0, 14))

        for st in self._recent_stations():
            cfg = st.manifest or {}
            meta = cfg.get("station", {}) if isinstance(cfg.get("station", {}), dict) else {}
            name = meta.get("name", st.station_id)
            row = tk.Frame(body, bg=UI["card"])
            row.pack(fill="x", padx=8, pady=4)
            tk.Label(row, text=name, font=FONT_BODY, fg=UI["text"], bg=UI["card"]).pack(side="left", padx=12, pady=8)
            tk.Label(row, text=ribbon_cat_for_station(st), font=FONT_SMALL, fg=UI["muted"], bg=UI["card"]).pack(side="left", padx=6)
            tk.Button(
                row, text="▶ PLAY", font=("Segoe UI", _scale_font(10), "bold"),
                bg=UI["accent"], fg="#000", relief="flat", cursor="hand2",
                command=lambda s=st, w=win: (w.destroy(), self.launch_station(s)),
            ).pack(side="right", padx=10)


    def _add_rounded_corners(self, parent_frame: tk.Frame, radius: int, bg_color: str, card_color: str):
        if not HAS_PIL:
            return

        # Cache key
        k = f"{radius}_{bg_color}_{card_color}"
        if not hasattr(self, "_corner_cache"):
            self._corner_cache = {}
        
        if k not in self._corner_cache:
            def make_corner(anchor):
                # high-res for better antialiasing then downscale?
                # For now simple drawing.
                # anchor: nw, ne, sw, se
                size = radius
                img = Image.new("RGBA", (size, size), bg_color)
                draw = ImageDraw.Draw(img)
                
                # Draw the card-colored arc (masking the bg color)
                # Effectively we are drawing the "card" onto the "bg" base.
                if anchor == "nw":
                    # Draw a circle sector filled with card_color
                    # Center at (radius, radius)
                    # Bbox (0, 0, 2*r, 2*r)
                    draw.pieslice([(0, 0), (radius*2, radius*2)], 180, 270, fill=card_color)
                elif anchor == "ne":
                    draw.pieslice([(-radius, 0), (radius, radius*2)], 270, 360, fill=card_color)
                elif anchor == "sw":
                    draw.pieslice([(0, -radius), (radius*2, radius)], 90, 180, fill=card_color)
                elif anchor == "se":
                    draw.pieslice([(-radius, -radius), (radius, radius)], 0, 90, fill=card_color)
                
                return ImageTk.PhotoImage(img)

            self._corner_cache[k] = {
                "nw": make_corner("nw"),
                "ne": make_corner("ne"),
                "sw": make_corner("sw"),
                "se": make_corner("se"),
            }

        corners = self._corner_cache[k]

        # Place labels at corners
        tk.Label(parent_frame, image=corners["nw"], bg=card_color, borderwidth=0).place(x=0, y=0, anchor="nw")
        tk.Label(parent_frame, image=corners["ne"], bg=card_color, borderwidth=0).place(relx=1.0, y=0, anchor="ne")
        tk.Label(parent_frame, image=corners["sw"], bg=card_color, borderwidth=0).place(x=0, rely=1.0, anchor="sw")
        tk.Label(parent_frame, image=corners["se"], bg=card_color, borderwidth=0).place(relx=1.0, rely=1.0, anchor="se")

    # A tile = the .oradio's rounded PNG (logo, or a generated stock placeholder).
    # The title is a SEPARATE placed widget below it (not inside the card), so a long
    # title can never stretch the card. Selection = a rounded accent outline baked
    # into the image, so the card reads as a rounded card, not a sharp rectangle.
    ART = 265  # px (pre-scale) square art size

    def _hex_rgb(self, hexc: str):
        hexc = str(hexc).lstrip("#")
        if len(hexc) == 3:
            hexc = "".join(c * 2 for c in hexc)
        try:
            return (int(hexc[0:2], 16), int(hexc[2:4], 16), int(hexc[4:6], 16))
        except Exception:
            return (255, 255, 255)

    def _placeholder_art(self, key: str, size: int):
        """Deterministic 'stock' base (full square, rounded later) for logo-less
        stations: a stable color keyed off the id with the station's initial."""
        if not HAS_PIL:
            return None
        import colorsys
        h = int(hashlib.md5(key.encode("utf-8")).hexdigest(), 16)
        r, g, b = colorsys.hsv_to_rgb((h % 360) / 360.0, 0.45, 0.55)
        img = Image.new("RGBA", (size, size), (int(r * 255), int(g * 255), int(b * 255), 255))
        d = ImageDraw.Draw(img)
        letter = (key[:1] or "?").upper()
        try:
            from PIL import ImageFont
            font = ImageFont.truetype("segoeui.ttf", int(size * 0.46))
        except Exception:
            font = None
        try:
            bbox = d.textbbox((0, 0), letter, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            d.text(((size - tw) / 2 - bbox[0], (size - th) / 2 - bbox[1]), letter, fill=(255, 255, 255, 235), font=font)
        except Exception:
            pass
        return img

    def _station_base_pil(self, station: "StationInfo", size: int):
        """Opaque square RGBA base — the author's bundled thumbnail.png if present, else a logo, else
        a placeholder — rounded afterward. (Both the carousel card and galaxy node use this.)"""
        cfg = station.manifest or {}
        st_meta = cfg.get("station", {}) if isinstance(cfg.get("station", {}), dict) else {}
        thumb = oradio_thumbnail(station)
        if thumb and HAS_PIL:
            try:
                return ImageOps.fit(Image.open(thumb).convert("RGBA"), (size, size),
                                    method=Image.Resampling.LANCZOS)
            except Exception as e:
                print(f"Failed to load thumbnail for {station.station_id}: {e}")
        logo_path = st_meta.get("logo", "")
        if logo_path and HAS_PIL:
            p = resolve_cfg_path(station.path, logo_path)
            if os.path.exists(p):
                try:
                    return ImageOps.fit(Image.open(p).convert("RGBA"), (size, size), method=Image.Resampling.LANCZOS)
                except Exception as e:
                    print(f"Failed to load logo {logo_path}: {e}")
        return self._placeholder_art(station.station_id, size)

    # -----------------------------
    # Picture-frame brick (carousel icon overlays)
    # -----------------------------
    def _picture_frame_brick(self):
        """Lazy-load the picture-frame brick (bricks/ui.frame/picture_frame.py)."""
        pf = getattr(self, "_pf_brick", None)
        if pf is None:
            import importlib.util
            path = os.path.join(BASE, "bricks", "ui.frame", "picture_frame.py")
            spec = importlib.util.spec_from_file_location("picture_frame", path)
            pf = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(pf)
            self._pf_brick = pf
        return pf

    def _shortcut_brick(self):
        """Lazy-load the shortcut/launcher brick (bricks/ui.shortcut/launch_shortcut.py)."""
        sc = getattr(self, "_sc_brick", None)
        if sc is None:
            import importlib.util
            path = os.path.join(BASE, "bricks", "ui.shortcut", "launch_shortcut.py")
            spec = importlib.util.spec_from_file_location("launch_shortcut", path)
            sc = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(sc)
            self._sc_brick = sc
        return sc

    def _station_open_spec(self, station: "StationInfo"):
        """The oradio's `open` directive ({'kind': 'shortcut'|'html', ...}), or {}."""
        spec = (getattr(station, "descriptor", None) or {}).get("open")
        return spec if isinstance(spec, dict) else {}

    def _launch_shortcut_open(self, station: "StationInfo", spec: dict) -> bool:
        """Open an oradio AS a launcher: run its shortcut target (a game/exe/url) instead of the
        runtime. Returns True if handled (so the normal launch is skipped)."""
        target = str(spec.get("target", "")).strip()
        name = (station.manifest.get("station", {}) or {}).get("name", station.station_id)
        if not target:
            messagebox.showinfo("Shortcut", f"{name} has no shortcut target set.")
            return True
        try:
            info = self._shortcut_brick().launch(
                target, kind=spec.get("launch", "auto"),
                args=spec.get("args"), cwd=spec.get("cwd"))
        except Exception as e:
            messagebox.showerror("Shortcut", f"Could not launch {name}:\n{e}")
            return True
        try:
            self.now_playing.config(text=f"Launched — {name}")
            self.now_sub.config(text=f"{info.get('kind','')}: {target}")
        except Exception:
            pass
        self._note_shell_activity()
        return True

    def _apply_station_frame(self, base, station_id: str, size: int):
        """Composite this oradio's assigned picture frame (if any) over its carousel icon."""
        if base is None or not HAS_PIL:
            return base
        try:
            pf = self._picture_frame_brick()
            fid = pf.get_assignment(station_id)
            if not fid or fid == "none":
                return base
            overlay = pf.frame_overlay(fid, size)
            return Image.alpha_composite(base.convert("RGBA"), overlay)
        except Exception:
            return base

    def _set_station_frame(self, station_id: str, frame_id: str):
        """Assign a picture frame to an oradio (via the brick) and re-render the carousel."""
        try:
            self._picture_frame_brick().assign(station_id, frame_id)
        except Exception as e:
            messagebox.showerror("Picture frame", f"Could not set frame:\n{e}")
            return
        try:
            self._render_cards()
        except Exception:
            pass
        try:
            self._attach_galaxy_thumbs()
        except Exception:
            pass

    def _round_tile_image(self, base, size: int, selected: bool):
        """Apply rounded corners; when selected, bake a rounded accent outline."""
        if base is None or not HAS_PIL:
            return None
        radius = int(size * 0.13)
        img = base.copy()
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, size - 1, size - 1), radius=radius, fill=255)
        img.putalpha(mask)
        if selected:
            d = ImageDraw.Draw(img)
            w = max(3, int(size * 0.022))
            d.rounded_rectangle((w // 2, w // 2, size - 1 - w // 2, size - 1 - w // 2),
                                radius=radius, outline=self._hex_rgb(UI["accent"]) + (255,), width=w)
        return ImageTk.PhotoImage(img)

    def _make_tile(self, parent, base, name: str, idx: int, on_launch):
        """Build a tile (rounded-image Label) + a SEPARATE title Label; both are
        placed by _relayout. Returns the card; title is on card._titlewidget."""
        size = int(self.ART * UI_SCALE)
        img_n = self._round_tile_image(base, size, False)
        img_s = self._round_tile_image(base, size, True)
        card = tk.Label(parent, image=img_n, bd=0, highlightthickness=0, bg=UI["bg"])
        card._img_normal = img_n
        card._img_sel = img_s
        card._is_tile = True
        title = tk.Label(parent, text=name, font=("Segoe UI", _scale_font(15), "bold"),
                         fg=UI["text"], bg=UI["bg"], wraplength=int(size * 1.1), justify="center")
        card._titlewidget = title
        self._bind_tile_launch(card, idx, on_launch, extra=[title])
        return card

    def _bind_tile_launch(self, card, idx: int, on_launch, extra=()):
        """Single-click focuses the tile; double-click OR long-hold launches it."""
        def on_press(_e):
            self._select_index(idx)
            self._tile_hold_after = self.root.after(550, lambda: (self._cancel_tile_hold(), on_launch()))
        def on_release(_e):
            self._cancel_tile_hold()
        def on_double(_e):
            self._cancel_tile_hold()
            on_launch()
        for w in [card] + list(extra):
            w.bind("<ButtonPress-1>", on_press, add="+")
            w.bind("<ButtonRelease-1>", on_release, add="+")
            w.bind("<Double-Button-1>", on_double, add="+")

    def _cancel_tile_hold(self):
        h = getattr(self, "_tile_hold_after", None)
        if h:
            try: self.root.after_cancel(h)
            except Exception: pass
            self._tile_hold_after = None

    def _card_set_selected(self, card, selected: bool, base_bg: str):
        title = getattr(card, "_titlewidget", None)
        try:
            card.configure(bg=base_bg, image=(card._img_sel if selected else card._img_normal))
        except Exception:
            pass
        if title is not None:
            try: title.configure(bg=base_bg, fg=(UI["accent"] if selected else UI["text"]))
            except Exception: pass

    def _station_title(self, station: "StationInfo") -> str:
        """What shows under a card / galaxy node: the Title set at MINT (manifest.title), not the
        loom-node label or the slug id. Falls back to the station name, then the id."""
        d = getattr(station, "descriptor", None) or {}
        title = str(d.get("title") or "").strip()
        if title:
            return title
        meta = (getattr(station, "manifest", None) or {}).get("station", {}) or {}
        return str(meta.get("name") or station.station_id)

    def _create_station_card(self, parent, station: StationInfo, idx: int):
        name = self._station_title(station)
        base = self._station_base_pil(station, int(self.ART * UI_SCALE))
        base = self._apply_station_frame(base, station.station_id, int(self.ART * UI_SCALE))
        card = self._make_tile(parent, base, name, idx, lambda s=station: self.launch_station(s))
        for w in (card, card._titlewidget):
            w.bind("<Button-3>", lambda e, sid=station.station_id: self.on_station_right_click(e, sid), add="+")
        return card

    def _set_card_bg(self, card: tk.Frame, bg: str):
        try:
            card.configure(bg=bg)
            for w in card.winfo_children():
                if isinstance(w, (tk.Label, tk.Frame)):
                    try:
                        w.configure(bg=bg)
                    except Exception:
                        pass
        except Exception:
            pass

    def _select_index(self, idx: int):
        if not self.cards:
            return
        self.selected_idx = int(clamp(idx, 0, len(self.cards) - 1))
        self._highlight_selected()
        self._relayout(self.selected_idx, animate=True)
        # Morph the background ribbon to the newly focused tile's assigned skin.
        self._focus_station_ribbon(self._focused_station())
        self._note_shell_activity()

    def _highlight_selected(self):
        for i, c in enumerate(self.cards):
            self._card_set_selected(c["frame"], i == self.selected_idx, UI["bg"])

    def _nav(self, step: int):
        if self._view != "home":
            return
        if self._nav_mode == "galaxy":
            self.galaxy.orbit(0.18 * step, 0.0)
            self._note_shell_activity()
            return
        if not self.cards:
            return
        self._select_index(self.selected_idx + step)

    def _play_selected(self):
        if self._view != "home" or not self.cards:
            return
        tile = self._focused_tile()
        if not tile:
            return
        if tile.get("kind") == "all":
            self._open_all_oradios()
            return
        st = tile.get("station")
        if st is not None:
            self.launch_station(st)

    def _on_mousewheel(self, e):
        if self._view != "home":
            return
        if self._nav_mode == "galaxy":
            self.galaxy.zoom(0.9 if e.delta > 0 else 1.1)
            self._note_shell_activity()
            return
        if not self.cards:
            return
        self._nav(1 if e.delta < 0 else -1)

    def _drag_start(self, e):
        if self._nav_mode == "galaxy":
            self._galaxy_press(e)
            return
        self._drag_last_x = e.x_root
        self._drag_moved = False

    def _drag_move(self, e):
        if self._nav_mode == "galaxy":
            self._galaxy_drag(e)
            return
        if self._drag_last_x is None:
            return
        step = max(1, self._tile_step_px())
        # convert horizontal drag distance into discrete tile steps
        moved = int((self._drag_last_x - e.x_root) / step)
        if moved != 0:
            self._drag_moved = True
            self._drag_last_x = e.x_root
            self._nav(moved)

    def _drag_end(self, e):
        if self._nav_mode == "galaxy":
            self._galaxy_release(e)
            return
        self._drag_last_x = None

    # -----------------------------
    # Galaxy map (spatial nav)
    # -----------------------------
    def toggle_nav_mode(self):
        if not (HAS_CV2 and HAS_PIL):
            messagebox.showinfo("Galaxy map", "The galaxy map needs OpenCV + Pillow (video backend).")
            return
        self._nav_mode = "galaxy" if self._nav_mode == "carousel" else "carousel"
        if self._nav_mode == "galaxy":
            self.galaxy.set_nodes(self.stations)
            self._attach_galaxy_thumbs()
            # carry the carousel's focus into the map
            st = self._focused_station()
            if st is not None:
                for i, n in enumerate(self.galaxy.nodes):
                    if n["station"].station_id == st.station_id:
                        self.galaxy.focus = i
                        break
            self._set_home_overlay(False)              # hide the flat tiles
            self.home_hint.place(x=18, y=14)
            self.home_hint.config(text="Galaxy map  •  drag to orbit  •  wheel to zoom  •  Q/E roll  •  click a node  •  double-click/hold to launch")
            if self.ribbon_video:
                self.ribbon_video.overlay_cb = self._draw_galaxy
            if self.galaxy.nodes:
                self._focus_station_ribbon(self.galaxy.nodes[self.galaxy.focus]["station"])
            self.btn_map.config(text="▦ Carousel")
        else:
            if self.ribbon_video:
                self.ribbon_video.overlay_cb = None
            self.home_hint.config(text="Scroll / drag / arrows to browse  •  double-click or hold a tile to launch")
            self.btn_map.config(text="◆ Galaxy")
            self._set_home_overlay(True)               # bring the tiles back
        self._note_shell_activity()

    def _draw_galaxy(self, frame):
        self.galaxy.draw(frame, accent=self._hex_rgb(UI["accent"]))

    def _load_edge_texture_images(self):
        textures = {}
        try:
            from oradio_engine.loom_runtime import load_edge_textures
            raw = load_edge_textures(Path(CLUB_DIR), self._active_loom_id)
        except Exception:
            raw = {}
        for key, path in raw.items():
            try:
                arr = cv2.imread(str(path), cv2.IMREAD_UNCHANGED) if cv2 is not None else None
                if arr is None or arr.size == 0:
                    continue
                if len(arr.shape) == 2:
                    arr = cv2.cvtColor(arr, cv2.COLOR_GRAY2BGRA)
                elif arr.shape[2] == 3:
                    arr = cv2.cvtColor(arr, cv2.COLOR_BGR2BGRA)
                textures[str(key)] = arr
            except Exception:
                continue
        self.galaxy.set_edge_textures(textures)

    def _circular_thumb(self, pil_img, res=128):
        """Square RGBA PIL -> circular RGBA numpy (res,res,4) for a galaxy node."""
        img = pil_img.convert("RGBA").resize((res, res), Image.Resampling.LANCZOS)
        mask = Image.new("L", (res, res), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, res - 1, res - 1), fill=255)
        img.putalpha(mask)
        return np.array(img)

    def _attach_galaxy_thumbs(self):
        if np is None or not HAS_PIL:
            self._load_edge_texture_images()
            return
        res = 128
        for n in self.galaxy.nodes:
            st = n.get("station")
            try:
                base = self._station_base_pil(st, res)
                base = self._apply_station_frame(base, getattr(st, "station_id", ""), res)
                n["thumb"] = self._circular_thumb(base, res)
            except Exception:
                n["thumb"] = None
        # Sun thumb comes later from the home-loop clip; until then a warm glow draws.
        self._load_edge_texture_images()

    def _home_right_click(self, e):
        if self._nav_mode == "galaxy":
            idx = self.galaxy.hit_test(e.x, e.y)
            if idx is not None and 0 <= idx < len(self.galaxy.nodes):
                st = self.galaxy.nodes[idx].get("station")
                if st is not None:
                    self.on_station_right_click(e, st.station_id)
                    return
            edge = self.galaxy.hit_test_edge(e.x, e.y)
            if edge is not None:
                self._edit_galaxy_edge_texture(e, edge)

    def _edit_galaxy_edge_texture(self, event, edge):
        i, j = edge
        if i >= len(self.galaxy.nodes) or j >= len(self.galaxy.nodes):
            return
        left = str(self.galaxy.nodes[i].get("id", "")).strip()
        right = str(self.galaxy.nodes[j].get("id", "")).strip()
        left_title = str(self.galaxy.nodes[i].get("label", left))
        right_title = str(self.galaxy.nodes[j].get("label", right))
        try:
            from oradio_engine.loom_runtime import edge_style_key, load_edge_textures, set_edge_texture
            current = load_edge_textures(Path(CLUB_DIR), self._active_loom_id).get(edge_style_key(left, right), "")
        except Exception:
            edge_style_key = lambda a, b: "__".join(sorted((a, b)))
            set_edge_texture = None
            current = ""
        menu = tk.Menu(self.root, tearoff=0)
        title = f"Line texture · {left_title} ↔ {right_title}"
        menu.add_command(label=title, state="disabled")
        menu.add_separator()

        def _load():
            p = filedialog.askopenfilename(
                title=f"Choose line texture · {left_title} ↔ {right_title}",
                filetypes=[("Images", "*.png *.jpg *.jpeg *.webp *.bmp"), ("All", "*.*")],
            )
            if not p or set_edge_texture is None:
                return
            try:
                set_edge_texture(Path(CLUB_DIR), self._active_loom_id, left, right, p)
                self._load_edge_texture_images()
                self.mode_lbl.config(text=f"Edge texture set · {left_title} ↔ {right_title}")
            except Exception as exc:
                messagebox.showerror("Edge texture", f"Could not set texture:\n{exc}")

        def _clear():
            if set_edge_texture is None:
                return
            try:
                set_edge_texture(Path(CLUB_DIR), self._active_loom_id, left, right, None)
                self._load_edge_texture_images()
                self.mode_lbl.config(text=f"Edge texture cleared · {left_title} ↔ {right_title}")
            except Exception as exc:
                messagebox.showerror("Edge texture", f"Could not clear texture:\n{exc}")

        label = "Load line texture…"
        if current:
            label = f"Load line texture…  ({Path(current).name})"
        menu.add_command(label=label, command=_load)
        menu.add_command(label="Clear line texture", command=_clear, state=("normal" if current else "disabled"))
        menu.tk_popup(event.x_root, event.y_root)

    def _galaxy_press(self, e):
        self._gx_last = (e.x, e.y)
        self._gx_moved = False
        self._gx_press_node = self.galaxy.hit_test(e.x, e.y)
        if self._gx_press_node is not None:
            idx = self._gx_press_node
            self._tile_hold_after = self.root.after(550, lambda: (self._cancel_tile_hold(), self._galaxy_launch(idx)))

    def _galaxy_drag(self, e):
        if self._gx_last is None:
            return
        dx = e.x - self._gx_last[0]
        dy = e.y - self._gx_last[1]
        if abs(dx) + abs(dy) > 4:
            self._gx_moved = True
            self._cancel_tile_hold()
        self._gx_last = (e.x, e.y)
        self.galaxy.orbit(dx * 0.01, -dy * 0.01)

    def _galaxy_release(self, e):
        self._cancel_tile_hold()
        if not self._gx_moved and self._gx_press_node is not None:
            self._galaxy_focus(self._gx_press_node)
        self._gx_last = None
        self._gx_press_node = None

    def _galaxy_roll(self, d):
        if self._view == "home" and self._nav_mode == "galaxy":
            self.galaxy.roll_by(d)
            self._note_shell_activity()

    def _galaxy_focus(self, idx):
        if not (0 <= idx < len(self.galaxy.nodes)):
            return
        old = self.galaxy.focus
        # Speed of light: only kick in once a destination is 2+ authored crossover
        # jumps away, so a long bond-chain across the map feels quick instead of a
        # crawl. Adjacent bonds (1 jump) and default genesis routing through the
        # source oradio (unmapped peers) stay at native speed — nothing is "far"
        # until a real crossover chain makes it so.
        if self.ribbon_video and 0 <= old < len(self.galaxy.nodes):
            hops = self.galaxy.bond_distance(old, idx)
            if hops is not None and hops >= 2:
                self.ribbon_video.set_speed(clamp(1.0 + (hops - 1) * 0.9, 1.0, 4.0))
            else:
                self.ribbon_video.set_speed(1.0)
        self.galaxy.focus = idx
        self._focus_station_ribbon(self.galaxy.nodes[idx]["station"])
        self._note_shell_activity()

    def _galaxy_launch(self, idx):
        if 0 <= idx < len(self.galaxy.nodes):
            st = self.galaxy.nodes[idx]["station"]
            if st is not None:
                self.launch_station(st)

    def _home_double_click(self, e):
        # Galaxy-mode double-click on the field launches the node under the cursor.
        if self._nav_mode != "galaxy":
            return
        self._cancel_tile_hold()
        idx = self.galaxy.hit_test(e.x, e.y)
        if idx is not None:
            self._galaxy_launch(idx)

    def _force_card_refresh(self):
        """Re-place tiles after a view transition."""
        if not self.cards:
            return
        self.root.update_idletasks()
        self._relayout(self.selected_idx, animate=False)

    # -----------------------------
    # Runtime view
    # -----------------------------
    def _build_runtime_view(self):
        self.runtime = tk.Frame(self.root, bg=UI["bg"])

        left = tk.Frame(self.runtime, bg=UI["panel"], width=int(320 * UI_SCALE))
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        top_left = tk.Frame(left, bg=UI["panel"])
        top_left.pack(fill="x", padx=14, pady=14)

        self.btn_back = tk.Button(
            top_left, text="← Back", font=FONT_BODY,
            bg=UI["panel"], fg=UI["text"], relief="flat",
            command=self.stop_station
        )
        self.btn_back.pack(side="left")

        self.btn_stop = tk.Button(
            top_left, text="⏹ Stop", font=FONT_BODY,
            bg=UI["panel"], fg=UI["danger"], relief="flat",
            command=self.stop_station
        )
        self.btn_stop.pack(side="right")

        status_box = tk.Frame(left, bg=UI["panel"])
        status_box.pack(fill="x", padx=14, pady=(0, 10))

        tk.Label(status_box, text="Runtime Status", font=("Segoe UI", 12, "bold"), fg=UI["text"], bg=UI["panel"]).pack(anchor="w")

        self.status_lines = tk.Text(
            status_box, height=12, wrap="word",
            bg=UI["surface"], fg=UI["text"], font=("Consolas", 10),
            relief="flat", bd=0
        )
        self.status_lines.pack(fill="x", pady=(8, 0))
        self.status_lines.config(state="disabled")

        tk.Label(left, text="(Feed activity coming next)", font=FONT_BODY, fg=UI["muted"], bg=UI["panel"]).pack(
            anchor="w", padx=14, pady=(6, 0)
        )

        center = tk.Frame(self.runtime, bg=UI["surface"])
        center.pack(side="left", fill="both", expand=True)

        self.runtime_title = tk.Label(center, text="Visual Surface", font=FONT_H2, fg=UI["muted"], bg=UI["surface"])
        self.runtime_title.pack(expand=True)

        bottom = tk.Frame(self.runtime, bg="#000000", height=84)
        bottom.pack(side="bottom", fill="x")
        bottom.pack_propagate(False)

        self.now_playing = tk.Label(bottom, text="", font=("Segoe UI", 18, "bold"), fg=UI["text"], bg="#000000")
        self.now_playing.pack(anchor="w", padx=20, pady=(12, 0))

        self.now_sub = tk.Label(bottom, text="", font=("Segoe UI", 12), fg=UI["muted"], bg="#000000")
        self.now_sub.pack(anchor="w", padx=20, pady=(2, 0))

    # -----------------------------
    # View transitions
    # -----------------------------
    def show_home(self, instant: bool = False):
        if self._transitioning:
            return
        self._view = "home"
        self.mode_lbl.config(text="Station Browser")
        self.runtime.pack_forget()
        self.home.pack(fill="both", expand=True)
        # Re-place the floating tiles once the home has geometry again.
        self.root.after(80, lambda: self._relayout(self.selected_idx, animate=False))
        if sys.platform == "darwin":
            self.root.update_idletasks()
        self._transitioning = False if instant else True
        if not instant:
            self.root.after(180, lambda: setattr(self, "_transitioning", False))

    def show_runtime(self, instant: bool = False):
        if self._transitioning:
            return
        self._view = "runtime"
        self.mode_lbl.config(text="Station Runtime")
        self.home.pack_forget()
        self.runtime.pack(fill="both", expand=True)
        self._transitioning = False if instant else True
        if not instant:
            self.root.after(180, lambda: setattr(self, "_transitioning", False))

    # -----------------------------
    # Station actions
    # -----------------------------
    def _open_plan_for(self, station: "StationInfo") -> Optional[dict]:
        """The shared open plan for a minted .oradio (same resolver the file-manager double-click
        uses, so an oradio opens to the SAME thing from the carousel/galaxy). None for a
        legacy/non-oradio station (which uses the runtime spawn). See bookmark/launch.py."""
        lp = str(getattr(station, "launch_path", "") or "")
        if getattr(station, "source_kind", "") != "oradio" or not lp.lower().endswith(".oradio"):
            return None
        try:
            if not zipfile.is_zipfile(lp):
                return None  # descriptor (YAML) oradio -> let proc.launch hand it to oradio_player
            from bookmark.launch import resolve_open_plan
            return resolve_open_plan(lp, bricks_root=os.path.join(BASE, "bricks"))
        except Exception:
            return None

    def launch_station(self, station: StationInfo):
        print(f"DEBUG: launch_station called for {station.station_id}")
        print(f"DEBUG: Station path: {station.path}")
        name = (station.manifest.get("station", {}) or {}).get("name", station.station_id)
        self.ribbon_state.note_launch()

        plan = self._open_plan_for(station)
        mode = plan.get("mode") if plan else None

        # An oradio can open AS a launcher: run the target (a Steam game / exe / url) instead of a
        # runtime. The "visual museum" path.
        if mode == "shortcut":
            self._launch_shortcut_open(station, plan)
            return
        # A pure visual-loop oradio (or one whose app-brick isn't installed) IS already the live
        # backdrop in RibbonOS — there's nothing to spawn; settle on its loop. (No standalone player
        # by design; the file-manager path offers "open in RibbonOS" instead.)
        if mode == "loop":
            self.now_playing.config(text=f"Now Showing — {name}")
            self.now_sub.config(text=(f"app brick not installed: {plan['unresolved_brick']}"
                                      if plan.get("unresolved_brick") else "visual loop"))
            self._focus_station_ribbon(station)
            self._note_shell_activity()
            return

        # app / html / descriptor / legacy -> spawn via the runtime path (oradio_player resolves the
        # plan and executes it: app -> the brick asset e.g. bookmark.py, html -> served page, etc).
        _oled("loading_start", station_id=station.station_id)
        self.proc.launch(station)
        self.now_playing.config(text=f"Now Playing — {name}")
        self.now_sub.config(text="Launching runtime…")
        self.show_runtime()
        self._apply_ribbon_shell_state(force=True)

    def stop_station(self):
        self.proc.stop()
        self.now_playing.config(text="")
        self.now_sub.config(text="")
        self.show_home()
        self._note_shell_activity()
        # Force card refresh on Mac to ensure proper rendering
        if sys.platform == "darwin":
            self.root.after(50, self._force_card_refresh)

    # -----------------------------
    # Settings
    # -----------------------------
    def open_settings(self):
        win = tk.Toplevel(self.root)
        win.title("Settings")
        win.geometry(scaled_geometry(900, 600))
        win.configure(bg=UI["bg"])

        nb = ttk.Notebook(win)
        nb.pack(fill="both", expand=True, padx=12, pady=12)

        gen = tk.Frame(nb, bg=UI["bg"])
        nb.add(gen, text="General")
        self._build_general_settings(gen)

        mdl = tk.Frame(nb, bg=UI["bg"])
        nb.add(mdl, text="Models")
        self._build_model_settings(mdl)

        voc = tk.Frame(nb, bg=UI["bg"])
        nb.add(voc, text="Voices")
        self._build_voice_settings(voc)

        plug = tk.Frame(nb, bg=UI["bg"])
        nb.add(plug, text="Plugins")
        self._build_plugin_manager(plug)

        vis = tk.Frame(nb, bg=UI["bg"])
        nb.add(vis, text="Visual Models")
        self._build_visual_models_panel(vis)

        st = tk.Frame(nb, bg=UI["bg"])
        nb.add(st, text="Storage")
        self._build_storage_tools(st)

        acli = tk.Frame(nb, bg=UI["bg"])
        nb.add(acli, text="Audio CLI")
        self._build_audio_cli_settings(acli)

        env = tk.Frame(nb, bg=UI["bg"])
        nb.add(env, text="Environment")
        self._build_environment_settings(env)

    def _build_general_settings(self, parent: tk.Frame) -> None:
        """Build the General settings panel."""
        
        # Make scrollable
        scrollbar = tk.Scrollbar(parent, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        
        canvas = tk.Canvas(parent, bg=UI["bg"], highlightthickness=0, yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        
        scrollbar.configure(command=canvas.yview)
        
        scroll_frame = tk.Frame(canvas, bg=UI["bg"])
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
        
        tk.Label(scroll_frame, text="General Settings", font=FONT_H2, fg=UI["text"], bg=UI["bg"]).pack(
            anchor="w", padx=14, pady=(14, 8)
        )
        
        wrap = tk.Frame(scroll_frame, bg=UI["bg"])
        wrap.pack(fill="both", expand=True, padx=14, pady=8)
        
        cfg = get_global_config()
        general = cfg.get("general", {})
        
        # Auto-start last station
        auto_start_var = tk.BooleanVar(value=general.get("auto_start_last_station", False))
        auto_frame = tk.Frame(wrap, bg=UI["panel"], padx=12, pady=10)
        auto_frame.pack(fill="x", pady=8)
        tk.Checkbutton(
            auto_frame, 
            text="Auto-start last active station on launch",
            variable=auto_start_var,
            bg=UI["panel"], fg=UI["text"], selectcolor=UI["bg"],
            font=FONT_BODY
        ).pack(anchor="w")
        
        # Web Server Settings
        server_frame = tk.LabelFrame(wrap, text="🌐 Web Server (Tailscale / LAN Access)", fg=UI["text"],
                                      bg=UI["panel"], font=FONT_BODY, padx=12, pady=8)
        server_frame.pack(fill="x", pady=8)
        
        always_server_var = tk.BooleanVar(value=general.get("always_launch_server", False))
        tk.Checkbutton(
            server_frame,
            text="Always launch web server on startup",
            variable=always_server_var,
            bg=UI["panel"], fg=UI["text"], selectcolor=UI["bg"],
            font=FONT_BODY
        ).pack(anchor="w")
        tk.Label(server_frame, text="Starts the Radio OS web shell automatically when the desktop app opens.\n"
                 "Access stations from any browser on your network or via Tailscale.",
                 fg=UI["muted"], bg=UI["panel"], font=FONT_SMALL, justify="left").pack(anchor="w", pady=(2, 8))
        
        tk.Label(server_frame, text="Web Server Port:", fg=UI["text"],
                 bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")
        server_port_var = tk.StringVar(value=str(general.get("web_server_port", 7800)))
        tk.Entry(server_frame, textvariable=server_port_var, bg=UI["card"], fg=UI["text"],
                 insertbackground=UI["text"], width=10).pack(anchor="w", pady=(2, 4))
        tk.Label(server_frame, text="(Default: 7800 — accessible via http://your-ip:port)",
                 fg=UI["muted"], bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")
        
        # Audio CLI Settings
        audio_cli_frame = tk.LabelFrame(wrap, text="🎤 Audio CLI (Voice Control)", fg=UI["text"],
                                         bg=UI["panel"], font=FONT_BODY, padx=12, pady=8)
        audio_cli_frame.pack(fill="x", pady=8)
        
        audio_cli_var = tk.BooleanVar(value=general.get("audio_cli_enabled", False))
        tk.Checkbutton(
            audio_cli_frame,
            text="Enable Audio CLI on startup",
            variable=audio_cli_var,
            bg=UI["panel"], fg=UI["text"], selectcolor=UI["bg"],
            font=FONT_BODY
        ).pack(anchor="w")
        tk.Label(audio_cli_frame, text="Voice-command interface. Say 'Hey Radio OS' to activate,\n"
                 "'Thanks Radio OS' to deactivate. Requires microphone access.\n"
                 "Uses whisper.cpp (set WHISPER_CPP_BIN / WHISPER_CPP_MODEL env vars)\n"
                 "or falls back to Google Speech Recognition.",
                 fg=UI["muted"], bg=UI["panel"], font=FONT_SMALL, justify="left").pack(anchor="w", pady=(2, 8))

        # Status poll interval
        poll_frame = tk.LabelFrame(wrap, text="Status Update Interval", fg=UI["text"], 
                                    bg=UI["panel"], font=FONT_BODY, padx=12, pady=8)
        poll_frame.pack(fill="x", pady=8)
        
        tk.Label(poll_frame, text="Update runtime status every (ms):", fg=UI["text"], 
                bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")
        poll_var = tk.StringVar(value=str(general.get("status_poll_ms", 1000)))
        tk.Entry(poll_frame, textvariable=poll_var, bg=UI["card"], fg=UI["text"], 
                insertbackground=UI["text"], width=10).pack(anchor="w", pady=(2, 4))
        tk.Label(poll_frame, text="(Lower = more responsive, higher = less CPU usage)", 
                fg=UI["muted"], bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")
        
        # Theme
        theme_frame = tk.LabelFrame(wrap, text="UI Theme", fg=UI["text"], 
                                     bg=UI["panel"], font=FONT_BODY, padx=12, pady=8)
        theme_frame.pack(fill="x", pady=8)
        
        tk.Label(theme_frame, text="Choose a color theme:", fg=UI["text"], 
                bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")
        
        theme_var = tk.StringVar(value=general.get("theme", "dark"))
        
        # Theme selection with preview swatches
        theme_select_frame = tk.Frame(theme_frame, bg=UI["panel"])
        theme_select_frame.pack(fill="x", pady=(2, 4))
        
        tk.Label(theme_select_frame, text="Theme:", fg=UI["text"], 
                bg=UI["panel"], font=FONT_SMALL).pack(side="left", padx=(0, 8))
        
        theme_combo = ttk.Combobox(theme_select_frame, textvariable=theme_var, 
                                   values=list(COLOR_THEMES.keys()), state="readonly", width=15)
        theme_combo.pack(side="left", padx=(0, 12))
        
        # Preview swatches
        swatch_frame = tk.Frame(theme_select_frame, bg=UI["panel"])
        swatch_frame.pack(side="left")
        
        preview_swatches = []
        
        def update_preview(*args):
            theme_name = theme_var.get()
            if theme_name in COLOR_THEMES:
                colors = COLOR_THEMES[theme_name]
                swatch_colors = [colors["bg"], colors["panel"], colors["accent"], colors["text"]]
                for i, swatch in enumerate(preview_swatches):
                    if i < len(swatch_colors):
                        swatch.config(bg=swatch_colors[i])
        
        # Create 4 color swatches
        for i in range(4):
            swatch = tk.Label(swatch_frame, text="  ", bg=UI["bg"], width=3, height=1, relief="solid", borderwidth=1)
            swatch.pack(side="left", padx=1)
            preview_swatches.append(swatch)
        
        theme_combo.bind("<<ComboboxSelected>>", update_preview)
        update_preview()  # Initial preview
        
        tk.Label(theme_frame, text="(Requires restart to apply)", 
                fg=UI["muted"], bg=UI["panel"], font=FONT_SMALL).pack(anchor="w", pady=(4, 0))

        # UI Scale
        scale_frame = tk.LabelFrame(wrap, text="UI Scale (DPI Zoom)", fg=UI["text"], 
                                     bg=UI["panel"], font=FONT_BODY, padx=12, pady=8)
        scale_frame.pack(fill="x", pady=8)

        tk.Label(scale_frame, text="Zoom Level (0.8 - 2.5):", fg=UI["text"], 
                bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")

        # Use global UI_SCALE as default
        # Note: we re-read config here to be safe, though UI_SCALE global exists
        _cur_gen = get_global_config().get("general", {})
        scale_var = tk.DoubleVar(value=_cur_gen.get("ui_scale", 1.0))
        
        scale_slider = tk.Scale(scale_frame, from_=0.8, to=2.5, resolution=0.1, orient="horizontal",
                                variable=scale_var, bg=UI["panel"], fg=UI["text"], highlightthickness=0, length=300)
        scale_slider.pack(anchor="w", pady=(2, 4))
        
        tk.Label(scale_frame, text="(Requires restart to apply)", 
                fg=UI["muted"], bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")
        
        # Save button
        def save_general():
            cfg = get_global_config()
            new_theme = theme_var.get()
            new_scale = scale_var.get()
            
            old_gen = cfg.get("general", {})
            old_theme = old_gen.get("theme", "dark")
            old_scale = float(old_gen.get("ui_scale", 1.0))
            
            cfg["general"] = {
                "auto_start_last_station": auto_start_var.get(),
                "always_launch_server": always_server_var.get(),
                "web_server_port": int(server_port_var.get() or 7800),
                "audio_cli_enabled": audio_cli_var.get(),
                "status_poll_ms": int(poll_var.get() or 1000),
                "theme": new_theme,
                "ui_scale": new_scale,
            }
            save_global_config(cfg)
            
            # If theme or scale changed, restart the app
            if new_theme != old_theme or abs(new_scale - old_scale) > 0.001:
                if messagebox.askyesno("Display Settings Changed", 
                    "Display settings will be applied after restart.\n\nClose and reopen the application?"):
                    self._restart_app()
                    return
            
            messagebox.showinfo("Success", "General settings saved!")
        
        tk.Button(wrap, text="Save Settings", font=FONT_BODY, bg=UI["accent"], 
                 fg="#000", relief="flat", command=save_general).pack(anchor="w", pady=16)

    def _build_model_settings(self, parent: tk.Frame) -> None:
        """Build the Model Provider settings panel (defaults for new stations)."""
        
        # Make scrollable
        scrollbar = tk.Scrollbar(parent, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        
        canvas = tk.Canvas(parent, bg=UI["bg"], highlightthickness=0, yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        
        scrollbar.configure(command=canvas.yview)
        
        scroll_frame = tk.Frame(canvas, bg=UI["bg"])
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
        
        tk.Label(scroll_frame, text="Default Model Settings", font=FONT_H2, fg=UI["text"], bg=UI["bg"]).pack(
            anchor="w", padx=14, pady=(14, 4)
        )
        tk.Label(scroll_frame, text="Set default LLM providers, endpoints, and models for new stations", 
                font=FONT_SMALL, fg=UI["muted"], bg=UI["bg"]).pack(anchor="w", padx=14, pady=(0, 8))
        
        wrap = tk.Frame(scroll_frame, bg=UI["bg"])
        wrap.pack(fill="both", expand=True, padx=14, pady=8)
        
        cfg = get_global_config()
        models = cfg.get("default_models", {})
        courtroom = cfg.get("courtroom", {}) if isinstance(cfg.get("courtroom"), dict) else {}

        # LLM Provider Selection
        provider_frame = tk.LabelFrame(wrap, text="LLM Provider", fg=UI["text"], 
                                       bg=UI["panel"], font=FONT_BODY, padx=12, pady=8)
        provider_frame.pack(fill="x", pady=8)
        
        tk.Label(provider_frame, text="Primary Provider:", fg=UI["text"], 
                bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")
        provider_var = tk.StringVar(value=models.get("provider", "ollama"))
        provider_options = ["ollama", "anthropic", "openai", "google"]
        provider_combo = ttk.Combobox(provider_frame, textvariable=provider_var, 
                                     values=provider_options, state="readonly", width=30)
        provider_combo.pack(anchor="w", pady=(2, 8))
        
        tk.Label(provider_frame, text="• ollama: Local models or OpenAI-compatible API\n"
                                     "• anthropic: Claude API (requires API key)\n"
                                     "• openai: GPT models (requires API key)\n"
                                     "• google: Gemini API (requires API key)", 
                fg=UI["muted"], bg=UI["panel"], font=FONT_SMALL, justify="left").pack(anchor="w")
        
        # Ollama/Local Endpoint
        ollama_frame = tk.LabelFrame(wrap, text="Ollama / Local LLM Endpoint", fg=UI["text"], 
                                     bg=UI["panel"], font=FONT_BODY, padx=12, pady=8)
        ollama_frame.pack(fill="x", pady=8)
        
        tk.Label(ollama_frame, text="Endpoint URL:", fg=UI["text"], 
                bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")
        tk.Label(ollama_frame, text="(e.g., http://localhost:11434 or any OpenAI-compatible endpoint)", 
                fg=UI["muted"], bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")
        
        ollama_var = tk.StringVar(value=models.get("llm_endpoint", "http://127.0.0.1:11434/api/generate"))
        tk.Entry(ollama_frame, textvariable=ollama_var, bg=UI["card"], fg=UI["text"], 
                insertbackground=UI["text"]).pack(fill="x", pady=(2, 8))
        
        # API Keys for Cloud Providers
        api_frame = tk.LabelFrame(wrap, text="Cloud Provider API Keys", fg=UI["text"], 
                                  bg=UI["panel"], font=FONT_BODY, padx=12, pady=8)
        api_frame.pack(fill="x", pady=8)
        
        # Anthropic API Key
        tk.Label(api_frame, text="Anthropic API Key (Claude):", fg=UI["text"], 
                bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")
        anthropic_var = tk.StringVar(value=models.get("anthropic_api_key", ""))
        tk.Entry(api_frame, textvariable=anthropic_var, bg=UI["card"], fg=UI["text"], 
                insertbackground=UI["text"], show="•").pack(fill="x", pady=(2, 8))
        
        # OpenAI API Key
        tk.Label(api_frame, text="OpenAI API Key (GPT):", fg=UI["text"], 
                bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")
        openai_var = tk.StringVar(value=models.get("openai_api_key", ""))
        tk.Entry(api_frame, textvariable=openai_var, bg=UI["card"], fg=UI["text"], 
                insertbackground=UI["text"], show="•").pack(fill="x", pady=(2, 8))
        
        # Google/Gemini API Key
        tk.Label(api_frame, text="Google API Key (Gemini):", fg=UI["text"], 
                bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")
        google_var = tk.StringVar(value=models.get("google_api_key", ""))
        tk.Entry(api_frame, textvariable=google_var, bg=UI["card"], fg=UI["text"], 
                insertbackground=UI["text"], show="•").pack(fill="x", pady=(2, 8))
        
        # Producer Model
        producer_frame = tk.LabelFrame(wrap, text="Default Producer Model", fg=UI["text"], 
                                       bg=UI["panel"], font=FONT_BODY, padx=12, pady=8)
        producer_frame.pack(fill="x", pady=8)
        
        tk.Label(producer_frame, text="Model Name:", fg=UI["text"], 
                bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")
        tk.Label(producer_frame, text="(e.g., llama3.1:70b, claude-3-opus-20240229, gpt-4o, gemini-1.5-pro)", 
                fg=UI["muted"], bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")
        
        producer_var = tk.StringVar(value=models.get("producer_model", "rnj-1:8b"))
        tk.Entry(producer_frame, textvariable=producer_var, bg=UI["card"], fg=UI["text"], 
                insertbackground=UI["text"]).pack(fill="x", pady=(2, 8))
        tk.Label(producer_frame, text="(Context-building, slower, higher quality)", 
                fg=UI["muted"], bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")
        
        # Host Model
        host_frame = tk.LabelFrame(wrap, text="Default Host Model", fg=UI["text"], 
                                   bg=UI["panel"], font=FONT_BODY, padx=12, pady=8)
        host_frame.pack(fill="x", pady=8)
        
        tk.Label(host_frame, text="Model Name:", fg=UI["text"], 
                bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")
        tk.Label(host_frame, text="(e.g., llama3.1:70b, claude-3-opus-20240229, gpt-4o, gemini-1.5-pro)", 
                fg=UI["muted"], bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")
        
        host_var = tk.StringVar(value=models.get("host_model", "rnj-1:8b"))
        tk.Entry(host_frame, textvariable=host_var, bg=UI["card"], fg=UI["text"], 
                insertbackground=UI["text"]).pack(fill="x", pady=(2, 8))
        tk.Label(host_frame, text="(Live hosting, faster responses)", 
                fg=UI["muted"], bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")
        
        # Courtroom (local 27b) — the OpenAI-compatible local LLM the Bookmark courtroom chat uses.
        court_frame = tk.LabelFrame(wrap, text="🎟️ Courtroom (local 27b)", fg=UI["text"],
                                    bg=UI["panel"], font=FONT_BODY, padx=12, pady=8)
        court_frame.pack(fill="x", pady=8)
        tk.Label(court_frame, text="OpenAI-compatible base URL (e.g. llama.cpp --jinja server):",
                 fg=UI["text"], bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")
        court_url_var = tk.StringVar(value=courtroom.get("base_url", "http://127.0.0.1:9080"))
        tk.Entry(court_frame, textvariable=court_url_var, bg=UI["card"], fg=UI["text"],
                 insertbackground=UI["text"]).pack(fill="x", pady=(2, 8))
        tk.Label(court_frame, text="Model name (blank = server default):", fg=UI["text"],
                 bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")
        court_model_var = tk.StringVar(value=courtroom.get("model", ""))
        tk.Entry(court_frame, textvariable=court_model_var, bg=UI["card"], fg=UI["text"],
                 insertbackground=UI["text"]).pack(fill="x", pady=(2, 8))
        tk.Label(court_frame, text="Max tokens (thinking models need lots — 4096+):", fg=UI["text"],
                 bg=UI["panel"], font=FONT_SMALL).pack(anchor="w", pady=(6, 0))
        court_maxtok_var = tk.StringVar(value=str(courtroom.get("max_tokens", 4096)))
        tk.Entry(court_frame, textvariable=court_maxtok_var, bg=UI["card"], fg=UI["text"],
                 insertbackground=UI["text"]).pack(fill="x", pady=(2, 8))
        court_enabled_var = tk.BooleanVar(value=bool(courtroom.get("enabled", True)))
        tk.Checkbutton(court_frame, text="Enable 27b replies in the courtroom chat",
                       variable=court_enabled_var, fg=UI["text"], bg=UI["panel"],
                       selectcolor=UI["card"], activebackground=UI["panel"],
                       activeforeground=UI["text"], font=FONT_SMALL).pack(anchor="w")

        # Save button
        def save_models():
            cfg = get_global_config()
            cfg["default_models"] = {
                "provider": provider_var.get(),
                "llm_endpoint": ollama_var.get(),
                "anthropic_api_key": anthropic_var.get(),
                "openai_api_key": openai_var.get(),
                "google_api_key": google_var.get(),
                "producer_model": producer_var.get(),
                "host_model": host_var.get(),
            }
            try:
                _max_tok = int(court_maxtok_var.get().strip() or 4096)
            except ValueError:
                _max_tok = 4096
            cfg["courtroom"] = {
                "base_url": court_url_var.get().strip(),
                "model": court_model_var.get().strip(),
                "enabled": bool(court_enabled_var.get()),
                "max_tokens": _max_tok,
            }
            save_global_config(cfg)
            messagebox.showinfo("Success", "Model settings saved!")
        
        tk.Button(wrap, text="Save Settings", font=FONT_BODY, bg=UI["accent"], 
                 fg="#000", relief="flat", command=save_models).pack(anchor="w", pady=16)

    def _build_voice_settings(self, parent: tk.Frame) -> None:
        """Build the Voice settings panel (defaults for new stations)."""
        
        # Make scrollable
        scrollbar = tk.Scrollbar(parent, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        
        canvas = tk.Canvas(parent, bg=UI["bg"], highlightthickness=0, yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        
        scrollbar.configure(command=canvas.yview)
        
        scroll_frame = tk.Frame(canvas, bg=UI["bg"])
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
        
        tk.Label(scroll_frame, text="Default Voice Settings", font=FONT_H2, fg=UI["text"], bg=UI["bg"]).pack(
            anchor="w", padx=14, pady=(14, 4)
        )
        tk.Label(scroll_frame, text="Set global voice paths used as defaults for new stations", 
                font=FONT_SMALL, fg=UI["muted"], bg=UI["bg"]).pack(anchor="w", padx=14, pady=(0, 8))
        
        wrap = tk.Frame(scroll_frame, bg=UI["bg"])
        wrap.pack(fill="both", expand=True, padx=14, pady=8)
        
        cfg = get_global_config()
        voices = cfg.get("default_voices", {})
        
        # Voice Provider Selection
        provider_frame = tk.LabelFrame(wrap, text="Voice Provider", fg=UI["text"], 
                                       bg=UI["panel"], font=FONT_BODY, padx=12, pady=8)
        provider_frame.pack(fill="x", pady=8)
        
        tk.Label(provider_frame, text="TTS Provider:", fg=UI["text"], 
                bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")
        provider_var = tk.StringVar(value=voices.get("provider", "piper"))
        provider_options = ["piper", "kokoro", "openai", "elevenlabs", "google_cloud_tts", "azure_speech"]
        provider_combo = ttk.Combobox(provider_frame, textvariable=provider_var, 
                                     values=provider_options, state="readonly", width=30)
        provider_combo.pack(anchor="w", pady=(2, 8))
        
        tk.Label(provider_frame, text="• piper: Local offline TTS (requires binary + ONNX models)\n"
                                     "• elevenlabs: ElevenLabs API (requires API key)\n"
                                     "• google_cloud_tts: Google Cloud TTS (requires credentials)\n"
                                     "• azure_speech: Azure Speech Services (requires API key)", 
                fg=UI["muted"], bg=UI["panel"], font=FONT_SMALL, justify="left").pack(anchor="w")
        
        # Piper Binary (for local)
        piper_frame = tk.LabelFrame(wrap, text="Locale/Offline TTS Configuration", fg=UI["text"], 
                                  bg=UI["panel"], font=FONT_BODY, padx=12, pady=8)
        piper_frame.pack(fill="x", pady=8)
        
        tk.Label(piper_frame, text="Piper Binary Path (if using Piper):", fg=UI["text"], 
                bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")

        piper_row = tk.Frame(piper_frame, bg=UI["panel"])
        piper_row.pack(fill="x", pady=(2, 4))
        
        piper_var = tk.StringVar(value=voices.get("piper_bin", ""))
        tk.Entry(piper_row, textvariable=piper_var, bg=UI["card"], fg=UI["text"], 
                insertbackground=UI["text"]).pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        def browse_piper():
            path = filedialog.askopenfilename(parent=parent.winfo_toplevel(),
                                              title="Select Piper Binary")
            if path:
                piper_var.set(path)
        
        tk.Button(piper_row, text="Browse", bg=UI["card"], fg=UI["text"], relief="flat",
                 command=browse_piper).pack(side="left")
        
        # API Configuration (for cloud providers)
        api_frame = tk.LabelFrame(wrap, text="API Provider Configuration", fg=UI["text"], 
                                  bg=UI["panel"], font=FONT_BODY, padx=12, pady=8)
        api_frame.pack(fill="x", pady=8)
        
        tk.Label(api_frame, text="API Key (ElevenLabs/Azure):", fg=UI["text"], 
                bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")
        api_key_var = tk.StringVar(value=voices.get("api_key", ""))
        tk.Entry(api_frame, textvariable=api_key_var, bg=UI["card"], fg=UI["text"], 
                insertbackground=UI["text"], show="•").pack(fill="x", pady=(2, 8))
        
        tk.Label(api_frame, text="Google Cloud Credentials Path (JSON):", fg=UI["text"], 
                bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")
        
        gcloud_row = tk.Frame(api_frame, bg=UI["panel"])
        gcloud_row.pack(fill="x", pady=(2, 4))
        
        gcloud_var = tk.StringVar(value=voices.get("google_credentials", ""))
        tk.Entry(gcloud_row, textvariable=gcloud_var, bg=UI["card"], fg=UI["text"], 
                insertbackground=UI["text"]).pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        def browse_gcloud():
            path = filedialog.askopenfilename(parent=parent.winfo_toplevel(),
                                              title="Select Google Credentials JSON",
                                              filetypes=[("JSON", "*.json"), ("All", "*.*")])
            if path:
                gcloud_var.set(path)
        
        tk.Button(gcloud_row, text="Browse", bg=UI["card"], fg=UI["text"], relief="flat",
                 command=browse_gcloud).pack(side="left")
        
        # Global Voices Directory
        voices_dir_frame = tk.LabelFrame(wrap, text="Global Voices Directory (Local Models)", fg=UI["text"], 
                                         bg=UI["panel"], font=FONT_BODY, padx=12, pady=8)
        voices_dir_frame.pack(fill="x", pady=8)
        
        tk.Label(voices_dir_frame, text="Voice Models Directory:", fg=UI["text"], 
                bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")
        tk.Label(voices_dir_frame, text="(Stations can reference voices relative to this path)", 
                fg=UI["muted"], bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")
        
        voices_dir_row = tk.Frame(voices_dir_frame, bg=UI["panel"])
        voices_dir_row.pack(fill="x", pady=(2, 4))
        
        voices_dir_var = tk.StringVar(value=voices.get("voices_directory", ""))
        tk.Entry(voices_dir_row, textvariable=voices_dir_var, bg=UI["card"], fg=UI["text"], 
                insertbackground=UI["text"]).pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        def browse_voices_dir():
            path = filedialog.askdirectory(parent=parent.winfo_toplevel(),
                                          title="Select Voices Directory")
            if path:
                voices_dir_var.set(path)
        
        tk.Button(voices_dir_row, text="Browse", bg=UI["card"], fg=UI["text"], relief="flat",
                 command=browse_voices_dir).pack(side="left")
        
        # Default Voice Presets (for Piper local models or API voice IDs)
        presets_frame = tk.LabelFrame(wrap, text="Default Character Voices", fg=UI["text"], 
                                      bg=UI["panel"], font=FONT_BODY, padx=12, pady=8)
        presets_frame.pack(fill="x", pady=8)
        
        tk.Label(presets_frame, text="Piper: .onnx paths | Kokoro: voice keys (e.g. af_sarah) | API: voice IDs", 
                fg=UI["muted"], bg=UI["panel"], font=FONT_SMALL).pack(anchor="w", pady=(0, 8))
        
        voice_chars = ["host", "expert", "skeptic", "optimist", "coach"]
        voice_vars = {}
        
        for char in voice_chars:
            char_row = tk.Frame(presets_frame, bg=UI["panel"])
            char_row.pack(fill="x", pady=2)
            
            tk.Label(char_row, text=f"{char.title()}:", fg=UI["text"], bg=UI["panel"], 
                    font=FONT_SMALL, width=10, anchor="w").pack(side="left")
            
            var = tk.StringVar(value=voices.get(f"voice_{char}", ""))
            voice_vars[char] = var
            
            tk.Entry(char_row, textvariable=var, bg=UI["card"], fg=UI["text"], 
                    insertbackground=UI["text"]).pack(side="left", fill="x", expand=True, padx=(0, 4))
            
            tk.Button(char_row, text="...", bg=UI["card"], fg=UI["text"], relief="flat", width=3,
                     command=lambda v=var: self._browse_voice_file(v, parent)).pack(side="left")
        
        # Save button
        def save_voices():
            cfg = get_global_config()
            voice_cfg = {
                "provider": provider_var.get(),
                "piper_bin": piper_var.get(),
                "api_key": api_key_var.get(),
                "google_credentials": gcloud_var.get(),
                "voices_directory": voices_dir_var.get(),
            }
            for char, var in voice_vars.items():
                voice_cfg[f"voice_{char}"] = var.get()
            
            cfg["default_voices"] = voice_cfg
            save_global_config(cfg)
            messagebox.showinfo("Success", "Voice settings saved!")
        
        tk.Button(wrap, text="Save Settings", font=FONT_BODY, bg=UI["accent"], 
                 fg="#000", relief="flat", command=save_voices).pack(anchor="w", pady=16)

    def _browse_voice_file(self, var: tk.StringVar, parent: tk.Widget) -> None:
        """Browse for a voice file (.onnx)."""
        path = filedialog.askopenfilename(
            parent=parent.winfo_toplevel(),
            title="Select Voice Model",
            filetypes=[("ONNX Models", "*.onnx"), ("All Files", "*.*")]
        )
        if path:
            var.set(path)

    def _build_storage_tools(self, parent: tk.Frame) -> None:
        """Build the Storage tools panel."""
        
        # Make scrollable
        scrollbar = tk.Scrollbar(parent, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        
        canvas = tk.Canvas(parent, bg=UI["bg"], highlightthickness=0, yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        
        scrollbar.configure(command=canvas.yview)
        
        scroll_frame = tk.Frame(canvas, bg=UI["bg"])
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
        
        tk.Label(scroll_frame, text="Storage & Maintenance", font=FONT_H2, fg=UI["text"], bg=UI["bg"]).pack(
            anchor="w", padx=14, pady=(14, 8)
        )
        
        wrap = tk.Frame(scroll_frame, bg=UI["bg"])
        wrap.pack(fill="both", expand=True, padx=14, pady=8)
        
        # Log Management
        log_frame = tk.LabelFrame(wrap, text="Log Management", fg=UI["text"], 
                                  bg=UI["panel"], font=FONT_BODY, padx=12, pady=8)
        log_frame.pack(fill="x", pady=8)
        
        tk.Label(log_frame, text="Clean up old runtime logs to free disk space", 
                fg=UI["muted"], bg=UI["panel"], font=FONT_SMALL).pack(anchor="w", pady=(0, 8))
        
        def clear_all_logs():
            if not messagebox.askyesno("Clear Logs", 
                                      "Delete all runtime.log files from all stations?\n\nThis cannot be undone."):
                return
            
            count = 0
            for station in self.stations:
                log_path = os.path.join(station.path, "runtime.log")
                if os.path.exists(log_path):
                    try:
                        os.remove(log_path)
                        count += 1
                    except Exception as e:
                        print(f"Failed to delete {log_path}: {e}")
            
            messagebox.showinfo("Logs Cleared", f"Deleted {count} log file(s)")
        
        tk.Button(log_frame, text="Clear All Station Logs", bg=UI["card"], fg=UI["text"], 
                 relief="flat", command=clear_all_logs, font=FONT_BODY).pack(anchor="w", pady=4)
        
        # Database Management
        db_frame = tk.LabelFrame(wrap, text="Database Management", fg=UI["text"], 
                                 bg=UI["panel"], font=FONT_BODY, padx=12, pady=8)
        db_frame.pack(fill="x", pady=8)
        
        tk.Label(db_frame, text="Manage station databases and queue state", 
                fg=UI["muted"], bg=UI["panel"], font=FONT_SMALL).pack(anchor="w", pady=(0, 8))
        
        def vacuum_databases():
            if not messagebox.askyesno("Vacuum Databases", 
                                      "Optimize all station databases?\n\nThis may take a moment."):
                return
            
            import sqlite3
            count = 0
            for station in self.stations:
                db_path = os.path.join(station.path, "station.sqlite")
                if os.path.exists(db_path):
                    try:
                        conn = sqlite3.connect(db_path)
                        conn.execute("VACUUM")
                        conn.close()
                        count += 1
                    except Exception as e:
                        print(f"Failed to vacuum {db_path}: {e}")
            
            messagebox.showinfo("Databases Optimized", f"Vacuumed {count} database(s)")
        
        tk.Button(db_frame, text="Vacuum All Databases", bg=UI["card"], fg=UI["text"], 
                 relief="flat", command=vacuum_databases, font=FONT_BODY).pack(anchor="w", pady=4)
        
        # Export/Backup
        export_frame = tk.LabelFrame(wrap, text="Backup & Export", fg=UI["text"], 
                                     bg=UI["panel"], font=FONT_BODY, padx=12, pady=8)
        export_frame.pack(fill="x", pady=8)
        
        tk.Label(export_frame, text="Export station configurations for backup or sharing", 
                fg=UI["muted"], bg=UI["panel"], font=FONT_SMALL).pack(anchor="w", pady=(0, 8))
        
        def export_station():
            if not self.stations:
                messagebox.showwarning("No Stations", "No stations to export")
                return
            
            # Just use the focused station (falls back to the first if the
            # "All .oradios" box is focused).
            station = self._focused_station() or self.stations[0]
            if station is not None:

                dest = filedialog.asksaveasfilename(
                    parent=parent.winfo_toplevel(),
                    title=f"Export {station.station_id}",
                    defaultextension=".yaml",
                    initialfile=f"{station.station_id}_manifest.yaml",
                    filetypes=[("YAML Files", "*.yaml"), ("All Files", "*.*")]
                )
                
                if dest:
                    import shutil
                    src = os.path.join(station.path, "manifest.yaml")
                    try:
                        shutil.copy2(src, dest)
                        messagebox.showinfo("Success", f"Exported manifest to:\n{dest}")
                    except Exception as e:
                        messagebox.showerror("Export Failed", str(e))
        
        tk.Button(export_frame, text="Export Selected Station Manifest", bg=UI["card"], 
                 fg=UI["text"], relief="flat", command=export_station, font=FONT_BODY).pack(anchor="w", pady=4)
        
        # Global config path info
        info_frame = tk.LabelFrame(wrap, text="Configuration Location", fg=UI["text"], 
                                   bg=UI["panel"], font=FONT_BODY, padx=12, pady=8)
        info_frame.pack(fill="x", pady=8)
        
        config_path = get_global_config_path()
        tk.Label(info_frame, text=f"Global config: {config_path}", 
                fg=UI["muted"], bg=UI["panel"], font=FONT_SMALL, wraplength=800).pack(anchor="w")
        
        def open_config_dir():
            import subprocess
            import platform
            config_dir = os.path.dirname(config_path)
            
            if platform.system() == "Windows":
                os.startfile(config_dir)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", config_dir])
            else:
                subprocess.Popen(["xdg-open", config_dir])
        
        tk.Button(info_frame, text="Open Config Directory", bg=UI["card"], fg=UI["text"], 
                 relief="flat", command=open_config_dir, font=FONT_BODY).pack(anchor="w", pady=(8, 0))

    def _build_audio_cli_settings(self, parent: tk.Frame) -> None:
        """Build the Audio CLI settings panel (default interface mode, wake phrases, etc.)."""

        # Make scrollable
        scrollbar = tk.Scrollbar(parent, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        canvas = tk.Canvas(parent, bg=UI["bg"], highlightthickness=0, yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar.configure(command=canvas.yview)

        scroll_frame = tk.Frame(canvas, bg=UI["bg"])
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        tk.Label(scroll_frame, text="Audio CLI Settings", font=FONT_H2, fg=UI["text"], bg=UI["bg"]).pack(
            anchor="w", padx=14, pady=(14, 4)
        )
        tk.Label(scroll_frame, text="Configure voice-command interface behaviour, default mode, and wake phrases",
                font=FONT_SMALL, fg=UI["muted"], bg=UI["bg"]).pack(anchor="w", padx=14, pady=(0, 8))

        wrap = tk.Frame(scroll_frame, bg=UI["bg"])
        wrap.pack(fill="both", expand=True, padx=14, pady=8)

        cfg = get_global_config()
        acli_cfg = cfg.get("audio_cli", {})

        # ── Default Interface Mode ──
        mode_frame = tk.LabelFrame(wrap, text="🖥  Default Interface Mode", fg=UI["text"],
                                    bg=UI["panel"], font=FONT_BODY, padx=12, pady=8)
        mode_frame.pack(fill="x", pady=8)

        tk.Label(mode_frame,
                 text="Choose which interface Audio CLI controls by default when started.",
                 fg=UI["muted"], bg=UI["panel"], font=FONT_SMALL, justify="left").pack(anchor="w", pady=(0, 6))

        mode_var = tk.StringVar(value=acli_cfg.get("default_mode", "tkinter"))

        mode_select_frame = tk.Frame(mode_frame, bg=UI["panel"])
        mode_select_frame.pack(fill="x", pady=(0, 4))

        tk.Radiobutton(
            mode_select_frame, text="Desktop (tkinter)  — control the desktop shell directly",
            variable=mode_var, value="tkinter",
            bg=UI["panel"], fg=UI["text"], selectcolor=UI["bg"],
            font=FONT_BODY, anchor="w"
        ).pack(anchor="w", pady=2)

        tk.Radiobutton(
            mode_select_frame, text="Web  — control Radio OS via the web server REST API",
            variable=mode_var, value="web",
            bg=UI["panel"], fg=UI["text"], selectcolor=UI["bg"],
            font=FONT_BODY, anchor="w"
        ).pack(anchor="w", pady=2)

        tk.Label(mode_frame,
                 text="You can always switch modes at runtime by saying\n"
                      "'switch to web mode' or 'switch to desktop mode'.",
                 fg=UI["muted"], bg=UI["panel"], font=FONT_SMALL, justify="left").pack(anchor="w", pady=(4, 0))

        # ── Audio Output Mode (Speaker / Headphone) ──
        audio_mode_frame = tk.LabelFrame(wrap, text="🔊  Audio Output Mode", fg=UI["text"],
                                          bg=UI["panel"], font=FONT_BODY, padx=12, pady=8)
        audio_mode_frame.pack(fill="x", pady=8)

        tk.Label(audio_mode_frame,
                 text="Choose how Audio CLI handles its own voice output and mic input.",
                 fg=UI["muted"], bg=UI["panel"], font=FONT_SMALL, justify="left").pack(anchor="w", pady=(0, 6))

        audio_mode_var = tk.StringVar(value=acli_cfg.get("audio_output_mode", "speaker"))

        audio_mode_select = tk.Frame(audio_mode_frame, bg=UI["panel"])
        audio_mode_select.pack(fill="x", pady=(0, 4))

        tk.Radiobutton(
            audio_mode_select,
            text="Speaker  — mic is muted while speaking, barge-in disabled\n"
                 "          (prevents self-interruption on laptop / desktop speakers)",
            variable=audio_mode_var, value="speaker",
            bg=UI["panel"], fg=UI["text"], selectcolor=UI["bg"],
            font=FONT_BODY, anchor="w", justify="left"
        ).pack(anchor="w", pady=2)

        tk.Radiobutton(
            audio_mode_select,
            text="Headphone  — mic stays live, barge-in enabled\n"
                 "             (you can interrupt narration by speaking)",
            variable=audio_mode_var, value="headphone",
            bg=UI["panel"], fg=UI["text"], selectcolor=UI["bg"],
            font=FONT_BODY, anchor="w", justify="left"
        ).pack(anchor="w", pady=2)

        tk.Label(audio_mode_frame,
                 text="You can also switch at runtime by saying\n"
                      "'switch to speaker mode' or 'switch to headphone mode'.",
                 fg=UI["muted"], bg=UI["panel"], font=FONT_SMALL, justify="left").pack(anchor="w", pady=(4, 0))

        # ── Web Server URL (used for web mode) ──
        url_frame = tk.LabelFrame(wrap, text="🌐 Web Server URL", fg=UI["text"],
                                   bg=UI["panel"], font=FONT_BODY, padx=12, pady=8)
        url_frame.pack(fill="x", pady=8)

        tk.Label(url_frame,
                 text="Base URL of the Radio OS web server (used when default mode is Web).",
                 fg=UI["muted"], bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")

        url_var = tk.StringVar(value=acli_cfg.get("web_url", "http://127.0.0.1:7800"))
        tk.Entry(url_frame, textvariable=url_var, bg=UI["card"], fg=UI["text"],
                 insertbackground=UI["text"], font=FONT_BODY, width=40).pack(anchor="w", pady=(4, 2))
        tk.Label(url_frame, text="(Default: http://127.0.0.1:7800)",
                 fg=UI["muted"], bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")

        # ── Wake / Exit Phrases ──
        phrase_frame = tk.LabelFrame(wrap, text="🎙  Wake & Exit Phrases", fg=UI["text"],
                                      bg=UI["panel"], font=FONT_BODY, padx=12, pady=8)
        phrase_frame.pack(fill="x", pady=8)

        tk.Label(phrase_frame, text="Wake phrase (activates session):", fg=UI["text"],
                 bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")
        wake_var = tk.StringVar(value=acli_cfg.get("wake_phrase", "hey radio"))
        tk.Entry(phrase_frame, textvariable=wake_var, bg=UI["card"], fg=UI["text"],
                 insertbackground=UI["text"], font=FONT_BODY, width=30).pack(anchor="w", pady=(2, 8))

        tk.Label(phrase_frame, text="Exit phrase (ends session):", fg=UI["text"],
                 bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")
        exit_var = tk.StringVar(value=acli_cfg.get("exit_phrase", "thanks radio"))
        tk.Entry(phrase_frame, textvariable=exit_var, bg=UI["card"], fg=UI["text"],
                 insertbackground=UI["text"], font=FONT_BODY, width=30).pack(anchor="w", pady=(2, 4))

        # ── STT Engine Preference ──
        stt_frame = tk.LabelFrame(wrap, text="🗣  Speech-to-Text Engine", fg=UI["text"],
                                   bg=UI["panel"], font=FONT_BODY, padx=12, pady=8)
        stt_frame.pack(fill="x", pady=8)

        tk.Label(stt_frame,
                 text="Preferred STT backend (whisper.cpp is used when binary & model paths\n"
                      "are set in Environment tab; otherwise Google Speech Recognition).",
                 fg=UI["muted"], bg=UI["panel"], font=FONT_SMALL, justify="left").pack(anchor="w", pady=(0, 6))

        stt_var = tk.StringVar(value=acli_cfg.get("stt_engine", "auto"))

        tk.Radiobutton(
            stt_frame, text="Auto  — whisper.cpp if available, otherwise Google SR",
            variable=stt_var, value="auto",
            bg=UI["panel"], fg=UI["text"], selectcolor=UI["bg"],
            font=FONT_BODY, anchor="w"
        ).pack(anchor="w", pady=2)

        tk.Radiobutton(
            stt_frame, text="whisper.cpp only",
            variable=stt_var, value="whisper",
            bg=UI["panel"], fg=UI["text"], selectcolor=UI["bg"],
            font=FONT_BODY, anchor="w"
        ).pack(anchor="w", pady=2)

        tk.Radiobutton(
            stt_frame, text="Google Speech Recognition only",
            variable=stt_var, value="google",
            bg=UI["panel"], fg=UI["text"], selectcolor=UI["bg"],
            font=FONT_BODY, anchor="w"
        ).pack(anchor="w", pady=2)

        # ── LLM Provider for Audio CLI ──
        llm_frame = tk.LabelFrame(wrap, text="🤖 Command Parser LLM", fg=UI["text"],
                                   bg=UI["panel"], font=FONT_BODY, padx=12, pady=8)
        llm_frame.pack(fill="x", pady=8)

        acli_llm = acli_cfg.get("llm", {})
        global_models = cfg.get("default_models", {})

        # Resolve what's currently active for the status display
        active_provider = (acli_llm.get("provider") or "").strip().lower()
        if not active_provider or active_provider == "default":
            active_provider_display = global_models.get("provider", "ollama")
            active_model_display = (global_models.get("model") or global_models.get("host_model")
                                    or global_models.get("producer_model") or "llama3.1:8b")
            source_label = "inherited from Models tab"
        else:
            active_provider_display = active_provider
            active_model_display = acli_llm.get("model", "") or "(using global model)"
            source_label = "Audio CLI override"

        # Current status display
        status_text = f"Currently using:  {active_provider_display} / {active_model_display}  ({source_label})"
        tk.Label(llm_frame, text=status_text,
                 fg=UI["good"], bg=UI["panel"], font=FONT_BODY).pack(anchor="w", pady=(0, 8))

        tk.Label(llm_frame,
                 text="Choose which LLM processes voice commands.\n"
                      "Set to 'default' to use the global provider from the Models tab,\n"
                      "or pick a specific provider and model for Audio CLI only.",
                 fg=UI["muted"], bg=UI["panel"], font=FONT_SMALL, justify="left").pack(anchor="w", pady=(0, 6))

        # Provider dropdown
        tk.Label(llm_frame, text="Provider:", fg=UI["text"],
                 bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")
        acli_provider_var = tk.StringVar(value=acli_llm.get("provider", "default"))
        acli_provider_options = ["default", "ollama", "anthropic", "openai", "google"]
        acli_provider_combo = ttk.Combobox(llm_frame, textvariable=acli_provider_var,
                                           values=acli_provider_options, state="readonly", width=30)
        acli_provider_combo.pack(anchor="w", pady=(2, 8))

        # Model name
        tk.Label(llm_frame, text="Model Name (leave empty to use global):", fg=UI["text"],
                 bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")
        acli_model_var = tk.StringVar(value=acli_llm.get("model", ""))
        tk.Entry(llm_frame, textvariable=acli_model_var, bg=UI["card"], fg=UI["text"],
                 insertbackground=UI["text"], font=FONT_BODY, width=40).pack(anchor="w", pady=(2, 4))
        tk.Label(llm_frame,
                 text="Examples: llama3.1:8b, gpt-4o-mini, claude-3-haiku-20240307, gemini-1.5-flash",
                 fg=UI["muted"], bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")

        # Endpoint override (for ollama)
        tk.Label(llm_frame, text="Endpoint (ollama only, leave empty for global):", fg=UI["text"],
                 bg=UI["panel"], font=FONT_SMALL).pack(anchor="w", pady=(8, 0))
        acli_endpoint_var = tk.StringVar(value=acli_llm.get("endpoint", ""))
        tk.Entry(llm_frame, textvariable=acli_endpoint_var, bg=UI["card"], fg=UI["text"],
                 insertbackground=UI["text"], font=FONT_BODY, width=50).pack(anchor="w", pady=(2, 4))
        tk.Label(llm_frame,
                 text="e.g. http://127.0.0.1:11434/api/generate — only needed if different from Models tab",
                 fg=UI["muted"], bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")

        # ── Save / Reset ──
        def save_audio_cli_settings():
            cfg = get_global_config()
            acli_settings = {
                "default_mode": mode_var.get(),
                "audio_output_mode": audio_mode_var.get(),
                "web_url": url_var.get().strip() or "http://127.0.0.1:7800",
                "wake_phrase": wake_var.get().strip() or "hey radio",
                "exit_phrase": exit_var.get().strip() or "thanks radio",
                "stt_engine": stt_var.get(),
            }
            # LLM override — only save if not "default" or if model/endpoint specified
            llm_override = {}
            prov = acli_provider_var.get().strip().lower()
            mdl = acli_model_var.get().strip()
            ep = acli_endpoint_var.get().strip()
            if prov and prov != "default":
                llm_override["provider"] = prov
            if mdl:
                llm_override["model"] = mdl
            if ep:
                llm_override["endpoint"] = ep
            if llm_override:
                acli_settings["llm"] = llm_override

            cfg["audio_cli"] = acli_settings
            save_global_config(cfg)
            messagebox.showinfo("Success",
                "Audio CLI settings saved!\n\n"
                "Changes take effect the next time Audio CLI is started.")

        def reset_audio_cli_settings():
            if messagebox.askyesno("Reset Audio CLI Settings",
                                   "This will reset all Audio CLI settings to defaults.\n\nAre you sure?"):
                cfg = get_global_config()
                cfg.pop("audio_cli", None)
                save_global_config(cfg)
                # Reset UI to defaults
                mode_var.set("tkinter")
                audio_mode_var.set("speaker")
                url_var.set("http://127.0.0.1:7800")
                wake_var.set("hey radio")
                exit_var.set("thanks radio")
                stt_var.set("auto")
                acli_provider_var.set("default")
                acli_model_var.set("")
                acli_endpoint_var.set("")
                messagebox.showinfo("Reset Complete", "Audio CLI settings have been reset to defaults.")

        button_frame = tk.Frame(wrap, bg=UI["bg"])
        button_frame.pack(fill="x", pady=16)

        tk.Button(button_frame, text="Save Audio CLI Settings", font=FONT_BODY, bg=UI["accent"],
                 fg="#000", relief="flat", command=save_audio_cli_settings).pack(side="left", padx=(0, 8))

        tk.Button(button_frame, text="Reset All", font=FONT_BODY, bg=UI["card"],
                 fg=UI["text"], relief="flat", command=reset_audio_cli_settings).pack(side="left")

    def _build_environment_settings(self, parent: tk.Frame) -> None:
        """Build the Environment Variables settings panel."""
        
        # Make scrollable
        scrollbar = tk.Scrollbar(parent, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        
        canvas = tk.Canvas(parent, bg=UI["bg"], highlightthickness=0, yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        
        scrollbar.configure(command=canvas.yview)
        
        scroll_frame = tk.Frame(canvas, bg=UI["bg"])
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
        
        tk.Label(scroll_frame, text="Environment Variables", font=FONT_H2, fg=UI["text"], bg=UI["bg"]).pack(
            anchor="w", padx=14, pady=(14, 4)
        )
        tk.Label(scroll_frame, text="Configure global environment variables used by Radio OS stations", 
                font=FONT_SMALL, fg=UI["muted"], bg=UI["bg"]).pack(anchor="w", padx=14, pady=(0, 8))
        
        wrap = tk.Frame(scroll_frame, bg=UI["bg"])
        wrap.pack(fill="both", expand=True, padx=14, pady=8)
        
        cfg = get_global_config()
        env_vars = cfg.get("environment", {})
        
        # Dictionary to store StringVar objects
        env_var_widgets = {}
        
        # Define environment variables with descriptions
        env_config = [
            {
                "var": "RADIO_OS_ROOT",
                "label": "Radio OS Root Directory",
                "description": "Base directory for Radio OS installation",
                "placeholder": "Auto-detected (current project root)",
                "current": os.path.abspath(os.path.dirname(__file__)),
            },
            {
                "var": "RADIO_OS_PLUGINS",
                "label": "Global Plugins Directory", 
                "description": "Directory containing global Radio OS plugins",
                "placeholder": "Default: {RADIO_OS_ROOT}/plugins",
                "current": env_vars.get("RADIO_OS_PLUGINS", ""),
            },
            {
                "var": "RADIO_OS_VOICES",
                "label": "Global Voices Directory",
                "description": "Directory containing TTS voice models",
                "placeholder": "Default: {RADIO_OS_ROOT}/voices",
                "current": env_vars.get("RADIO_OS_VOICES", ""),
            },
            {
                "var": "CONTEXT_MODEL", 
                "label": "Default Context Model",
                "description": "Default LLM model for station producers",
                "placeholder": "e.g. qwen3:8b, llama3.1:8b",
                "current": env_vars.get("CONTEXT_MODEL", ""),
            },
            {
                "var": "HOST_MODEL",
                "label": "Default Host Model", 
                "description": "Default LLM model for station hosts",
                "placeholder": "e.g. qwen3:8b, llama3.1:8b",
                "current": env_vars.get("HOST_MODEL", ""),
            },
            {
                "var": "OLLAMA_ENDPOINT",
                "label": "Ollama Endpoint",
                "description": "URL for Ollama API server",
                "placeholder": "Default: http://localhost:11434",
                "current": env_vars.get("OLLAMA_ENDPOINT", ""),
            },
            {
                "var": "PIPER_BIN",
                "label": "Piper TTS Binary Path",
                "description": "Path to Piper text-to-speech executable",
                "placeholder": "Auto-detected from voices/ directory",
                "current": env_vars.get("PIPER_BIN", ""),
            },
            {
                "var": "OPENAI_API_KEY",
                "label": "OpenAI API Key",
                "description": "API key for OpenAI services (GPT-4, DALL-E, etc.)",
                "placeholder": "sk-...",
                "current": env_vars.get("OPENAI_API_KEY", ""),
                "sensitive": True,
            },
            {
                "var": "ANTHROPIC_API_KEY", 
                "label": "Anthropic API Key",
                "description": "API key for Claude models",
                "placeholder": "sk-ant-...",
                "current": env_vars.get("ANTHROPIC_API_KEY", ""),
                "sensitive": True,
            },
            {
                "var": "GOOGLE_API_KEY",
                "label": "Google API Key",
                "description": "API key for Google Gemini models",
                "placeholder": "AIza...",
                "current": env_vars.get("GOOGLE_API_KEY", ""),
                "sensitive": True,
            }
        ]
        
        # Create UI for each environment variable
        for env_info in env_config:
            var_name = env_info["var"]
            
            # Container frame
            var_frame = tk.LabelFrame(wrap, text=env_info["label"], fg=UI["text"], 
                                     bg=UI["panel"], font=FONT_BODY, padx=12, pady=8)
            var_frame.pack(fill="x", pady=8)
            
            # Description
            tk.Label(var_frame, text=env_info["description"], fg=UI["muted"], 
                    bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")
            
            # Input frame
            input_frame = tk.Frame(var_frame, bg=UI["panel"])
            input_frame.pack(fill="x", pady=(4, 0))
            
            # Entry widget
            is_sensitive = env_info.get("sensitive", False)
            show_char = "*" if is_sensitive else None
            
            entry_var = tk.StringVar(value=env_info["current"])
            env_var_widgets[var_name] = entry_var
            
            entry = tk.Entry(input_frame, textvariable=entry_var, bg=UI["card"], fg=UI["text"], 
                           insertbackground=UI["text"], font=FONT_BODY, show=show_char)
            entry.pack(side="left", fill="x", expand=True, pady=(2, 0))
            
            # Browse button for path variables
            if "directory" in env_info["description"].lower() or "path" in env_info["description"].lower():
                def make_browse_cmd(var_name, entry_var):
                    def browse_path():
                        if "directory" in env_config[[i["var"] for i in env_config].index(var_name)]["description"].lower():
                            path = filedialog.askdirectory(title=f"Select {var_name}")
                        else:
                            path = filedialog.askopenfilename(title=f"Select {var_name}")
                        if path:
                            entry_var.set(path)
                    return browse_path
                
                tk.Button(input_frame, text="Browse", bg=UI["card"], fg=UI["text"], 
                         relief="flat", command=make_browse_cmd(var_name, entry_var), 
                         font=FONT_SMALL).pack(side="right", padx=(8, 0))
            
            # Show/hide toggle for sensitive fields
            if is_sensitive:
                def make_toggle_cmd(entry_widget):
                    def toggle_visibility():
                        current_show = entry_widget.cget("show")
                        entry_widget.config(show="" if current_show else "*")
                    return toggle_visibility
                
                tk.Button(input_frame, text="👁", bg=UI["card"], fg=UI["text"], 
                         relief="flat", command=make_toggle_cmd(entry), 
                         font=FONT_SMALL, width=3).pack(side="right", padx=(4, 0))
            
            # Placeholder/current value info
            placeholder_text = env_info["placeholder"]
            if env_info["current"] and not is_sensitive:
                placeholder_text += f" (Current: {env_info['current'][:50]}{'...' if len(env_info['current']) > 50 else ''})"
            
            tk.Label(var_frame, text=placeholder_text, fg=UI["muted"], 
                    bg=UI["panel"], font=("Arial", 9), wraplength=700).pack(anchor="w", pady=(2, 0))
        
        # Save function
        def save_environment():
            cfg = get_global_config()
            cfg["environment"] = {}
            
            for var_name, var_widget in env_var_widgets.items():
                value = var_widget.get().strip()
                if value:  # Only store non-empty values
                    cfg["environment"][var_name] = value
            
            save_global_config(cfg)
            messagebox.showinfo("Success", "Environment variables saved!\n\nNote: Changes will apply to newly launched stations.")
        
        # Reset function
        def reset_environment():
            if messagebox.askyesno("Reset Environment Variables", 
                                 "This will clear all custom environment variables.\n\nAre you sure?"):
                cfg = get_global_config()
                cfg["environment"] = {}
                save_global_config(cfg)
                
                # Clear all entry widgets
                for var_widget in env_var_widgets.values():
                    var_widget.set("")
                
                messagebox.showinfo("Reset Complete", "Environment variables have been reset.")
        
        # Button frame
        button_frame = tk.Frame(wrap, bg=UI["bg"])
        button_frame.pack(fill="x", pady=16)
        
        tk.Button(button_frame, text="Save Environment Variables", font=FONT_BODY, bg=UI["accent"], 
                 fg="#000", relief="flat", command=save_environment).pack(side="left", padx=(0, 8))
        
        tk.Button(button_frame, text="Reset All", font=FONT_BODY, bg=UI["card"], 
                 fg=UI["text"], relief="flat", command=reset_environment).pack(side="left")

    def _build_visual_models_panel(self, parent: tk.Frame) -> None:
        """Build the Visual Models settings panel."""
        # Title
        tk.Label(parent, text="Vision Model Configuration", font=FONT_H2, fg=UI["text"], bg=UI["bg"]).pack(
            anchor="w", padx=14, pady=(14, 8)
        )
        
        # Scrollable container
        scrollbar = ttk.Scrollbar(parent, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        
        canvas = tk.Canvas(parent, bg=UI["bg"], highlightthickness=0, yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, padx=14, pady=8)
        
        scrollbar.configure(command=canvas.yview)
        
        scroll_frame = tk.Frame(canvas, bg=UI["bg"])
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        
        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
        
        # Load current config
        cfg = get_global_config()
        visual_cfg = cfg.get("visual_models", {})
        
        # Model Type Selection (Local or API)
        model_type_var = tk.StringVar(value=visual_cfg.get("model_type", "local"))
        
        type_frame = tk.LabelFrame(scroll_frame, text="Model Type", fg=UI["text"], bg=UI["panel"], 
                                    font=FONT_BODY, padx=12, pady=8)
        type_frame.pack(fill="x", pady=8)
        
        tk.Radiobutton(type_frame, text="Local Model (e.g., Ollama/LLaVA)", variable=model_type_var, 
                       value="local", fg=UI["text"], bg=UI["panel"], selectcolor=UI["accent"]).pack(anchor="w")
        tk.Radiobutton(type_frame, text="API-based Model", variable=model_type_var, 
                       value="api", fg=UI["text"], bg=UI["panel"], selectcolor=UI["accent"]).pack(anchor="w")
        
        # Local Model Config
        local_frame = tk.LabelFrame(scroll_frame, text="Local Model Settings", fg=UI["text"], 
                                     bg=UI["panel"], font=FONT_BODY, padx=12, pady=8)
        local_frame.pack(fill="x", pady=8)
        
        tk.Label(local_frame, text="Model Name / Endpoint:", fg=UI["text"], bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")
        local_model_var = tk.StringVar(value=visual_cfg.get("local_model", ""))
        local_model_entry = tk.Entry(local_frame, textvariable=local_model_var, bg=UI["card"], fg=UI["text"], 
                                      insertbackground=UI["text"])
        local_model_entry.pack(fill="x", pady=(2, 8))
        tk.Label(local_frame, text="(e.g., llava:latest, or http://localhost:11434)", 
                 fg=UI["muted"], bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")
        
        # API Model Config
        api_frame = tk.LabelFrame(scroll_frame, text="API Model Settings", fg=UI["text"], 
                                   bg=UI["panel"], font=FONT_BODY, padx=12, pady=8)
        api_frame.pack(fill="x", pady=8)
        
        tk.Label(api_frame, text="API Provider:", fg=UI["text"], bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")
        api_provider_var = tk.StringVar(value=visual_cfg.get("api_provider", "openai"))
        provider_options = ["openai", "anthropic", "google", "custom"]
        provider_menu = ttk.Combobox(api_frame, textvariable=api_provider_var, values=provider_options, 
                                     state="readonly", width=30)
        provider_menu.pack(fill="x", pady=(2, 8))
        
        tk.Label(api_frame, text="Model Name:", fg=UI["text"], bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")
        api_model_var = tk.StringVar(value=visual_cfg.get("api_model", "gpt-4-vision"))
        api_model_entry = tk.Entry(api_frame, textvariable=api_model_var, bg=UI["card"], fg=UI["text"], 
                                    insertbackground=UI["text"])
        api_model_entry.pack(fill="x", pady=(2, 8))
        
        tk.Label(api_frame, text="API Key:", fg=UI["text"], bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")
        api_key_var = tk.StringVar(value=visual_cfg.get("api_key", ""))
        api_key_entry = tk.Entry(api_frame, textvariable=api_key_var, bg=UI["card"], fg=UI["text"], 
                                  insertbackground=UI["text"], show="•")
        api_key_entry.pack(fill="x", pady=(2, 8))
        
        tk.Label(api_frame, text="API Endpoint (optional):", fg=UI["text"], bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")
        api_endpoint_var = tk.StringVar(value=visual_cfg.get("api_endpoint", ""))
        api_endpoint_entry = tk.Entry(api_frame, textvariable=api_endpoint_var, bg=UI["card"], fg=UI["text"], 
                                       insertbackground=UI["text"])
        api_endpoint_entry.pack(fill="x", pady=(2, 8))
        
        # Vision-specific options
        opts_frame = tk.LabelFrame(scroll_frame, text="Vision Processing Options", fg=UI["text"], 
                                    bg=UI["panel"], font=FONT_BODY, padx=12, pady=8)
        opts_frame.pack(fill="x", pady=8)
        
        tk.Label(opts_frame, text="Max Image Size (width):", fg=UI["text"], bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")
        max_size_var = tk.StringVar(value=visual_cfg.get("max_image_size", "1024"))
        max_size_entry = tk.Entry(opts_frame, textvariable=max_size_var, bg=UI["card"], fg=UI["text"], 
                                   insertbackground=UI["text"], width=10)
        max_size_entry.pack(anchor="w", pady=(2, 8))
        
        tk.Label(opts_frame, text="Image Quality (1-100):", fg=UI["text"], bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")
        quality_var = tk.StringVar(value=visual_cfg.get("image_quality", "85"))
        quality_entry = tk.Entry(opts_frame, textvariable=quality_var, bg=UI["card"], fg=UI["text"], 
                                  insertbackground=UI["text"], width=10)
        quality_entry.pack(anchor="w", pady=(2, 8))
        
        # Save button
        def save_visual_config():
            cfg = get_global_config()
            cfg["visual_models"] = {
                "model_type": model_type_var.get(),
                "local_model": local_model_var.get(),
                "api_provider": api_provider_var.get(),
                "api_model": api_model_var.get(),
                "api_key": api_key_var.get(),
                "api_endpoint": api_endpoint_var.get(),
                "max_image_size": max_size_var.get(),
                "image_quality": quality_var.get(),
            }
            save_global_config(cfg)
            messagebox.showinfo("Success", "Visual model settings saved!")

        quick_frame = tk.Frame(scroll_frame, bg=UI["bg"])
        quick_frame.pack(fill="x", pady=(0, 8), before=type_frame)
        tk.Button(
            quick_frame,
            text="Save Settings",
            font=FONT_BODY,
            bg=UI["accent"],
            fg="#000",
            relief="flat",
            command=save_visual_config,
        ).pack(side="right")
        
        btn_frame = tk.Frame(scroll_frame, bg=UI["bg"])
        btn_frame.pack(fill="x", pady=(16, 0))
        
        tk.Button(btn_frame, text="Save Settings", font=FONT_BODY, bg=UI["accent"], 
                  fg="#000", relief="flat", command=save_visual_config).pack(side="left", padx=4)

    # -----------------------------
    # Builder / Club entry points
    # -----------------------------
    def open_bookmark_builder(self):
        """Open Bookmark — the reskinned .oradio authoring surface (oracle-radio) — with no
        oradio loaded. Bookmark is no longer a runtime; it's how .oradios are authored now."""
        self._note_shell_activity()
        bookmark = ORADIO_BOOKMARK
        if not os.path.exists(bookmark):
            messagebox.showinfo("Bookmark", f"Bookmark not found at:\n{bookmark}")
            return
        try:
            # cwd MUST be the oracle-radio dir so Bookmark's `bookmark/` brick package imports.
            subprocess.Popen([sys.executable, bookmark], cwd=ORADIO_BOOKMARK_DIR)
        except Exception as e:
            messagebox.showerror("Bookmark", f"Could not open Bookmark:\n{e}")

    def open_loom(self):
        """Open Loom — the .loom universe surface (loom/app2.py). Authors/loads the relationship
        lens (universe title + nodes + soulmate bonds) over already-minted .oradios."""
        self._note_shell_activity()
        try:
            # run as a module so `loom`/`oradio_engine` packages resolve; cwd = oracle-radio.
            subprocess.Popen([sys.executable, "-m", "loom.app2"], cwd=ORADIO_BOOKMARK_DIR)
        except Exception as e:
            messagebox.showerror("Loom", f"Could not open Loom:\n{e}")

    def open_club(self):
        """The Club. For now its first job is PROVENANCE: raise the one-time author questionnaire
        on a first oradio, then show the identity card + let you stamp existing oradios."""
        self._note_shell_activity()
        try:
            from bookmark import identity
        except Exception as e:
            messagebox.showerror("Club", f"identity module unavailable:\n{e}")
            return
        ident = identity.load_identity(CLUB_DIR)
        if ident is None:
            self._club_questionnaire()
        else:
            self._club_identity_card(ident)

    def _unstamped_oradios(self):
        """Minted .oradio bundles on disk that carry no author provenance yet."""
        from bookmark import identity
        out = []
        for p in _discover_oradio_candidates():
            try:
                if zipfile.is_zipfile(str(p)) and identity.read_author(str(p)) is None:
                    out.append(str(p))
            except Exception:
                pass
        return out

    def _club_questionnaire(self):
        """One-time, 3-question provenance seed. Saves locally; only name + derived seed ever get
        stamped into an oradio. See bookmark/identity.py."""
        from bookmark import identity
        win = tk.Toplevel(self.root)
        win.title("Club — who are you? (one-time)")
        win.configure(bg=UI["bg"])
        win.geometry("580x460")
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text="✶ Provenance", bg=UI["bg"], fg=UI["accent"],
                 font=FONT_H1).pack(anchor="w", padx=18, pady=(16, 2))
        tk.Label(win, text="Asked once. Your answers never leave this machine — only a derived seed\n"
                           "and your name are stamped into what you author, so your lineage stays\n"
                           "traceable and two people with the same name still differ.",
                 bg=UI["bg"], fg=UI["muted"], font=FONT_SMALL, justify="left").pack(
            anchor="w", padx=18, pady=(0, 8))

        qs = [("What's your name — how do you identify yourself?", "e.g. evengineer1ng"),
              ("Who are you?", "a declaration — we infer nothing (write anything)"),
              ("What thread are you trying to pull?", "what are you here to do?")]
        entries = []
        for q, hint in qs:
            tk.Label(win, text=q, bg=UI["bg"], fg=UI["text"], font=FONT_BODY).pack(
                anchor="w", padx=18, pady=(8, 0))
            e = tk.Entry(win, bg=UI["card"], fg=UI["text"], insertbackground=UI["text"], relief="flat")
            e.pack(fill="x", padx=18)
            tk.Label(win, text=hint, bg=UI["bg"], fg=UI["muted"], font=FONT_SMALL).pack(
                anchor="w", padx=18)
            entries.append(e)
        entries[0].focus_set()

        seed_lbl = tk.Label(win, text="seed: —", bg=UI["bg"], fg="#6f8cff", font=("Consolas", 9))
        seed_lbl.pack(anchor="w", padx=18, pady=(10, 0))

        def _preview(*_):
            seed_lbl.config(text="seed: " + identity.derive_seed(
                entries[0].get(), entries[1].get(), entries[2].get()), fg="#6f8cff")
        for e in entries:
            e.bind("<KeyRelease>", _preview)

        def _save():
            name = entries[0].get().strip()
            if not name:
                seed_lbl.config(text="a name is required", fg="#b85c5c")
                return
            ident = identity.set_identity(CLUB_DIR, name, entries[1].get(), entries[2].get())
            win.destroy()
            self._club_identity_card(ident)   # straight to the card (offers stamping)

        row = tk.Frame(win, bg=UI["bg"]); row.pack(fill="x", padx=18, pady=14, side="bottom")
        tk.Button(row, text="Seal identity", command=_save, bg="#3a6b4a", fg="#ffffff",
                  relief="flat", bd=0, padx=14, pady=6, font=FONT_BODY, cursor="hand2").pack(side="right")
        tk.Button(row, text="Cancel", command=win.destroy, bg=UI["card"], fg=UI["text"],
                  relief="flat", bd=0, padx=12, pady=6, cursor="hand2").pack(side="right", padx=(0, 8))

    def _club_identity_card(self, ident):
        """Show the sealed identity + offer to retro-stamp any unstamped oradios (cheap provenance
        before the lineage grows)."""
        from bookmark import identity
        win = tk.Toplevel(self.root)
        win.title("Club — your provenance")
        win.configure(bg=UI["bg"])
        win.geometry("560x320")
        win.transient(self.root)

        tk.Label(win, text=f"✶ {ident.name}", bg=UI["bg"], fg=UI["accent"],
                 font=FONT_H1).pack(anchor="w", padx=18, pady=(16, 2))
        tk.Label(win, text="seed", bg=UI["bg"], fg=UI["muted"], font=FONT_SMALL).pack(
            anchor="w", padx=18, pady=(8, 0))
        tk.Label(win, text=ident.seed, bg=UI["bg"], fg="#6f8cff", font=("Consolas", 11)).pack(
            anchor="w", padx=18)
        if ident.who:
            tk.Label(win, text=f"“{ident.who}”", bg=UI["bg"], fg=UI["text"],
                     font=FONT_BODY, wraplength=500, justify="left").pack(anchor="w", padx=18, pady=(10, 0))
        if ident.thread:
            tk.Label(win, text=f"thread: {ident.thread}", bg=UI["bg"], fg=UI["muted"],
                     font=FONT_SMALL, wraplength=500, justify="left").pack(anchor="w", padx=18)

        unstamped = self._unstamped_oradios()
        msg = tk.Label(win, text="", bg=UI["bg"], fg=UI["muted"], font=FONT_SMALL,
                       wraplength=500, justify="left")
        msg.pack(anchor="w", padx=18, pady=(14, 0))

        def _stamp():
            res = identity.stamp_many(unstamped, ident.stamp())
            msg.config(text=f"Stamped {res['stamped']} oradio(s) with your provenance "
                            f"({res['skipped']} skipped).", fg=UI["accent"])
            # refresh the on-disk descriptors so the carousel/galaxy see the new author
            self.stations = load_stations()

        row = tk.Frame(win, bg=UI["bg"]); row.pack(fill="x", padx=18, pady=16, side="bottom")
        if unstamped:
            msg.config(text=f"{len(unstamped)} existing oradio(s) carry no author yet "
                            "(e.g. your genesis kernel, minted before this).")
            tk.Button(row, text=f"Stamp my {len(unstamped)} existing oradio(s)", command=_stamp,
                      bg="#3a6b4a", fg="#ffffff", relief="flat", bd=0, padx=14, pady=6,
                      font=FONT_BODY, cursor="hand2").pack(side="right")
        else:
            msg.config(text="Every oradio on disk already carries its author. ✓")
        tk.Button(row, text="Close", command=win.destroy, bg=UI["card"], fg=UI["text"],
                  relief="flat", bd=0, padx=12, pady=6, cursor="hand2").pack(side="left")

    # -----------------------------
    # Station editor / builder (legacy wizard — retired from the UI, kept for now)
    # -----------------------------
    def create_station_wizard(self):
        wiz = StationWizard(self)
        result = wiz.run_and_get_result()
        if not result:
            return

        manifest = result.get("manifest")
        if not manifest:
            return

        # Derive station_id from manifest
        station_block = manifest.get("station", {})
        station_id = station_block.get("id")

        if not station_id:
            name = station_block.get("name", "")
            station_id = name.lower().replace(" ", "_")

        if not station_id:
            messagebox.showerror("Error", "Station has no id or name.")
            return

        self.refresh_stations(select_id=station_id)
        self.edit_station(self._find_station(station_id))

    def edit_station(self, station: Optional[StationInfo]):
        if not station:
            return
        
        # Use the wizard but pre-populate with existing station data
        wiz = StationWizard(self, edit_mode=True, station=station)
        result = wiz.run_and_get_result()
        
        if result:
            # Manifest already saved by wizard, just refresh
            self.refresh_stations(select_id=station.station_id)

    def _find_station(self, station_id: str) -> Optional[StationInfo]:
        for s in self.stations:
            if s.station_id == station_id:
                return s
        return None

    def refresh_stations(self, select_id: Optional[str] = None):
        current_id = select_id
        if not current_id:
            focused = self._focused_station() if hasattr(self, "_focused_station") else None
            current_id = getattr(focused, "station_id", None) or getattr(self, "_current_oradio_id", None)
        loom_path = getattr(self, "_active_loom_path", None)
        if loom_path is not None:
            self.stations = load_oradio_shell_items_for(loom_path) or []
        else:
            self.stations = load_stations()
        self._render_cards()
        if getattr(self, "_nav_mode", "") == "galaxy":
            try:
                self.galaxy.set_nodes(self.stations)
                self._attach_galaxy_thumbs()
            except Exception:
                pass
        # selected_idx indexes the TILES now, so resolve select_id against home_tiles.
        if current_id:
            for i, t in enumerate(self.home_tiles):
                st = t.get("station")
                if st is not None and st.station_id == current_id:
                    self.selected_idx = i
                    self._highlight_selected()
                    self._focus_station_ribbon(self._focused_station())
                    break
        self.root.after(60, lambda: self._relayout(self.selected_idx, animate=False))

    def _prompt_text(self, title: str, prompt: str) -> Optional[str]:
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry(scaled_geometry(520, 200))
        win.configure(bg=UI["bg"])

        tk.Label(win, text=prompt, font=FONT_BODY, fg=UI["text"], bg=UI["bg"], wraplength=480, justify="left").pack(
            padx=16, pady=(16, 8), anchor="w"
        )
        entry = tk.Entry(win, font=FONT_BODY, bg=UI["panel"], fg=UI["text"], insertbackground=UI["text"])
        entry.pack(fill="x", padx=16, pady=(0, 12))
        entry.focus_set()

        out = {"val": None}

        def ok():
            out["val"] = entry.get()
            win.destroy()

        def cancel():
            win.destroy()

        btns = tk.Frame(win, bg=UI["bg"])
        btns.pack(fill="x", padx=16, pady=10)
        tk.Button(btns, text="Cancel", font=FONT_BODY, bg=UI["panel"], fg=UI["text"], relief="flat", command=cancel).pack(
            side="right", padx=6
        )
        tk.Button(btns, text="OK", font=FONT_BODY, bg=UI["accent"], fg="#000", relief="flat", command=ok).pack(
            side="right", padx=6
        )

        win.bind("<Return>", lambda e: ok())
        win.bind("<Escape>", lambda e: cancel())

        self.root.wait_window(win)
        return out["val"]

    # -----------------------------
    # Live runtime status polling
    # -----------------------------
    def _tick(self):
        self.ribbon_state.tick()
        self.clock_var.set(time.strftime("%I:%M %p"))
        self._apply_ribbon_shell_state()
        self._poll_switch_request()      # adopt a loom the Loom app asked us to load (no station needed)
        self._check_station_switch()
        self._update_loom_label()        # keep the top-bar "◈ loom: …" current
        self._update_status_panel()
        self.root.after(self._status_poll_ms, self._tick)

    def _apply_ribbon_shell_state(self, force: bool = False):
        alpha = round(self.ribbon_state.overlay_alpha_hint(), 3)
        if not force and alpha == self._last_overlay_alpha:
            return
        self._last_overlay_alpha = alpha

        # Ribbon overlay derives from the ACTIVE shell palette (UI) so theming stays coherent.
        # The standalone midnight/sunset RIBBON_SHELL_THEMES clashed with the carousel's UI theme
        # (that was the "why is it blue, not monokai green"). Follow the theme, don't fight it.
        palette = {"bg": UI["bg"], "overlay": UI["panel"], "accent": UI["accent"]}
        fade = max(0.0, min(1.0, 1.0 - alpha))

        stage_bg = blend_hex(UI["bg"], palette["bg"], 0.72)
        bar_bg = blend_hex(UI["bg"], palette["overlay"], 0.52)
        chip_bg = blend_hex(UI["panel"], palette["overlay"], 0.55)
        accent_bg = blend_hex(UI["accent"], palette["accent"], 0.65)
        card_bg = blend_hex(UI["card"], stage_bg, 0.72 * fade)
        selected_bg = blend_hex(UI["card_hover"], palette["overlay"], 0.25 + 0.45 * fade)
        text_fg = blend_hex(UI["text"], stage_bg, 0.72 * fade)
        muted_fg = blend_hex(UI["muted"], stage_bg, 0.78 * fade)
        surface_bg = blend_hex(UI["surface"], palette["bg"], 0.30)

        self.root.configure(bg=stage_bg)
        self.top_bar.configure(bg=bar_bg)
        self.top_right.configure(bg=bar_bg)
        self.title_lbl.configure(bg=bar_bg, fg=text_fg)
        self.mode_lbl.configure(bg=bar_bg, fg=muted_fg)
        self.top_clock_lbl.configure(bg=bar_bg, fg=muted_fg)

        for widget in (self.btn_new, self.btn_loom, self.btn_club, self.btn_map, self.btn_settings):
            widget.configure(bg=chip_bg, fg=text_fg)

        if self.btn_server:
            server_text = str(self.btn_server.cget("text")).upper()
            if "ON" in server_text:
                self.btn_server.configure(bg=blend_hex(UI["good"], palette["accent"], 0.25), fg="#000000")
            else:
                self.btn_server.configure(bg=chip_bg, fg=text_fg)

        if self.btn_mic:
            mic_text = str(self.btn_mic.cget("text")).upper()
            if "ACTIVE" in mic_text:
                self.btn_mic.configure(bg=blend_hex(UI["danger"], palette["overlay"], 0.15), fg=text_fg)
            elif "ON" in mic_text:
                self.btn_mic.configure(bg=blend_hex(UI["good"], palette["overlay"], 0.18), fg=text_fg)
            else:
                self.btn_mic.configure(bg=chip_bg, fg=text_fg)

        self.home.configure(bg=stage_bg)
        self.home_bg.configure(bg=stage_bg)
        self.home_hint.configure(bg=stage_bg, fg=muted_fg)

        # Tiles float on the live ribbon; their title/ring strips track the stage tone.
        for i, c in enumerate(self.cards):
            frame = c.get("frame")
            if frame is None:
                continue
            self._card_set_selected(frame, i == self.selected_idx, stage_bg)

        # Idle reveal: once booted into the home loop, 30s of inactivity (phase==DIM)
        # hides the tiles entirely so the bare ribbon plays full-screen; any activity
        # flips the state machine back to ACTIVE (via _note_shell_activity) and restores them.
        # (Galaxy mode keeps the tiles hidden regardless — the map is the nav surface.)
        if (getattr(self, "ribbon_media_started", False) and self._view == "home"
                and self._nav_mode == "carousel"):
            self._set_home_overlay(self.ribbon_state.phase != "DIM")

        self.runtime.configure(bg=stage_bg)
        self.runtime_title.configure(bg=surface_bg, fg=muted_fg)
        self.status_lines.configure(bg=surface_bg, fg=text_fg, insertbackground=text_fg)
        self.now_playing.configure(bg="#000000", fg=text_fg)
        self.now_sub.configure(bg="#000000", fg=muted_fg)

    def _style_card(self, card: tk.Frame, bg: str, panel_bg: str, accent_bg: str, text_fg: str, muted_fg: str):
        try:
            card.configure(bg=bg)
        except Exception:
            return
        for child in card.winfo_children():
            try:
                if isinstance(child, tk.Frame):
                    child.configure(bg=bg)
                    for grandchild in child.winfo_children():
                        if isinstance(grandchild, tk.Button):
                            label = str(grandchild.cget("text")).upper()
                            button_bg = accent_bg if "PLAY" in label else panel_bg
                            button_fg = "#000000" if "PLAY" in label else text_fg
                            grandchild.configure(bg=button_bg, fg=button_fg, activebackground=accent_bg)
                        else:
                            try:
                                grandchild.configure(bg=bg, fg=muted_fg)
                            except Exception:
                                pass
                elif isinstance(child, tk.Label):
                    text = str(child.cget("text"))
                    fg = muted_fg if "feeds active" in text.lower() or "voices" in text.lower() else text_fg
                    if text.isupper() and len(text) <= 24:
                        child.configure(bg=accent_bg, fg="#000000")
                    else:
                        child.configure(bg=bg, fg=fg)
            except Exception:
                pass

    def _active_loom_label(self) -> str:
        """A short, readable name for the active loom (its file stem, e.g. 'stonehenge')."""
        p = getattr(self, "_active_loom_path", None)
        if p:
            try:
                return Path(p).stem
            except Exception:
                pass
        return str(getattr(self, "_active_loom_id", "") or "—")

    def _update_loom_label(self):
        lbl = getattr(self, "loom_lbl", None)
        if lbl is None:
            return
        try:
            lbl.config(text=f"◈ loom: {self._active_loom_label()}")
        except Exception:
            pass

    def _poll_switch_request(self):
        """Honor a `.switch_request` written by the Loom app (action 'load_loom') or a shell reload
        ('refresh_shell') EVEN when no station process is running — that's the common case while
        authoring. A station-initiated 'station_id' switch is left untouched here so the code-20
        path in _check_station_switch still consumes it."""
        try:
            rq_path = os.path.join(BASE, ".switch_request")
            if not os.path.exists(rq_path):
                return
            with open(rq_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            action = data.get("action")
            if action not in ("load_loom", "refresh_shell"):
                return  # a station switch -> _check_station_switch handles it on exit code 20
            try:
                os.remove(rq_path)
            except OSError:
                pass
            if action == "load_loom":
                raw = data.get("loom_path")
                target = Path(raw) if raw else None
                if target and target.exists():
                    target_id = self._loom_id_for(target)
                    if target_id != self._active_loom_id:
                        self._switch_to_loom(target_id, target)
                        return
                    self._active_loom_path = target
                    self._active_loom_id = target_id
                    try:
                        write_active_loom_state(Path(BASE), target)
                    except Exception:
                        pass
                self.refresh_stations()
            else:
                self.refresh_stations()
            self._update_loom_label()
        except Exception as e:
            print(f"[Shell] switch-request poll failed: {e}")

    def _check_station_switch(self):
        # Check if process exited with magic code 20
        if not self.proc or not self.proc.proc:
            return

        ret = self.proc.proc.poll()
        if ret == 20: 
            # It's a switch request
            try:
                rq_path = os.path.join(BASE, ".switch_request")
                if os.path.exists(rq_path):
                    with open(rq_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    
                    # Consume file
                    try:
                        os.remove(rq_path)
                    except:
                        pass
                    action = data.get("action")
                    if action == "load_loom":
                        raw_path = data.get("loom_path")
                        target_path = Path(raw_path) if raw_path else None
                        if target_path and target_path.exists():
                            target_id = self._loom_id_for(target_path)
                            if target_id != self._active_loom_id:
                                self._switch_to_loom(target_id, target_path)
                            else:
                                self._active_loom_path = target_path
                                self._active_loom_id = target_id
                                try:
                                    write_active_loom_state(Path(BASE), target_path)
                                except Exception:
                                    pass
                                self.refresh_stations()
                        else:
                            self.refresh_stations()
                        return
                    if action == "refresh_shell":
                        self.refresh_stations()
                        return
                    target_id = data.get("station_id")
                    if target_id:
                        print(f"[Shell] Switching to station: {target_id}")
                        self.proc.stop() # Ensure closed
                        
                        # Find station info
                        st = self._find_station(target_id)
                        if st:
                            self.launch_station(st)
                        else:
                            print(f"[Shell] Station {target_id} not found.")
            except Exception as e:
                print(f"[Shell] Switch failed: {e}")

    def _update_status_panel(self):
        if self._view != "runtime":
            return

        st = self.proc.station
        alive = self.proc.is_alive()
        lines: List[str] = []

        if self.proc.proc is not None:
            try:
                lines.append(f"returncode: {self.proc.proc.poll()}")
            except Exception:
                pass

        if st:
            lp = os.path.join(st.path, "runtime.log")
            if os.path.exists(lp):
                try:
                    with open(lp, "r", encoding="utf-8", errors="ignore") as f:
                        tail = f.read()[-4000:]
                    if tail.strip():
                        lines.append("")
                        lines.append("---- runtime.log tail ----")
                        lines.extend(tail.strip().splitlines()[-25:])
                except Exception:
                    pass

        lines.append(f"proc_alive: {alive}")

        if not st:
            lines.append("station: (none)")
            self._set_status_text("\n".join(lines))
            return

        name = (st.manifest.get("station", {}) or {}).get("name", st.station_id)
        lines.append(f"station: {name} ({st.station_id})")

        sp = station_status_path(st.path)
        status = None
        if os.path.exists(sp):
            try:
                with open(sp, "r", encoding="utf-8") as f:
                    status = json.load(f)
            except Exception:
                status = None

        if status:
            hb = int(status.get("ts", 0) or 0)
            age = now_ts() - hb if hb else -1
            lines.append(f"heartbeat_age_sec: {age}")
            for k in ["db_queued", "db_claimed", "audio_q", "last_event", "last_title", "last_source"]:
                if k in status:
                    lines.append(f"{k}: {status.get(k)}")
        else:
            lines.append("status.json: (missing)")

        dbp = station_db_path(st.path)
        if os.path.exists(dbp):
            try:
                lines.append(f"db_size_mb: {os.path.getsize(dbp)/1024/1024:.2f}")
            except Exception:
                pass

        self._set_status_text("\n".join(lines))
        self.now_sub.config(text="Live" if alive else "Not running")

    def _set_status_text(self, text: str):
        self.status_lines.config(state="normal")
        self.status_lines.delete("1.0", "end")
        self.status_lines.insert("1.0", text)
        self.status_lines.config(state="disabled")

    def _on_close(self):
        _oled("shutdown")
        try:
            if self.ribbon_video:
                self.ribbon_video.stop()
        except Exception:
            pass
        try:
            self.proc.stop()
        except Exception:
            pass
        # Stop Audio CLI if running
        try:
            if self._audio_cli_session and self._audio_cli_session.is_running:
                self._audio_cli_session.stop_listener()
        except Exception:
            pass
        # Stop web server if running
        try:
            if self._web_server_stop:
                self._web_server_stop.set()
        except Exception:
            pass
        self.root.destroy()

    def run(self):
        self.root.mainloop()
CHARACTER_PRESETS = {

    "Universal FM": {
        "host": {
            "role": "moderator",
            "traits": ["calm", "smart"],
            "focus": ["flow", "continuity"]
        },
        "expert": {
            "role": "technical_voice",
            "traits": ["precise", "knowledgeable"],
            "focus": ["details", "accuracy"]
        },
        "skeptic": {
            "role": "critical_voice",
            "traits": ["cautious", "blunt"],
            "focus": ["risk", "downsides"]
        },
        "optimist": {
            "role": "positive_voice",
            "traits": ["energetic", "hopeful"],
            "focus": ["opportunity", "strengths"]
        },
        "storyteller": {
            "role": "narrative_voice",
            "traits": ["creative", "engaging"],
            "focus": ["examples", "analogies"]
        },
    },

    "Hockey FM": {
        "host": {
            "role": "play_by_play_host",
            "traits": ["smooth", "engaging"],
            "focus": ["flow", "pacing"]
        },
        "analyst": {
            "role": "tactical_breakdown",
            "traits": ["smart", "precise"],
            "focus": ["systems", "matchups"]
        },
        "stats_guru": {
            "role": "analytics_voice",
            "traits": ["data_driven", "calm"],
            "focus": ["metrics", "trends"]
        },
        "hype": {
            "role": "energy_driver",
            "traits": ["excited", "passionate"],
            "focus": ["big_plays", "emotion"]
        },
        "coach": {
            "role": "leadership_voice",
            "traits": ["motivational", "firm"],
            "focus": ["habits", "discipline"]
        }
    }
}
# ============================================================
# Onboarding Wizard (Gold Standard Manifest Generator)
# ============================================================

PRESET_ROLES = [
    "host", "engineer", "skeptic", "macro", "optimist", "coach",
    "analyst", "stats_guru", "hype", "moderator", "narrator",
    "risk_manager", "execution_specialist", "news_anchor"
]

PRESET_TRAITS = [
    "calm", "smart", "technical", "precise", "critical", "grounded",
    "contextual", "broad", "energetic", "constructive", "motivational",
    "long_term", "blunt", "curious", "skeptical", "disciplined",
    "measured", "creative", "engaging", "data_driven"
]

PRESET_FOCUS = [
    "flow", "continuity", "systems", "signals", "risk", "failure_modes",
    "regimes", "liquidity", "opportunity", "growth", "discipline", "milestones",
    "positioning", "execution", "orderflow", "volatility", "macro", "narrative",
    "pacing", "big_plays", "metrics", "trends", "strategy", "news"
]

# Known feed templates matching your gold manifest keys.
# If a plugin exists but isn't listed here, we still allow it (enabled + empty config),
# but these templates give a friendly default schema in the wizard.
FEED_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "reddit": {
        "enabled": True,
        "subreddits": [],
        "poll_sec": 30,
        "limit": 20,
        "priority": 60,
        "burst_delay": 0.2,
        "seen_ttl_sec": 3600,
    },
    "markets": {
        "enabled": True,
        "symbols": [],
        "poll_sec": 15,
        "breakout_pct": 0.2,
        "priority": 90,
    },
    "portfolio_event": {
        "enabled": True,
        "mode": "hyperliquid",
        "user_address": "",
        "poll_sec": 6,
        "min_emit_gap_sec": 20,
        "min_equity_delta_frac": 0.003,
        "big_equity_delta_frac": 0.015,
        "positions_change_priority": 95,
        "equity_change_priority": 93,
        "big_move_priority": 98,
        "base_url": "https://api.hyperliquid.xyz",
    },
    "rss": {
        "enabled": True,
        "urls": [],
        "poll_sec": 180,
        "priority": 72,
    },
    "bluesky": {
        "enabled": True,
        "hashtags": [],
        "poll_sec": 60,
        "limit": 20,
        "priority": 70,
    },
    "document": {
        "enabled": True,
        "files": [
            {
                "name": "strategy",
                "path": "./strategy_reference.txt",
                "max_chars": 5000,
                "announce": True,
                "announce_priority": 86,
                "candidate": False,
            },
            {
                "name": "playbook",
                "path": "./coach_playbook.txt",
                "max_chars": 7000,
                "announce": False,
                "candidate": True,
                "candidate_priority": 80,
            },
        ],
        "poll_sec": 2.5,
        "announce_cooldown_sec": 600,
    },
}

def _build_default_quotas() -> Dict[str, int]:
    # Baseline defaults
    base = {
        "reddit": 6,
        "markets": 4,
        "portfolio_event": 6,
        "bluesky": 2,
        "document": 4,
        "rss": 1,
    }
    # Dynamically correct based on installed plugins
    try:
        for name, info in discover_plugins().items():
            if info.get("is_feed", True):
                if name not in base:
                    base[name] = 3
    except Exception:
        pass
    return base

DEFAULT_SCHED_QUOTAS = _build_default_quotas()

def _build_default_weights() -> Dict[str, float]:
    # Baseline defaults
    base = {
        "reddit": 0.50,
        "bluesky": 0.25,
        "markets": 0.10,
        "portfolio_event": 0.10,
        "rss": 0.03,
        "document": 0.02,
    }
    # Dynamically correct based on installed plugins
    try:
        for name, info in discover_plugins().items():
            if info.get("is_feed", True):
                if name not in base:
                    base[name] = 0.05
    except Exception:
        pass
    return base

DEFAULT_MIX_WEIGHTS = _build_default_weights()

DEFAULT_CHARSET = {
    "host":   {"role": "host",   "traits": ["calm", "smart"],              "focus": ["flow", "continuity"]},
    "engineer": {"role": "engineer", "traits": ["technical", "precise"],     "focus": ["systems", "signals"]},
    "skeptic":  {"role": "skeptic",  "traits": ["critical", "grounded"],     "focus": ["risk", "failure_modes"]},
    "macro":    {"role": "macro",    "traits": ["contextual", "broad"],      "focus": ["regimes", "liquidity"]},
    "optimist": {"role": "optimist", "traits": ["energetic", "constructive"],"focus": ["opportunity", "growth"]},
    "coach":    {"role": "coach",    "traits": ["motivational", "long_term"],"focus": ["discipline", "milestones"]},
}


def _deepcopy_jsonable(x: Any) -> Any:
    return json.loads(json.dumps(x))

def _normalize_weights(weights: Dict[str, float]) -> Dict[str, float]:
    # Remove negatives, normalize to sum=1.0, keep stable keys.
    w2 = {k: max(0.0, float(v)) for k, v in (weights or {}).items()}
    s = sum(w2.values())
    if s <= 0:
        # fallback equal
        keys = list(w2.keys()) or []
        if not keys:
            return {}
        eq = 1.0 / len(keys)
        return {k: eq for k in keys}
    return {k: (v / s) for k, v in w2.items()}

def _pie_segments(weights: Dict[str, float]) -> List[tuple]:
    # Returns list of (key, start_angle, extent_angle)
    w = _normalize_weights(weights)
    out = []
    a = 0.0
    for k, frac in w.items():
        ext = 360.0 * frac
        out.append((k, a, ext))
        a += ext
    return out

def _try_play_wav(path: str) -> None:
    # Best-effort audio playback for voice sampling.
    try:
        if os.name == "nt":
            import winsound
            winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
            return
    except Exception:
        pass

    # Optional fallback if installed
    try:
        import soundfile as sf
        import sounddevice as sd
        data, sr = sf.read(path, dtype="float32")
        sd.play(data, sr)
        return
    except Exception:
        pass

    # Last resort: open file (user can play it)
    try:
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception:
        pass


class StationWizard:
    """
    Friendly wizard that produces the gold-standard manifest.yaml.
    Can create new stations or edit existing ones.
    """
    def __init__(self, shell: "RadioShell", edit_mode: bool = False, station: Optional["StationInfo"] = None):
        self.shell = shell
        self.root = shell.root
        self.edit_mode = edit_mode
        self.station = station

        self.plugins = discover_plugins()  # available plugin modules

        # Result payload
        self._result: Optional[Dict[str, Any]] = None

        # Load global config for defaults
        global_cfg = get_global_config()
        default_models = global_cfg.get("default_models", {})
        default_voices = global_cfg.get("default_voices", {})

        # State - defaults for new station (use global config or fallback)
        self.station_id = ""
        self.station_name = "My Radio Station"
        self.station_host = "Host"
        self.station_category = "Custom"
        self.station_logo = ""

        self.meta_plugin = "radio_station"  # default meta plugin
        
        self.llm_endpoint = default_models.get("llm_endpoint", "http://127.0.0.1:11434/api/generate")
        self.llm_provider = default_models.get("provider", "ollama")
        self.model_producer = default_models.get("producer_model", "gpt-4o")
        self.model_host = default_models.get("host_model", "gpt-4o")
        self.model_navigator = default_models.get("navigator_model", "")
        self.model_char_manager = default_models.get("character_manager_model", "")
        self.model_embedding = default_models.get("embedding_model", "")
        self.embedding_enabled = bool(default_models.get("embedding_enabled", False))

        self.piper_bin = default_voices.get("piper_bin", "")
        self.voices_provider = default_voices.get("provider", "kokoro")
        # voices assigned per character (dynamic) - use global defaults
        self.voices: Dict[str, str] = {
            "host": default_voices.get("voice_host", ""),
            "expert": default_voices.get("voice_expert", ""),
            "skeptic": default_voices.get("voice_skeptic", ""),
            "optimist": default_voices.get("voice_optimist", ""),
            "coach": default_voices.get("voice_coach", ""),
        }

        # Feeds chosen/configured
        self.feed_cfg: Dict[str, Dict[str, Any]] = {}
        # Characters chosen/configured (2-10, must include host)
        self.characters = {
            "host": {
                "role": "moderator",
                "traits": ["calm", "smart"],
                "focus": ["flow", "continuity"]
            }
        }

        # Mix weights (ready for runtime later)
        self.mix_weights: Dict[str, float] = _deepcopy_jsonable(DEFAULT_MIX_WEIGHTS)

        # Scheduler quotas
        self.scheduler_quotas: Dict[str, int] = _deepcopy_jsonable(DEFAULT_SCHED_QUOTAS)

        # Preserve original manifest to avoid data loss on save
        self.existing_manifest: Optional[Dict[str, Any]] = None

        # If editing, load existing station data
        if edit_mode and station:
            self._load_existing_station(station)

        # Wizard window
        self.win = tk.Toplevel(self.root)
        self.win.title("Edit Station" if edit_mode else "New Station Wizard")
        self.win.geometry(scaled_geometry(1100, 760))
        self.win.configure(bg=UI["bg"])
        self.win.grab_set()

        self._build()

    # -------------
    # Public API
    # -------------
    def run_and_get_result(self) -> Optional[Dict[str, Any]]:
        self.root.wait_window(self.win)
        return self._result
    
    def _load_existing_station(self, station: "StationInfo"):
        """Load existing station manifest data into wizard state."""
        manifest_path = station_manifest_path(station.path)
        cfg = safe_read_yaml(manifest_path)
        
        if not cfg:
            return

        # Keep a copy of the full manifest to preserve extra fields (pacing, riff, etc)
        self.existing_manifest = _deepcopy_jsonable(cfg)
        
        # Load station basics
        st_block = cfg.get("station", {})
        self.station_id = station.station_id
        self.station_name = st_block.get("name", station.station_id)
        self.station_host = st_block.get("host", "Kai")
        self.station_category = st_block.get("category", "Custom")
        self.station_logo = st_block.get("logo", "")
        
        # Load meta plugin
        self.meta_plugin = cfg.get("meta_plugin", "radio_station")
        
        # Load models
        llm_block = cfg.get("llm", {})
        self.llm_endpoint = llm_block.get("endpoint", "http://127.0.0.1:11434/api/generate")
        self.llm_provider = llm_block.get("provider", "ollama")
        
        models_block = cfg.get("models", {})
        self.model_producer = models_block.get("producer", "rnj-1:8b")
        self.model_host = models_block.get("host", "rnj-1:8b")
        self.model_navigator = models_block.get("navigator", "")
        self.model_char_manager = models_block.get("character_manager", "")
        self.model_embedding = models_block.get("embedding", "")
        self.embedding_enabled = bool(cfg.get("embedding", {}).get("enabled", False))
        
        # Load audio
        audio_block = cfg.get("audio", {})
        self.piper_bin = audio_block.get("piper_bin", "")
        self.voices_provider = audio_block.get("voices_provider", "kokoro")
        
        # Load voices
        voices_block = cfg.get("voices", {})
        if isinstance(voices_block, dict):
            self.voices = dict(voices_block)
        
        # Load feeds
        feeds_block = cfg.get("feeds", {})
        if isinstance(feeds_block, dict):
            self.feed_cfg = _deepcopy_jsonable(feeds_block)
        
        # Load characters
        chars_block = cfg.get("characters", {})
        if isinstance(chars_block, dict) and chars_block:
            self.characters = _deepcopy_jsonable(chars_block)
        
        # Load mix weights
        mix_block = cfg.get("mix", {})
        if isinstance(mix_block, dict):
            weights = mix_block.get("weights", {})
            if isinstance(weights, dict):
                self.mix_weights = dict(weights)
        
        # Load scheduler quotas
        sched_block = cfg.get("scheduler", {})
        if isinstance(sched_block, dict):
            quotas = sched_block.get("source_quotas", {})
            if isinstance(quotas, dict):
                self.scheduler_quotas = dict(quotas)
    
    def _refresh_voices_tab(self):
        # Capture any current UI edits before we destroy the widgets
        try:
            if hasattr(self, "var_piper_bin"):
                self.piper_bin = (self.var_piper_bin.get() or "").strip()

            if hasattr(self, "voice_vars") and isinstance(self.voice_vars, dict):
                for k, var in self.voice_vars.items():
                    try:
                        self.voices[k] = (var.get() or "").strip()
                    except Exception:
                        pass
        except Exception:
            pass

        for w in self.tab_voices.winfo_children():
            w.destroy()

        self._build_voices()
    def _discover_feed_names(self) -> List[str]:
        # Prefer live plugin discovery; fall back to FEED_TEMPLATES keys.
        names = sorted(k for k, meta in (self.plugins or {}).items() if meta.get("is_feed", True))
        if names:
            return names
        return sorted(FEED_TEMPLATES.keys())

    def _make_scrollable_frame(self, parent: tk.Widget, bg: str):
        """
        Returns: (outer_frame, inner_frame, canvas)
        - outer_frame contains canvas + scrollbar
        - inner_frame is where you pack your rows
        - mousewheel is bound only when cursor is over the canvas
        """
        outer = tk.Frame(parent, bg=bg)
        outer.pack(fill="both", expand=True)

        canvas = tk.Canvas(outer, bg=bg, highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        vsb = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        vsb.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=vsb.set)

        inner = tk.Frame(canvas, bg=bg)
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_configure(_e=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_canvas_configure(e):
            # keep inner width matched to visible canvas width
            canvas.itemconfigure(win_id, width=e.width)

        inner.bind("<Configure>", _on_configure)
        canvas.bind("<Configure>", _on_canvas_configure)

        # Wheel scrolling (Windows/macOS)
        def _wheel(e):
            # delta is platform dependent; normalize a bit
            delta = 0
            try:
                if sys.platform == "darwin":
                    # macOS: delta usually matches scroll units directly
                    delta = int(-1 * e.delta)
                else:
                    # Windows: 120 increments
                    delta = int(-1 * (e.delta / 120))
            except Exception:
                delta = 0
            if delta != 0:
                canvas.yview_scroll(delta, "units")

        # Linux wheel
        def _wheel_up(_e):
            canvas.yview_scroll(-1, "units")

        def _wheel_down(_e):
            canvas.yview_scroll(1, "units")

        def _bind_wheel(_e=None):
            canvas.bind_all("<MouseWheel>", _wheel)
            canvas.bind_all("<Button-4>", _wheel_up)
            canvas.bind_all("<Button-5>", _wheel_down)

        def _unbind_wheel(_e=None):
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")

        canvas.bind("<Enter>", _bind_wheel)
        canvas.bind("<Leave>", _unbind_wheel)

        return outer, inner, canvas
    def _render_mix_ui(self):

        # Clear old UI
        for w in self.mix_wrap.winfo_children():
            w.destroy()

        tk.Label(
            self.mix_wrap,
            text="Feed mix (future-ready)",
            font=FONT_H2,
            fg=UI["text"],
            bg=UI["bg"]
        ).pack(anchor="w")

        tk.Label(
            self.mix_wrap,
            text="Adjust how often each enabled feed appears.",
            font=FONT_BODY,
            fg=UI["muted"],
            bg=UI["bg"]
        ).pack(anchor="w", pady=(4, 10))

        body = tk.Frame(self.mix_wrap, bg=UI["bg"])
        body.pack(fill="both", expand=True)

        left = tk.Frame(body, bg=UI["panel"], width=int(360 * UI_SCALE))
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        right = tk.Frame(body, bg=UI["bg"])
        right.pack(side="left", fill="both", expand=True, padx=(12, 0))

        # 🔥 LIVE enabled feeds
        enabled = [
            k for k, v in self.feed_cfg.items()
            if isinstance(v, dict) and v.get("enabled", False)
        ]

        if not enabled:
            enabled = list(DEFAULT_MIX_WEIGHTS.keys())

        self.weight_sliders = {}

        tk.Label(
            left,
            text="Weights",
            font=("Segoe UI", 12, "bold"),
            fg=UI["text"],
            bg=UI["panel"]
        ).pack(anchor="w", padx=12, pady=(12, 8))

        for k in enabled:
            if k not in self.mix_weights:
                self.mix_weights[k] = 0.0

            row = tk.Frame(left, bg=UI["panel"])
            row.pack(fill="x", padx=12, pady=6)

            tk.Label(row, text=k, fg=UI["muted"], bg=UI["panel"], width=14, anchor="w").pack(side="left")

            v = tk.DoubleVar(value=float(self.mix_weights.get(k, 0.0)))
            self.weight_sliders[k] = v

            tk.Scale(
                row,
                from_=0.0, to=1.0, resolution=0.01,
                orient="horizontal",
                variable=v,
                length=200,
                bg=UI["panel"], fg=UI["text"],
                highlightthickness=0,
                command=lambda _=None: self._mix_redraw()
            ).pack(side="left", fill="x", expand=True)

        tk.Button(
            left,
            text="Normalize (sum=1)",
            bg=UI["panel"],
            fg=UI["accent"],
            relief="flat",
            command=self._mix_normalize_clicked
        ).pack(anchor="w", padx=12, pady=(8, 12))

        tk.Label(
            right,
            text="Preview pie",
            font=("Segoe UI", 12, "bold"),
            fg=UI["text"],
            bg=UI["bg"]
        ).pack(anchor="w")

        self.pie = tk.Canvas(
            right,
            bg=UI["surface"],
            highlightthickness=0,
            width=int(520 * UI_SCALE),
            height=int(520 * UI_SCALE)
        )
        self.pie.pack(pady=12)
        
        # Draw initial pie chart
        self._mix_redraw()

    # -------------
    # UI Build
    # -------------
    def _build(self):
        top = tk.Frame(self.win, bg=UI["bg"])
        top.pack(fill="x", padx=16, pady=(14, 8))

        tk.Label(top, text="Create a new station", font=FONT_H1, fg=UI["text"], bg=UI["bg"]).pack(anchor="w")
        tk.Label(
            top,
            text="Flow: station → feeds → characters → voices → mix → done.",
            font=FONT_BODY, fg=UI["muted"], bg=UI["bg"]
        ).pack(anchor="w", pady=(4, 0))

        self.nb = ttk.Notebook(self.win)
        self.nb.pack(fill="both", expand=True, padx=12, pady=12)

        self.tab_basics = tk.Frame(self.nb, bg=UI["bg"])
        self.tab_feeds = tk.Frame(self.nb, bg=UI["bg"])
        self.tab_chars = tk.Frame(self.nb, bg=UI["bg"])
        self.tab_voices = tk.Frame(self.nb, bg=UI["bg"])
        self.tab_visual = tk.Frame(self.nb, bg=UI["bg"])
        self.tab_mix = tk.Frame(self.nb, bg=UI["bg"])
        self.tab_review = tk.Frame(self.nb, bg=UI["bg"])

        self.nb.add(self.tab_basics, text="1) Station")
        self.nb.add(self.tab_feeds, text="2) Feeds")
        self.nb.add(self.tab_chars, text="3) Characters")
        self.nb.add(self.tab_voices, text="4) Voices")
        self.nb.add(self.tab_visual, text="5) Visual Models")
        self.nb.add(self.tab_mix, text="6) Mix")
        self.nb.add(self.tab_review, text="7) Review")

        self._build_basics()
        self._build_feeds()
        self._build_characters()
        self._build_voices()
        self._build_visual_models()
        self._build_mix()
        self._build_review()

        # Footer nav
        footer = tk.Frame(self.win, bg=UI["bg"])
        footer.pack(fill="x", padx=12, pady=(0, 12))

        self.btn_back = tk.Button(
            footer, text="← Back", font=FONT_BODY,
            bg=UI["panel"], fg=UI["text"], relief="flat",
            command=self._go_back
        )
        self.btn_back.pack(side="left")

        self.btn_next = tk.Button(
            footer, text="Next →", font=FONT_BODY,
            bg=UI["accent"], fg="#000", relief="flat",
            command=self._go_next
        )
        self.btn_next.pack(side="right")

        self.btn_cancel = tk.Button(
            footer, text="Cancel", font=FONT_BODY,
            bg=UI["panel"], fg=UI["muted"], relief="flat",
            command=self._cancel
        )
        self.btn_cancel.pack(side="right", padx=8)

        def on_tab_change(e):
            self._sync_nav_buttons()

            idx = self.nb.index("current")

            # Mix tab index = 4
            if idx == 4:
                self._render_mix_ui()

            # Voices tab refresh you already had
            if idx == 3:
                self._refresh_voices_tab()


        self.nb.bind("<<NotebookTabChanged>>", on_tab_change)

        self._sync_nav_buttons()
    def _build_voices(self):
        _outer, wrap, _canvas = self._make_scrollable_frame(self.tab_voices, UI["bg"])
        wrap.configure(padx=14, pady=14)

        tk.Label(
            wrap,
            text="Voices & TTS",
            font=FONT_H2,
            fg=UI["text"],
            bg=UI["bg"]
        ).grid(row=0, column=0, sticky="w", pady=(0, 12), columnspan=3)

        # Provider
        self.var_voices_provider = tk.StringVar(value=getattr(self, "voices_provider", "kokoro"))
        tk.Label(
            wrap, text="TTS Provider",
            font=FONT_BODY, fg=UI["muted"], bg=UI["bg"]
        ).grid(row=1, column=0, sticky="w", pady=6)

        ttk.Combobox(
            wrap,
            textvariable=self.var_voices_provider,
            values=["kokoro", "openai", "piper", "elevenlabs", "system"],
            state="readonly"
        ).grid(row=1, column=1, sticky="ew", pady=6)

        # Piper binary
        self.var_piper_bin = tk.StringVar(value=self.piper_bin)

        tk.Label(
            wrap, text="Piper Binary / Model Path",
            font=FONT_BODY, fg=UI["muted"], bg=UI["bg"]
        ).grid(row=2, column=0, sticky="w", pady=6)

        tk.Entry(
            wrap,
            textvariable=self.var_piper_bin,
            bg=UI["surface"],
            fg=UI["text"],
            insertbackground=UI["text"]
        ).grid(row=2, column=1, sticky="ew", pady=6)

        tk.Button(
            wrap, text="Browse",
            bg=UI["panel"], fg=UI["text"], relief="flat",
            command=lambda: self._browse_file_into(self.var_piper_bin)
        ).grid(row=2, column=2, padx=8)

        ttk.Separator(wrap, orient="horizontal").grid(
            row=3, column=0, columnspan=3, sticky="ew", pady=14
        )

        tk.Label(
            wrap,
            text="Assign voices to characters",
            font=("Segoe UI", 12, "bold"),
            fg=UI["text"],
            bg=UI["bg"]
        ).grid(row=4, column=0, sticky="w", columnspan=3)

        char_keys = sorted(self.characters.keys())

        self.voice_vars = {}

        r = 5
        for k in char_keys:
            self.voice_vars[k] = tk.StringVar(value=self.voices.get(k, ""))

            tk.Label(
                wrap,
                text=f"{k}",
                font=FONT_BODY,
                fg=UI["muted"],
                bg=UI["bg"]
            ).grid(row=r, column=0, sticky="w", pady=6)

            tk.Entry(
                wrap,
                textvariable=self.voice_vars[k],
                bg=UI["surface"],
                fg=UI["text"],
                insertbackground=UI["text"]
            ).grid(row=r, column=1, sticky="ew", pady=6)

            btnrow = tk.Frame(wrap, bg=UI["bg"])
            btnrow.grid(row=r, column=2, sticky="e")

            tk.Button(
                btnrow,
                text="Browse",
                bg=UI["panel"], fg=UI["text"], relief="flat",
                command=lambda vv=self.voice_vars[k]: self._browse_file_into(vv)
            ).pack(side="left", padx=4)

            tk.Button(
                btnrow,
                text="Sample",
                bg=UI["panel"], fg=UI["accent"], relief="flat",
                command=lambda key=k: self._sample_voice(key)
            ).pack(side="left", padx=4)

            r += 1

        wrap.grid_columnconfigure(1, weight=1)

        ttk.Separator(wrap, orient="horizontal").grid(
            row=r, column=0, columnspan=3, sticky="ew", pady=14
        )

        self.var_sample_text = tk.StringVar(
            value="Checking in—let’s talk markets, risk, and what matters next."
        )

        tk.Label(
            wrap, text="Sample text",
            font=FONT_BODY, fg=UI["muted"], bg=UI["bg"]
        ).grid(row=r+1, column=0, sticky="w")

        tk.Entry(
            wrap,
            textvariable=self.var_sample_text,
            bg=UI["surface"],
            fg=UI["text"],
            insertbackground=UI["text"]
        ).grid(row=r+1, column=1, columnspan=2, sticky="ew")

    def _build_visual_models(self):
        """Build visual models configuration tab (prefilled with global settings)."""
        wrap = tk.Frame(self.tab_visual, bg=UI["bg"])
        wrap.pack(fill="both", expand=True, padx=14, pady=14)

        # Title
        tk.Label(
            wrap,
            text="Vision Model (Optional)",
            font=FONT_H2,
            fg=UI["text"],
            bg=UI["bg"]
        ).pack(anchor="w", pady=(0, 12))

        # Scrollable container
        scrollbar = ttk.Scrollbar(wrap, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        canvas = tk.Canvas(wrap, bg=UI["bg"], highlightthickness=0, yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, pady=8)

        scrollbar.configure(command=canvas.yview)

        scroll_frame = tk.Frame(canvas, bg=UI["bg"])
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        # Model Type Selection
        type_frame = tk.LabelFrame(scroll_frame, text="Model Type", fg=UI["text"], bg=UI["panel"],
                                    font=FONT_BODY, padx=12, pady=8)
        type_frame.pack(fill="x", pady=8, padx=8)

        tk.Radiobutton(type_frame, text="Local Model (e.g., Ollama/LLaVA)", 
                       variable=self.var_visual_model_type, value="local",
                       fg=UI["text"], bg=UI["panel"], selectcolor=UI["accent"]).pack(anchor="w", pady=4)
        tk.Radiobutton(type_frame, text="API-based Model", 
                       variable=self.var_visual_model_type, value="api",
                       fg=UI["text"], bg=UI["panel"], selectcolor=UI["accent"]).pack(anchor="w", pady=4)

        # Local Model Config
        local_frame = tk.LabelFrame(scroll_frame, text="Local Model Settings", fg=UI["text"],
                                     bg=UI["panel"], font=FONT_BODY, padx=12, pady=8)
        local_frame.pack(fill="x", pady=8, padx=8)

        tk.Label(local_frame, text="Model Name / Endpoint:", fg=UI["text"], bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")
        tk.Entry(local_frame, textvariable=self.var_visual_model_local, bg=UI["card"], fg=UI["text"],
                insertbackground=UI["text"]).pack(fill="x", pady=(2, 8))
        tk.Label(local_frame, text="(e.g., llava:latest or http://localhost:11434)",
                 fg=UI["muted"], bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")

        # API Model Config
        api_frame = tk.LabelFrame(scroll_frame, text="API Model Settings", fg=UI["text"],
                                   bg=UI["panel"], font=FONT_BODY, padx=12, pady=8)
        api_frame.pack(fill="x", pady=8, padx=8)

        tk.Label(api_frame, text="API Provider:", fg=UI["text"], bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")
        provider_menu = ttk.Combobox(api_frame, textvariable=self.var_visual_model_api_provider,
                                     values=["openai", "anthropic", "google", "custom"],
                                     state="readonly", width=30)
        provider_menu.pack(fill="x", pady=(2, 8))

        tk.Label(api_frame, text="Model Name:", fg=UI["text"], bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")
        tk.Entry(api_frame, textvariable=self.var_visual_model_api_model, bg=UI["card"], fg=UI["text"],
                insertbackground=UI["text"]).pack(fill="x", pady=(2, 8))

        # Max image size
        opts_frame = tk.LabelFrame(scroll_frame, text="Processing Options", fg=UI["text"],
                                    bg=UI["panel"], font=FONT_BODY, padx=12, pady=8)
        opts_frame.pack(fill="x", pady=8, padx=8)

        tk.Label(opts_frame, text="Max Image Size (width):", fg=UI["text"], bg=UI["panel"], font=FONT_SMALL).pack(anchor="w")
        tk.Entry(opts_frame, textvariable=self.var_visual_model_max_size, bg=UI["card"], fg=UI["text"],
                insertbackground=UI["text"], width=10).pack(anchor="w", pady=(2, 8))

        btn_row = tk.Frame(scroll_frame, bg=UI["bg"])
        btn_row.pack(fill="x", pady=(12, 0), padx=8)
        tk.Button(
            btn_row,
            text="Save Visual Models",
            bg=UI["accent"],
            fg="#000",
            relief="flat",
            command=self._save_visual_models_tab,
            font=FONT_BODY,
        ).pack(side="right")

    def _save_visual_models_tab(self):
        """Save visual model settings from the wizard tab."""
        # Persist immediately for edit mode; otherwise just keep staged values.
        if self.edit_mode and self.station:
            manifest_path = station_manifest_path(self.station.path)
            cfg = safe_read_yaml(manifest_path)
            if not isinstance(cfg, dict):
                cfg = {}

            cfg.setdefault("visual_models", {})
            cfg["visual_models"]["model_type"] = self.var_visual_model_type.get().strip()
            cfg["visual_models"]["local_model"] = self.var_visual_model_local.get().strip()
            cfg["visual_models"]["api_provider"] = self.var_visual_model_api_provider.get().strip()
            cfg["visual_models"]["api_model"] = self.var_visual_model_api_model.get().strip()
            cfg["visual_models"]["api_key"] = self.var_visual_model_api_key.get().strip()
            cfg["visual_models"]["max_image_size"] = self.var_visual_model_max_size.get().strip()

            safe_write_yaml(manifest_path, cfg)
            messagebox.showinfo("Success", "Visual model settings saved!")
        else:
            # For new stations, values are staged in the wizard and will be written on Create.
            self._refresh_preview()
            messagebox.showinfo("Saved", "Visual model settings staged for this station.")

    # -------------
    # Step 1: basics
    # -------------
    def _build_basics(self):
        _outer, wrap, _canvas = self._make_scrollable_frame(self.tab_basics, UI["bg"])
        wrap.configure(padx=18, pady=18)

        tk.Label(wrap, text="Station settings", font=FONT_H2, fg=UI["text"], bg=UI["bg"]).grid(
            row=0, column=0, sticky="w", pady=(0, 12), columnspan=3
        )

        self.var_station_id = tk.StringVar(value=self.station_id if self.edit_mode else "")
        self.var_station_name = tk.StringVar(value=self.station_name)
        self.var_station_host = tk.StringVar(value=self.station_host)
        self.var_station_cat = tk.StringVar(value=self.station_category)
        self.var_station_logo = tk.StringVar(value=self.station_logo)

        self.var_llm_endpoint = tk.StringVar(value=self.llm_endpoint)
        self.var_model_producer = tk.StringVar(value=self.model_producer)
        self.var_model_host = tk.StringVar(value=self.model_host)
        self.var_model_nav = tk.StringVar(value=self.model_navigator)
        self.var_model_embedding = tk.StringVar(value=self.model_embedding)
        self.var_embedding_enabled = tk.BooleanVar(value=self.embedding_enabled)
        self.var_llm_provider = tk.StringVar(value=self.llm_provider)  # Default to self.llm_provider
        
        # Visual model variables
        global_cfg = get_global_config()
        visual_cfg = global_cfg.get("visual_models", {})
        self.var_visual_model_type = tk.StringVar(value=visual_cfg.get("model_type", "local"))
        self.var_visual_model_local = tk.StringVar(value=visual_cfg.get("local_model", ""))
        self.var_visual_model_api_provider = tk.StringVar(value=visual_cfg.get("api_provider", "openai"))
        self.var_visual_model_api_model = tk.StringVar(value=visual_cfg.get("api_model", "gpt-4-vision"))
        self.var_visual_model_api_key = tk.StringVar(value=visual_cfg.get("api_key", ""))
        self.var_visual_model_max_size = tk.StringVar(value=visual_cfg.get("max_image_size", "1024"))

        # Station ID row - read-only in edit mode
        if self.edit_mode:
            tk.Label(wrap, text="Station ID (folder name)", font=FONT_BODY, fg=UI["muted"], bg=UI["bg"]).grid(
                row=1, column=0, sticky="w", padx=(0, 10), pady=6
            )
            tk.Label(wrap, text=self.station_id, font=FONT_BODY, fg=UI["accent"], bg=UI["bg"]).grid(
                row=1, column=1, sticky="w", pady=6
            )
        else:
            self._row(wrap, 1, "Station ID (folder name)", self.var_station_id, hint="e.g. algotradingfm2")
        
        self._row(wrap, 2, "Station name", self.var_station_name)
        self._row(wrap, 3, "Lead character name", self.var_station_host, hint="Primary on-air identity (any name)")
        self._row(wrap, 4, "Category", self.var_station_cat)
        self._row_with_browse(wrap, 5, "Logo", self.var_station_logo, kind="file")
        
        # Meta Plugin selector
        self.var_meta_plugin = tk.StringVar(value=self.meta_plugin)
        tk.Label(wrap, text="Meta Plugin", font=FONT_BODY, fg=UI["muted"], bg=UI["bg"]).grid(
            row=6, column=0, sticky="w", padx=(0, 10), pady=6
        )
        meta_plugins = discover_meta_plugins()
        meta_combo = ttk.Combobox(
            wrap, textvariable=self.var_meta_plugin,
            values=meta_plugins,
            state="readonly", width=30
        )
        meta_combo.grid(row=6, column=1, sticky="w", pady=6)
        tk.Label(wrap, text="Core AI behavior controller", font=FONT_SMALL, fg=UI["muted"], bg=UI["bg"]).grid(
            row=6, column=2, sticky="w", padx=(10, 0)
        )

        ttk.Separator(wrap, orient="horizontal").grid(row=7, column=0, columnspan=3, sticky="ew", pady=14)

        tk.Label(wrap, text="Models & LLM", font=FONT_H2, fg=UI["text"], bg=UI["bg"]).grid(
            row=8, column=0, sticky="w", pady=(0, 10), columnspan=3
        )
        
        # Provider selector
        tk.Label(wrap, text="LLM Provider", font=FONT_BODY, fg=UI["muted"], bg=UI["bg"]).grid(
            row=9, column=0, sticky="w", padx=(0, 10), pady=6
        )
        provider_combo = ttk.Combobox(
            wrap, textvariable=self.var_llm_provider,
            values=["ollama", "anthropic", "openai", "google"],
            state="readonly", width=30
        )
        provider_combo.grid(row=9, column=1, sticky="ew", pady=6)
        provider_combo.bind("<<ComboboxSelected>>", lambda e: self._update_llm_labels())
        
        # Endpoint label - changes based on provider
        self.endpoint_label = tk.Label(wrap, text="Endpoint", font=FONT_BODY, fg=UI["muted"], bg=UI["bg"])
        self.endpoint_label.grid(row=10, column=0, sticky="w", padx=(0, 10), pady=6)
        
        endpoint_ent = tk.Entry(wrap, textvariable=self.var_llm_endpoint, font=FONT_BODY, 
                               bg=UI["surface"], fg=UI["text"], insertbackground=UI["text"], width=64)
        endpoint_ent.grid(row=10, column=1, sticky="ew", pady=6)
        
        self.endpoint_hint = tk.Label(wrap, text="", font=FONT_SMALL, fg=UI["muted"], bg=UI["bg"])
        self.endpoint_hint.grid(row=10, column=2, sticky="w", padx=(10, 0))
        
        self._row(wrap, 11, "Curator model (producer key)", self.var_model_producer, width=64, hint="Discovery planning")
        self._row(wrap, 12, "Interpreter model (host key)", self.var_model_host, width=64, hint="Lead voice output")
        self._row(wrap, 13, "Navigator model", self.var_model_nav, width=64, hint="Procedural move selector")
        
        # Character Manager modelself.model_char_manager
        self.var_model_char_manager = tk.StringVar(value="")
        self._row(wrap, 14, "Character Manager model", self.var_model_char_manager, width=64, 
         hint="(Optional) LLM for routing context queries")
        self._row(wrap, 15, "Embedding model (optional)", self.var_model_embedding, width=64,
         hint="For semantic text context search")

        tk.Checkbutton(
            wrap,
            text="Enable embeddings (global)",
            variable=self.var_embedding_enabled,
            bg=UI["bg"], fg=UI["text"],
            selectcolor=UI["panel"],
            activebackground=UI["bg"],
            activeforeground=UI["accent"],
        ).grid(row=16, column=1, sticky="w", pady=6)

        wrap.grid_columnconfigure(1, weight=1)
    
    def _update_llm_labels(self):
        """Update labels based on selected LLM provider."""
        provider = self.var_llm_provider.get()

        if provider == "ollama":
            default_endpoint = "http://127.0.0.1:11434/api/generate"
            current = (self.var_llm_endpoint.get() or "").strip().lower()
            if not current or any(k in current for k in ["anthropic", "openai", "google", "gemini", "claude"]):
                self.var_llm_endpoint.set(default_endpoint)
        
        hints = {
            "ollama": "http://127.0.0.1:11434/api/generate",
            "anthropic": "Set ANTHROPIC_API_KEY env var, model name e.g. claude-3-opus",
            "openai": "Set OPENAI_API_KEY env var, model name e.g. gpt-4",
            "google": "Set GOOGLE_API_KEY env var, model name e.g. gemini-pro",
        }
        
        self.endpoint_hint.config(text=hints.get(provider, ""))

    def _row(self, parent, r, label, var, width=40, hint=""):
        tk.Label(parent, text=label, font=FONT_BODY, fg=UI["muted"], bg=UI["bg"]).grid(
            row=r, column=0, sticky="w", padx=(0, 10), pady=6
        )
        ent = tk.Entry(parent, textvariable=var, font=FONT_BODY, bg=UI["surface"], fg=UI["text"],
                       insertbackground=UI["text"], width=width)
        ent.grid(row=r, column=1, sticky="ew", pady=6)
        if hint:
            tk.Label(parent, text=hint, font=FONT_SMALL, fg=UI["muted"], bg=UI["bg"]).grid(
                row=r, column=2, sticky="w", padx=(10, 0)
            )
    
    def _row_with_browse(self, parent, r, label, var, width=40, kind="file"):
        """Row with browse button for files/folders."""
        tk.Label(parent, text=label, font=FONT_BODY, fg=UI["muted"], bg=UI["bg"]).grid(
            row=r, column=0, sticky="w", padx=(0, 10), pady=6
        )
        ent = tk.Entry(parent, textvariable=var, font=FONT_BODY, bg=UI["surface"], fg=UI["text"],
                       insertbackground=UI["text"], width=width)
        ent.grid(row=r, column=1, sticky="ew", pady=6)
        
        tk.Button(
            parent, text="Browse",
            bg=UI["panel"], fg=UI["text"], relief="flat",
            command=lambda: self._browse_file_into(var, kind=kind)
        ).grid(row=r, column=2, padx=8)

    # -------------
    # Step 2: feeds (HIGH-LEVEL TOGGLES + editor)
    # -------------
    def _build_feeds(self):
        _outer, wrap, _canvas = self._make_scrollable_frame(self.tab_feeds, UI["bg"])
        wrap.configure(padx=14, pady=14)

        tk.Label(
            wrap,
            text="Choose feeds (plugins) and configure them",
            font=FONT_H2, fg=UI["text"], bg=UI["bg"]
        ).pack(anchor="w", pady=(0, 6))

        tk.Label(
            wrap,
            text="Toggle feeds from the high-level list. Click a feed to edit its config on the right.",
            font=FONT_BODY, fg=UI["muted"], bg=UI["bg"]
        ).pack(anchor="w", pady=(0, 12))

        body = tk.Frame(wrap, bg=UI["bg"])
        body.pack(fill="both", expand=True)

        # LEFT SIDE
        left = tk.Frame(body, bg=UI["panel"], width=int(360 * UI_SCALE))
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        # RIGHT SIDE
        right = tk.Frame(body, bg=UI["bg"])
        right.pack(side="left", fill="both", expand=True, padx=(12, 0))

        # ==============================
        # Scroll restore logic
        # ==============================

        self.feed_main_canvas = _canvas

        def _bind_main_scroll(_e=None):
            def _main_wheel(e):
                delta = 0
                try:
                    if sys.platform == "darwin":
                        delta = int(-1 * e.delta)
                    else:
                        delta = int(-1 * (e.delta / 120))
                except Exception:
                    pass

                if delta:
                    self.feed_main_canvas.yview_scroll(delta, "units")

            self.feed_main_canvas.bind_all("<MouseWheel>", _main_wheel)

            if sys.platform.startswith("linux"):
                self.feed_main_canvas.bind_all(
                    "<Button-4>",
                    lambda e: self.feed_main_canvas.yview_scroll(-1, "units")
                )
                self.feed_main_canvas.bind_all(
                    "<Button-5>",
                    lambda e: self.feed_main_canvas.yview_scroll(1, "units")
                )

        def _unbind_main_scroll(_e=None):
            self.feed_main_canvas.unbind_all("<MouseWheel>")
            if sys.platform.startswith("linux"):
                self.feed_main_canvas.unbind_all("<Button-4>")
                self.feed_main_canvas.unbind_all("<Button-5>")

        right.bind("<Enter>", _bind_main_scroll)
        right.bind("<Leave>", _unbind_main_scroll)
        
        # Set initial scroll binding for the main area
        _bind_main_scroll()

        # ==============================
        # Feed discovery
        # ==============================

        names = self._discover_feed_names()

        if not names:
            names = sorted(FEED_TEMPLATES.keys())

        for n in names:
            self._ensure_feed_cfg(n)

        # ==============================
        # Bulk actions
        # ==============================

        topbar = tk.Frame(left, bg=UI["panel"])
        topbar.pack(fill="x", padx=12, pady=(12, 8))

        tk.Label(
            topbar,
            text="Feed Toggles",
            font=("Segoe UI", 12, "bold"),
            fg=UI["text"], bg=UI["panel"]
        ).pack(anchor="w", pady=(0, 8))

        btnrow = tk.Frame(topbar, bg=UI["panel"])
        btnrow.pack(fill="x")

        tk.Button(
            btnrow, text="Enable All",
            bg=UI["panel"], fg=UI["accent"], relief="flat",
            command=lambda: self._bulk_set_feeds(names, True)
        ).pack(side="left", padx=(0, 6))

        tk.Button(
            btnrow, text="Disable All",
            bg=UI["panel"], fg=UI["danger"], relief="flat",
            command=lambda: self._bulk_set_feeds(names, False)
        ).pack(side="left", padx=(0, 6))

        tk.Button(
            btnrow, text="Enable Defaults",
            bg=UI["panel"], fg=UI["text"], relief="flat",
            command=self._enable_default_feeds
        ).pack(side="left", padx=(0, 6))

        tk.Button(
            btnrow, text="Invert",
            bg=UI["panel"], fg=UI["text"], relief="flat",
            command=lambda: self._invert_feeds(names)
        ).pack(side="right")

        ttk.Separator(left, orient="horizontal").pack(fill="x", padx=12, pady=(8, 10))

        # ==============================
        # Scrollable checkbox list
        # ==============================

        self.feed_enabled_vars: Dict[str, tk.BooleanVar] = {}

        scroll = tk.Frame(left, bg=UI["panel"])
        scroll.pack(fill="both", expand=True, padx=12)

        vsb = ttk.Scrollbar(scroll, orient="vertical")
        vsb.pack(side="right", fill="y")

        canvas = tk.Canvas(scroll, bg=UI["panel"], highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        vsb.configure(command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)

        chk_frame = tk.Frame(canvas, bg=UI["panel"])
        win_id = canvas.create_window((0, 0), window=chk_frame, anchor="nw")

        def _on_canvas_resize(e):
            canvas.itemconfigure(win_id, width=e.width)

        def _on_mousewheel(e):
            if sys.platform == "darwin":
                if e.delta:
                    canvas.yview_scroll(int(-1 * e.delta), "units")
            else:
                canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

        def _bind_scroll(_e):
            # Unbind main scroll first to avoid conflicts
            self.feed_main_canvas.unbind_all("<MouseWheel>")
            if sys.platform.startswith("linux"):
                self.feed_main_canvas.unbind_all("<Button-4>")
                self.feed_main_canvas.unbind_all("<Button-5>")
            
            # Bind checkbox canvas scroll
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            if sys.platform.startswith("linux"):
                canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
                canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

        def _unbind_scroll(_e):
            # Unbind checkbox canvas scroll
            canvas.unbind_all("<MouseWheel>")
            if sys.platform.startswith("linux"):
                canvas.unbind_all("<Button-4>")
                canvas.unbind_all("<Button-5>")
            
            # Restore main scroll
            _bind_main_scroll()

        for w in (scroll, canvas, chk_frame, vsb):
            w.bind("<Enter>", _bind_scroll)
            w.bind("<Leave>", _unbind_scroll)

        canvas.bind("<Configure>", _on_canvas_resize)

        def _on_chk_frame_configure(_e=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        chk_frame.bind("<Configure>", _on_chk_frame_configure)

        # ==============================
        # Create checkboxes
        # ==============================

        for n in names:
            cfg = self._ensure_feed_cfg(n)

            v = tk.BooleanVar(value=bool(cfg.get("enabled", False)))
            self.feed_enabled_vars[n] = v

            row = tk.Frame(chk_frame, bg=UI["panel"])
            row.pack(fill="x", pady=3)

            tk.Checkbutton(
                row,
                text=n,
                variable=v,
                command=lambda nn=n: self._toggle_feed_from_var(nn),
                bg=UI["panel"], fg=UI["text"],
                selectcolor=UI["panel"],
                activebackground=UI["panel"],
                anchor="w"
            ).pack(fill="x")

        ttk.Separator(left, orient="horizontal").pack(fill="x", padx=12, pady=(10, 10))

        tk.Label(
            left,
            text="Click to edit config",
            font=("Segoe UI", 11, "bold"),
            fg=UI["text"], bg=UI["panel"]
        ).pack(anchor="w", padx=12)

        self.feed_list = tk.Listbox(
            left,
            bg=UI["surface"], fg=UI["text"],
            font=FONT_BODY,
            relief="flat",
            exportselection=False
        )
        self.feed_list.pack(fill="both", expand=True, padx=12, pady=(8, 12))

        for n in names:
            self.feed_list.insert("end", n)

        self.feed_list.bind("<<ListboxSelect>>", lambda e: self._feed_load_selected())

        # ==============================
        # Right editor
        # ==============================

        self.feed_editor_title = tk.Label(
            right,
            text="Select a feed on the left",
            font=FONT_H2, fg=UI["muted"], bg=UI["bg"]
        )
        self.feed_editor_title.pack(anchor="w", pady=(0, 10))

        self.feed_editor = tk.Frame(right, bg=UI["bg"])
        self.feed_editor.pack(fill="both", expand=True)

        if self.feed_list.size() > 0:
            self.feed_list.selection_set(0)
            self._feed_load_selected()

    # ---- helpers for high-level toggles ----
    def _toggle_feed_from_var(self, feed_name: str):
        cfg = self._ensure_feed_cfg(feed_name)
        v = self.feed_enabled_vars.get(feed_name)
        if v is None:
            return
        cfg["enabled"] = bool(v.get())
        self.feed_cfg[feed_name] = cfg
        # keep editor pill accurate if currently open
        self._feed_load_selected()

    def _set_feed_enabled(self, feed_name: str, enabled: bool):
        cfg = self._ensure_feed_cfg(feed_name)
        cfg["enabled"] = bool(enabled)
        self.feed_cfg[feed_name] = cfg
        if hasattr(self, "feed_enabled_vars") and feed_name in self.feed_enabled_vars:
            self.feed_enabled_vars[feed_name].set(bool(enabled))

    def _bulk_set_feeds(self, feed_names: List[str], enabled: bool):
        for n in feed_names:
            self._set_feed_enabled(n, enabled)
        self._feed_load_selected()

    def _invert_feeds(self, feed_names: List[str]):
        for n in feed_names:
            cfg = self._ensure_feed_cfg(n)
            cur = bool(cfg.get("enabled", False))
            self._set_feed_enabled(n, not cur)
        self._feed_load_selected()

    def _enable_default_feeds(self):
        # DEFAULT_SCHED_QUOTAS keys are your “recommended” gold set
        defaults = set(DEFAULT_SCHED_QUOTAS.keys())
        all_names = list(self.feed_cfg.keys()) if self.feed_cfg else []
        if not all_names and hasattr(self, "feed_enabled_vars"):
            all_names = list(self.feed_enabled_vars.keys())

        # If we still don't know, fall back to templates
        if not all_names:
            all_names = list(FEED_TEMPLATES.keys())

        for n in all_names:
            self._set_feed_enabled(n, n in defaults)

        self._feed_load_selected()


    def _feed_selected(self) -> Optional[str]:
        sel = self.feed_list.curselection()
        if not sel:
            return None
        return self.feed_list.get(sel[0])

    def _ensure_feed_cfg(self, feed_name: str) -> Dict[str, Any]:
        if feed_name not in self.feed_cfg:
            # Priority: plugin defaults -> FEED_TEMPLATES -> minimal stub
            meta = (self.plugins or {}).get(feed_name, {}) if isinstance(self.plugins, dict) else {}
            base = meta.get("defaults")
            if not isinstance(base, dict):
                base = FEED_TEMPLATES.get(feed_name)
            if not isinstance(base, dict):
                base = {"enabled": False}

            cfg = _deepcopy_jsonable(base)
            cfg.setdefault("enabled", False)  # IMPORTANT: default to off
            self.feed_cfg[feed_name] = cfg

        return self.feed_cfg[feed_name]


    def _feed_enable_selected(self):
        n = self._feed_selected()
        if not n:
            return
        cfg = self._ensure_feed_cfg(n)
        cfg["enabled"] = True
        self._feed_load_selected()

    def _feed_disable_selected(self):
        n = self._feed_selected()
        if not n:
            return
        cfg = self._ensure_feed_cfg(n)
        cfg["enabled"] = False
        self._feed_load_selected()

    def _feed_reset_selected(self):
        n = self._feed_selected()
        if not n:
            return
        base = FEED_TEMPLATES.get(n, {"enabled": True})
        self.feed_cfg[n] = _deepcopy_jsonable(base)
        self._feed_load_selected()

    def _clear(self, parent: tk.Widget):
        for w in parent.winfo_children():
            w.destroy()

    def _feed_load_selected(self):
        n = self._feed_selected()
        if not n:
            return

        cfg = self._ensure_feed_cfg(n)

        # Merge defaults so new keys (like auth) appear
        meta = (self.plugins or {}).get(n, {})
        if isinstance(meta, dict):
            defs = meta.get("defaults")
            if isinstance(defs, dict):
                for k, v in defs.items():
                    if k not in cfg:
                        # Copy default value if missing
                        cfg[k] = v

        self._clear(self.feed_editor)
        self.feed_editor_title.config(text=f"{n} feed")

        # enabled summary
        enabled = bool(cfg.get("enabled", False))
        pill = tk.Label(
            self.feed_editor,
            text=("ENABLED" if enabled else "DISABLED"),
            font=("Segoe UI", 10, "bold"),
            fg=("#000" if enabled else UI["text"]),
            bg=(UI["good"] if enabled else UI["panel"]),
            padx=10, pady=4
        )
        pill.pack(anchor="w", pady=(0, 10))

        # Live search "ready" panels (stubs now, wired later)
        if n == "reddit":
            self._render_reddit_live_search_stub(self.feed_editor, cfg)
        elif n == "bluesky":
            self._render_bluesky_live_search_stub(self.feed_editor, cfg)

        # generic config editor for feed fields
        form = tk.Frame(self.feed_editor, bg=UI["bg"])
        form.pack(fill="both", expand=True, pady=(10, 0))

        rows: List[tuple] = []
        for k in sorted(cfg.keys()):
            if k == "enabled":
                continue
            rows.append((k, cfg[k]))

        self._feed_vars: Dict[str, tk.Variable] = {}
        for i, (k, v) in enumerate(rows):
            row = tk.Frame(form, bg=UI["bg"])
            row.pack(fill="x", pady=6)

            tk.Label(row, text=k, font=FONT_BODY, fg=UI["muted"], bg=UI["bg"], width=22, anchor="w").pack(side="left")

            if isinstance(v, bool):
                vv = tk.BooleanVar(value=bool(v))
                tk.Checkbutton(row, variable=vv, bg=UI["bg"], fg=UI["text"], selectcolor=UI["bg"]).pack(side="left")
                self._feed_vars[k] = vv
            else:
                if isinstance(v, list):
                    sv = tk.StringVar(value=json.dumps(v, ensure_ascii=False))
                else:
                    sv = tk.StringVar(value=str(v))
                ent = tk.Entry(row, textvariable=sv, bg=UI["surface"], fg=UI["text"], insertbackground=UI["text"])
                ent.pack(fill="x", expand=True)
                self._feed_vars[k] = sv

        # Save feed config changes button
        def apply():
            for k, var in self._feed_vars.items():
                if isinstance(var, tk.BooleanVar):
                    cfg[k] = bool(var.get())
                else:
                    raw = str(var.get() or "").strip()
                    try:
                        cfg[k] = yaml.safe_load(raw)
                    except Exception:
                        cfg[k] = raw
            self.feed_cfg[n] = cfg

        tk.Button(
            self.feed_editor,
            text="Apply feed changes",
            bg=UI["accent"], fg="#000", relief="flat",
            command=apply
        ).pack(anchor="w", pady=12)

    def _render_reddit_live_search_stub(self, parent: tk.Widget, cfg: Dict[str, Any]):
        box = tk.Frame(parent, bg=UI["panel"])
        box.pack(fill="x", pady=(0, 10))
        tk.Label(box, text="Reddit: live subreddit search (ready for integration)", font=("Segoe UI", 11, "bold"),
                 fg=UI["text"], bg=UI["panel"]).pack(anchor="w", padx=12, pady=(10, 2))
        tk.Label(box, text="For now, add subreddits below as a list. Later we’ll wire real search + click-to-add.",
                 font=FONT_SMALL, fg=UI["muted"], bg=UI["panel"]).pack(anchor="w", padx=12, pady=(0, 10))

        row = tk.Frame(box, bg=UI["panel"])
        row.pack(fill="x", padx=12, pady=(0, 12))
        q = tk.StringVar()
        tk.Entry(row, textvariable=q, bg=UI["surface"], fg=UI["text"], insertbackground=UI["text"]).pack(
            side="left", fill="x", expand=True
        )

        def add_sub():
            s = (q.get() or "").strip()
            if not s:
                return
            subs = cfg.get("subreddits", [])
            if not isinstance(subs, list):
                subs = []
            if s not in subs:
                subs.append(s)
            cfg["subreddits"] = subs
            q.set("")
            # reflect immediately in config editor if it exists
            self._feed_load_selected()

        tk.Button(row, text="Add", bg=UI["panel"], fg=UI["accent"], relief="flat", command=add_sub).pack(side="left", padx=8)

    def _render_bluesky_live_search_stub(self, parent: tk.Widget, cfg: Dict[str, Any]):
        box = tk.Frame(parent, bg=UI["panel"])
        box.pack(fill="x", pady=(0, 10))
        tk.Label(box, text="Bluesky: live hashtag suggestions (ready for integration)", font=("Segoe UI", 11, "bold"),
                 fg=UI["text"], bg=UI["panel"]).pack(anchor="w", padx=12, pady=(10, 2))
        tk.Label(box, text="For now, add hashtags below. Later we’ll fetch real suggestions and show a clickable list.",
                 font=FONT_SMALL, fg=UI["muted"], bg=UI["panel"]).pack(anchor="w", padx=12, pady=(0, 10))

        row = tk.Frame(box, bg=UI["panel"])
        row.pack(fill="x", padx=12, pady=(0, 12))
        q = tk.StringVar()
        tk.Entry(row, textvariable=q, bg=UI["surface"], fg=UI["text"], insertbackground=UI["text"]).pack(
            side="left", fill="x", expand=True
        )

        def add_tag():
            s = (q.get() or "").strip().lstrip("#")
            if not s:
                return
            tags = cfg.get("hashtags", [])
            if not isinstance(tags, list):
                tags = []
            if s not in tags:
                tags.append(s)
            cfg["hashtags"] = tags
            q.set("")
            self._feed_load_selected()

        tk.Button(row, text="Add", bg=UI["panel"], fg=UI["accent"], relief="flat", command=add_tag).pack(side="left", padx=8)
    def _characters_changed(self):
        """
        Single source of truth sync between characters + voices + UI.
        Fixes duplicates, stale entries, and missed refreshes.
        """

        # --- 1) Capture current voice UI edits if present
        try:
            if hasattr(self, "voice_vars") and isinstance(self.voice_vars, dict):
                for k, var in self.voice_vars.items():
                    try:
                        self.voices[k] = (var.get() or "").strip()
                    except Exception:
                        pass
        except Exception:
            pass

        # --- 2) Ensure every character has a voice entry
        for k in self.characters.keys():
            if k not in self.voices:
                self.voices[k] = ""

        # --- 3) Remove voices for deleted characters
        for k in list(self.voices.keys()):
            if k not in self.characters:
                self.voices.pop(k, None)

        # --- 4) Refresh voices UI if tab exists (safe always)
        try:
            if hasattr(self, "tab_voices"):
                self._refresh_voices_tab()
        except Exception:
            pass


    # -------------
    # Step 3: characters
    # -------------


    def _append_to_json_list(self, var: tk.StringVar, value: str):
        v = (value or "").strip()
        if not v:
            return
        try:
            arr = parse_list_field(var.get())
            if not isinstance(arr, list):
                arr = []
        except Exception:
            arr = []
        if v not in arr:
            arr.append(v)
        var.set(json.dumps(arr, ensure_ascii=False))

    def _refresh_char_list(self):
        self.char_list.delete(0, "end")
        for k in sorted(self.characters.keys()):
            self.char_list.insert("end", k)

    def _char_selected_key(self) -> Optional[str]:
        sel = self.char_list.curselection()
        if not sel:
            return None
        return self.char_list.get(sel[0])

    def _char_load_selected(self):
        k = self._char_selected_key()
        if not k:
            return
        c = self.characters.get(k, {})
        if not isinstance(c, dict):
            return
        self.var_char_key.set(k)
        self.var_char_role.set(str(c.get("role", "")))
        self.var_char_traits.set(json.dumps(c.get("traits", []), ensure_ascii=False))
        self.var_char_focus.set(json.dumps(c.get("focus", []), ensure_ascii=False))
        
        # Load context engine config
        if hasattr(self, "context_engine_frame"):
            context_cfg = c.get("context_engine", {})
            self.context_engine_frame.load_config(context_cfg)
            if hasattr(self, "_char_context_engines"):
                self._char_context_engines[k] = context_cfg
    def _char_apply(self):
        old = self._char_selected_key()
        if not old:
            return

        new_key = (self.var_char_key.get() or "").strip().lower()
        if not new_key:
            messagebox.showerror("Character", "Character key cannot be empty.")
            return

        role = (self.var_char_role.get() or "").strip()
        traits = parse_list_field(self.var_char_traits.get())
        focus = parse_list_field(self.var_char_focus.get())

        if not isinstance(traits, list):
            traits = []
        if not isinstance(focus, list):
            focus = []

        if old == "host" and new_key != "host":
            messagebox.showerror("Character", "Lead voice key must remain 'host'.")
            return

        # rename if needed
        if new_key != old:
            if new_key in self.characters:
                messagebox.showerror("Character", f"'{new_key}' already exists.")
                return
            self.characters[new_key] = self.characters.pop(old)
            
            # Rename context engine config if exists
            if hasattr(self, "_char_context_engines") and old in self._char_context_engines:
                self._char_context_engines[new_key] = self._char_context_engines.pop(old)

        # Get context engine config
        context_engine = {}
        if hasattr(self, "context_engine_frame"):
            context_engine = self.context_engine_frame.get_config()
            if hasattr(self, "_char_context_engines"):
                self._char_context_engines[new_key] = context_engine

        self.characters[new_key] = {
            "role": role,
            "traits": traits,
            "focus": focus
        }
        
        # Add context_engine if enabled
        if context_engine.get("enabled"):
            self.characters[new_key]["context_engine"] = context_engine

        self._refresh_char_list()
        self._characters_changed()   # 🔥 SYNC VOICES

        # Reselect
        for i in range(self.char_list.size()):
            if self.char_list.get(i) == new_key:
                self.char_list.selection_clear(0, "end")
                self.char_list.selection_set(i)
                self.char_list.see(i)
                break

        messagebox.showinfo("Character saved", f"{new_key} updated.")

    def _char_add(self):

        win = tk.Toplevel(self.win)
        win.title("Add Character")
        win.geometry(scaled_geometry(520, 300))
        win.configure(bg=UI["bg"])
        win.grab_set()

        tk.Label(
            win, text="Add a character",
            font=FONT_H2, fg=UI["text"], bg=UI["bg"]
        ).pack(anchor="w", padx=14, pady=(14, 8))

        tk.Label(
            win, text="Pick a suggested role, then choose a key name.",
            font=FONT_BODY, fg=UI["muted"], bg=UI["bg"]
        ).pack(anchor="w", padx=14)

        key_var = tk.StringVar()
        role_var = tk.StringVar()

        row1 = tk.Frame(win, bg=UI["bg"])
        row1.pack(fill="x", padx=14, pady=(14, 6))

        tk.Label(row1, text="Key", fg=UI["muted"], bg=UI["bg"], width=10, anchor="w").pack(side="left")
        tk.Entry(
            row1, textvariable=key_var,
            bg=UI["surface"], fg=UI["text"], insertbackground=UI["text"]
        ).pack(side="left", fill="x", expand=True)

        row2 = tk.Frame(win, bg=UI["bg"])
        row2.pack(fill="x", padx=14, pady=6)

        tk.Label(row2, text="Role", fg=UI["muted"], bg=UI["bg"], width=10, anchor="w").pack(side="left")
        cb = ttk.Combobox(row2, values=PRESET_ROLES, state="readonly")
        cb.pack(side="left", fill="x", expand=True)
        cb.bind("<<ComboboxSelected>>", lambda e: role_var.set(cb.get()))

        def ok():
            k = (key_var.get() or "").strip().lower()
            if not k:
                return
            if k == "host":
                messagebox.showerror("Character", "Lead voice key 'host' already exists.")
                return
            if k in self.characters:
                messagebox.showerror("Character", "That key already exists.")
                return

            role = (role_var.get() or "").strip() or k

            traits = []
            focus = []

            if "engineer" in role:
                traits = ["technical", "precise"]
                focus = ["systems", "signals"]
            elif "skeptic" in role or "risk" in role:
                traits = ["critical", "grounded"]
                focus = ["risk", "failure_modes"]
            elif "macro" in role:
                traits = ["contextual", "broad"]
                focus = ["regimes", "liquidity"]
            elif "optimist" in role or "hype" in role:
                traits = ["energetic", "constructive"]
                focus = ["opportunity", "growth"]

            self.characters[k] = {
                "role": role,
                "traits": traits,
                "focus": focus
            }

            self._refresh_char_list()
            self._characters_changed()   # 🔥 SYNC VOICES

            win.destroy()

        btn = tk.Frame(win, bg=UI["bg"])
        btn.pack(fill="x", padx=14, pady=14)

        tk.Button(btn, text="Cancel", bg=UI["panel"], fg=UI["text"], relief="flat", command=win.destroy).pack(side="right", padx=6)
        tk.Button(btn, text="Add", bg=UI["accent"], fg="#000", relief="flat", command=ok).pack(side="right", padx=6)

    def _char_remove(self):
        k = self._char_selected_key()
        if not k:
            return
        
        # Prevent removing the last character
        if len(self.characters) <= 1:
            messagebox.showerror("Characters", "Cannot remove the only character. At least one is required.")
            return

        if len(self.characters) <= 2:
            messagebox.showerror("Characters", "Need at least 2 characters.")
            return

        if not messagebox.askyesno("Remove", f"Remove '{k}'?"):
            return

        self.characters.pop(k, None)

        self._refresh_char_list()
        self._characters_changed()   # 🔥 SYNC VOICES

        if self.char_list.size() > 0:
            self.char_list.selection_set(0)
            self._char_load_selected()


    def _char_load_preset_set(self):
        mem_presets = globals().get("CHARACTER_PRESETS", {})
        if not isinstance(mem_presets, dict):
            mem_presets = {}

        disk_presets = self._load_disk_character_presets()
        if not isinstance(disk_presets, dict):
            disk_presets = {}

        # Merge (disk overrides same-name in-memory)
        presets: Dict[str, Any] = {}
        presets.update(mem_presets)
        presets.update(disk_presets)

        if not presets:
            messagebox.showerror("Presets", "No character presets found.")
            return

        win = tk.Toplevel(self.win)
        win.title("Load Character Preset Set")
        win.geometry(scaled_geometry(520, 520))
        win.configure(bg=UI["bg"])
        win.grab_set()

        tk.Label(win, text="Choose a preset set", font=FONT_H2, fg=UI["text"], bg=UI["bg"]).pack(anchor="w", padx=14, pady=(14, 8))

        hint = "Includes built-in presets + anything you saved to disk."
        tk.Label(win, text=hint, font=FONT_SMALL, fg=UI["muted"], bg=UI["bg"]).pack(anchor="w", padx=14, pady=(0, 10))

        lb = tk.Listbox(win, bg=UI["surface"], fg=UI["text"], font=FONT_BODY, relief="flat")
        lb.pack(fill="both", expand=True, padx=14, pady=12)

        names = sorted(presets.keys())
        for name in names:
            lb.insert("end", name)

        def load():
            sel = lb.curselection()
            if not sel:
                return

            name = lb.get(sel[0])
            chosen = presets.get(name, {})
            if not isinstance(chosen, dict):
                return

            if "host" not in chosen:
                messagebox.showerror("Presets", "Preset must include lead voice key 'host'.")
                return

            if not messagebox.askyesno("Replace characters", f"Load '{name}'?\nThis replaces your current characters."):
                return

            self.characters = _deepcopy_jsonable(chosen)

            keys = sorted(self.characters.keys())
            if len(keys) > 10:
                others = [k for k in keys if k != "host"]
                keep = ["host"] + others[:9]
                self.characters = {k: self.characters[k] for k in keep}

            self._refresh_char_list()
            self._characters_changed()   # 🔥 SYNC VOICES

            if self.char_list.size() > 0:
                self.char_list.selection_set(0)
                self._char_load_selected()

            win.destroy()


        btn = tk.Frame(win, bg=UI["bg"])
        btn.pack(fill="x", padx=14, pady=(0, 14))
        tk.Button(btn, text="Cancel", bg=UI["panel"], fg=UI["text"], relief="flat", command=win.destroy).pack(side="right", padx=6)
        tk.Button(btn, text="Load", bg=UI["accent"], fg="#000", relief="flat", command=load).pack(side="right", padx=6)

        # -------------
        # Step 4: voices
        # -------------
    def _build_characters(self):
        _outer, wrap, _canvas = self._make_scrollable_frame(self.tab_chars, UI["bg"])
        wrap.configure(padx=14, pady=14)

        tk.Label(
            wrap,
            text="Choose your characters",
            font=FONT_H2,
            fg=UI["text"],
            bg=UI["bg"]
        ).pack(anchor="w")

        tk.Label(
            wrap,
            text="At least one character is required (can have any name). Add from presets or create custom characters.",
            font=FONT_BODY,
            fg=UI["muted"],
            bg=UI["bg"]
        ).pack(anchor="w", pady=(4, 10))

        body = tk.Frame(wrap, bg=UI["bg"])
        body.pack(fill="both", expand=True)

        # =========================
        # LEFT PANEL (LIST + BUTTONS)
        # =========================

        left = tk.Frame(body, bg=UI["panel"], width=int(260 * UI_SCALE))
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        self.char_list = tk.Listbox(
            left,
            bg=UI["surface"],
            fg=UI["text"],
            font=FONT_BODY,
            relief="flat",
            exportselection=False
        )
        self.char_list.pack(fill="both", expand=True, padx=10, pady=10)

        # -------------------------
        # BUTTON AREA (2 ROWS)
        # -------------------------

        btns = tk.Frame(left, bg=UI["panel"])
        btns.pack(fill="x", padx=10, pady=(0, 10))

        # Row 1 — Add / Remove
        row1 = tk.Frame(btns, bg=UI["panel"])
        row1.pack(fill="x")

        tk.Button(
            row1,
            text="Add…",
            bg=UI["panel"],
            fg=UI["accent"],
            relief="flat",
            command=self._char_add
        ).pack(side="left", padx=4)

        tk.Button(
            row1,
            text="Remove",
            bg=UI["panel"],
            fg=UI["danger"],
            relief="flat",
            command=self._char_remove
        ).pack(side="left", padx=4)

        # Row 2 — Presets
        row2 = tk.Frame(btns, bg=UI["panel"])
        row2.pack(fill="x", pady=(6, 0))

        tk.Button(
            row2,
            text="Save preset set…",
            bg=UI["panel"],
            fg=UI["text"],
            relief="flat",
            command=self._char_save_preset_set
        ).pack(side="left", padx=4)

        tk.Button(
            row2,
            text="Load preset set…",
            bg=UI["panel"],
            fg=UI["text"],
            relief="flat",
            command=self._char_load_preset_set
        ).pack(side="left", padx=4)

        # Populate list
        self._refresh_char_list()

        # =========================
        # RIGHT PANEL (EDITOR)
        # =========================

        right = tk.Frame(body, bg=UI["bg"])
        right.pack(side="left", fill="both", expand=True, padx=(12, 0))

        self.var_char_key = tk.StringVar(value="")
        self.var_char_role = tk.StringVar(value="")
        self.var_char_traits = tk.StringVar(value="[]")
        self.var_char_focus = tk.StringVar(value="[]")

        # ---- Key ----

        tk.Label(
            right,
            text="Character key",
            font=FONT_BODY,
            fg=UI["muted"],
            bg=UI["bg"]
        ).pack(anchor="w")

        tk.Entry(
            right,
            textvariable=self.var_char_key,
            bg=UI["surface"],
            fg=UI["text"],
            insertbackground=UI["text"]
        ).pack(fill="x", pady=(0, 10))

        # ---- Role ----

        tk.Label(
            right,
            text="Role (choose from presets or type)",
            font=FONT_BODY,
            fg=UI["muted"],
            bg=UI["bg"]
        ).pack(anchor="w")

        row_role = tk.Frame(right, bg=UI["bg"])
        row_role.pack(fill="x", pady=(0, 10))

        tk.Entry(
            row_role,
            textvariable=self.var_char_role,
            bg=UI["surface"],
            fg=UI["text"],
            insertbackground=UI["text"]
        ).pack(side="left", fill="x", expand=True)

        role_pick = ttk.Combobox(
            row_role,
            values=PRESET_ROLES,
            state="readonly",
            width=20
        )
        role_pick.pack(side="left", padx=8)
        role_pick.bind(
            "<<ComboboxSelected>>",
            lambda e: self.var_char_role.set(role_pick.get())
        )

        # ---- Traits ----

        tk.Label(
            right,
            text="Traits (JSON list) — or use picker",
            font=FONT_BODY,
            fg=UI["muted"],
            bg=UI["bg"]
        ).pack(anchor="w")

        row_traits = tk.Frame(right, bg=UI["bg"])
        row_traits.pack(fill="x", pady=(0, 10))

        tk.Entry(
            row_traits,
            textvariable=self.var_char_traits,
            bg=UI["surface"],
            fg=UI["text"],
            insertbackground=UI["text"]
        ).pack(side="left", fill="x", expand=True)

        traits_pick = ttk.Combobox(
            row_traits,
            values=PRESET_TRAITS,
            state="readonly",
            width=20
        )
        traits_pick.pack(side="left", padx=8)

        tk.Button(
            row_traits,
            text="＋",
            bg=UI["panel"],
            fg=UI["accent"],
            relief="flat",
            command=lambda: self._append_to_json_list(
                self.var_char_traits,
                traits_pick.get()
            )
        ).pack(side="left")

        # ---- Focus ----

        tk.Label(
            right,
            text="Focus (JSON list) — or use picker",
            font=FONT_BODY,
            fg=UI["muted"],
            bg=UI["bg"]
        ).pack(anchor="w")

        row_focus = tk.Frame(right, bg=UI["bg"])
        row_focus.pack(fill="x", pady=(0, 10))

        tk.Entry(
            row_focus,
            textvariable=self.var_char_focus,
            bg=UI["surface"],
            fg=UI["text"],
            insertbackground=UI["text"]
        ).pack(side="left", fill="x", expand=True)

        focus_pick = ttk.Combobox(
            row_focus,
            values=PRESET_FOCUS,
            state="readonly",
            width=20
        )
        focus_pick.pack(side="left", padx=8)

        tk.Button(
            row_focus,
            text="＋",
            bg=UI["panel"],
            fg=UI["accent"],
            relief="flat",
            command=lambda: self._append_to_json_list(
                self.var_char_focus,
                focus_pick.get()
            )
        ).pack(side="left")

        # ---- Context Engine ----
        
        from context_engine_ui import build_context_engine_ui
        
        # Store context engine config per character
        if not hasattr(self, "_char_context_engines"):
            self._char_context_engines = {}
        
        def get_context_cfg():
            char_key = self.var_char_key.get().strip()
            return self._char_context_engines.get(char_key, {})
        
        def set_context_cfg(cfg):
            char_key = self.var_char_key.get().strip()
            self._char_context_engines[char_key] = cfg
        
        self.context_engine_frame = build_context_engine_ui(
            parent=right,
            bg=UI["panel"],
            surface=UI["surface"],
            text_color=UI["text"],
            muted=UI["muted"],
            accent=UI["accent"],
            get_context_cfg_func=get_context_cfg,
            set_context_cfg_func=set_context_cfg,
            station_dir=""  # Will use station_dir when available
        )
        self.context_engine_frame.pack(fill="x", pady=10)

        # ---- Save ----

        btn_row = tk.Frame(right, bg=UI["bg"])
        btn_row.pack(anchor="w", pady=12)

        tk.Button(
            btn_row,
            text="Save character",
            bg=UI["accent"],
            fg="#000",
            relief="flat",
            command=self._char_apply
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            btn_row,
            text="Save station now",
            bg=UI["panel"],
            fg=UI["text"],
            relief="flat",
            command=self._save_manifest_only
        ).pack(side="left")

        # -------------------------
        # Selection wiring
        # -------------------------

        self.char_list.bind(
            "<<ListboxSelect>>",
            lambda e: self._char_load_selected()
        )

        if self.char_list.size() > 0:
            self.char_list.selection_set(0)
            self._char_load_selected()

    def _browse_file_into(self, var: tk.StringVar, kind: str = "file"):
        if kind == "file":
            p = filedialog.askopenfilename(parent=self.win)
        else:
            p = filedialog.askdirectory(parent=self.win)

        if p:
            var.set(p)

    def _sample_voice(self, voice_key: str):
        provider_name = self.var_voices_provider.get().strip()
        piper = (self.var_piper_bin.get() or "").strip()
        model = (self.voice_vars.get(voice_key).get() or "").strip() if voice_key in self.voice_vars else ""
        text = (self.var_sample_text.get() or "").strip()

        if not text:
            messagebox.showerror("Sample voice", "Sample text is empty.")
            return

        # For non-Piper providers, just show info for now to avoid freezing UI with model loading
        if provider_name != "piper":
            messagebox.showinfo("Sample Voice", f"Sampling for '{provider_name}' is not yet supported in the wizard.\nPlease create the station and test live.")
            return

        if not piper or not os.path.exists(piper):
            messagebox.showerror("Sample voice", "Set a valid Piper binary path first.")
            return
        if not model or not os.path.exists(model):
            messagebox.showerror("Sample voice", f"Set a valid voice model path for '{voice_key}'.")
            return

        try:
            import tempfile
            out_wav = os.path.join(tempfile.gettempdir(), f"radioos_sample_{voice_key}.wav")
            # Piper usage differs by build; this is a common pattern:
            # echo "text" | piper -m model.onnx -f out.wav
            cmd = [piper, "-m", model, "-f", out_wav]
            proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            proc.communicate(text + "\n", timeout=20)
            if os.path.exists(out_wav):
                _try_play_wav(out_wav)
            else:
                messagebox.showerror("Sample voice", "Failed to produce wav output.")
        except Exception as e:
            messagebox.showerror("Sample voice", f"Voice sample failed.\n\n{e}")
    def _character_presets_path(self) -> str:
        # Stored in repo root alongside shell.py; change if you want per-user
        return os.path.join(BASE, "character_presets.yaml")

    def _load_disk_character_presets(self) -> Dict[str, Any]:
        p = self._character_presets_path()
        if not os.path.exists(p):
            return {}
        try:
            with open(p, "r", encoding="utf-8") as f:
                obj = yaml.safe_load(f) or {}
            return obj if isinstance(obj, dict) else {}
        except Exception:
            return {}

    def _save_disk_character_presets(self, presets: Dict[str, Any]) -> None:
        p = self._character_presets_path()
        tmp = p + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.safe_dump(presets, f, sort_keys=False, allow_unicode=True)
        os.replace(tmp, p)

    def _char_save_preset_set(self):
        # Validate current set
        if not self.characters:
            messagebox.showerror("Presets", "Cannot save: no characters defined.")
            return
        if len(self.characters) < 2:
            messagebox.showerror("Presets", "Need at least 2 characters to save a preset.")
            return

        name = self.shell._prompt_text("Save Character Preset Set", "Preset name (e.g. 'AlgoTrading FM v2'):")
        if not name:
            return
        name = name.strip()
        if not name:
            return

        disk = self._load_disk_character_presets()

        # If exists, confirm overwrite
        if name in disk:
            if not messagebox.askyesno("Overwrite preset", f"Preset '{name}' exists.\nOverwrite?"):
                return

        disk[name] = _deepcopy_jsonable(self.characters)
        self._save_disk_character_presets(disk)
        messagebox.showinfo("Preset saved", f"Saved '{name}' to {self._character_presets_path()}")

    # -------------
    # Step 5: mix weights pie + sliders
    # -------------
    def _build_mix(self):
        # Create wrapper frame - actual rendering happens in _render_mix_ui when tab is shown
        self.weight_sliders = {}
        _outer, self.mix_wrap, _canvas = self._make_scrollable_frame(self.tab_mix, UI["bg"])
        self.mix_wrap.configure(padx=14, pady=14)
        
        # Initialize pie canvas placeholder
        self.pie = None


    def _mix_collect(self) -> Dict[str, float]:
        w = {}
        for k, var in self.weight_sliders.items():
            try:
                w[k] = float(var.get())
            except Exception:
                w[k] = 0.0
        return w

    def _mix_normalize_clicked(self):
        w = _normalize_weights(self._mix_collect())
        for k, frac in w.items():
            if k in self.weight_sliders:
                self.weight_sliders[k].set(frac)
        self._mix_redraw()

    def _mix_redraw(self):
        w = self._mix_collect()
        w = _normalize_weights(w)
        # update state
        self.mix_weights.update(w)
        
        # Safety check - pie canvas may not exist yet
        if not self.pie:
            return

        self.pie.delete("all")
        cx, cy = 260, 260
        r = 200
        x0, y0, x1, y1 = cx - r, cy - r, cx + r, cy + r

        segs = _pie_segments(w)

        # Use a rotating palette that relies on system colors lightly (no hardcoding too many),
        # but tkinter requires explicit fill colors; keep a small stable palette.
        palette = ["#4cc9f0", "#2ee59d", "#ff4d6d", "#f7b801", "#b084f5", "#2a9d8f", "#e76f51", "#8ecae6"]
        for i, (k, start, ext) in enumerate(segs):
            fill = palette[i % len(palette)]
            self.pie.create_arc(x0, y0, x1, y1, start=start, extent=ext, fill=fill, outline=UI["bg"])

        # Legend
        y = 20
        for i, (k, _, _) in enumerate(segs):
            frac = w.get(k, 0.0)
            fill = palette[i % len(palette)]
            self.pie.create_rectangle(20, y, 36, y + 16, fill=fill, outline="")
            self.pie.create_text(44, y + 8, text=f"{k}: {frac:.2f}", anchor="w", fill=UI["text"], font=("Segoe UI", 10))
            y += 22

    # -------------
    # Step 6: review
    # -------------
    def _build_review(self):
        _outer, wrap, _canvas = self._make_scrollable_frame(self.tab_review, UI["bg"])
        wrap.configure(padx=14, pady=14)

        tk.Label(wrap, text="Review & Create", font=FONT_H2, fg=UI["text"], bg=UI["bg"]).pack(anchor="w", pady=(0, 10))
        tk.Label(
            wrap,
            text="This is the exact manifest.yaml that will be written into stations/<station_id>/manifest.yaml.",
            font=FONT_BODY, fg=UI["muted"], bg=UI["bg"]
        ).pack(anchor="w", pady=(0, 10))

        self.review_text = tk.Text(wrap, bg=UI["surface"], fg=UI["text"], font=("Consolas", 10),
                                   relief="flat", bd=0, wrap="none", height=28)
        self.review_text.pack(fill="both", expand=True)

        btnrow = tk.Frame(wrap, bg=UI["bg"])
        btnrow.pack(fill="x", pady=10)

        tk.Button(btnrow, text="Refresh preview", bg=UI["panel"], fg=UI["text"], relief="flat", command=self._refresh_preview).pack(
            side="left", padx=6
        )
        button_text = "Save Changes" if self.edit_mode else "Create station"
        tk.Button(btnrow, text=button_text, bg=UI["accent"], fg="#000", relief="flat", command=self._finish).pack(
            side="right", padx=6
        )

        self._refresh_preview()

    def _load_default_manifest(self) -> Dict[str, Any]:
        path = os.path.join(BASE, "templates", "default_manifest.yaml")

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            if not isinstance(data, dict):
                raise ValueError("Template is not a dict")
            return data
        except Exception as e:
            raise RuntimeError(f"Failed loading default manifest: {e}")

    def _merge_manifests(self, base: Dict[str, Any], override: Dict[str, Any]) -> None:
        """Recursive merge of override into base."""
        for k, v in override.items():
            if k in base and isinstance(base[k], dict) and isinstance(v, dict):
                self._merge_manifests(base[k], v)
            else:
                base[k] = _deepcopy_jsonable(v)

    def _build_manifest(self) -> Dict[str, Any]:

        manifest = self._load_default_manifest()

        # If editing an existing station, overlay its configuration first.
        # This ensures that fields NOT managed by the wizard (pacing, riff, producer settings)
        # are preserved, rather than being reset to default template values.
        if self.existing_manifest:
            self._merge_manifests(manifest, self.existing_manifest)

        # -------- Station --------

        manifest["station"]["name"] = self.var_station_name.get().strip()
        manifest["station"]["host"] = self.var_station_host.get().strip()
        manifest["station"]["category"] = self.var_station_cat.get().strip()
        manifest["station"]["logo"] = self.var_station_logo.get().strip()
        
        # -------- Meta Plugin --------
        manifest["meta_plugin"] = self.var_meta_plugin.get().strip() or "radio_station"

        # -------- Models --------

        manifest["llm"]["endpoint"] = self.var_llm_endpoint.get().strip()
        manifest["llm"]["provider"] = self.var_llm_provider.get().strip()

        manifest["models"]["producer"] = self.var_model_producer.get().strip()
        manifest["models"]["host"] = self.var_model_host.get().strip()
        manifest["models"]["navigator"] = self.var_model_nav.get().strip()
        manifest["models"]["character_manager"] = self.var_model_char_manager.get().strip()
        manifest["models"]["embedding"] = self.var_model_embedding.get().strip()

        manifest.setdefault("embedding", {})
        manifest["embedding"]["enabled"] = bool(self.var_embedding_enabled.get())
        
        # -------- Visual Models --------
        manifest.setdefault("visual_models", {})
        manifest["visual_models"]["model_type"] = self.var_visual_model_type.get().strip()
        manifest["visual_models"]["local_model"] = self.var_visual_model_local.get().strip()
        manifest["visual_models"]["api_provider"] = self.var_visual_model_api_provider.get().strip()
        manifest["visual_models"]["api_model"] = self.var_visual_model_api_model.get().strip()
        manifest["visual_models"]["api_key"] = self.var_visual_model_api_key.get().strip()
        manifest["visual_models"]["max_image_size"] = self.var_visual_model_max_size.get().strip()

        # -------- Audio --------

        manifest["audio"]["voices_provider"] = self.var_voices_provider.get().strip()
        manifest["audio"]["piper_bin"] = self.var_piper_bin.get().strip()

        # Sync voice vars from UI before saving
        if hasattr(self, "voice_vars") and isinstance(self.voice_vars, dict):
            for k, var in self.voice_vars.items():
                try:
                    self.voices[k] = var.get().strip()
                except Exception:
                    pass

        manifest["voices"] = _deepcopy_jsonable(self.voices)

        # -------- Characters --------

        manifest["characters"] = _deepcopy_jsonable(self.characters)

        # -------- Feeds --------

        # -------- Feeds --------

        feeds_out: Dict[str, Any] = {}

        # Include ALL discovered feeds (enabled or not) so future toggles don’t need wizard edits.
        all_names = self._discover_feed_names()

        for name in all_names:
            cfg = self._ensure_feed_cfg(name)
            if not isinstance(cfg, dict):
                cfg = {"enabled": False}

            out = _deepcopy_jsonable(cfg)
            out.setdefault("enabled", False)
            feeds_out[name] = out

        manifest["feeds"] = feeds_out
        # -------- Scheduler quotas --------
        manifest.setdefault("scheduler", {})
        manifest["scheduler"].setdefault("source_quotas", {})

        sq = manifest["scheduler"]["source_quotas"]
        if not isinstance(sq, dict):
            sq = {}
            manifest["scheduler"]["source_quotas"] = sq

        for name, fcfg in feeds_out.items():
            # Don’t force quotas for disabled feeds unless you want it.
            # But having them present is nice for later enabling.
            sq.setdefault(name, int(self.scheduler_quotas.get(name, DEFAULT_SCHED_QUOTAS.get(name, 1))))
        manifest.setdefault("mix", {})
        manifest["mix"].setdefault("weights", {})

        mw = manifest["mix"]["weights"]
        if not isinstance(mw, dict):
            mw = {}
            manifest["mix"]["weights"] = mw

        for name, fcfg in feeds_out.items():
            enabled = bool(fcfg.get("enabled", False))
            if enabled:
                mw.setdefault(name, float(self.mix_weights.get(name, DEFAULT_MIX_WEIGHTS.get(name, 0.0))))
            else:
                mw.setdefault(name, 0.0)



        # -------- Scheduler quotas (optional but nice) --------

        if "scheduler" in manifest:
            manifest["scheduler"]["source_quotas"] = _deepcopy_jsonable(self.scheduler_quotas)

        # -------- Mix --------

        manifest["mix"]["weights"] = _deepcopy_jsonable(self.mix_weights)

        return manifest


    def _finish(self):
        try:
            manifest = self._build_manifest()
        except Exception as e:
            messagebox.showerror("Save station" if self.edit_mode else "Create station", f"Failed to build manifest:\n\n{e}")
            return

        # In edit mode, use existing station_id and path
        if self.edit_mode and self.station:
            station_id = self.station.station_id
            station_dir = self.station.path
        else:
            station_id = (self.var_station_id.get() or "").strip()
            if not station_id:
                messagebox.showerror("Create station", "Station ID is required.")
                return
            station_dir = os.path.join(STATIONS_DIR, station_id)
        
        os.makedirs(station_dir, exist_ok=True)

        out_path = os.path.join(station_dir, "manifest.yaml")

        try:
            with open(out_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(
                    manifest,
                    f,
                    sort_keys=False,
                    allow_unicode=True
                )
        except Exception as e:
            messagebox.showerror("Save station" if self.edit_mode else "Create station", f"Failed to write manifest:\n\n{e}")
            return

        self._result = {"manifest": manifest}
        self.win.destroy()

    def _save_manifest_only(self):
        try:
            manifest = self._build_manifest()
        except Exception as e:
            messagebox.showerror("Save station" if self.edit_mode else "Create station", f"Failed to build manifest:\n\n{e}")
            return

        if self.edit_mode and self.station:
            station_id = self.station.station_id
            station_dir = self.station.path
        else:
            station_id = (self.var_station_id.get() or "").strip()
            if not station_id:
                messagebox.showerror("Save station", "Station ID is required to save.")
                return
            station_dir = os.path.join(STATIONS_DIR, station_id)

        os.makedirs(station_dir, exist_ok=True)
        out_path = os.path.join(station_dir, "manifest.yaml")

        try:
            with open(out_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(
                    manifest,
                    f,
                    sort_keys=False,
                    allow_unicode=True
                )
        except Exception as e:
            messagebox.showerror("Save station", f"Failed to write manifest:\n\n{e}")
            return

        messagebox.showinfo("Saved", f"Station saved to {out_path}")

    def _refresh_preview(self):
        try:
            m = self._build_manifest()
            s = yaml.safe_dump(m, sort_keys=False, allow_unicode=True)
        except Exception as e:
            s = f"Error building manifest:\n{e}"
        self.review_text.config(state="normal")
        self.review_text.delete("1.0", "end")
        self.review_text.insert("1.0", s)
        self.review_text.config(state="disabled")

    # -------------
    # Navigation + validation
    # -------------
    def _sync_nav_buttons(self):
        idx = self.nb.index("current")
        self.btn_back.config(state=("disabled" if idx == 0 else "normal"))
        self.btn_next.config(state=("disabled" if idx == self.nb.index("end") - 1 else "normal"))

        # Keep preview fresh on review tab
        if idx == (self.nb.index("end") - 1):
            self._refresh_preview()

    def _go_back(self):
        idx = self.nb.index("current")
        if idx > 0:
            self.nb.select(idx - 1)

    def _go_next(self):
        idx = self.nb.index("current")
        if not self._validate_step(idx):
            return
        end = self.nb.index("end") - 1
        if idx < end:
            self.nb.select(idx + 1)

    def _cancel(self):
        self._result = None
        self.win.destroy()

    def _validate_step(self, idx: int) -> bool:
        # 0 basics
        if idx == 0:
            sid = (self.var_station_id.get() or "").strip()
            if not sid:
                messagebox.showerror("Station", "Station ID is required.")
                return False
            # folder safe-ish
            bad = any(c in sid for c in r'\/:*?"<>|')
            if bad:
                messagebox.showerror("Station", "Station ID contains invalid filename characters.")
                return False

            self.station_id = sid
            self.station_name = (self.var_station_name.get() or sid).strip()
            self.station_host = (self.var_station_host.get() or "Kai").strip()
            self.station_category = (self.var_station_cat.get() or "Custom").strip()
            self.station_logo = (self.var_station_logo.get() or "").strip()
            self.meta_plugin = (self.var_meta_plugin.get() or "radio_station").strip()

            self.llm_endpoint = (self.var_llm_endpoint.get() or "").strip()
            self.model_producer = (self.var_model_producer.get() or "").strip()
            self.model_host = (self.var_model_host.get() or "").strip()
            self.model_navigator = (self.var_model_nav.get() or "").strip()
            self.model_embedding = (self.var_model_embedding.get() or "").strip()
            self.embedding_enabled = bool(self.var_embedding_enabled.get())
            return True

        # Characters step: ensure at least one character exists
        if idx == 2:
            if not self.characters:
                messagebox.showerror("Characters", "At least one character is required.")
                return False
            return True

        # 3 voices: store piper + voices
        if idx == 3:
            # capture piper bin
            self.piper_bin = (self.var_piper_bin.get() or "").strip()

            # capture per-character voices (ALL of them)
            if hasattr(self, "voice_vars") and isinstance(self.voice_vars, dict):
                for k, var in self.voice_vars.items():
                    try:
                        self.voices[k] = (var.get() or "").strip()
                    except Exception:
                        self.voices[k] = ""

            # optional: if characters changed since voices tab was built, keep map stable
            # remove stale keys (characters removed)
            for k in list(self.voices.keys()):
                if k not in self.characters:
                    self.voices.pop(k, None)

            return True

        return True

    # -------------
    # Manifest builder (Gold Standard)
    # -------------
    def _build_manifest(self) -> Dict[str, Any]:
        # Determine enabled feeds; if user never touched feeds, default to your gold set
        if not self.feed_cfg:
            self.feed_cfg = {k: _deepcopy_jsonable(v) for k, v in FEED_TEMPLATES.items() if k in DEFAULT_SCHED_QUOTAS}

        # Ensure every feed has enabled boolean
        for k, v in list(self.feed_cfg.items()):
            if not isinstance(v, dict):
                self.feed_cfg[k] = {"enabled": True}
            self.feed_cfg[k].setdefault("enabled", True)

        enabled_feeds = [k for k, v in self.feed_cfg.items() if isinstance(v, dict) and v.get("enabled", False)]
        if not enabled_feeds:
            # require at least one feed (fallback to reddit)
            self.feed_cfg["reddit"] = _deepcopy_jsonable(FEED_TEMPLATES["reddit"])
            enabled_feeds = ["reddit"]

        # Scheduler quotas: include enabled feeds only, with default values if missing
        quotas = {}
        for k in enabled_feeds:
            quotas[k] = int(self.scheduler_quotas.get(k, DEFAULT_SCHED_QUOTAS.get(k, 1)))

        # Mix weights: include enabled feeds only (normalize)
        mw = {k: float(self.mix_weights.get(k, DEFAULT_MIX_WEIGHTS.get(k, 0.0))) for k in enabled_feeds}
        mw = _normalize_weights(mw)

        # Voices: keep the keys your runtime expects; keep as-is even if empty
        voices = dict(self.voices)

        # Build gold-standard manifest structure
        station_block: Dict[str, Any] = {
            "name": self.station_name,
            "host": self.station_host,
            "category": self.station_category,
        }
        
        # Add logo if set
        if self.station_logo and self.station_logo.strip():
            station_block["logo"] = self.station_logo
        
        manifest: Dict[str, Any] = {
            "station": station_block,
            "meta_plugin": self.meta_plugin or "radio_station",
            "llm": {
                "endpoint": self.llm_endpoint,
            },
            "models": {
                "producer": self.model_producer,
                "host": self.model_host,
                "navigator": self.model_navigator,
                "embedding": self.model_embedding,
            },
            "embedding": {
                "enabled": bool(self.embedding_enabled),
            },
            "scheduler": {
                "source_quotas": quotas,
                "reclaim_every_sec": 10,
                "reaper_every_sec": 3,
                "claim_timeout_sec": 45,
            },
            "riff": {
                "tag_catalog": [
                    "execution",
                    "risk",
                    "performance",
                    "psychology",
                    "trends",
                    "strategy",
                    "news",
                ],
                "shapes": [
                    "connect_two",
                    "myth_bust",
                    "failure_mode",
                    "tradeoff",
                    "tease_next",
                ],
            },
            "pacing": {
                "idle_riff_sec": 20,
                "between_segments_sec": 2,
                "queue_target_depth": 16,
                "queue_max_depth": 40,
                "producer_tick_sec": 30,
                "audio_target_depth": 8,
                "audio_max_depth": 10,
                "audio_tick_sleep": 0.05,
            },
            "producer": {
                "target_depth": 8,
                "max_depth": 20,
                "tick_sec": 12,
                "max_tokens": 320,
                "temperature": 0.35,
                "per_source_cap": 2,
                "source_limits": {
                    "rss": {"max_share": 0.20, "max_abs": 4},
                    "reddit": {"max_share": 0.45, "max_abs": 10},
                    "markets": {"max_share": 0.40, "max_abs": 8},
                    "portfolio_event": {"max_share": 0.35, "max_abs": 6},
                    "bluesky": {"max_share": 0.30, "max_abs": 6},
                    "document": {"max_share": 0.25, "max_abs": 4},
                },
            },
            "host": {
                "max_comments": 4,
                "between_segments_sec": 2,
                "idle_riff_sec": 23,
                "station_id_sec": 240,
                "max_tokens": 420,
                "temperature": 0.6,
            },
            "tts": {
                "spam_break_priority": 96,
                "min_gap_sec": 6,
                "deprioritize_penalty": 15,
            },
            "audio": {
                "piper_bin": self.piper_bin,
            },
            "voices": voices,
            "feeds": _deepcopy_jsonable(self.feed_cfg),
            "characters": _deepcopy_jsonable(self.characters),
            "mix": {
                "weights": mw
            },
        }

        # A couple of gold-standard cleanup rules:
        # - Ensure portfolio_event user_address is quoted-like string (yaml handles it)
        # - Ensure document.files is list of dicts
        if "document" in manifest["feeds"]:
            d = manifest["feeds"]["document"]
            if isinstance(d, dict) and "files" in d and not isinstance(d["files"], list):
                d["files"] = []

        return manifest


    # -------------
    # Utility
    # -------------
    def _build_manifest_preview_only(self) -> str:
        m = self._build_manifest()
        return yaml.safe_dump(m, sort_keys=False, allow_unicode=True)

# -----------------------------
# Station Editor Window
# -----------------------------
class EditorWindow:
    def __init__(self, shell: RadioShell, station: StationInfo):
        self.shell = shell
        self.station = station
        self.path = station.path
        self.mp = station_manifest_path(self.path)

        self.cfg = safe_read_yaml(self.mp)

        self.win = tk.Toplevel(shell.root)
        self.win.title(f"Edit Station — {station.station_id}")
        self.win.geometry(scaled_geometry(980, 720))
        self.win.configure(bg=UI["bg"])
        self.win.grab_set()

        self.nb = ttk.Notebook(self.win)
        self.nb.pack(fill="both", expand=True, padx=12, pady=12)

        self.tab_station   = tk.Frame(self.nb, bg=UI["bg"])
        self.tab_models    = tk.Frame(self.nb, bg=UI["bg"])
        self.tab_scheduler = tk.Frame(self.nb, bg=UI["bg"])
        self.tab_riff      = tk.Frame(self.nb, bg=UI["bg"])
        self.tab_pacing    = tk.Frame(self.nb, bg=UI["bg"])
        self.tab_producer  = tk.Frame(self.nb, bg=UI["bg"])
        self.tab_navigator = tk.Frame(self.nb, bg=UI["bg"])
        self.tab_host      = tk.Frame(self.nb, bg=UI["bg"])
        self.tab_tts       = tk.Frame(self.nb, bg=UI["bg"])
        self.tab_feeds     = tk.Frame(self.nb, bg=UI["bg"])
        self.tab_chars     = tk.Frame(self.nb, bg=UI["bg"])

        self.nb.add(self.tab_station, text="Station")
        self.nb.add(self.tab_models, text="Models & Audio")
        self.nb.add(self.tab_scheduler, text="Scheduler")
        self.nb.add(self.tab_riff, text="Riff Engine")
        self.nb.add(self.tab_pacing, text="Pacing")
        self.nb.add(self.tab_producer, text="Curator")
        self.nb.add(self.tab_navigator, text="Navigator")
        self.nb.add(self.tab_host, text="Interpreter")
        self.nb.add(self.tab_tts, text="TTS")
        self.nb.add(self.tab_feeds, text="Feeds")
        self.nb.add(self.tab_chars, text="Characters")

        # dynamic var store (path_key -> {field->Var})
        self._dynamic_vars: Dict[str, Dict[str, tk.Variable]] = {}

        self._build_station_tab()
        self._build_models_tab()
        self._build_dynamic_section(self.tab_scheduler, ["scheduler"], "Scheduler")
        self._build_dynamic_section(self.tab_riff, ["riff"], "Riff Engine")
        self._build_dynamic_section(self.tab_pacing, ["pacing"], "Pacing")
        self._build_dynamic_section(self.tab_producer, ["producer"], "Curator (producer)")
        self._build_dynamic_section(self.tab_navigator, ["navigator"], "Navigator")
        self._build_dynamic_section(self.tab_host, ["host"], "Interpreter (host)")
        self._build_dynamic_section(self.tab_tts, ["tts"], "TTS Anti-spam")
        self._build_feeds_tab()
        self._build_chars_tab()
        self._build_footer()

    def _cfg_get(self, path: List[str], default=None):
        cur: Any = self.cfg
        for p in path:
            if not isinstance(cur, dict) or p not in cur:
                return default
            cur = cur[p]
        return cur

    def _cfg_set(self, path: List[str], value):
        cur = self.cfg
        for p in path[:-1]:
            if p not in cur or not isinstance(cur[p], dict):
                cur[p] = {}
            cur = cur[p]
        cur[path[-1]] = value

    def _build_dynamic_section(self, parent, section_path: List[str], title: str):
        wrap = tk.Frame(parent, bg=UI["bg"])
        wrap.pack(fill="both", expand=True, padx=14, pady=14)

        tk.Label(wrap, text=title, font=FONT_H2, fg=UI["text"], bg=UI["bg"]).pack(anchor="w", pady=(0, 12))

        section = self._cfg_get(section_path, {})
        if not isinstance(section, dict):
            section = {}

        keybase = ".".join(section_path)
        self._dynamic_vars[keybase] = {}

        # keep stable order
        for key in sorted(section.keys()):
            val = section[key]
            row = tk.Frame(wrap, bg=UI["bg"])
            row.pack(fill="x", pady=6)

            tk.Label(row, text=key, fg=UI["muted"], bg=UI["bg"], width=24, anchor="w").pack(side="left")

            # bool
            if isinstance(val, bool):
                v = tk.BooleanVar(value=val)
                tk.Checkbutton(row, variable=v, bg=UI["bg"], fg=UI["text"], selectcolor=UI["bg"]).pack(side="left")
                self._dynamic_vars[keybase][key] = v
                continue

            # list
            if isinstance(val, list):
                v = tk.StringVar(value=json.dumps(val, ensure_ascii=False))
                ent = tk.Entry(row, textvariable=v, bg=UI["surface"], fg=UI["text"], insertbackground=UI["text"])
                ent.pack(fill="x", expand=True)
                self._dynamic_vars[keybase][key] = v
                continue

            # scalar
            v = tk.StringVar(value=str(val))
            ent = tk.Entry(row, textvariable=v, bg=UI["surface"], fg=UI["text"], insertbackground=UI["text"])
            ent.pack(fill="x", expand=True)
            self._dynamic_vars[keybase][key] = v

    def _row_entry(self, parent, row: int, label: str, var: tk.StringVar, width: int = 32,
                   browse: bool = False, browse_kind: str = "file"):
        tk.Label(parent, text=label, font=FONT_BODY, fg=UI["muted"], bg=UI["bg"]).grid(
            row=row, column=0, sticky="w", padx=(0, 10), pady=4
        )

        ent = tk.Entry(parent, textvariable=var, font=FONT_BODY,
                       bg=UI["surface"], fg=UI["text"], insertbackground=UI["text"], width=width)
        ent.grid(row=row, column=1, sticky="ew", pady=4)

        if browse:
            def do_browse():
                p = filedialog.askopenfilename() if browse_kind == "file" else filedialog.askdirectory()
                if p:
                    var.set(p)
            tk.Button(parent, text="Browse", font=FONT_BODY, bg=UI["panel"], fg=UI["text"], relief="flat", command=do_browse).grid(
                row=row, column=2, padx=6
            )

    def _update_editor_llm_endpoint(self):
        provider = (self.var_provider.get() or "").strip().lower()
        if provider == "ollama":
            default_endpoint = "http://127.0.0.1:11434/api/generate"
            current = (self.var_endpoint.get() or "").strip().lower()
            if not current or any(k in current for k in ["anthropic", "openai", "google", "gemini", "claude"]):
                self.var_endpoint.set(default_endpoint)

    # -----------------------------
    # Tabs
    # -----------------------------
    def _build_station_tab(self):
        wrap = tk.Frame(self.tab_station, bg=UI["bg"])
        wrap.pack(fill="both", expand=True, padx=14, pady=14)

        tk.Label(wrap, text="Station Metadata", font=FONT_H2, fg=UI["text"], bg=UI["bg"]).grid(
            row=0, column=0, sticky="w", pady=(0, 10), columnspan=2
        )

        self.var_name = tk.StringVar(value=str(self._cfg_get(["station", "name"], self.station.station_id)))
        self.var_host = tk.StringVar(value=str(self._cfg_get(["station", "host"], "Kai")))
        self.var_cat  = tk.StringVar(value=str(self._cfg_get(["station", "category"], "Custom")))
        self.var_logo = tk.StringVar(value=str(self._cfg_get(["station", "logo"], "")))
        self.var_meta_plugin = tk.StringVar(value=str(self._cfg_get(["meta_plugin"], "radio_station")))

        self._row_entry(wrap, 1, "Name", self.var_name)
        self._row_entry(wrap, 2, "Lead Character Name", self.var_host)
        self._row_entry(wrap, 3, "Category", self.var_cat)
        self._row_entry(wrap, 4, "Logo Art", self.var_logo, browse=True, browse_kind="file")
        
        # Meta Plugin selector
        tk.Label(wrap, text="Meta Plugin", font=FONT_BODY, fg=UI["muted"], bg=UI["bg"]).grid(
            row=5, column=0, sticky="w", padx=(0, 10), pady=6
        )
        meta_plugins = discover_meta_plugins()
        meta_combo = ttk.Combobox(
            wrap, textvariable=self.var_meta_plugin,
            values=meta_plugins,
            state="readonly", width=30
        )
        meta_combo.grid(row=5, column=1, sticky="w", pady=6)
        tk.Label(wrap, text="Core AI behavior controller", font=FONT_SMALL, fg=UI["muted"], bg=UI["bg"]).grid(
            row=5, column=2, sticky="w", padx=(10, 0)
        )

        wrap.grid_columnconfigure(1, weight=1)

        # Add Save button for station settings
        btn_row = tk.Frame(wrap, bg=UI["bg"])
        btn_row.grid(row=6, column=0, columnspan=3, sticky="e", pady=(16, 0))
        tk.Button(
            btn_row,
            text="Save Settings",
            font=FONT_BODY,
            bg=UI["accent"],
            fg="#000",
            relief="flat",
            command=self._quick_save_station_settings
        ).pack(side="right", padx=6)

    def _quick_save_station_settings(self):
        """Save only station metadata (name, host, category, logo, meta_plugin) without touching other config."""
        self._cfg_set(["station", "name"], self.var_name.get())
        self._cfg_set(["station", "host"], self.var_host.get())
        self._cfg_set(["station", "category"], self.var_cat.get())
        self._cfg_set(["station", "logo"], self.var_logo.get())
        self._cfg_set(["meta_plugin"], self.var_meta_plugin.get())
        self._write_manifest()
        messagebox.showinfo("Success", "Station settings saved!")

    def _build_models_tab(self):
        wrap = tk.Frame(self.tab_models, bg=UI["bg"])
        wrap.pack(fill="both", expand=True, padx=14, pady=14)

        tk.Label(wrap, text="LLM / Models", font=FONT_H2, fg=UI["text"], bg=UI["bg"]).grid(
            row=0, column=0, sticky="w", pady=(0, 10), columnspan=3
        )

        self.var_endpoint   = tk.StringVar(value=str(self._cfg_get(["llm", "endpoint"], "")))
        self.var_model_host = tk.StringVar(value=str(self._cfg_get(["models", "host"], "")))
        self.var_model_prod = tk.StringVar(value=str(self._cfg_get(["models", "producer"], "")))
        self.var_model_nav  = tk.StringVar(value=str(self._cfg_get(["models", "navigator"], "")))
        self.var_model_char_mgr = tk.StringVar(value=str(self._cfg_get(["models", "character_manager"], "")))
        self.var_model_embedding = tk.StringVar(value=str(self._cfg_get(["models", "embedding"], "")))
        self.var_embedding_enabled = tk.BooleanVar(value=bool(self._cfg_get(["embedding", "enabled"], False)))
        
        # Detect provider from existing config
        endpoint = self._cfg_get(["llm", "endpoint"], "")
        provider = "ollama"
        if "anthropic" in str(endpoint).lower() or "claude" in str(self._cfg_get(["models", "host"], "")).lower():
            provider = "anthropic"
        elif "openai" in str(endpoint).lower() or "gpt" in str(self._cfg_get(["models", "host"], "")).lower():
            provider = "openai"
        elif "google" in str(endpoint).lower() or "gemini" in str(self._cfg_get(["models", "host"], "")).lower():
            provider = "google"
        
        self.var_provider = tk.StringVar(value=provider)

        # Provider selector
        tk.Label(wrap, text="LLM Provider", font=FONT_BODY, fg=UI["muted"], bg=UI["bg"]).grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=4
        )
        provider_combo = ttk.Combobox(
            wrap, textvariable=self.var_provider,
            values=["ollama", "anthropic", "openai", "google"],
            state="readonly", width=30
        )
        provider_combo.grid(row=1, column=1, sticky="ew", pady=4)
        provider_combo.bind("<<ComboboxSelected>>", lambda e: self._update_editor_llm_endpoint())
        
        # Endpoint row
        endpoint_label = tk.Label(wrap, text="Endpoint / API", font=FONT_BODY, fg=UI["muted"], bg=UI["bg"])
        endpoint_label.grid(row=2, column=0, sticky="w", padx=(0, 10), pady=4)
        
        tk.Entry(wrap, textvariable=self.var_endpoint, bg=UI["surface"], fg=UI["text"],
                insertbackground=UI["text"], width=60).grid(row=2, column=1, sticky="ew", pady=4)
        
        hint_text = "Ollama: http://localhost:11434  |  Others: Set env var"
        tk.Label(wrap, text=hint_text, font=FONT_SMALL, fg=UI["muted"], bg=UI["bg"]).grid(
            row=2, column=2, sticky="w", padx=(10, 0)
        )

        self._update_editor_llm_endpoint()
        
        self._row_entry(wrap, 3, "Interpreter model (host key)", self.var_model_host, width=60)
        self._row_entry(wrap, 4, "Curator model (producer key)", self.var_model_prod, width=60)
        self._row_entry(wrap, 5, "Navigator model", self.var_model_nav, width=60)
        self._row_entry(wrap, 6, "Character Manager model", self.var_model_char_mgr, width=60)
        self._row_entry(wrap, 7, "Embedding model (optional)", self.var_model_embedding, width=60)

        tk.Checkbutton(
            wrap,
            text="Enable embeddings (global)",
            variable=self.var_embedding_enabled,
            bg=UI["bg"], fg=UI["text"],
            selectcolor=UI["panel"],
            activebackground=UI["bg"],
            activeforeground=UI["accent"],
        ).grid(row=8, column=1, sticky="w", pady=4)

        ttk.Separator(wrap, orient="horizontal").grid(row=9, column=0, columnspan=3, sticky="ew", pady=12)

        # Visual Models section
        tk.Label(wrap, text="Vision Model (Optional)", font=FONT_H2, fg=UI["text"], bg=UI["bg"]).grid(
            row=10, column=0, sticky="w", pady=(0, 10), columnspan=3
        )

        # Load visual model config from manifest or global settings
        vis_cfg = self._cfg_get(["visual_models"], {})
        if not isinstance(vis_cfg, dict) or not vis_cfg:
            global_cfg = get_global_config()
            vis_cfg = global_cfg.get("visual_models", {})

        self.var_vis_model_type = tk.StringVar(value=vis_cfg.get("model_type", "local"))
        self.var_vis_model_local = tk.StringVar(value=vis_cfg.get("local_model", ""))
        self.var_vis_model_api_provider = tk.StringVar(value=vis_cfg.get("api_provider", "openai"))
        self.var_vis_model_api_model = tk.StringVar(value=vis_cfg.get("api_model", "gpt-4-vision"))
        self.var_vis_model_max_size = tk.StringVar(value=vis_cfg.get("max_image_size", "1024"))

        # Model type selection
        tk.Label(wrap, text="Model Type", font=FONT_BODY, fg=UI["muted"], bg=UI["bg"]).grid(
            row=11, column=0, sticky="w", padx=(0, 10), pady=4
        )
        type_frame = tk.Frame(wrap, bg=UI["bg"])
        type_frame.grid(row=11, column=1, sticky="w", pady=4, columnspan=2)

        tk.Radiobutton(type_frame, text="Local", variable=self.var_vis_model_type, value="local",
                       fg=UI["text"], bg=UI["bg"], selectcolor=UI["accent"]).pack(side="left", padx=8)
        tk.Radiobutton(type_frame, text="API", variable=self.var_vis_model_type, value="api",
                       fg=UI["text"], bg=UI["bg"], selectcolor=UI["accent"]).pack(side="left", padx=8)

        self._row_entry(wrap, 10, "Local model", self.var_vis_model_local, width=60)
        self._row_entry(wrap, 11, "API provider", self.var_vis_model_api_provider, width=60)
        self._row_entry(wrap, 12, "API model", self.var_vis_model_api_model, width=60)
        self._row_entry(wrap, 13, "Max image width", self.var_vis_model_max_size, width=60)
        
        # Quick save button for visual models
        vis_btn_row = tk.Frame(wrap, bg=UI["bg"])
        vis_btn_row.grid(row=13, column=2, sticky="e", pady=(8, 4))
        tk.Button(vis_btn_row, text="Save", bg=UI["accent"], fg="#000", relief="flat",
                 command=self._quick_save_visual_models, font=FONT_SMALL).pack()

        ttk.Separator(wrap, orient="horizontal").grid(row=14, column=0, columnspan=3, sticky="ew", pady=12)

        tk.Label(wrap, text="Audio / Voices", font=FONT_H2, fg=UI["text"], bg=UI["bg"]).grid(
            row=15, column=0, sticky="w", pady=(0, 10), columnspan=3
        )

        self.var_piper = tk.StringVar(value=str(self._cfg_get(["audio", "piper_bin"], "")))
        self._row_entry(wrap, 16, "Piper binary", self.var_piper, width=60, browse=True, browse_kind="file")

        voices = self._cfg_get(["voices"], {})
        if not isinstance(voices, dict):
            voices = {}

        # explicit keys matching your manifest
        chars = self._cfg_get(["characters"], {})
        if not isinstance(chars, dict):
            chars = {}

        voice_keys = sorted(chars.keys())

        self.voice_vars: Dict[str, tk.StringVar] = {}
        r = 17
        for k in voice_keys:
            v = tk.StringVar(value=str(voices.get(k, "")))
            self.voice_vars[k] = v
            self._row_entry(wrap, r, f"Voice: {k}", v, width=60, browse=True, browse_kind="file")
            r += 1

        wrap.grid_columnconfigure(1, weight=1)

    def _build_feeds_tab(self):
        wrap = tk.Frame(self.tab_feeds, bg=UI["bg"])
        wrap.pack(fill="both", expand=True, padx=12, pady=12)

        tk.Label(
            wrap, text="Feeds",
            font=FONT_H2, fg=UI["text"], bg=UI["bg"]
        ).pack(anchor="w", pady=(0, 10))

        feeds = self._cfg_get(["feeds"], {})
        if not isinstance(feeds, dict):
            feeds = {}

        nb = ttk.Notebook(wrap)
        nb.pack(fill="both", expand=True)

        for fname in sorted(feeds.keys()):
            feed_cfg = feeds[fname]
            if not isinstance(feed_cfg, dict):
                feed_cfg = {}

            tab = tk.Frame(nb, bg=UI["bg"])
            nb.add(tab, text=fname)

            # Make each feed tab scrollable
            canvas_outer = tk.Frame(tab, bg=UI["bg"])
            canvas_outer.pack(fill="both", expand=True)

            canvas = tk.Canvas(canvas_outer, bg=UI["bg"], highlightthickness=0)
            canvas.pack(side="left", fill="both", expand=True)

            vsb = ttk.Scrollbar(canvas_outer, orient="vertical", command=canvas.yview)
            vsb.pack(side="right", fill="y")
            canvas.configure(yscrollcommand=vsb.set)

            body = tk.Frame(canvas, bg=UI["bg"])
            body_window = canvas.create_window((0, 0), window=body, anchor="nw")

            def make_configure_handlers(c=canvas, b=body, w=body_window):
                def _on_body_configure(_e=None):
                    c.configure(scrollregion=c.bbox("all"))
                def _on_canvas_configure(e):
                    c.itemconfigure(w, width=e.width)
                return _on_body_configure, _on_canvas_configure

            on_body_cfg, on_canvas_cfg = make_configure_handlers()
            body.bind("<Configure>", on_body_cfg)
            canvas.bind("<Configure>", on_canvas_cfg)

            # Mousewheel scrolling
            def make_scroll_handler(c=canvas):
                def _wheel(e):
                    delta = 0
                    try:
                        if sys.platform == "darwin":
                            delta = int(-1 * e.delta)
                        else:
                            delta = int(-1 * (e.delta / 120))
                    except Exception:
                        pass
                    if delta:
                        c.yview_scroll(delta, "units")
                return _wheel

            wheel_handler = make_scroll_handler()

            def bind_wheel(_e, c=canvas, h=wheel_handler):
                c.bind("<MouseWheel>", h)
                if sys.platform.startswith("linux"):
                    c.bind("<Button-4>", lambda e: c.yview_scroll(-1, "units"))
                    c.bind("<Button-5>", lambda e: c.yview_scroll(1, "units"))

            def unbind_wheel(_e, c=canvas):
                c.unbind("<MouseWheel>")
                if sys.platform.startswith("linux"):
                    c.unbind("<Button-4>")
                    c.unbind("<Button-5>")

            canvas.bind("<Enter>", bind_wheel)
            canvas.bind("<Leave>", unbind_wheel)

            # Add padding to body
            tk.Frame(body, bg=UI["bg"], height=14).pack()
            content = tk.Frame(body, bg=UI["bg"])
            content.pack(fill="both", expand=True, padx=14)
            body = content  # Continue using body for the rest of the code

            # ==========================
            # ENABLED TOGGLE
            # ==========================

            enabled = bool(feed_cfg.get("enabled", False))
            v_en = tk.BooleanVar(value=enabled)

            row = tk.Frame(body, bg=UI["bg"])
            row.pack(anchor="w", pady=6)

            tk.Checkbutton(
                row,
                text="Enabled",
                variable=v_en,
                bg=UI["bg"], fg=UI["text"],
                selectcolor=UI["bg"]
            ).pack(side="left")

            # dynamic storage for this feed
            keybase = f"feeds.{fname}"
            self._dynamic_vars[keybase] = {"enabled": v_en}

            # ==========================
            # EXISTING FIELDS
            # ==========================

            for k, v in feed_cfg.items():
                if k == "enabled":
                    continue

                line = tk.Frame(body, bg=UI["bg"])
                line.pack(fill="x", pady=6)

                tk.Label(
                    line, text=k,
                    fg=UI["muted"], bg=UI["bg"],
                    width=22, anchor="w"
                ).pack(side="left")

                if isinstance(v, list):
                    sv = tk.StringVar(value=json.dumps(v, ensure_ascii=False))
                else:
                    sv = tk.StringVar(value=str(v))

                ent = tk.Entry(
                    line,
                    textvariable=sv,
                    bg=UI["surface"], fg=UI["text"],
                    insertbackground=UI["text"]
                )
                ent.pack(fill="x", expand=True)

                self._dynamic_vars[keybase][k] = sv

            # ==========================
            # ADD NEW FIELD UI
            # ==========================

            ttk.Separator(body, orient="horizontal").pack(fill="x", pady=14)

            add_row = tk.Frame(body, bg=UI["bg"])
            add_row.pack(fill="x", pady=(6, 4))

            new_key = tk.StringVar()
            new_val = tk.StringVar()

            tk.Entry(
                add_row,
                textvariable=new_key,
                bg=UI["surface"], fg=UI["text"],
                insertbackground=UI["text"],
                width=22
            ).pack(side="left", padx=(0, 6))

            tk.Entry(
                add_row,
                textvariable=new_val,
                bg=UI["surface"], fg=UI["text"],
                insertbackground=UI["text"]
            ).pack(side="left", fill="x", expand=True, padx=(0, 6))

            def add_field(fname=fname, k_var=new_key, v_var=new_val, body_ref=body):
                k = (k_var.get() or "").strip()
                raw = (v_var.get() or "").strip()

                if not k:
                    return

                keybase = f"feeds.{fname}"

                # Smart parse YAML/JSON
                try:
                    parsed = yaml.safe_load(raw)
                except Exception:
                    parsed = raw

                if isinstance(parsed, list):
                    sv = tk.StringVar(value=json.dumps(parsed, ensure_ascii=False))
                else:
                    sv = tk.StringVar(value=str(parsed))

                # New visual row
                line = tk.Frame(body_ref, bg=UI["bg"])
                line.pack(fill="x", pady=6)

                tk.Label(
                    line, text=k,
                    fg=UI["muted"], bg=UI["bg"],
                    width=22, anchor="w"
                ).pack(side="left")

                ent = tk.Entry(
                    line,
                    textvariable=sv,
                    bg=UI["surface"], fg=UI["text"],
                    insertbackground=UI["text"]
                )
                ent.pack(fill="x", expand=True)

                self._dynamic_vars[keybase][k] = sv

                k_var.set("")
                v_var.set("")

            tk.Button(
                add_row,
                text="Add Field",
                bg=UI["panel"], fg=UI["accent"],
                relief="flat",
                command=add_field
            ).pack(side="left")


    def _build_chars_tab(self):
        wrap = tk.Frame(self.tab_chars, bg=UI["bg"])
        wrap.pack(fill="both", expand=True, padx=14, pady=14)

        tk.Label(
            wrap, text="Characters",
            font=FONT_H2, fg=UI["text"], bg=UI["bg"]
        ).pack(anchor="w", pady=(0, 10))

        body = tk.Frame(wrap, bg=UI["bg"])
        body.pack(fill="both", expand=True)

        # ============================
        # LEFT PANEL (LIST + BUTTONS)
        # ============================

        left = tk.Frame(body, bg=UI["panel"], width=int(240 * UI_SCALE))
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        self.char_list = tk.Listbox(
            left,
            bg=UI["surface"],
            fg=UI["text"],
            font=FONT_BODY,
            relief="flat",
            exportselection=False
        )
        self.char_list.pack(fill="both", expand=True, padx=10, pady=10)

        btns = tk.Frame(left, bg=UI["panel"])
        btns.pack(fill="x", padx=10, pady=(0, 10))

        tk.Button(
            btns, text="Add",
            bg=UI["panel"], fg=UI["text"], relief="flat",
            command=self._char_add_safe
        ).pack(side="left", padx=4)

        tk.Button(
            btns, text="Remove",
            bg=UI["panel"], fg=UI["danger"], relief="flat",
            command=self._char_remove_safe
        ).pack(side="left", padx=4)

        tk.Button(
            btns, text="Load Preset",
            bg=UI["panel"], fg=UI["accent"], relief="flat",
            command=self._load_character_preset
        ).pack(side="left", padx=4)

        # ============================
        # LOAD EXISTING CHARACTERS
        # ============================

        chars = self._cfg_get(["characters"], {})
        if not isinstance(chars, dict):
            chars = {}

        self._chars = chars

        self.char_list.delete(0, "end")
        for k in sorted(self._chars.keys()):
            self.char_list.insert("end", k)

        self.char_list.bind("<<ListboxSelect>>", self._char_load_selected_safe)

        # ============================
        # RIGHT PANEL (EDITOR)
        # ============================

        right = tk.Frame(body, bg=UI["bg"])
        right.pack(side="left", fill="both", expand=True, padx=(12, 0))

        self.var_char_role   = tk.StringVar()
        self.var_char_traits = tk.StringVar()
        self.var_char_focus  = tk.StringVar()

        tk.Label(right, text="Role", fg=UI["muted"], bg=UI["bg"]).pack(anchor="w")
        tk.Entry(
            right, textvariable=self.var_char_role,
            bg=UI["surface"], fg=UI["text"],
            insertbackground=UI["text"]
        ).pack(fill="x", pady=(0, 10))

        tk.Label(right, text="Traits (list)", fg=UI["muted"], bg=UI["bg"]).pack(anchor="w")
        tk.Entry(
            right, textvariable=self.var_char_traits,
            bg=UI["surface"], fg=UI["text"],
            insertbackground=UI["text"]
        ).pack(fill="x", pady=(0, 10))

        tk.Label(right, text="Focus (list)", fg=UI["muted"], bg=UI["bg"]).pack(anchor="w")
        tk.Entry(
            right, textvariable=self.var_char_focus,
            bg=UI["surface"], fg=UI["text"],
            insertbackground=UI["text"]
        ).pack(fill="x", pady=(0, 10))
        
        # ---- Context Engine UI ----
        
        from context_engine_ui import build_context_engine_ui
        
        # Store context engine config per character
        if not hasattr(self, "_char_context_engines"):
            self._char_context_engines = {}
        
        def get_context_cfg():
            sel = self.char_list.curselection()
            if not sel:
                return {}
            key = self.char_list.get(sel[0])
            return self._char_context_engines.get(key, {})
        
        def set_context_cfg(cfg):
            sel = self.char_list.curselection()
            if sel:
                key = self.char_list.get(sel[0])
                self._char_context_engines[key] = cfg
        
        self.context_engine_frame = build_context_engine_ui(
            parent=right,
            bg=UI["bg"],
            surface=UI["surface"],
            text_color=UI["text"],
            muted=UI["muted"],
            accent=UI["accent"],
            get_context_cfg_func=get_context_cfg,
            set_context_cfg_func=set_context_cfg,
            station_dir=self.station_dir
        )
        self.context_engine_frame.pack(fill="x", pady=10)

        tk.Button(
            right,
            text="Apply Changes",
            bg=UI["accent"], fg="#000", relief="flat",
            command=self._char_apply_safe
        ).pack(anchor="w", pady=10)

        # ============================
        # AUTO SELECT FIRST
        # ============================

        if self.char_list.size() > 0:
            self.char_list.selection_set(0)
            self._char_load_selected_safe()

    # -----------------------------
    # Character ops
    # -----------------------------
    def _load_character_preset(self):
        win = tk.Toplevel(self.win)
        win.title("Load Character Preset")
        win.geometry(scaled_geometry(320, 340))
        win.configure(bg=UI["bg"])
        win.grab_set()

        tk.Label(
            win, text="Choose preset",
            fg=UI["text"], bg=UI["bg"],
            font=FONT_BODY
        ).pack(pady=10)

        lb = tk.Listbox(
            win,
            bg=UI["surface"],
            fg=UI["text"],
            font=FONT_BODY,
            relief="flat"
        )
        lb.pack(fill="both", expand=True, padx=12, pady=6)

        for name in CHARACTER_PRESETS.keys():
            lb.insert("end", name)

        def load():
            sel = lb.curselection()
            if not sel:
                return

            preset_name = lb.get(sel[0])
            preset = CHARACTER_PRESETS[preset_name]

            if not messagebox.askyesno(
                "Overwrite Characters",
                f"Load '{preset_name}' preset?\n\nThis will replace current characters."
            ):
                return

            # Inject
            self._chars.clear()
            self._chars.update(json.loads(json.dumps(preset)))  # deep copy

            # Refresh list UI
            self.char_list.delete(0, "end")
            for k in sorted(self._chars.keys()):
                self.char_list.insert("end", k)

            if self.char_list.size() > 0:
                self.char_list.selection_set(0)
                self._char_load_selected_safe()

            win.destroy()

        tk.Button(
            win, text="Load",
            bg=UI["accent"], fg="#000", relief="flat",
            command=load
        ).pack(pady=10)

    def _char_selected_key(self):
        sel = self.char_list.curselection()
        if not sel:
            return None
        return self.char_list.get(sel[0])


    def _char_load_selected_safe(self, evt=None):
        key = self._char_selected_key()
        if not key:
            return

        c = self._chars.get(key, {})
        if not isinstance(c, dict):
            return

        self.var_char_role.set(str(c.get("role", "")))
        self.var_char_traits.set(json.dumps(c.get("traits", []), ensure_ascii=False))
        self.var_char_focus.set(json.dumps(c.get("focus", []), ensure_ascii=False))
        
        # Load context engine config
        if hasattr(self, "context_engine_frame"):
            context_cfg = c.get("context_engine", {})
            self.context_engine_frame.load_config(context_cfg)
            if hasattr(self, "_char_context_engines"):
                self._char_context_engines[key] = context_cfg


    def _char_add_safe(self):
        name = self.shell._prompt_text("Add character", "Character key (e.g. analyst):")
        if not name:
            return

        name = name.strip().lower()

        if not name or name in self._chars:
            return

        self._chars[name] = {
            "role": name,
            "traits": [],
            "focus": []
        }

        self.char_list.insert("end", name)
        self.char_list.selection_clear(0, "end")
        self.char_list.selection_set("end")
        self._char_load_selected_safe()


    def _char_remove_safe(self):
        key = self._char_selected_key()
        if not key:
            return

        if key == "host":
            messagebox.showerror("Not allowed", "Lead voice key 'host' cannot be removed.")
            return

        if not messagebox.askyesno("Remove", f"Remove '{key}'?"):
            return

        idx = self.char_list.curselection()[0]

        self._chars.pop(key, None)
        self.char_list.delete(idx)

        if self.char_list.size() > 0:
            self.char_list.selection_set(0)
            self._char_load_selected_safe()


    def _char_apply_safe(self):
        key = self._char_selected_key()
        if not key:
            return

        try:
            role = self.var_char_role.get().strip()

            traits = parse_list_field(self.var_char_traits.get())
            focus  = parse_list_field(self.var_char_focus.get())

            # HARD GUARANTEE list type
            if not isinstance(traits, list):
                traits = []

            if not isinstance(focus, list):
                focus = []

            # Get context engine config
            context_engine = {}
            if hasattr(self, "context_engine_frame"):
                context_engine = self.context_engine_frame.get_config()
                if hasattr(self, "_char_context_engines"):
                    self._char_context_engines[key] = context_engine

            self._chars[key] = {
                "role": role,
                "traits": traits,
                "focus": focus
            }
            
            # Add context_engine if enabled
            if context_engine.get("enabled"):
                self._chars[key]["context_engine"] = context_engine


        except Exception as e:
            messagebox.showerror(
                "Character Error",
                f"Invalid traits/focus format.\n\n{e}\n\nUse JSON list like:\n[\"calm\", \"smart\"]"
            )

    def _select_list_item(self, key: str):
        for i in range(self.char_list.size()):
            if self.char_list.get(i) == key:
                self.char_list.selection_clear(0, "end")
                self.char_list.selection_set(i)
                self.char_list.see(i)
                self._char_load_selected_safe()  # FIX: correct method
                return


    def _char_apply(self):
        key = self._char_selected_key()
        if not key:
            return

        role = (self.var_char_role.get() or "").strip()
        traits = parse_list_field(self.var_char_traits.get())
        focus = parse_list_field(self.var_char_focus.get())

        self._chars[key] = {"role": role, "traits": traits, "focus": focus}
        messagebox.showinfo("Saved", f"{key} updated.")

    # -----------------------------
    # Footer
    # -----------------------------
    def _build_footer(self):
        footer = tk.Frame(self.win, bg=UI["bg"])
        footer.pack(fill="x", padx=12, pady=(0, 12))

        tk.Button(footer, text="Save", font=FONT_BODY, bg=UI["accent"], fg="#000", relief="flat", command=self.save).pack(
            side="right", padx=6
        )
        tk.Button(footer, text="Close", font=FONT_BODY, bg=UI["panel"], fg=UI["text"], relief="flat", command=self.win.destroy).pack(
            side="right", padx=6
        )
        tk.Button(footer, text="Duplicate Station…", font=FONT_BODY, bg=UI["panel"], fg=UI["text"], relief="flat", command=self.duplicate_station).pack(
            side="left", padx=6
        )
        tk.Button(footer, text="Open Folder…", font=FONT_BODY, bg=UI["panel"], fg=UI["text"], relief="flat", command=self.open_folder).pack(
            side="left", padx=6
        )

    def open_folder(self):
        try:
            if sys.platform == "win32":
                os.startfile(self.path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", self.path])
            else:
                subprocess.Popen(["xdg-open", self.path])
        except Exception:
            pass

    def _quick_save_visual_models(self):
        """Save only visual model settings without touching other config."""
        self._cfg_set(["visual_models", "model_type"], self.var_vis_model_type.get())
        self._cfg_set(["visual_models", "local_model"], self.var_vis_model_local.get())
        self._cfg_set(["visual_models", "api_provider"], self.var_vis_model_api_provider.get())
        self._cfg_set(["visual_models", "api_model"], self.var_vis_model_api_model.get())
        self._cfg_set(["visual_models", "max_image_size"], self.var_vis_model_max_size.get())
        
        self._write_manifest()
        messagebox.showinfo("Success", "Visual model settings saved!")
    
    def _write_manifest(self):
        """Write the manifest to disk."""
        try:
            with open(self.mp, "w", encoding="utf-8") as f:
                yaml.safe_dump(self.cfg, f, sort_keys=False, allow_unicode=True)
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to write manifest: {e}")

    def duplicate_station(self):
        new_id = self.shell._prompt_text("Duplicate Station", "New station id:")
        if not new_id:
            return
        new_id = new_id.strip()
        if not new_id:
            return

        dst = os.path.join(STATIONS_DIR, new_id)
        if os.path.exists(dst):
            messagebox.showerror("Exists", "That station id already exists.")
            return

        shutil.copytree(self.path, dst)
        self.shell.refresh_stations(select_id=new_id)

    # -----------------------------
    # Save manifest (FULL FIX: do not wipe feeds/pacing, no missing vars)
    # -----------------------------
    def save(self):
        # Station metadata
        self._cfg_set(["station", "name"], self.var_name.get())
        self._cfg_set(["station", "host"], self.var_host.get())
        self._cfg_set(["station", "category"], self.var_cat.get())
        self._cfg_set(["station", "logo"], self.var_logo.get())
        self._cfg_set(["meta_plugin"], self.var_meta_plugin.get())

        # LLM / models
        self._cfg_set(["llm", "endpoint"], self.var_endpoint.get())
        self._cfg_set(["llm", "provider"], self.var_provider.get())
        self._cfg_set(["models", "host"], self.var_model_host.get())
        self._cfg_set(["models", "producer"], self.var_model_prod.get())
        self._cfg_set(["models", "navigator"], self.var_model_nav.get())
        self._cfg_set(["models", "character_manager"], self.var_model_char_mgr.get())
        self._cfg_set(["models", "embedding"], self.var_model_embedding.get())
        self._cfg_set(["embedding", "enabled"], bool(self.var_embedding_enabled.get()))

        # Visual Models
        self._cfg_set(["visual_models", "model_type"], self.var_vis_model_type.get())
        self._cfg_set(["visual_models", "local_model"], self.var_vis_model_local.get())
        self._cfg_set(["visual_models", "api_provider"], self.var_vis_model_api_provider.get())
        self._cfg_set(["visual_models", "api_model"], self.var_vis_model_api_model.get())
        self._cfg_set(["visual_models", "max_image_size"], self.var_vis_model_max_size.get())

        # Audio / voices
        self._cfg_set(["audio", "piper_bin"], self.var_piper.get())
        self.cfg.setdefault("voices", {})
        if not isinstance(self.cfg.get("voices"), dict):
            self.cfg["voices"] = {}
        for k, v in self.voice_vars.items():
            self.cfg["voices"][k] = v.get()

        # Characters edited in-place
        self.cfg["characters"] = self._chars

        # Dynamic sections merge (scheduler/riff/pacing/producer/host/tts/feeds.*)
        for keybase, fields in self._dynamic_vars.items():
            path = keybase.split(".")
            current = self._cfg_get(path, {})
            if not isinstance(current, dict):
                current = {}

            for k, var in fields.items():
                # booleans
                if isinstance(var, tk.BooleanVar):
                    current[k] = bool(var.get())
                    continue

                raw = str(var.get() or "").strip()

                # Detect original type if present
                try:
                    orig = self._cfg_get(path + [k], None)
                except Exception:
                    orig = None

                # If it USED to be a list, force list parse
                if isinstance(orig, list):
                    current[k] = parse_list_field(raw)
                    continue

                # If user typed a list-looking thing for a NEW field, parse as list too
                # - starts with [ ... ]  (JSON/YAML list)
                # - or contains commas and no obvious dict/brace structure
                looks_like_list = (
                    (raw.startswith("[") and raw.endswith("]")) or
                    ("," in raw and not any(ch in raw for ch in "{}:"))
                )
                if looks_like_list:
                    current[k] = parse_list_field(raw)
                    continue

                # Otherwise YAML/JSON scalar parse
                if raw == "":
                    current[k] = ""
                    continue

                try:
                    v = yaml.safe_load(raw)
                    current[k] = v
                except Exception:
                    current[k] = parse_scalar_field(raw)

            self._cfg_set(path, current)

        # Write manifest
        safe_write_yaml(self.mp, self.cfg)

        # Refresh shell UI
        self.shell.refresh_stations(select_id=self.station.station_id)


# ═══════════════════════════════════════════════════════════════════════════
# Headless Shell — runtime-first boot (no tkinter)
# ═══════════════════════════════════════════════════════════════════════════
class HeadlessShell:
    """
    Lightweight process manager that runs the station runtime, web server,
    and Audio CLI without any graphical UI.  This is the default boot path.
    """

    def __init__(self, *, launch_web: bool = False):
        import threading, signal

        self._stop = threading.Event()
        self.proc = StationProcess()
        self.stations: List[StationInfo] = load_stations()
        self._web_thread = None
        self._web_stop = None
        self._web_url = None
        self._audio_cli_session = None
        self._launch_web = launch_web
        self._plugins: Optional[Dict[str, Dict[str, Any]]] = None

        # Graceful shutdown on SIGINT / SIGTERM
        signal.signal(signal.SIGINT, lambda *_: self._shutdown())
        signal.signal(signal.SIGTERM, lambda *_: self._shutdown())

    # ── helpers ──────────────────────────────────────────────────────────

    def _find_station(self, station_id: str) -> Optional[StationInfo]:
        for s in self.stations:
            if s.station_id == station_id:
                return s
        return None

    # ── plugin management (headless / web) ───────────────────────────────

    def get_plugins(self) -> Dict[str, Dict[str, Any]]:
        """Discover and cache available plugins."""
        if self._plugins is None:
            self._plugins = discover_plugins()
        return self._plugins

    def refresh_plugins(self) -> Dict[str, Dict[str, Any]]:
        """Re-discover plugins (invalidates cache)."""
        self._plugins = discover_plugins()
        return self._plugins

    def get_station_feeds(self, station_id: str) -> Dict[str, Any]:
        """Return feed config for a station, merged with plugin metadata."""
        station = self._find_station(station_id)
        if not station:
            return {}
        feeds_cfg = station.manifest.get("feeds", {}) or {}
        plugins = self.get_plugins()
        result: Dict[str, Any] = {}
        for name, cfg in feeds_cfg.items():
            if not isinstance(cfg, dict):
                cfg = {}
            meta = plugins.get(name, {})
            result[name] = {
                "enabled": bool(cfg.get("enabled", False)),
                "config": {k: v for k, v in cfg.items() if k != "enabled"},
                "plugin_display": meta.get("display", name),
                "plugin_desc": meta.get("desc", ""),
                "has_plugin": name in plugins,
            }
        # Available but not configured
        for name, meta in plugins.items():
            if name not in result and meta.get("is_feed", True):
                result[name] = {
                    "enabled": False,
                    "config": meta.get("defaults", {}) or {},
                    "plugin_display": meta.get("display", name),
                    "plugin_desc": meta.get("desc", ""),
                    "has_plugin": True,
                }
        return result

    def toggle_feed(self, station_id: str, feed_name: str, enabled: bool) -> bool:
        """Enable or disable a feed for a station. Returns True on success."""
        station = self._find_station(station_id)
        if not station:
            return False
        mp = station_manifest_path(station.path)
        cfg = safe_read_yaml(mp)
        feeds = cfg.setdefault("feeds", {})
        if feed_name not in feeds or not isinstance(feeds.get(feed_name), dict):
            plugins = self.get_plugins()
            defaults = (plugins.get(feed_name, {}).get("defaults") or {}).copy()
            feeds[feed_name] = defaults
        feeds[feed_name]["enabled"] = bool(enabled)
        safe_write_yaml(mp, cfg)
        station.manifest = cfg
        return True

    def update_feed_config(self, station_id: str, feed_name: str,
                           updates: Dict[str, Any]) -> bool:
        """Update config keys for a feed. Returns True on success."""
        station = self._find_station(station_id)
        if not station:
            return False
        mp = station_manifest_path(station.path)
        cfg = safe_read_yaml(mp)
        feeds = cfg.setdefault("feeds", {})
        if feed_name not in feeds or not isinstance(feeds.get(feed_name), dict):
            feeds[feed_name] = {}
        feeds[feed_name].update(updates)
        safe_write_yaml(mp, cfg)
        station.manifest = cfg
        return True

    def bulk_set_feeds(self, station_id: str,
                       feed_states: Dict[str, bool]) -> List[str]:
        """Enable/disable multiple feeds at once. Returns list of changed names."""
        station = self._find_station(station_id)
        if not station:
            return []
        mp = station_manifest_path(station.path)
        cfg = safe_read_yaml(mp)
        feeds = cfg.setdefault("feeds", {})
        plugins = self.get_plugins()
        changed = []
        for name, enabled in feed_states.items():
            if name not in feeds or not isinstance(feeds.get(name), dict):
                defaults = (plugins.get(name, {}).get("defaults") or {}).copy()
                feeds[name] = defaults
            feeds[name]["enabled"] = bool(enabled)
            changed.append(name)
        safe_write_yaml(mp, cfg)
        station.manifest = cfg
        return changed

    # ── web server ──────────────────────────────────────────────────────

    def _start_web_server(self):
        import threading
        try:
            from web_server import start_web_shell, WEB_SHELL_PORT
        except ImportError as e:
            print(f"[RadioOS] Web server unavailable: {e}")
            return

        self._web_stop = threading.Event()

        def _on_start(url):
            self._web_url = url

        cfg = get_global_config()
        port = int(cfg.get("general", {}).get("web_server_port", WEB_SHELL_PORT))

        self._web_thread = threading.Thread(
            target=start_web_shell,
            kwargs={
                "port": port,
                "stop_event": self._web_stop,
                "callback_on_start": _on_start,
            },
            daemon=True,
        )
        self._web_thread.start()
        print(f"[RadioOS] Web server starting on port {port} …")

    # ── audio CLI ───────────────────────────────────────────────────────

    def _start_audio_cli(self):
        try:
            from audio_cli import AudioCLISession

            acli_cfg = get_global_config().get("audio_cli", {})
            default_mode = acli_cfg.get("default_mode", "web")
            web_url = acli_cfg.get("web_url", "http://127.0.0.1:7800")

            if default_mode == "web" or self._launch_web:
                self._audio_cli_session = AudioCLISession(shell=None, web_url=web_url)
            else:
                # In headless mode without web, fall back to web mode anyway
                self._audio_cli_session = AudioCLISession(shell=None, web_url=web_url)

            self._audio_cli_session.start_listener()
            print("[RadioOS] Audio CLI listener started.")
        except Exception as e:
            print(f"[RadioOS] Audio CLI init failed: {e}")
            self._audio_cli_session = None

    # ── lifecycle ───────────────────────────────────────────────────────

    def _shutdown(self):
        print("\n[RadioOS] Shutting down …")
        self._stop.set()

        # Stop Audio CLI
        try:
            if self._audio_cli_session and self._audio_cli_session.is_running:
                self._audio_cli_session.stop_listener()
        except Exception:
            pass

        # Stop web server
        try:
            if self._web_stop:
                self._web_stop.set()
        except Exception:
            pass

        # Stop station process
        try:
            self.proc.stop()
        except Exception:
            pass

    def run(self):
        import time, webbrowser

        print(f"╔══════════════════════════════════════════════════╗")
        print(f"║  📻 Radio OS {RADIO_OS_VERSION}  —  headless runtime        ║")
        print(f"╚══════════════════════════════════════════════════╝")

        # 1. Start the web server (needed for Audio CLI web mode + remote control)
        self._start_web_server()

        # 2. If --web, open browser once server is ready
        if self._launch_web:
            cfg = get_global_config()
            try:
                from web_server import WEB_SHELL_PORT
            except ImportError:
                WEB_SHELL_PORT = 7800
            port = int(cfg.get("general", {}).get("web_server_port", WEB_SHELL_PORT))
            url = f"http://127.0.0.1:{port}"

            def _open_browser():
                import time as _t
                _t.sleep(1.5)  # give server a moment to bind
                webbrowser.open(url)
                print(f"[RadioOS] Opened {url} in default browser.")

            import threading
            threading.Thread(target=_open_browser, daemon=True).start()

        # 3. Start Audio CLI listener
        self._start_audio_cli()

        print("[RadioOS] Running. Launch stations via web UI or Audio CLI.")
        print("[RadioOS] Press Ctrl-C to stop.")
        print()

        # 5. Block until stopped
        try:
            while not self._stop.is_set():
                # Check for station switch requests (same logic as desktop _tick)
                self._check_station_switch()
                self._stop.wait(timeout=1.0)
        except KeyboardInterrupt:
            pass
        finally:
            self._shutdown()

    def _check_station_switch(self):
        """Mirror RadioShell._check_station_switch for headless mode."""
        if not self.proc or not self.proc.proc:
            return
        ret = self.proc.proc.poll()
        if ret == 20:
            try:
                rq_path = os.path.join(BASE, ".switch_request")
                if os.path.exists(rq_path):
                    with open(rq_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    try:
                        os.remove(rq_path)
                    except Exception:
                        pass
                    target_id = data.get("station_id")
                    if target_id:
                        print(f"[RadioOS] Switching to station: {target_id}")
                        self.proc.stop()
                        st = self._find_station(target_id)
                        if st:
                            self.proc.launch(st)
                        else:
                            print(f"[RadioOS] Station {target_id} not found.")
            except Exception as e:
                print(f"[RadioOS] Switch failed: {e}")


# -----------------------------
# Entrypoint
# -----------------------------
class _SettingsHost(RadioShell):
    """A RadioShell stand-in for the settings-only window — enough state to build every settings
    tab without booting the whole desktop. The kernel (Bookmark) launches this via --settings so
    it can edit the shared global RadioOS config from within, reusing the real settings code as-is.
    """

    def __init__(self, root):
        self.root = root
        self.stations = {}
        self._focused_station = None
        try:
            self.proc = StationProcess()
        except Exception:
            self.proc = None

    def __getattr__(self, name):  # safety net for any unset instance attr a tab build touches
        if name.startswith("__"):
            raise AttributeError(name)
        return lambda *a, **k: None


def run_settings_only():
    """Open ONLY the settings window (shared global config). Used by the kernel's Settings entry."""
    root = tk.Tk()
    root.title("Radio OS — Settings")
    root.withdraw()  # the settings Toplevel is the visible window
    host = _SettingsHost(root)
    host.open_settings()
    for child in root.winfo_children():
        if isinstance(child, tk.Toplevel):
            child.protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Radio OS — runtime-first boot",
        epilog=(
            "Boot modes:\n"
            "  (default)   Headless — web server + Audio CLI, no window\n"
            "  --desktop   Launch the classic tkinter desktop shell\n"
            "  --web       Headless + open web UI in default browser\n"
            "  --settings  Open only the settings window (shared global config)\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--desktop", action="store_true",
                        help="Launch the tkinter desktop shell")
    parser.add_argument("--web", action="store_true",
                        help="Headless mode + open web UI in default browser")
    parser.add_argument("--settings", action="store_true",
                        help="Open only the settings window (for the kernel to edit global config)")
    args = parser.parse_args()

    if args.settings:
        # Settings-only window — the kernel opens this to edit global RadioOS settings.
        run_settings_only()
    elif args.desktop:
        # Classic tkinter desktop shell
        RadioShell().run()
    elif args.web:
        # Headless with web browser opened
        HeadlessShell(launch_web=True).run()
    else:
        # Default: fully headless — web server + Audio CLI, no window
        HeadlessShell(launch_web=False).run()
