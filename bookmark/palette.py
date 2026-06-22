"""The brick palette — organized, searchable browse over the brick catalog.

This is the reskin of Bookmark's old top widget-dropdown: with hundreds of bricks (and more
mined every week) a flat menu doesn't scale, so bricks are presented as a searchable tree
grouped by ``family.subfamily``, with a detail pane showing the selected brick's contract
(kind, packet I/O, provides/requires, side-effects). It is **connector-model-agnostic**: it
only browses and emits a "place this brick" intent via ``on_place`` — whatever canvas/wiring
model we land on (blueprint nodes, pyramid stack…) consumes that intent.

Standalone-runnable: ``python -m bookmark.palette [bricks_root]`` opens it against a catalog
so it can be iterated without launching the whole bookmark.py monolith.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from .brick_kernel import ATL_BRICKS, Brick, BrickRegistry

# Dark palette matching bookmark.py's existing surfaces (#0e0e0e family).
BG = "#0e0e0e"
PANEL = "#141414"
FG = "#d6d6d6"
MUTED = "#7a7a7a"
ACCENT = "#4cc9f0"
BROKEN = "#a05050"
DET = "#6cc070"     # deterministic marker
LIVE = "#d0a050"    # non-deterministic / side-effecting marker


class BrickPalette(tk.Frame):
    """A searchable, family-grouped tree of bricks + a contract detail pane.

    Parameters
    ----------
    registry:
        The loaded brick catalog to browse.
    on_place:
        Optional callback invoked with a :class:`Brick` when the user asks to place one
        (double-click or the Place button). The canvas hooks this later; until then it's a
        no-op and placing just prints.
    """

    def __init__(self, master, registry: BrickRegistry,
                 on_place: Optional[Callable[[Brick], None]] = None,
                 manage_theme: bool = False, **kw):
        super().__init__(master, bg=BG, **kw)
        self.registry = registry
        self.on_place = on_place
        self._manage_theme = manage_theme  # only flip the GLOBAL ttk theme when standalone
        self._family_nodes: dict[str, str] = {}

        self._build_style()
        self._build_search()
        self._build_tree()
        self._build_detail()
        self.query.trace_add("write", lambda *_: self.repopulate())
        self.repopulate()

    # ---- construction -----------------------------------------------------
    def _build_style(self) -> None:
        style = ttk.Style(self)
        # Switching ttk themes is application-global, so only do it when we own the window
        # (standalone). Embedded in bookmark.py we must not restyle the host's ttk widgets.
        if self._manage_theme:
            try:
                style.theme_use("clam")  # clam respects bg/fg; default Windows theme doesn't
            except tk.TclError:
                pass
        style.configure("Brick.Treeview", background=PANEL, fieldbackground=PANEL,
                        foreground=FG, borderwidth=0, rowheight=22)
        style.map("Brick.Treeview", background=[("selected", "#23485a")],
                  foreground=[("selected", "#ffffff")])
        style.configure("Brick.Treeview.Heading", background=BG, foreground=MUTED,
                        borderwidth=0)

    def _build_search(self) -> None:
        bar = tk.Frame(self, bg=BG)
        bar.pack(fill="x", padx=8, pady=(8, 4))
        tk.Label(bar, text="bricks", bg=BG, fg=ACCENT,
                 font=("Segoe UI", 11, "bold")).pack(side="left")
        self.count_lbl = tk.Label(bar, text="", bg=BG, fg=MUTED, font=("Segoe UI", 9))
        self.count_lbl.pack(side="right")
        self.query = tk.StringVar()
        # NB: the trace is wired in __init__ AFTER the tree exists, so the placeholder
        # insert below can't fire repopulate() before self.tree is built.
        entry = tk.Entry(self, textvariable=self.query, bg=PANEL, fg=FG,
                         insertbackground=FG, relief="flat",
                         font=("Segoe UI", 10))
        entry.pack(fill="x", padx=8, pady=(0, 6), ipady=4)
        entry.insert(0, "")
        self._placeholder(entry, "search id, tag, packet type…")

    def _build_tree(self) -> None:
        wrap = tk.Frame(self, bg=BG)
        wrap.pack(fill="both", expand=True, padx=8)
        self.tree = ttk.Treeview(wrap, style="Brick.Treeview", show="tree",
                                 selectmode="browse")
        vsb = ttk.Scrollbar(wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        self.tree.tag_configure("broken", foreground=BROKEN)
        self.tree.tag_configure("family", foreground=MUTED)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-1>", lambda e: self._place_selected())

    def _build_detail(self) -> None:
        self.detail = tk.Text(self, height=8, bg=BG, fg=FG, relief="flat",
                              wrap="word", font=("Consolas", 9),
                              insertbackground=FG, padx=8, pady=6)
        self.detail.pack(fill="x", padx=8, pady=(4, 0))
        self.detail.configure(state="disabled")
        self.detail.tag_configure("key", foreground=ACCENT)
        self.detail.tag_configure("det", foreground=DET)
        self.detail.tag_configure("live", foreground=LIVE)
        self.detail.tag_configure("err", foreground=BROKEN)

        self.place_btn = tk.Button(self, text="＋ place on canvas", command=self._place_selected,
                                   bg="#1e3a4d", fg=ACCENT, activebackground="#2a4f65",
                                   relief="flat", font=("Segoe UI", 10), state="disabled")
        self.place_btn.pack(fill="x", padx=8, pady=8, ipady=3)

    # ---- behavior ---------------------------------------------------------
    def repopulate(self) -> None:
        """Rebuild the tree from the registry, filtered by the search query."""
        q = (self.query.get() or "").strip().lower()
        if q == "search id, tag, packet type…":
            q = ""
        self.tree.delete(*self.tree.get_children())
        self._family_nodes.clear()

        shown = 0
        for brick in sorted(self.registry, key=lambda b: b.id):
            if q and not self._matches(brick, q):
                continue
            fam = brick.family or "(loose)"
            parent = self._family_nodes.get(fam)
            if parent is None:
                parent = self.tree.insert("", "end", text=fam, open=bool(q),
                                          tags=("family",))
                self._family_nodes[fam] = parent
            leaf = brick.id.rsplit(".", 1)[-1]
            marker = "" if brick.available else "  ⚠"
            tags = () if brick.available else ("broken",)
            self.tree.insert(parent, "end", iid=brick.id, text=f"{leaf}{marker}", tags=tags)
            shown += 1

        avail = len(self.registry.available())
        self.count_lbl.config(text=f"{shown} shown · {avail}/{len(self.registry)} ok")

    @staticmethod
    def _matches(brick: Brick, q: str) -> bool:
        hay = " ".join((brick.id, brick.kind, " ".join(brick.tags),
                        " ".join(brick.inputs), " ".join(brick.outputs),
                        brick.description)).lower()
        return q in hay

    def _selected_brick(self) -> Optional[Brick]:
        sel = self.tree.selection()
        if not sel:
            return None
        return self.registry.get(sel[0])

    def _on_select(self, _evt) -> None:
        brick = self._selected_brick()
        self.detail.configure(state="normal")
        self.detail.delete("1.0", "end")
        if brick is None:  # a family header
            self.place_btn.config(state="disabled")
            self.detail.configure(state="disabled")
            return
        self._render_detail(brick)
        self.detail.configure(state="disabled")
        self.place_btn.config(state="normal" if brick.available else "disabled")

    def _render_detail(self, brick: Brick) -> None:
        def line(label, value, tag="key"):
            self.detail.insert("end", f"{label} ", (tag,))
            self.detail.insert("end", f"{value}\n")

        line("id", brick.id)
        det_tag = "det" if brick.deterministic else "live"
        det_txt = "deterministic" if brick.deterministic else "live / side-effecting"
        self.detail.insert("end", "kind ", ("key",))
        self.detail.insert("end", f"{brick.kind}   ")
        self.detail.insert("end", f"{det_txt}\n", (det_tag,))
        if brick.inputs or brick.outputs:
            line("in →", ", ".join(brick.inputs) or "—")
            line("out ←", ", ".join(brick.outputs) or "—")
        if brick.provides:
            line("provides", ", ".join(brick.provides))
        if brick.requires:
            line("requires", ", ".join(brick.requires))
        if brick.side_effects:
            line("effects", ", ".join(brick.side_effects), "live")
        if brick.description:
            self.detail.insert("end", f"\n{brick.description}\n")
        if not brick.available:
            self.detail.insert("end", f"\n⚠ unavailable: {brick.error}\n", ("err",))

    def _place_selected(self) -> None:
        brick = self._selected_brick()
        if brick is None or not brick.available:
            return
        if self.on_place is not None:
            self.on_place(brick)
        else:
            print(f"[palette] place intent: {brick.id}")

    # ---- small helpers ----------------------------------------------------
    @staticmethod
    def _placeholder(entry: tk.Entry, text: str) -> None:
        entry.insert(0, text)
        entry.config(fg=MUTED)

        def focus_in(_e):
            if entry.get() == text:
                entry.delete(0, "end")
                entry.config(fg=FG)

        def focus_out(_e):
            if not entry.get():
                entry.insert(0, text)
                entry.config(fg=MUTED)

        entry.bind("<FocusIn>", focus_in)
        entry.bind("<FocusOut>", focus_out)


class BrickBar(tk.Frame):
    """A thin, horizontal top-strip brick organizer.

    The reskin of the old flat ``Widget:`` dropdown: families become cascade submenus under a
    single "browse" button, and a search field flattens the menu to matches. One row tall, so
    it sits above the toolbar without disturbing the existing window layout, yet scales to
    hundreds of bricks. Like :class:`BrickPalette` it only emits a ``on_place`` intent.
    """

    def __init__(self, master, registry: BrickRegistry,
                 on_place: Optional[Callable[[Brick], None]] = None, **kw):
        super().__init__(master, bg=BG, **kw)
        self.registry = registry
        self.on_place = on_place
        self._submenus: list[tk.Menu] = []

        tk.Label(self, text="bricks", bg=BG, fg=ACCENT,
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=(8, 8))

        self.query = tk.StringVar()
        entry = tk.Entry(self, textvariable=self.query, bg=PANEL, fg=FG,
                         insertbackground=FG, relief="flat", width=24, font=("Segoe UI", 10))
        entry.pack(side="left", ipady=3, pady=4)
        BrickPalette._placeholder(entry, "search id, tag, packet type…")

        self.browse = tk.Menubutton(self, text="▾ browse",
                                    bg="#1e3a4d", fg=ACCENT, activebackground="#2a4f65",
                                    relief="flat", font=("Segoe UI", 10), padx=10, pady=3,
                                    cursor="hand2")
        # The menu MUST be a child of the menubutton for it to post on click.
        self.menu = tk.Menu(self.browse, tearoff=0, bg=PANEL, fg=FG,
                            activebackground="#23485a", activeforeground="#ffffff")
        self.menu.configure(postcommand=self._rebuild_menu)
        self.browse.configure(menu=self.menu)
        self.browse.pack(side="left", padx=8)

        # Lay bricks by a string of emojis (the "send emojis -> lay bricks" loop).
        self.emoji_in = tk.Entry(self, bg=PANEL, fg=FG, insertbackground=FG, relief="flat",
                                 width=14, font=("Segoe UI", 12))
        self.emoji_in.pack(side="left", ipady=2, padx=(0, 6))
        BrickPalette._placeholder(self.emoji_in, "lay by emoji…")
        self.emoji_in.bind("<Return>", self._lay_emojis)

        avail = len(registry.available())
        tk.Label(self, text=f"{avail}/{len(registry)} ok", bg=BG, fg=MUTED,
                 font=("Segoe UI", 9)).pack(side="left", padx=6)

    def _q(self) -> str:
        q = (self.query.get() or "").strip().lower()
        return "" if q == "search id, tag, packet type…" else q

    def _rebuild_menu(self) -> None:
        self.menu.delete(0, "end")
        for sub in self._submenus:  # avoid leaking submenu objects across rebuilds
            sub.destroy()
        self._submenus.clear()

        bricks = [b for b in sorted(self.registry, key=lambda b: b.id) if b.available]
        q = self._q()
        if q:
            matches = [b for b in bricks if BrickPalette._matches(b, q)]
            if not matches:
                self.menu.add_command(label="(no matches)", state="disabled")
            for b in matches[:60]:
                self.menu.add_command(label=f"{b.emoji}  {b.id}", command=lambda br=b: self._place(br))
            return

        fams: dict[str, list[Brick]] = {}
        for b in bricks:
            fams.setdefault(b.family or "(loose)", []).append(b)
        for fam in sorted(fams):
            sub = tk.Menu(self.menu, tearoff=0, bg=PANEL, fg=FG,
                          activebackground="#23485a", activeforeground="#ffffff")
            for b in fams[fam]:
                leaf = b.id.rsplit(".", 1)[-1]
                sub.add_command(label=f"{b.emoji}  {leaf}", command=lambda br=b: self._place(br))
            self._submenus.append(sub)
            self.menu.add_cascade(label=f"{fam}  ({len(fams[fam])})", menu=sub)

    def _place(self, brick: Brick) -> None:
        if self.on_place is not None:
            self.on_place(brick)
        else:
            print(f"[brickbar] place intent: {brick.id}")

    def _lay_emojis(self, _event=None) -> None:
        """Parse the emoji input into bricks and lay each (left-to-right)."""
        text = self.emoji_in.get()
        if text == "lay by emoji…":
            return
        bricks = self.registry.bricks_for_emojis(text)
        for brick in bricks:
            self._place(brick)
        self.emoji_in.delete(0, "end")


def _demo(root_path=ATL_BRICKS) -> None:
    registry = BrickRegistry.from_path(root_path)
    win = tk.Tk()
    win.title("Bookmark · brick palette")
    win.configure(bg=BG)
    win.geometry("360x720")
    palette = BrickPalette(win, registry, manage_theme=True,
                           on_place=lambda b: print(f"PLACE -> {b.id}  ({', '.join(b.outputs) or 'no output'})"))
    palette.pack(fill="both", expand=True)
    win.mainloop()


if __name__ == "__main__":
    import sys
    _demo(sys.argv[1] if len(sys.argv) > 1 else ATL_BRICKS)
