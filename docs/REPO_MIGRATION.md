# Repo cartography & migration plan

> Goal this serves: **start using RibbonOS for real → mint the first real `kernel.oradio` (codename
> Bookmark).** This is an *extraction map*, not push-readiness. It says: future repo name · what
> moves in · what must stay out · first export targets from the current mixed checkouts.

Current `oracle-radio/`, `Radio-OS/`, and the `opencloset`/`openclaw` mining outputs are mixed
staging grounds. This carves them into canon repos.

---

## The five canon repos

### `kernel` — *who is allowed*
Tiny, strict, authoritative. **Mint authority lives here, not in ribbon-os.**
- **Owns:** the kernel lineage law (only a kernel mints a kernel; any minter mints `.oradio`s),
  mint authorization, root trust + descendant rules.
- **Owns `bookmark.py`** — the kernel-builder UI (the thing that, minted, *becomes* `kernel.oradio`).
- **Owns `kernel.oradio`** (the genesis canon kernel artifact).
- **Owns the mint engine:** `bookmark/mint.py` (palindrome loop bake, soulmate + kernel-exception,
  zip container, optional mp3), and the `.oradio` manifest schema in `bookmark/manifest.py`.
- The bookmark authoring surface that ships with it: `bookmark/palette.py`, `bookmark/canvas.py`,
  `bookmark/draft.py`.
- **DECISION (the debate):** `bookmark.py` is **kernel-class, not ribbon-os.** ribbon-os *launches*
  it; it does not *own* it. (Option B later: split into `kernel-contract` + `canon-kernels` if the
  law becomes a public standard — not yet.)

### `ribbon-os` — *how it runs / opens / installs*
The runtime shell. Depends on `kernel`, `radio-bricks`, `atlas`.
- **Owns:** `ribbon_os_shell.py`, the top toolbar (now brick-hosted: current toolbar + Loom),
  carousel + galaxy, the ribbon-media state machine + **transition/door PLAYBACK** + boot flow.
- **Owns the `.oradio` open/launch flow:** `bookmark/launch.py`, `oradio_player.py`,
  `oradio_player_ui.py`, `oradio_resolver.py`, `oradio_validate.py`, `antenna_resolver.py`.
- **Owns the Club runtime bridge:** `oradio_engine/club.py`, `oradio_engine/club_packages.py`,
  `club_gate.py`, `descriptor_club_gate.py`, `bookmark/club_manager.py`, and the warmed
  `html_bricks/bricks/club.surface/club.html` surface (the *contract* is shared; see note below).
- **Owns the `.oradio` runtime engine** (the deterministic per-oradio sim that emits a bus of rows,
  no LLM/audio): `oradio_engine/{contract,live,observation,detect,evidence,dipole,binding,
  descriptor,federation,lens,index,registry,loader,thread,inquiry,mix,antenna,plugins}.py`.
  *(This is the runtime engine; the determinism-at-SCALE substrate is `atlas`, below.)*
- **Owns Loom the surface:** `loom/app2.py` (the toolbar brick) + `.loom` handling
  (`oradio_engine/loom_graph.py`, `loom/dotloom.py`). The `.loom` *artifacts* go to gallery.
- Theme/config/transport: `radio_os_theme.py`, `app_paths.py`, `provisioning.py`, settings, web shell.
- Bootstrap opener build path (the optional `ribbon-bootstrap` split can wait — keep here for now).

### `radio-bricks` — *what reusable concept exists*  (the 600+ garden)
The shared brick garden **and** the brick system itself. Depended on by everyone.
- **Owns the brick system:** `bookmark/brick_kernel.py` (loom.concept.v1 contract, loader,
  registry, emoji addressing) + the brick manifest/tape half of `bookmark/manifest.py`.
- **Owns the bricks:** `bricks/` (LOCAL — picture-frame, etc.), `html_bricks/`, plus the mined
  Python/HTML/JSON bricks (`Radio-OS/radio_bricks/bricks`, `…/atl_bricks/bricks`) + mined concept docs.
- **Owns the visual-morphing / transition brick** (the user: "this engine IS a brick"):
  `bookmark/transitions.py` + `bookmark/door.py` + the OG engine `oradio_engine/visual_thumbnail.py`,
  `visual_tape.py`, `visual_index.py`. *(Consumed by kernel at mint-time and ribbon-os at play-time.)*
- Likely also the speech kernel brick: `oradio_engine/speech.py`.

### `atlas` — *what makes replay deterministic at scale*
- **Owns:** the determinism engine, loombits, shard/bank/dict storage strategy, heavyweight
  deterministic payloads, Atlas-specific compile/lookup.
- Sources: the `opencloset-courtroom` fork's `courtroom/atlas.py` + atlas pack, `bench/atlas_recall`,
  and any loombit/retrieval substrate the engine leans on.

### `oradio-gallery` — *what people download / tune into / browse*
Content, not engine.
- **Owns:** public `.oradio` examples (`spec/examples/*.oradio`, `exports/*.oradio`), featured
  looms/stations, shared `.loom` constellations, the HF/loomspeech dataset (`huggingface/`, `bench/`).

### Optional / later
- `club-catalog` — only if Club package metadata outgrows ribbon-os (manifests/channels/profiles/
  install recipes). **Not yet** — the contract lives in ribbon-os for now.
- `ribbon-bootstrap` — only if the opener wants separate tiny versioning. Else inside ribbon-os.

---

## Artifact boundaries
| Artifact | Home |
|---|---|
| `kernel.oradio` | **`kernel`** (it's THE canon kernel) |
| other `.oradio` | `oradio-gallery` |
| `.loom` (constellations) | `oradio-gallery` (points at existing `.oradio` nodes) |
| Club package manifest/contract | `ribbon-os` for now → `club-catalog` later |
| bricks (`*.py` / `*.concept.json`) | `radio-bricks` |

---

## ⚠️ Whole picture — it is NOT just bricks
The brick repo is huge and easy to over-index on. **600 organized bricks ≠ a bootable
`kernel.oradio`.** The critical path to "use RibbonOS for real" is mostly *non-brick*:

1. **Mint authority + lineage enforcement** (`kernel`): `mint.py` must honor the lineage law; the
   genesis kernel is the root exception. Without this, you can't *legitimately* mint `kernel.oradio`.
2. **Genesis ASSETS** (no brick provides these): a real 2.5–5s loop video for the kernel, its
   declaration, optional mp3, and the soulmate/kernel-exception. Someone must author the kernel's look.
3. **Visual-continuity engine** (a brick, but load-bearing): boot door + crossovers must actually
   play for boot to feel real. Don't let it get filed away as "just another brick."
4. **Open / launch / boot flow** (`ribbon-os`): opening `kernel.oradio`, the boot-door playback
   (already wired), carousel/galaxy.
5. **Club runtime bridge** (`ribbon-os`): install/download fulfillment is still a stub ("comes
   next"). To use for real, the kernel package must at minimum resolve locally — the bridge can't be vapor.
6. **Determinism substrate** (`atlas`): if oradios reference atlas retrieval/loombits, it must exist.
7. **Settings/global config** (`ribbon-os`): the global config the kernel edits.

**Critical path to mint+boot `kernel.oradio` (Bookmark):**
`kernel` (bookmark.py + mint.py + lineage law) · genesis loop asset + declaration ·
`radio-bricks` (the bricks the kernel is made of + the transition brick) ·
`ribbon-os` (open + boot door + carousel) · `atlas` (only if referenced)
→ run `bookmark.py` → mint `kernel.oradio` (is_kernel=True, genesis exception) → place in a `.loom`
→ boot RibbonOS → door into it.

---

## First export targets (extract these first)
1. `kernel`: `bookmark.py`, `bookmark/mint.py`, `bookmark/manifest.py` (mint half), the lineage law
   doc. Then mint the genesis `kernel.oradio` THROUGH it.
2. `radio-bricks`: `bookmark/brick_kernel.py`, `bricks/`, `html_bricks/`, `bookmark/transitions.py`,
   `bookmark/door.py`, `oradio_engine/visual_*`. Point `BRICK_ROOTS` at the new repo.
3. `ribbon-os`: `ribbon_os_shell.py`, `bookmark/launch.py`, `oradio_player*.py`, the Club bridge,
   `loom/app2.py`, the `oradio_engine` runtime core.
4. `atlas`: the `opencloset-courtroom` atlas pieces + `bench/atlas_recall`.
5. `oradio-gallery`: `spec/examples/`, `exports/`, sample `.loom`s, `huggingface/`.

> Cross-repo seams to keep clean: `ribbon-os → kernel` (open kernel.oradio + launch bookmark),
> everything `→ radio-bricks` (the brick system), `kernel`/`ribbon-os → atlas` (only where determinism
> at scale is needed). Keep `radio-bricks` and `atlas` dependency-free of `ribbon-os`/`kernel`.
