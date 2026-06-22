# RibbonOS · Oracle Radio

A simulation OS where every *thing* is an **`.oradio`** — an "Oracle Radio": a tiny (KB) declaration
that a general, domain-blind engine decodes and runs, wrapped in a seamless looping visual. You
arrange oradios into a **`.loom`** (a universe / relationship map) and fly through them in
**RibbonOS** (a galaxy/carousel shell) where every crossing between oradios is a deterministic,
seeded transition. Heavy capability (LLMs, voices, clips, live data) is resolved at the **endpoint**
by the Club — never shipped inside the artifact.

Three layers:

| Layer | What it is | Where |
|---|---|---|
| **`.loom`** | the universe — which oradios exist and who is bonded ("soulmates"); drives the galaxy map | `loom/`, `oradio_engine/loom_graph.py`, `*.loom` |
| **`.oradio`** | the KB declaration: a world, inputs, a skin+voice, outputs — references, no content. Minted by the kernel (Bookmark) | `spec/`, `bookmark/mint.py`, `exports/kernel.oradio` |
| **engine** | the domain-blind decoder that runs an oradio into a bus of rows (no LLM/audio inside) | `oradio_engine/` |

## Quickstart

```bash
git clone https://github.com/evengineer1ng/loom.git
cd loom
pip install -e .                 # core (stdlib + PyYAML)
pip install opencv-python numpy pillow   # RibbonOS visuals (Tk ships with python.org Python)

python ribbon_os_shell.py        # the galaxy/carousel shell (opens the active .loom)
# double-click a .oradio in your file manager, or:
python oradio_player.py exports/kernel.oradio   # opens the kernel -> Bookmark (the authoring app)
```

`kernel.oradio` is the genesis artifact: the **Bookmark** authoring kernel and your "door home"
(*"Come back here when you're lost"*). Only a kernel may mint a kernel; any oradio may mint a
non-kernel. Ribbon media (boot/pts/skins) lives outside the repo — set `RIBBON_OS_MEDIA_ROOT` or
drop it in `media/`; missing media degrades gracefully.

## The booth — a tape speaks (no model, no GPU)

Underneath the visuals, a *tape* (a finished F1 race, a heart-rate log, an RSS feed) becomes
language you read or hear, **deterministically** — a small grammar gives it a voice, no LLM at
runtime. ~5 orders of magnitude faster than a local LLM, 0% confabulation. The lesson: use a model
to *author* the renderer (compile time), not to *narrate* (runtime). See
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md), [`docs/BENCHMARK.md`](docs/BENCHMARK.md).

```bash
python -m oradio_engine open spec/examples/me.oradio --steps 5   # run an oradio headless
python -m oradio_engine club                                     # endpoint capability status
pytest                                                            # engine + shim + format suite (headless)
```

## Repo map

```
ribbon_os_shell.py    RibbonOS — the galaxy/carousel runtime: boot/pts/door playback, the
                      ribbon-media state machine, loom-switching, speed-of-light traversal.
bookmark.py           the kernel authoring app (Bookmark) — minted, it BECOMES kernel.oradio.
bookmark/             the kernel + brick system: mint.py (mint authority), transitions.py (the
                      deterministic carrier + transition personalities), door.py, launch.py
                      (the open-resolver), brick_kernel.py (loom.concept.v1 + registry).
oradio_engine/        the domain-blind .oradio decoder + the 5-verb organ contract + loom graph
                      + loom_runtime (crossover bake, active-loom, styles) + the Club bridge.
loom/                 the .loom authoring surface (app2.py) + dotloom.
bricks/               kernel-side bricks (kernel.authoring.bookmark, ui.frame, ui.shortcut).
radio_bricks/         the mined garden — 469 bricks.   atl_bricks/  — 150 mined bricks.
html_bricks/          polyglot html/json surfaces (club / loom / ui).
spec/                 the .oradio format — examples + ORADIO_FORMAT / SCHEMA docs.
plugins/organs/       reference simulation organs (oracle, neikos, forkuniverse).
tools/ bench/ tests/  bake/report/benchmark CLIs · datasets · the test suite.
docs/                 architecture, the loom, CANON, and the repo-topology + migration plan.
*.py (root)           endpoint/runtime: player UI, resolver, provisioning, voice, theme, booth…
archive/              retired code kept for reference (not imported).
```

**The one rule that matters: the decoder stays pure** — `tests/test_engine_purity.py` fails the
build if a heavy dep (PIL/numpy/cv2/tkinter/audio) creeps into `import oradio_engine`, since that
would fork the file format. RibbonOS visuals live in `bookmark/`/root, never in the engine core.

## Where the project is

Single repo for now (this one). The clean five-repo split — `kernel` · `ribbon-os` · `radio-bricks`
· `atlas` · `oradio-gallery` — is planned in [`docs/CANON_REPO_TOPOLOGY.md`](docs/CANON_REPO_TOPOLOGY.md)
and [`docs/REPO_MIGRATION.md`](docs/REPO_MIGRATION.md); it's reorganization, deferred until the
runtime path is solid. Current canon index: [`docs/CANON.md`](docs/CANON.md).

## License

Dual-scoped (see [`LICENSING.md`](LICENSING.md)): the **format/spec** (`spec/`) is **Apache-2.0** so
anyone can implement `.oradio`/`.loom` freely; the **engine, RibbonOS, and apps** are **AGPL-3.0**
(no closed SaaS forks). Commercial dual-licensing is available — copyright held in one place.
