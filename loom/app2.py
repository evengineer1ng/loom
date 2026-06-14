"""loom — candidate 2: the DECLARATION skin.

Not a form. A declaration. The lower panel shows the `.loom` (what you declared), not
the generated `.oradio` YAML (exhaust). Connections are attached pills, not settings
rows. No step numbers, no wizard. Big universe, big connections, a big seed-face.

Run:  python -m loom.app2     (candidate 1 is still `python -m loom.app`)
"""
from __future__ import annotations

from typing import Any, Dict, List

from loom.app import (ACCENT, BG, FIELD, LINE, MUTED, PANEL, ROLE_COLOR, TEXT,
                      UNIVERSE_EXAMPLES, identicon_cells, preview, role_of)


def declaration_text(universe: str, connections: List[Any]) -> str:
    """The `.loom` itself — the artifact, the way the author declared it."""
    out = ["Universe:", f"    {universe or '…'}", "", "Connections:"]
    names = [(c.get('plugin', '') if isinstance(c, dict) else str(c)) for c in connections]
    out += [f"    {n}" for n in names] if names else ["    …"]
    return "\n".join(out)


class LoomDeclaration:
    def __init__(self) -> None:
        import tkinter as tk
        self.tk = tk
        self.root = tk.Tk()
        self.root.title("loom")
        self.root.configure(bg=BG)
        self.root.geometry("940x780")
        self._conns: List[Dict[str, str]] = []
        self._ph_i = 0
        self._build()
        self._cycle()
        self._add("simulated_spatial_array")

    def _build(self) -> None:
        tk = self.tk
        w = tk.Frame(self.root, bg=BG); w.pack(fill="both", expand=True, padx=30, pady=26)

        tk.Label(w, text="loom", font=("Segoe UI", 22, "bold"), fg=MUTED, bg=BG).pack(anchor="w")

        top = tk.Frame(w, bg=BG); top.pack(fill="x", pady=(18, 0))
        left = tk.Frame(top, bg=BG); left.pack(side="left", fill="both", expand=True)

        tk.Label(left, text="Universe", font=("Segoe UI", 30, "bold"), fg=TEXT, bg=BG).pack(anchor="w")
        self.universe = tk.Text(left, height=2, wrap="word", bg=FIELD, fg=TEXT, insertbackground=ACCENT,
                                relief="flat", font=("Segoe UI", 17), padx=14, pady=12,
                                highlightthickness=1, highlightbackground=LINE)
        self.universe.pack(fill="x", pady=(8, 0))
        self.universe.bind("<KeyRelease>", lambda _e: self._refresh())

        # the big seed face
        self.sig = tk.Canvas(top, width=150, height=150, bg=BG, highlightthickness=0)
        self.sig.pack(side="left", padx=(24, 0))

        tk.Label(w, text="Connections", font=("Segoe UI", 30, "bold"), fg=TEXT, bg=BG).pack(anchor="w", pady=(26, 8))
        self.chips = tk.Frame(w, bg=BG); self.chips.pack(fill="x")
        self.adder = tk.Entry(w, bg=FIELD, fg=TEXT, insertbackground=ACCENT, relief="flat",
                              font=("Consolas", 12), highlightthickness=1, highlightbackground=LINE)
        self.adder.pack(fill="x", ipady=7, pady=(10, 0))
        self._ghost(self.adder, "type a plugin (or github:owner/repo) and press enter…")
        self.adder.bind("<Return>", lambda _e: self._add_from_entry())

        # the declaration is the artifact
        head = tk.Frame(w, bg=BG); head.pack(fill="x", pady=(26, 6))
        tk.Label(head, text=".loom", font=("Consolas", 12, "bold"), fg=MUTED, bg=BG).pack(side="left")
        self.size = tk.Label(head, text="", font=("Consolas", 12, "bold"), fg=ACCENT, bg=BG)
        self.size.pack(side="right")
        self.decl = tk.Text(w, height=8, bg=PANEL, fg=TEXT, relief="flat", font=("Consolas", 12),
                            padx=14, pady=12, highlightthickness=1, highlightbackground=LINE)
        self.decl.pack(fill="both", expand=True)

        foot = tk.Frame(w, bg=BG); foot.pack(fill="x", pady=(16, 0))
        self.status = tk.Label(foot, text="", font=("Segoe UI", 10), fg=MUTED, bg=BG); self.status.pack(side="left")
        self._btn(foot, "generate", self._generate, primary=True).pack(side="right")
        self._btn(foot, "test run", self._run).pack(side="right", padx=(0, 8))

    def _btn(self, parent, text, cmd, primary=False):
        b = self.tk.Label(parent, text=text, font=("Segoe UI", 12, "bold"),
                          fg="#06202a" if primary else TEXT, bg=ACCENT if primary else PANEL,
                          padx=20, pady=9, cursor="hand2")
        b.bind("<Button-1>", lambda _e: cmd()); return b

    # -- pills -- #
    def _add_from_entry(self):
        val = self.adder.get().strip()
        if not val or val.startswith("type a plugin"):
            return
        if val.startswith("github:"):
            name = val.split("/")[-1]
            self._add(name, source=val)
        else:
            self._add(val)
        self.adder.delete(0, "end")

    def _add(self, plugin: str, source: str = "") -> None:
        tk = self.tk
        r = role_of(plugin)
        chip = tk.Frame(self.chips, bg=PANEL, highlightthickness=1, highlightbackground=ROLE_COLOR.get(r, LINE))
        chip.pack(side="left", padx=(0, 8), pady=4)
        tk.Frame(chip, bg=ROLE_COLOR.get(r, MUTED), width=4).pack(side="left", fill="y")
        tk.Label(chip, text=plugin, font=("Consolas", 12), fg=TEXT, bg=PANEL, padx=8, pady=5).pack(side="left")
        x = tk.Label(chip, text="✕", font=("Segoe UI", 9), fg=MUTED, bg=PANEL, padx=6, cursor="hand2"); x.pack(side="left")
        entry = {"plugin": plugin, "source": source, "chip": chip}
        x.bind("<Button-1>", lambda _e: self._del(entry))
        self._conns.append(entry)
        self._refresh()

    def _del(self, entry):
        entry["chip"].destroy(); self._conns.remove(entry); self._refresh()

    def _conn_dicts(self):
        out = []
        for e in self._conns:
            c = {"plugin": e["plugin"]}
            if e["source"]:
                c["source"] = e["source"]
            out.append(c)
        return out

    # -- refresh -- #
    def _refresh(self):
        u = self._universe()
        conns = self._conn_dicts()
        self.decl.delete("1.0", "end"); self.decl.insert("1.0", declaration_text(u, conns))
        _t, n = preview(u or "untitled", conns)
        self.size.config(text=f"→ {n} byte .oradio")
        self._draw(u or "untitled")

    def _draw(self, u):
        cells = identicon_cells(u); c = self.sig; c.delete("all")
        m = len(cells); s = 150 // m
        for r in range(m):
            for col in range(m):
                c.create_rectangle(col*s, r*s, col*s+s, r*s+s, fill=cells[r][col], outline=cells[r][col])

    # -- placeholders -- #
    def _ghost(self, e, text):
        e.insert(0, text); e.config(fg=MUTED)
        e.bind("<FocusIn>", lambda _ev: (e.get() == text) and (e.delete(0, "end"), e.config(fg=TEXT)))
        e.bind("<FocusOut>", lambda _ev: (not e.get()) and (e.insert(0, text), e.config(fg=MUTED)))

    def _cycle(self):
        if not self.universe.get("1.0", "end").strip():
            self.universe.config(fg=MUTED); self.universe.delete("1.0", "end")
            self.universe.insert("1.0", UNIVERSE_EXAMPLES[self._ph_i % len(UNIVERSE_EXAMPLES)])
            self._ph_i += 1
            self.universe.bind("<FocusIn>", self._clear_ghost)
        self.root.after(2600, self._cycle); self._refresh()

    def _clear_ghost(self, _e):
        if self.universe.cget("fg") == MUTED:
            self.universe.delete("1.0", "end"); self.universe.config(fg=TEXT)

    def _universe(self):
        return "" if self.universe.cget("fg") == MUTED else self.universe.get("1.0", "end").strip()

    # -- actions -- #
    def _generate(self):
        from tkinter import filedialog
        from loom.dotloom import _slug
        u = self._universe()
        text, n = preview(u or "untitled", self._conn_dicts())
        p = filedialog.asksaveasfilename(parent=self.root, defaultextension=".oradio",
                                         initialfile=f"{_slug(u)}.oradio", filetypes=[("oradio", "*.oradio")])
        if not p:
            return
        open(p, "w", encoding="utf-8").write(text)
        self.status.config(text=f"generated · {n} bytes", fg=ACCENT)

    def _run(self):
        try:
            from oradio_engine.loader import open_oradio
            from loom.dotloom import Loom, Connection, loom_to_oradio
            res = open_oradio(loom_to_oradio(Loom(self._universe(),
                              [Connection.parse(c) for c in self._conn_dicts()])))
            if not res.ok:
                self.status.config(text=f"needs: {res.report.missing_required or res.report.asks}", fg=MUTED); return
            res.engine.run(steps=8)
            self.status.config(text=f"▶ {len(res.engine.bus)} beats", fg=ACCENT)
        except Exception as exc:
            self.status.config(text=f"· {exc}", fg=MUTED)

    def run(self):
        self.root.mainloop()


def main() -> None:
    LoomDeclaration().run()


if __name__ == "__main__":
    main()
