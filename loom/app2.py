"""loom — the galaxy-map declaration surface.

This surface no longer mints `.oradio` artifacts. Bookmark does that.

Instead, `.loom` is the lightweight declaration that arranges already-minted `.oradio`
nodes into a traversable universe: the words of the universe, the set of nodes present,
and each node's soulmate bond.

Run:  python -m loom.app2
"""
from __future__ import annotations

import shutil
import tempfile
import threading
from pathlib import Path
from typing import Any, Dict, List, Tuple

from loom.app import ACCENT, BG, FIELD, LINE, MUTED, PANEL, TEXT, UNIVERSE_EXAMPLES, identicon_cells
from loom.dotloom import _slug
from oradio_engine.loom_graph import (
    LoomGraph,
    declaration_size,
    declaration_text,
    graph_nodes,
    load_declaration_text,
    slugify_node,
)
from oradio_engine.loom_runtime import request_ribbonos_load, sync_crossovers


def _loom_dict(universe: str, nodes: List[Dict[str, str]]) -> Dict[str, Any]:
    return LoomGraph.from_any(universe, nodes).as_dict()


def _relationship_edges(nodes: List[Dict[str, Any]]) -> List[Tuple[str, str]]:
    node_ids = {str(node.get("id", "")).strip() for node in nodes if str(node.get("id", "")).strip()}
    seen = set()
    edges: List[Tuple[str, str]] = []
    for node in nodes:
        left = str(node.get("id", "")).strip()
        if not left:
            continue
        soulmates = node.get("soulmates") or []
        if not soulmates:
            soulmate = str(node.get("soulmate", "")).strip()
            soulmates = [soulmate] if soulmate else []
        for right in soulmates:
            right_id = str(right or "").strip()
            if not right_id or right_id not in node_ids:
                continue
            pair = tuple(sorted((left, right_id)))
            if pair in seen:
                continue
            seen.add(pair)
            edges.append(pair)
    return edges


class LoomDeclaration:
    def __init__(self) -> None:
        import tkinter as tk
        from tkinter import ttk

        self.tk = tk
        self.ttk = ttk
        self.root = tk.Tk()
        self.root.title("Loom")
        self.root.configure(bg=BG)
        self.root.geometry("1000x780")
        self.root.minsize(820, 600)
        self._rows: List[Dict[str, Any]] = []
        self._ph_i = 0
        self._build()
        self._cycle_hint()
        self._refresh()

    def _build(self) -> None:
        tk = self.tk
        w = tk.Frame(self.root, bg=BG)
        w.pack(fill="both", expand=True, padx=30, pady=24)

        tk.Label(w, text="Loom", font=("Segoe UI", 22, "bold"), fg=MUTED, bg=BG).pack(anchor="w")

        top = tk.Frame(w, bg=BG)
        top.pack(fill="x", pady=(16, 0))
        left = tk.Frame(top, bg=BG)
        left.pack(side="left", fill="both", expand=True)

        tk.Label(left, text="Universe", font=("Segoe UI", 30, "bold"), fg=TEXT, bg=BG).pack(anchor="w")
        tk.Label(left, text="this is your loom's title", font=("Segoe UI", 11), fg=MUTED, bg=BG).pack(anchor="w")
        box = tk.Frame(left, bg=FIELD, highlightthickness=1, highlightbackground=LINE)
        box.pack(fill="x", pady=(8, 0))
        self.universe = tk.Text(
            box,
            height=2,
            wrap="word",
            bg=FIELD,
            fg=TEXT,
            insertbackground=ACCENT,
            relief="flat",
            font=("Segoe UI", 17),
            padx=14,
            pady=12,
            highlightthickness=0,
        )
        self.universe.pack(fill="x")
        self.universe.bind("<KeyRelease>", lambda _e: self._refresh())
        self.hint = tk.Label(
            box,
            text="",
            fg=MUTED,
            bg=FIELD,
            font=("Segoe UI", 17),
            anchor="nw",
            justify="left",
            wraplength=560,
        )
        self.hint.place(x=16, y=12)
        self.hint.bind("<Button-1>", lambda _e: self.universe.focus_set())

        # The title is appended to a .loom file on save — show the greyed filename so that's clear.
        self.loom_name = tk.Label(left, text="untitled.loom", font=("Consolas", 12), fg=MUTED, bg=BG, anchor="w")
        self.loom_name.pack(anchor="w", pady=(6, 0))

        self.sig = tk.Canvas(top, width=150, height=150, bg=BG, highlightthickness=0)
        self.sig.pack(side="left", padx=(24, 0))

        row = tk.Frame(w, bg=BG)
        row.pack(fill="x", pady=(24, 8))
        tk.Label(row, text="Oradios", font=("Segoe UI", 30, "bold"), fg=TEXT, bg=BG).pack(side="left")
        self._btn(row, "open .loom", self._open_declaration).pack(side="right")
        self._btn(row, "new .loom", self._new_loom).pack(side="right", padx=(0, 8))
        self._btn(row, "add .oradio", self._add_oradio_from_picker).pack(side="right", padx=(0, 8))
        self._btn(row, "new node", self._add_row).pack(side="right", padx=(0, 8))

        tk.Label(
            w,
            text="Each node points at an existing .oradio and can name one or many soulmate bonds. The graph is the artifact.",
            font=("Segoe UI", 10, "bold"),
            fg=MUTED,
            bg=BG,
        ).pack(anchor="w", pady=(0, 8))

        self.rows = tk.Frame(w, bg=BG)
        self.rows.pack(fill="x")

        map_card = tk.Frame(w, bg=BG)
        map_card.pack(fill="both", expand=False, pady=(18, 0))
        tk.Label(map_card, text="Galaxy Map", font=("Segoe UI", 10, "bold"), fg=MUTED, bg=BG).pack(anchor="w", pady=(0, 4))
        map_shell = tk.Frame(map_card, bg=PANEL, highlightthickness=1, highlightbackground=LINE)
        map_shell.pack(fill="x")
        self.map_canvas = tk.Canvas(map_shell, height=170, bg=PANEL, highlightthickness=0)
        self.map_canvas.pack(fill="x", padx=12, pady=12)

        head = tk.Frame(w, bg=BG)
        head.pack(fill="x", pady=(16, 6))
        tk.Label(head, text=".loom", font=("Consolas", 12, "bold"), fg=MUTED, bg=BG).pack(side="left")
        self.size = tk.Label(head, text="", font=("Consolas", 12, "bold"), fg=ACCENT, bg=BG)
        self.size.pack(side="right")

        # Footer is PINNED to the bottom (packed before the expanding preview) so save / open /
        # load are always reachable even when the node list + preview overflow the window.
        foot = tk.Frame(w, bg=BG)
        foot.pack(fill="x", side="bottom", pady=(10, 0))
        self.status = tk.Label(foot, text="", font=("Segoe UI", 10), fg=MUTED, bg=BG)
        self.status.pack(side="left")
        self._btn(foot, "save .loom", self._generate, primary=True).pack(side="right")
        self._btn(foot, "open in Bookmark", self._open_in_bookmark).pack(side="right", padx=(0, 8))
        self._btn(foot, "load into RibbonOS", self._load_into_ribbonos).pack(side="right", padx=(0, 8))
        self._btn(foot, "regen crossovers", self._regenerate_all).pack(side="right", padx=(0, 8))

        self.decl = tk.Text(
            w,
            height=6,
            bg=PANEL,
            fg=TEXT,
            relief="flat",
            font=("Consolas", 12),
            padx=14,
            pady=12,
            highlightthickness=1,
            highlightbackground=LINE,
        )
        self.decl.pack(fill="both", expand=True)

    def _btn(self, parent, text, cmd, primary=False):
        b = self.tk.Label(
            parent,
            text=text,
            font=("Segoe UI", 12, "bold"),
            fg="#06202a" if primary else TEXT,
            bg=ACCENT if primary else PANEL,
            padx=20,
            pady=9,
            cursor="hand2",
        )
        b.bind("<Button-1>", lambda _e: cmd())
        return b

    def _add_oradio_from_picker(self) -> None:
        from pathlib import Path
        from tkinter import filedialog

        path = filedialog.askopenfilename(
            parent=self.root,
            title="Choose an .oradio node",
            filetypes=[("oradio", "*.oradio"), ("all files", "*.*")],
        )
        if not path:
            return
        stem = Path(path).stem
        self._add_row({"label": stem.replace("-", " "), "oradio": path, "id": slugify_node(stem)})

    def _add_row(self, data: Dict[str, str] | None = None) -> None:
        tk = self.tk
        data = data or {}
        row = tk.Frame(self.rows, bg=PANEL, highlightthickness=1, highlightbackground=LINE)
        row.pack(fill="x", pady=4)

        name = tk.Entry(
            row,
            bg=FIELD,
            fg=TEXT,
            insertbackground=ACCENT,
            relief="flat",
            font=("Segoe UI", 11),
            highlightthickness=1,
            highlightbackground=LINE,
        )
        name.pack(side="left", fill="x", expand=True, padx=(10, 6), pady=10, ipady=5)
        name.insert(0, data.get("label", ""))

        oradio = tk.Entry(
            row,
            bg=FIELD,
            fg=TEXT,
            insertbackground=ACCENT,
            relief="flat",
            font=("Consolas", 10),
            width=34,
            highlightthickness=1,
            highlightbackground=LINE,
        )
        oradio.pack(side="left", padx=6, pady=10, ipady=5)
        oradio.insert(0, data.get("oradio", ""))

        browse = tk.Label(row, text="choose file", font=("Segoe UI", 10, "bold"), fg=ACCENT, bg=PANEL, cursor="hand2", padx=8)
        browse.pack(side="left")

        soulmates = tk.Entry(
            row,
            bg=FIELD,
            fg=TEXT,
            insertbackground=ACCENT,
            relief="flat",
            font=("Consolas", 10),
            width=24,
            highlightthickness=1,
            highlightbackground=LINE,
        )
        soulmates.pack(side="left", padx=6, pady=10, ipady=5)
        existing_soulmates = data.get("soulmates", None)
        if isinstance(existing_soulmates, list):
            soulmates.insert(0, ", ".join(str(item).strip() for item in existing_soulmates if str(item).strip()))
        elif data.get("soulmate", ""):
            soulmates.insert(0, data.get("soulmate", ""))

        # Regenerate just THIS node's crossovers (its soulmate edges) — deterministic media can
        # break / go stale; this lets you rebake one node without stranding the whole loom.
        regen = tk.Label(row, text="↻", font=("Segoe UI", 12, "bold"), fg=ACCENT, bg=PANEL,
                         cursor="hand2", padx=8)
        regen.pack(side="left")

        rm = tk.Label(row, text="✕", font=("Segoe UI", 10), fg=MUTED, bg=PANEL, cursor="hand2", padx=10)
        rm.pack(side="left")

        entry = {
            "frame": row,
            "name": name,
            "oradio": oradio,
            "soulmates": soulmates,
            "id": data.get("id", ""),
        }
        self._rows.append(entry)

        browse.bind("<Button-1>", lambda _e, target=oradio, holder=entry: self._choose_oradio(target, holder))
        regen.bind("<Button-1>", lambda _e, target=entry: self._regen_node(target))
        rm.bind("<Button-1>", lambda _e, target=entry: self._del_row(target))
        name.bind("<KeyRelease>", lambda _e, target=entry: self._sync_id(target))
        name.bind("<FocusOut>", lambda _e, target=entry: self._sync_id(target))
        oradio.bind("<KeyRelease>", lambda _e, target=entry: self._sync_id(target))
        for widget in (name, oradio, soulmates):
            widget.bind("<KeyRelease>", lambda _e: self._refresh())

        self._sync_id(entry)
        self._refresh()

    def _choose_oradio(self, target, entry) -> None:
        from pathlib import Path
        from tkinter import filedialog

        path = filedialog.askopenfilename(
            parent=self.root,
            title="Choose an .oradio node",
            filetypes=[("oradio", "*.oradio"), ("all files", "*.*")],
        )
        if not path:
            return
        target.delete(0, "end")
        target.insert(0, path)
        if not entry["name"].get().strip():
            entry["name"].insert(0, Path(path).stem.replace("-", " "))
        self._sync_id(entry)
        self._refresh()

    def _sync_id(self, entry) -> None:
        label = entry["name"].get().strip()
        oradio = entry["oradio"].get().strip()
        entry["id"] = slugify_node(label or oradio)

    def _del_row(self, entry) -> None:
        entry["frame"].destroy()
        self._rows.remove(entry)
        self._refresh()

    def _row_nodes(self) -> List[Dict[str, str]]:
        nodes: List[Dict[str, str]] = []
        for row in self._rows:
            label = row["name"].get().strip()
            oradio = row["oradio"].get().strip()
            if not label and not oradio:
                continue
            node_id = row.get("id") or slugify_node(label or oradio)
            soulmates = self._parse_soulmates(row["soulmates"].get().strip(), own_id=node_id)
            nodes.append({
                "id": node_id,
                "label": label,
                "oradio": oradio,
                "soulmate": soulmates[0] if soulmates else "",
                "soulmates": soulmates,
            })
        return nodes

    def _parse_soulmates(self, text: str, own_id: str = "") -> List[str]:
        values: List[str] = []
        for part in str(text or "").replace(";", ",").split(","):
            value = part.strip()
            if not value or value == own_id or value in values:
                continue
            values.append(value)
        return values

    def _refresh(self) -> None:
        universe = self._universe()
        if universe:
            self.hint.place_forget()
        else:
            self.hint.place(x=16, y=12)
        nodes = self._row_nodes()
        text = declaration_text(universe, nodes)
        self.decl.delete("1.0", "end")
        self.decl.insert("1.0", text)
        self.size.config(text=f"→ {declaration_size(universe, nodes)} byte .loom")
        self.loom_name.config(text=f"{_slug(universe) or 'untitled'}.loom")
        self._draw(universe or "untitled")
        self._draw_map(universe, nodes)

    def _draw(self, universe: str) -> None:
        cells = identicon_cells(universe)
        c = self.sig
        c.delete("all")
        m = len(cells)
        s = 150 // m
        for r in range(m):
            for col in range(m):
                c.create_rectangle(col * s, r * s, col * s + s, r * s + s, fill=cells[r][col], outline=cells[r][col])

    def _draw_map(self, universe: str, nodes: List[Dict[str, str]]) -> None:
        canvas = self.map_canvas
        canvas.delete("all")
        width = max(int(canvas.winfo_width()), 520)
        height = max(int(canvas.winfo_height()), 280)
        laid_out = graph_nodes(universe, nodes, width=width, height=height)
        if not laid_out:
            canvas.create_text(width / 2, height / 2, text="Add a few .oradios to see the universe graph.", fill=MUTED, font=("Segoe UI", 14))
            return
        by_id = {node["id"]: node for node in laid_out}
        for node in laid_out:
            soulmate = node.get("soulmate", "")
            soulmates = node.get("soulmates") or ([soulmate] if soulmate else [])
            for soulmate_id in soulmates:
                if soulmate_id and soulmate_id in by_id:
                    target = by_id[soulmate_id]
                    canvas.create_line(node["x"], node["y"], target["x"], target["y"], fill=ACCENT, width=2, smooth=True)
        for node in laid_out:
            x, y = node["x"], node["y"]
            canvas.create_oval(x - 28, y - 28, x + 28, y + 28, fill=FIELD, outline=ACCENT, width=2)
            canvas.create_text(x, y - 4, text=node["id"][:12], fill=TEXT, font=("Consolas", 9, "bold"))
            if node.get("label"):
                canvas.create_text(x, y + 14, text=node["label"][:20], fill=MUTED, font=("Segoe UI", 8))

    def _cycle_hint(self) -> None:
        if not self._universe():
            self.hint.config(text=UNIVERSE_EXAMPLES[self._ph_i % len(UNIVERSE_EXAMPLES)])
            self.hint.place(x=16, y=12)
            self._ph_i += 1
        self.root.after(2600, self._cycle_hint)

    def _universe(self) -> str:
        return self.universe.get("1.0", "end").strip()

    def _generate(self) -> None:
        from loom.dotloom import _slug
        from tkinter import filedialog

        universe = self._universe()
        text = declaration_text(universe, self._row_nodes())
        path = filedialog.asksaveasfilename(
            parent=self.root,
            defaultextension=".loom",
            initialfile=f"{_slug(universe)}.loom",
            filetypes=[("loom", "*.loom"), ("yaml", "*.yaml"), ("all files", "*.*")],
        )
        if not path:
            return
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)
        self.status.config(text=f"saved · {path}", fg=ACCENT)

    def _project_root(self):
        return Path(__file__).resolve().parent.parent   # loom/ -> oracle-radio

    def _new_loom(self) -> None:
        """Start a fresh .loom: clear the title and all nodes."""
        self.universe.delete("1.0", "end")
        for row in list(self._rows):
            self._del_row(row)
        self.status.config(text="new .loom", fg=MUTED)
        self._refresh()

    def _load_into_ribbonos_legacy(self) -> None:
        """Write the current .loom where RibbonOS scans for it (the project root), so its oradios
        appear in the shell on the next scan. The .loom is the relationship lens RibbonOS loads."""
        universe = self._universe()
        text = declaration_text(universe, self._row_nodes())
        name = f"{_slug(universe) or 'untitled'}.loom"
        dest = self._project_root() / name
        try:
            dest.write_text(text, encoding="utf-8")
            self._force_ribbonos_reload()
            self.status.config(text=f"loaded into RibbonOS · {name} (requested shell reload)", fg=ACCENT)
        except Exception as exc:
            self.status.config(text=f"could not load into RibbonOS: {exc}", fg=MUTED)

    def _force_ribbonos_reload_legacy(self) -> None:
        """Best-effort nudge for a running RibbonOS shell to refresh loom/station state."""
        import json

        root = self._project_root()
        rq = root / ".switch_request"
        rq.write_text(json.dumps({"action": "refresh_shell"}), encoding="utf-8")

    def _open_in_bookmark(self) -> None:
        """Open the loom in Bookmark — the .oradio authoring surface / door into the universe."""
        import subprocess
        import sys

        root = self._project_root()
        bookmark = root / "bookmark.py"
        if not bookmark.exists():
            self.status.config(text="bookmark.py not found", fg=MUTED)
            return
        try:
            subprocess.Popen([sys.executable, str(bookmark)], cwd=str(root))
            self.status.config(text="opening Bookmark…", fg=ACCENT)
        except Exception as exc:
            self.status.config(text=f"could not open Bookmark: {exc}", fg=MUTED)

    def _open_declaration(self) -> None:
        from tkinter import filedialog

        path = filedialog.askopenfilename(
            parent=self.root,
            title="Open a .loom declaration",
            filetypes=[("loom", "*.loom"), ("yaml", "*.yaml"), ("json", "*.json"), ("all files", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as handle:
                universe, nodes = load_declaration_text(handle.read())
        except Exception as exc:
            self.status.config(text=f"could not open {path}: {exc}", fg=MUTED)
            return
        self.universe.delete("1.0", "end")
        self.universe.insert("1.0", universe)
        for row in list(self._rows):
            self._del_row(row)
        for node in nodes:
            self._add_row(node)
        self._refresh()
        self.status.config(text=f"opened · {path}", fg=ACCENT)

    def _load_into_ribbonos(self) -> None:
        """Write the current .loom where RibbonOS scans for it and bake its relationship media."""
        universe = self._universe()
        nodes = self._row_nodes()
        text = declaration_text(universe, nodes)
        name = f"{_slug(universe) or 'untitled'}.loom"
        dest = self._project_root() / name
        try:
            dest.write_text(text, encoding="utf-8")
        except Exception as exc:
            self.status.config(text=f"could not load into RibbonOS: {exc}", fg=MUTED)
            return

        self.status.config(text=f"loading into RibbonOS · {name} · baking traversal media…", fg=MUTED)

        def worker():
            try:
                built, failed = sync_crossovers(self._project_root(), dest, universe, nodes)
                request_ribbonos_load(self._project_root(), dest)
                note = f"loaded into RibbonOS · {name} · baked {built} crossover"
                if built != 1:
                    note += "s"
                if failed:
                    note += f" · {failed} skipped"
                note += " · requested shell reload"
                self.root.after(0, lambda: self.status.config(text=note, fg=ACCENT if failed == 0 else MUTED))
            except Exception as exc:
                self.root.after(0, lambda: self.status.config(text=f"could not load into RibbonOS: {exc}", fg=MUTED))

        threading.Thread(target=worker, daemon=True).start()

    # ------------------------------------------------------------------ regenerate crossovers
    def _regen_node(self, entry) -> None:
        """Rebake just this node's soulmate crossovers (with a progress bar)."""
        self._sync_id(entry)
        node_id = (entry.get("id") or "").strip()
        if not node_id:
            self.status.config(text="name the node first, then regenerate", fg=MUTED)
            return
        self._regenerate(only_nodes=[node_id], title=f"Regenerate · {node_id}")

    def _regenerate_all(self) -> None:
        """Rebake every relationship crossover in the loom (with a progress bar)."""
        self._regenerate(only_nodes=None, title="Regenerate all crossovers")

    def _regenerate(self, only_nodes, title: str) -> None:
        universe = self._universe()
        nodes = self._row_nodes()
        name = f"{_slug(universe) or 'untitled'}.loom"
        dest = self._project_root() / name
        try:
            dest.write_text(declaration_text(universe, nodes), encoding="utf-8")
        except Exception as exc:
            self.status.config(text=f"could not write .loom: {exc}", fg=MUTED)
            return

        edges = _relationship_edges(nodes)
        if only_nodes is not None:
            only = {str(n).strip() for n in only_nodes if str(n).strip()}
            edges = [(l, r) for (l, r) in edges if l in only or r in only]
        total = len(edges)
        if total == 0:
            self.status.config(text="no soulmate bonds to regenerate", fg=MUTED)
            return
        self._run_bake(title, total, only_nodes, dest, universe, nodes)

    @staticmethod
    def _fmt_dur(seconds: float) -> str:
        s = int(max(0, round(seconds)))
        m, sec = divmod(s, 60)
        return f"{m}:{sec:02d}" if m else f"{sec}s"

    def _run_bake(self, title, total, only_nodes, dest, universe, nodes) -> None:
        """Open a modal progress window and bake crossovers in a worker thread, streaming
        edges/sec + ETA from sync_crossovers' on_progress callback."""
        import time

        tk, ttk = self.tk, self.ttk
        win = tk.Toplevel(self.root)
        win.title(title)
        win.configure(bg=BG)
        win.geometry("480x190")
        win.transient(self.root)
        win.grab_set()
        win.protocol("WM_DELETE_WINDOW", lambda: None)  # don't let a half-bake be closed mid-render

        tk.Label(win, text=title, font=("Segoe UI", 15, "bold"), fg=TEXT, bg=BG).pack(anchor="w", padx=22, pady=(20, 2))
        edge_lbl = tk.Label(win, text="starting…", font=("Segoe UI", 10), fg=MUTED, bg=BG)
        edge_lbl.pack(anchor="w", padx=22)
        bar = ttk.Progressbar(win, mode="determinate", maximum=total, length=436)
        bar.pack(padx=22, pady=(12, 6))
        eta_lbl = tk.Label(win, text=f"0 / {total} edges", font=("Consolas", 10), fg=ACCENT, bg=BG)
        eta_lbl.pack(anchor="w", padx=22)

        t0 = time.time()

        def on_progress(done, tot, label):
            def ui():
                bar["value"] = done
                if label and label != "done":
                    edge_lbl.config(text=f"baking  {label}   ({min(done + 1, tot)}/{tot})")
                elapsed = time.time() - t0
                rate = done / elapsed if (done and elapsed > 0) else 0.0
                if rate > 0:
                    remaining = (tot - done) / rate
                    eta_lbl.config(text=f"{done}/{tot} edges · {rate:.2f} edges/s · "
                                        f"ETA {self._fmt_dur(remaining)} · elapsed {self._fmt_dur(elapsed)}")
                else:
                    eta_lbl.config(text=f"{done}/{tot} edges · elapsed {self._fmt_dur(elapsed)}")
            self.root.after(0, ui)

        def worker():
            try:
                built, failed = sync_crossovers(self._project_root(), dest, universe, nodes,
                                                only_nodes=only_nodes, on_progress=on_progress)
                request_ribbonos_load(self._project_root(), dest)

                def done_ui():
                    bar["value"] = total
                    summary = f"baked {built} crossover" + ("" if built == 1 else "s")
                    if failed:
                        summary += f" · {failed} skipped"
                    edge_lbl.config(text=f"done · {summary}")
                    eta_lbl.config(text=f"elapsed {self._fmt_dur(time.time() - t0)}")
                    win.protocol("WM_DELETE_WINDOW", win.destroy)
                    win.after(1400, win.destroy)
                    self.status.config(text=f"regenerated · {summary} · requested shell reload",
                                       fg=ACCENT if not failed else MUTED)
                self.root.after(0, done_ui)
            except Exception as exc:
                def fail_ui():
                    edge_lbl.config(text=f"failed: {exc}")
                    win.protocol("WM_DELETE_WINDOW", win.destroy)
                    self.status.config(text=f"regen failed: {exc}", fg=MUTED)
                self.root.after(0, fail_ui)

        threading.Thread(target=worker, daemon=True).start()

    def run(self):
        self.root.mainloop()


def main() -> None:
    LoomDeclaration().run()


if __name__ == "__main__":
    main()
