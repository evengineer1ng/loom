"""The snap canvas — Scratch/Lego-style brick blocks that click together by type.

Bricks stack in a vertical column: producers on top, consumers below, data flowing down. A
matching packet-type between a block and the one above it is a *snapped seam* (drawn flush,
colored by the packet type so the mortar is legible). An input nothing supplies is an *open
socket* — a hole the Club resolves. The column order is the resolver's topological run order,
so the picture is always a valid execution order or shows exactly where it isn't.

This is the visual skin over :class:`bookmark.draft.DraftGraph`; it stores no connections of
its own — it renders whatever the resolver derives. Drag-to-rearrange is a later increment;
for now laying a brick appends it and the column re-resolves.

Standalone: ``python -m bookmark.canvas`` opens a mini-Bookmark (brick bar + snap canvas).
"""

from __future__ import annotations

import json
import tkinter as tk
from typing import Dict, List, Optional

from .brick_kernel import ATL_BRICKS, Brick, BrickRegistry, make_packet
from .draft import DraftGraph, PlacedBrick, Resolution

BG = "#0e0e0e"
# A DISTINCT authoring-surface palette so the canvas reads as its own space, not the same
# near-black as the top brick bar / bottom debug panels.
CANVAS_BG = "#0f1626"
CANVAS_EDGE = "#33507a"
GRID = "#16223a"
BLOCK = "#1b2733"
BLOCK_EDGE = "#2f4456"
TEXT = "#e6e6e6"
MUTED = "#8a8a8a"
HOLE = "#b85c5c"        # open socket / unmet input
SEL = "#f4c66b"         # selected-block highlight (gold)
LOOSE = "#7a6a3a"       # a seam that didn't snap (type mismatch / no producer above)
DET = "#3a6b4a"         # deterministic stripe
LIVE = "#7d5a2e"        # live / side-effecting stripe
FIELD_BG = "#162033"    # editable controls should read as inputs, not labels
FIELD_EDGE = "#35527a"

# A small fixed palette; packet types hash into it so a given type is always the same color.
SEAM_PALETTE = ["#4cc9f0", "#f0a14c", "#9b6cf0", "#4cf0a1", "#f04c9b", "#c9f04c", "#4c7af0", "#f0d24c"]

BLOCK_W = 210
BLOCK_H = 46
NUB_W = 26          # width of the snap tab
NUB_H = 7
COL_X = 40          # left margin of the column
TOP_Y = 30
SNAP_GAP = 0        # bonded blocks sit flush
LOOSE_GAP = 16      # unbonded blocks leave a visible gap


def _seam_color(packet_type: str) -> str:
    return SEAM_PALETTE[hash(packet_type) % len(SEAM_PALETTE)]


def _coerce_param_value(param: Dict, raw: str):
    ptype = str(param.get("type", "string") or "string").strip().lower()
    if ptype == "int":
        try:
            return int(raw)
        except Exception:
            return int(param.get("default", 0) or 0)
    if ptype == "float":
        try:
            return float(raw)
        except Exception:
            return float(param.get("default", 0.0) or 0.0)
    if ptype == "bool":
        return str(raw).strip().lower() in {"1", "true", "yes", "on"}
    return raw


def _placement_payload(placed: PlacedBrick) -> Dict:
    payload = dict(getattr(placed, "payload", {}) or {})
    for param in (getattr(placed.brick, "concept", {}) or {}).get("params", []) or []:
        name = param.get("name")
        if not name:
            continue
        if name in placed.config:
            value = placed.config[name]
            if isinstance(value, str) and not value.strip():
                continue
            payload[name] = value
    return payload


def _validate_placement(placed: PlacedBrick) -> List[Dict[str, str]]:
    packet_type = placed.brick.inputs[0] if getattr(placed.brick, "inputs", ()) else "brick.input.v1"
    packet = make_packet(packet_type, _placement_payload(placed))
    return list(placed.brick.validate(packet, context=None) or [])


class SnapCanvas(tk.Frame):
    """A vertical snap-column rendering of a DraftGraph."""

    def __init__(self, master, registry: BrickRegistry,
                 draft: Optional[DraftGraph] = None, **kw):
        super().__init__(master, bg=CANVAS_BG, highlightthickness=1,
                         highlightbackground=CANVAS_EDGE, **kw)
        self.registry = registry
        self.draft = draft if draft is not None else DraftGraph(registry)
        self.zoom = 1.0
        self.selected: Optional[str] = None       # instance_id of the selected block
        self._blocks: List = []                   # [(instance_id, x0, y0, x1, y1)] for hit-testing
        self._press_xy = None
        self._dragged = False
        # Optional callback fired after the draft changes (place/remove/move) so the host can
        # refresh anything derived from it (e.g. the export brick list).
        self.on_change = None

        self.canvas = tk.Canvas(self, bg=CANVAS_BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # click selects a block / empty space deselects; drag pans.
        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<Button-3>", self._on_right_click)   # context menu on a block
        self.canvas.bind("<Delete>", lambda e: self._delete_selected())
        self.canvas.bind("<BackSpace>", lambda e: self._delete_selected())
        # zoom: mouse wheel + ctrl-wheel + trackpad pinch (pinch arrives as MouseWheel on Windows)
        self.canvas.bind("<MouseWheel>", self._on_wheel)
        self.canvas.bind("<Control-MouseWheel>", self._on_wheel)
        self.canvas.bind("<Button-4>", lambda e: self._zoom(1.1))   # x11 wheel up
        self.canvas.bind("<Button-5>", lambda e: self._zoom(0.9))   # x11 wheel down
        self.canvas.bind("<Configure>", lambda e: self.render())

        self.status = tk.Label(self, bg=CANVAS_BG, fg=MUTED, anchor="w", font=("Segoe UI", 9))
        self.status.pack(fill="x", side="bottom")

        self.render()

    def _changed(self):
        self.render()
        if callable(self.on_change):
            try:
                self.on_change()
            except Exception:
                pass

    # ---- public ----------------------------------------------------------
    def place(self, brick: Brick) -> PlacedBrick:
        inst = self.draft.place(brick)
        self.render()
        return inst

    def clear(self) -> None:
        self.draft = DraftGraph(self.registry)
        self.render()

    # ---- zoom ------------------------------------------------------------
    def _on_wheel(self, e):
        self._zoom(1.1 if getattr(e, "delta", 0) > 0 else 0.9)

    def _zoom(self, factor: float):
        self.zoom = max(0.4, min(3.0, self.zoom * factor))
        self.render()

    def _f(self, base: int) -> int:
        return max(6, int(base * self.zoom))

    # ---- rendering -------------------------------------------------------
    def _draw_grid(self, z: float) -> None:
        c = self.canvas
        step = max(10, int(28 * z))
        span = 4000
        for x in range(-span, span, step):
            c.create_line(x, -span, x, span, fill=GRID)
        for y in range(-span, span, step):
            c.create_line(-span, y, span, y, fill=GRID)

    def render(self) -> None:
        c = self.canvas
        c.delete("all")
        self._blocks = []
        z = self.zoom
        self._draw_grid(z)
        bw, bh = BLOCK_W * z, BLOCK_H * z
        colx, topy = COL_X * z, TOP_Y * z
        res = self.draft.resolve()

        order = self.draft.run_order()
        if not order:
            c.create_text(colx, topy, anchor="nw", fill=MUTED, font=("Segoe UI", self._f(11)),
                          text="lay a brick from the bar above…  (scroll to zoom · drag to pan)")
            self.status.config(text="empty draft  ·  zoom %d%%" % int(z * 100))
            return

        by_id = {p.instance_id: p for p in self.draft.placed}
        feeds: Dict[str, List] = {}
        for b in res.bonds:
            feeds.setdefault(b.consumer, []).append((b.producer, b.packet_type))
        holes_by: Dict[str, List[str]] = {}
        for inst, t in res.holes:
            holes_by.setdefault(inst, []).append(t)

        y = topy
        prev_id: Optional[str] = None
        for iid in order:
            placed = by_id[iid]
            snapped_type = None
            if prev_id is not None:
                for producer, t in feeds.get(iid, []):
                    if producer == prev_id:
                        snapped_type = t
                        break
            if prev_id is not None:
                y += (SNAP_GAP if snapped_type else LOOSE_GAP) * z
                if not snapped_type:
                    c.create_text(colx + bw + 12 * z, y - (LOOSE_GAP * z) / 2,
                                  anchor="w", fill=LOOSE, font=("Segoe UI", self._f(8)),
                                  text="… not snapped here")
            self._blocks.append((iid, colx, y, colx + bw, y + bh))
            self._draw_block(placed, colx, y, bw, bh, snapped_type, holes_by.get(iid, []),
                             iid == self.selected)
            y += bh
            prev_id = iid

        sel = ("  ·  selected: " + self.selected.rsplit(".", 1)[-1]) if self.selected else \
              "  ·  click a brick to select · right-click for actions"
        self.status.config(text="%s  ·  zoom %d%%%s" % (res.summary(), int(z * 100), sel))
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _draw_block(self, placed: PlacedBrick, x: float, y: float, bw: float, bh: float,
                    snapped_type: Optional[str], holes: List[str], selected: bool = False) -> None:
        b = placed.brick
        c = self.canvas
        z = self.zoom
        nub_w, nub_h = NUB_W * z, NUB_H * z

        top_color = _seam_color(snapped_type) if snapped_type else (HOLE if holes else BLOCK_EDGE)
        c.create_rectangle(x + 14 * z, y - nub_h, x + 14 * z + nub_w, y + 1,
                           fill=top_color, outline=top_color)

        c.create_rectangle(x, y, x + bw, y + bh, fill=BLOCK, outline=BLOCK_EDGE, width=1)
        stripe = DET if b.deterministic else LIVE
        c.create_rectangle(x, y, x + 5 * z, y + bh, fill=stripe, outline=stripe)

        out_color = _seam_color(b.outputs[0]) if b.outputs else BLOCK_EDGE
        c.create_rectangle(x + 14 * z, y + bh - 1, x + 14 * z + nub_w, y + bh + nub_h,
                           fill=out_color, outline=out_color)

        emoji = getattr(b, "emoji", "") or ""
        leaf = b.id.rsplit(".", 1)[-1]
        c.create_text(x + 14 * z, y + 9 * z, anchor="nw", fill=TEXT,
                      font=("Segoe UI", self._f(10), "bold"),
                      text=(f"{emoji} {leaf}" if emoji else leaf))
        sub = b.family + (f"  ·  {b.kind}" if b.kind else "")
        c.create_text(x + 14 * z, y + 27 * z, anchor="nw", fill=MUTED,
                      font=("Segoe UI", self._f(8)), text=sub)

        if holes:
            c.create_text(x + bw + 12 * z, y + bh / 2, anchor="w", fill=HOLE,
                          font=("Segoe UI", self._f(8)),
                          text="○ " + ", ".join(holes) + "  (Club)")

        if selected:
            pad = 3
            c.create_rectangle(x - pad, y - pad, x + bw + pad, y + bh + pad,
                               outline=SEL, width=max(2, int(2 * z)))

    # ---- selection + edit ------------------------------------------------
    def _hit(self, e) -> Optional[str]:
        """Map an event to the instance_id of the block under it (canvas coords, pan-aware)."""
        cx, cy = self.canvas.canvasx(e.x), self.canvas.canvasy(e.y)
        for iid, x0, y0, x1, y1 in self._blocks:
            if x0 <= cx <= x1 and y0 <= cy <= y1:
                return iid
        return None

    def _on_press(self, e):
        self.canvas.focus_set()
        self._press_xy = (e.x, e.y)
        self._dragged = False
        self.canvas.scan_mark(e.x, e.y)   # arm panning in case this becomes a drag

    def _on_drag(self, e):
        if self._press_xy is not None:
            dx = abs(e.x - self._press_xy[0]); dy = abs(e.y - self._press_xy[1])
            if dx + dy > 4:
                self._dragged = True
        self.canvas.scan_dragto(e.x, e.y, gain=1)

    def _on_release(self, e):
        if self._dragged:            # it was a pan, not a click
            return
        self.selected = self._hit(e)  # None = click on empty space => deselect
        self.render()

    def _on_right_click(self, e):
        iid = self._hit(e)
        if iid is None:
            return
        self.selected = iid
        self.render()
        m = tk.Menu(self, tearoff=0)
        m.add_command(label="Configure / inspect", command=lambda: self._configure(iid))
        m.add_separator()
        m.add_command(label="Move up", command=lambda: self._move(iid, -1))
        m.add_command(label="Move down", command=lambda: self._move(iid, +1))
        m.add_separator()
        m.add_command(label="Delete", command=lambda: self._delete(iid))
        m.tk_popup(e.x_root, e.y_root)

    def _delete_selected(self):
        if self.selected:
            self._delete(self.selected)

    def _delete(self, iid: str):
        self.draft.remove(iid)
        if self.selected == iid:
            self.selected = None
        self._changed()

    def _move(self, iid: str, delta: int):
        self.draft.move(iid, delta)
        self.selected = iid
        self._changed()

    def _configure(self, iid: str):
        placed = next((p for p in self.draft.placed if p.instance_id == iid), None)
        if placed is None:
            return
        b = placed.brick
        res = self.draft.resolve()
        bonds = [f"{bd.producer.rsplit('.',1)[-1]} --{bd.packet_type}--> in"
                 for bd in res.bonds if bd.consumer == iid]
        holes = [t for (i, t) in res.holes if i == iid]
        top = tk.Toplevel(self)
        top.title(f"brick · {b.id}")
        top.configure(bg=CANVAS_BG)
        top.geometry("440x420")
        shell = tk.Frame(top, bg=CANVAS_BG)
        shell.pack(fill="both", expand=True)
        scroll = tk.Scrollbar(shell, orient="vertical")
        scroll.pack(side="right", fill="y")
        viewport = tk.Canvas(shell, bg=CANVAS_BG, highlightthickness=0, yscrollcommand=scroll.set)
        viewport.pack(side="left", fill="both", expand=True)
        scroll.config(command=viewport.yview)
        inner = tk.Frame(viewport, bg=CANVAS_BG)
        inner_id = viewport.create_window((0, 0), window=inner, anchor="nw")

        def _sync_scroll(_event=None):
            viewport.configure(scrollregion=viewport.bbox("all"))

        def _fit_inner(_event=None):
            viewport.itemconfigure(inner_id, width=viewport.winfo_width())

        inner.bind("<Configure>", _sync_scroll)
        viewport.bind("<Configure>", _fit_inner)

        def _wheel(event):
            delta = getattr(event, "delta", 0)
            if delta:
                viewport.yview_scroll(int(-delta / 120), "units")
            elif getattr(event, "num", None) == 4:
                viewport.yview_scroll(-1, "units")
            elif getattr(event, "num", None) == 5:
                viewport.yview_scroll(1, "units")

        for widget in (top, shell, viewport, inner):
            widget.bind("<MouseWheel>", _wheel, add="+")
            widget.bind("<Button-4>", _wheel, add="+")
            widget.bind("<Button-5>", _wheel, add="+")
        emoji = getattr(b, "emoji", "") or ""
        tk.Label(inner, text=f"{emoji} {b.id}", bg=CANVAS_BG, fg=SEL,
                 font=("Segoe UI", 13, "bold"), anchor="w").pack(fill="x", padx=14, pady=(12, 2))
        body = tk.Text(inner, bg="#0e1422", fg=TEXT, relief="flat", wrap="word",
                       font=("Consolas", 10), padx=10, pady=10, highlightthickness=0)
        body.pack(fill="both", expand=True, padx=12, pady=8)

        def row(label, val):
            body.insert("end", f"{label}: ", ("k",))
            body.insert("end", f"{val}\n")

        row("kind", getattr(b, "kind", "") or "—")
        row("deterministic", getattr(b, "deterministic", False))
        row("inputs", ", ".join(b.inputs) or "—")
        row("outputs", ", ".join(b.outputs) or "—")
        row("requires", ", ".join(getattr(b, "requires", []) or []) or "—")
        row("provides", ", ".join(getattr(b, "provides", []) or []) or "—")
        body.insert("end", "\nbonds (mortar in):\n", ("k",))
        body.insert("end", ("  " + "\n  ".join(bonds) if bonds else "  (none yet)") + "\n")
        body.insert("end", "\nopen sockets (Club resolves):\n", ("k",))
        body.insert("end", ("  " + ", ".join(holes) if holes else "  (none — fully fed)") + "\n")
        c = (getattr(b, "concept", {}) or {})
        body.insert("end", "\n" + (c.get("description", "") or ""))
        body.tag_config("k", foreground=MUTED)
        body.config(state="disabled")

        # Tunable params: bricks that declare CONCEPT["params"] get editable fields here, stored
        # on this PLACEMENT (placed.config). Bricks with no params just show the contract above.
        params = c.get("params") or []
        vars_ = {}
        payload_box = None
        validation_lbl = None
        if params:
            from tkinter import ttk
            pframe = tk.LabelFrame(inner, text="parameters", bg=CANVAS_BG, fg=SEL,
                                   font=("Segoe UI", 9, "bold"))
            pframe.pack(fill="x", padx=12, pady=(0, 8))
            for p in params:
                name = p.get("name")
                if not name:
                    continue
                row = tk.Frame(pframe, bg=CANVAS_BG)
                row.pack(fill="x", padx=8, pady=3)
                tk.Label(row, text=(p.get("label") or name) + ":", bg=CANVAS_BG, fg=TEXT,
                         width=14, anchor="w").pack(side="left")
                cur = getattr(placed, "payload", {}).get(name, placed.config.get(name, p.get("default", "")))
                v = tk.StringVar(value=str(cur))
                vars_[name] = v
                if p.get("type") == "enum":
                    box = tk.Frame(row, bg=FIELD_EDGE, highlightthickness=1, highlightbackground=FIELD_EDGE)
                    box.pack(side="left", fill="x", expand=True)
                    combo = ttk.Combobox(box, textvariable=v, values=p.get("options", []),
                                         state="readonly")
                    combo.pack(fill="x", expand=True, padx=1, pady=1)
                else:
                    box = tk.Frame(row, bg=FIELD_EDGE, highlightthickness=1, highlightbackground=FIELD_EDGE)
                    box.pack(side="left", fill="x", expand=True)
                    tk.Entry(box, textvariable=v, bg=FIELD_BG, fg=TEXT, insertbackground=SEL,
                             relief="flat").pack(fill="x", expand=True, padx=1, pady=1)
                hint = str(p.get("hint", "") or "").strip()
                if hint:
                    tk.Label(pframe, text=hint, bg=CANVAS_BG, fg=MUTED,
                             font=("Segoe UI", 8), anchor="w", justify="left").pack(
                        fill="x", padx=8, pady=(0, 2))

        payload_frame = tk.LabelFrame(inner, text="payload", bg=CANVAS_BG, fg=SEL,
                                      font=("Segoe UI", 9, "bold"))
        payload_frame.pack(fill="both", expand=True, padx=12, pady=(0, 8))
        tk.Label(payload_frame,
                 text="Edit the placement payload this brick will receive. Params above also feed into it.",
                 bg=CANVAS_BG, fg=MUTED, anchor="w", justify="left",
                 font=("Segoe UI", 8)).pack(fill="x", padx=8, pady=(6, 4))
        payload_shell = tk.Frame(payload_frame, bg=FIELD_EDGE, highlightthickness=1, highlightbackground=FIELD_EDGE)
        payload_shell.pack(fill="both", expand=True, padx=8, pady=(0, 6))
        payload_box = tk.Text(payload_shell, height=9, bg=FIELD_BG, fg=TEXT, relief="flat",
                              wrap="none", font=("Consolas", 10), padx=8, pady=8,
                              insertbackground=SEL)
        payload_box.pack(fill="both", expand=True, padx=1, pady=1)
        payload_box.insert("1.0", json.dumps(dict(getattr(placed, "payload", {}) or {}), indent=2, ensure_ascii=False))
        validation_lbl = tk.Label(payload_frame, text="", bg=CANVAS_BG, fg=MUTED,
                                  anchor="w", justify="left", font=("Segoe UI", 8))
        validation_lbl.pack(fill="x", padx=8, pady=(0, 6))

        def _collect_payload():
            raw_payload = payload_box.get("1.0", "end").strip() if payload_box is not None else ""
            parsed = {}
            if raw_payload:
                parsed = json.loads(raw_payload)
                if not isinstance(parsed, dict):
                    raise ValueError("payload must be a JSON object")
            placed.payload = parsed
            for p in params:
                name = p.get("name")
                if not name:
                    continue
                placed.config[name] = _coerce_param_value(p, vars_[name].get())
            effective = _placement_payload(placed)
            placed.payload = dict(effective)
            return effective

        def _refresh_validation():
            try:
                effective = _collect_payload()
                if payload_box is not None:
                    payload_box.delete("1.0", "end")
                    payload_box.insert("1.0", json.dumps(effective, indent=2, ensure_ascii=False))
                issues = _validate_placement(placed)
                if issues:
                    msg = "Needs attention: " + " | ".join(
                        f"{item.get('code', 'issue')}: {item.get('message', '')}" for item in issues
                    )
                    validation_lbl.config(text=msg, fg=HOLE)
                else:
                    validation_lbl.config(
                        text="Looks good. Effective payload: " + json.dumps(effective, ensure_ascii=False),
                        fg="#97e0ac",
                    )
            except Exception as exc:
                validation_lbl.config(text=f"Payload error: {exc}", fg=HOLE)

        def _save_config():
            try:
                _collect_payload()
                issues = _validate_placement(placed)
            except Exception as exc:
                if validation_lbl is not None:
                    validation_lbl.config(text=f"Payload error: {exc}", fg=HOLE)
                return
            self._changed()
            if issues:
                msg = "saved with issues: " + " | ".join(
                    f"{item.get('code', 'issue')}: {item.get('message', '')}" for item in issues
                )
                if validation_lbl is not None:
                    validation_lbl.config(text=msg, fg=HOLE)
                return
            top.destroy()

        _refresh_validation()

        bar = tk.Frame(inner, bg=CANVAS_BG); bar.pack(fill="x", padx=12, pady=(0, 12))
        tk.Button(bar, text="Validate", command=_refresh_validation,
                  bg="#2b4b5c", fg="#d8edf7", relief="flat").pack(side="left", padx=(0, 6))
        tk.Button(bar, text="Save", command=_save_config,
                  bg=SEL, fg="#241804", relief="flat").pack(side="left")
        tk.Button(bar, text="Delete brick", command=lambda: (top.destroy(), self._delete(iid)),
                  bg="#5c2b2b", fg="#f0d6d6", relief="flat").pack(side="left")
        tk.Button(bar, text="Close", command=top.destroy,
                  bg=BLOCK, fg=TEXT, relief="flat").pack(side="right")


def _demo(root_path=ATL_BRICKS) -> None:
    from .palette import BrickBar
    reg = BrickRegistry.from_path(root_path)
    win = tk.Tk()
    win.title("Bookmark · snap canvas")
    win.configure(bg=BG)
    win.geometry("560x760")

    canvas = SnapCanvas(win, reg)
    bar = BrickBar(win, reg, on_place=canvas.place)
    bar.pack(fill="x", side="top")
    canvas.pack(fill="both", expand=True)
    win.mainloop()


if __name__ == "__main__":
    import sys
    _demo(sys.argv[1] if len(sys.argv) > 1 else ATL_BRICKS)
