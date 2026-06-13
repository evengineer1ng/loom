# Oracle Radio

A domain-blind **simulation codec**. An `.oradio` file is to a simulation what a
`.png` is to an image: a tiny (KB) declaration that a general engine *decodes* and
runs without knowing the domain. Heavy capability (LLMs, voices, theme clips, live
data) is resolved at the **endpoint** by the Club — never shipped in the artifact.

This repo ships three things:

| Ship target | What it is | Where it lives here |
|---|---|---|
| **loom** | The act of authoring an `.oradio` (a word — verb/noun/instrument, like *dream*: "I loom a world"), through a 4-question I/O contract — **Q1 world · Q2 inputs · Q3 theme+voice · Q4 outputs** — where the surface is just *where you loom*. | `radio_os_studio.py`, the player/UI modules, `docs/THE_LOOM.md` (surface still in progress) |
| **the `.oradio` format** | The KB declaration: a world, its inputs, a skin+voice, its outputs — all references, no content. That low-level-ness is *why* it's a portable file. | `examples/*.oradio`, `oradio_engine/descriptor.py`, `docs/ORADIO_FORMAT.md`, `docs/ORADIO_SCHEMA_V2.md` |
| **the club** | Machine-level capability resolver + the host the engine runs in (the bouncer): configure once, reuse forever; ask only when new/changed/vanished; install missing plugins from wherever they live. | `oradio_engine/club.py`, `provisioning.py` |

## The boundary (why this repo is small)

- **Engine core** (`oradio_engine/*.py`) — pure Python stdlib. The decoder is
  domain-blind. The only hard third-party dep is **PyYAML**, used solely to parse
  `.oradio` files.
- **Shims** (`oradio_engine/shims/`) — adapter *contracts*. They consume an organ's
  *output* (a state object handed in, or a read-only path to its emitted artifact —
  e.g. `league.sqlite`), never the organ's source. So no organ runtime is vendored
  here.
- **Endpoint** — the Club config (`~/.oradio_club/club.json`), resolved heavy assets,
  and the live data the shims point at. None of it is in the repo.

The simulation *organs* (ForkUniverse, Neikos, FTB, Oracle, ATL, MoCo) stay in their
own homes; the engine points at their emitted data. Oracle Radio is the decoder + the
format + the examples — not the organ host.

## Run

```bash
pip install -e .          # core (stdlib + PyYAML)
pip install -e ".[runtime]"  # + audio runtime (numpy/requests/sounddevice/soundfile)

python -m oradio_engine open examples/me.oradio --steps 5
python -m oradio_engine club            # endpoint capability status

pytest                    # engine + shim + format test suite
```

## The 5-verb organ contract

Every organ federates through one interface (`oradio_engine/contract.py`):
`identity · advance · observe · read_truth · apply_input`, with an explicit
`DETERMINISTIC` vs `LIVE` determinism class. A run is `world(t) = f(seed, tape[0..t])`
— deterministic organs replay byte-identical; live organs record to an immutable
intake tape so replay is byte-identical too.

See `docs/SIMULATION_ENGINE.md` (canonical), `docs/CANON.md` (current-canon index),
and `docs/THE_LOOM.md`.
