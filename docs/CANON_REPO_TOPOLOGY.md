# Canon Repo Topology

Status date: `2026-06-21`

This doc locks the repo-scale topology for the first real Loom / RibbonOS / Kernel ship.

It answers one practical question:
how do we package the family cleanly without collapsing kernel, runtime, bricks, determinism, and examples into one confused repo?

## First ship

The first public ship is two artifacts:

1. `RibbonOS Bootstrap`
2. `kernel.oradio`

This resolves the bootstrap paradox honestly.

`kernel.oradio` can only be the sole release artifact after a machine already has a `.oradio` opener.
So first release ships a tiny opener/bootstrap plus the kernel artifact itself.

## User flow

The intended first-run flow is:

1. User installs or runs `RibbonOS Bootstrap`.
2. User double-clicks `kernel.oradio`.
3. The opener routes `.oradio` files into RibbonOS.
4. `kernel.oradio` opens into the Club Manager.
5. Club Manager handles lightweight onboarding and setup.
6. Club Manager offers install choices:
   - kernel bricks
   - RibbonOS runtime assets
   - some, all, or none of the current brick garden
7. After that, the machine is a normal RibbonOS install.

The Club Manager is the front door for package acquisition and first-machine setup.
The kernel is the authority and bootstrap artifact.
RibbonOS is the runtime that actually opens and plays `.oradio` files.

## Repo split

Treat repos the same way we treat bricks: as composable units with a clear contract.

### `kernel`

Purpose:
- holds the canonical `kernel.oradio`
- holds `bookmark.py` as the source workstation for the canon kernel line
- holds kernel lineage rules
- holds kernel mint policy
- holds kernel export tests
- defines what a kernel may mint and what a non-kernel may mint

Belongs here:
- `bookmark.py`
- `bookmark/mint.py`
- kernel-specific mint/export helpers that define or enforce kernel law
- kernel lineage and descendant rules
- root-kernel trust rules
- soulmate / mint-law policy if it is kernel law
- export fixtures for the shipped kernel

Does not belong here:
- full runtime
- giant brick garden
- Atlas data payloads

The `kernel` repo is identity and authority, not the whole system.

### `ribbon-os`

Purpose:
- holds the runtime that opens `.oradio`
- holds the player, loader, Club wiring, and install/update machinery
- holds the bootstrap opener or the code that builds it

Belongs here:
- RibbonOS player/runtime
- Club Manager HTML and its runtime bridge
- loader, open path, club path, render path
- thumbnail and visual runtime surfaces
- installer/update logic
- `.oradio` file association logic

Does not belong here:
- the full mined brick inventory
- Atlas loombit payload banks
- every public example `.oradio`

RibbonOS is the runtime repo.

### `radio-bricks`

Purpose:
- holds the shared mined brick garden

Belongs here:
- Python bricks
- HTML bricks
- JSON bricks
- future non-Python concept bricks
- decomposition docs for mined concepts

Does not belong here:
- kernel authority
- full runtime shell
- heavyweight determinism payload stores

This is the main capability garden.
It is normal for it to contain hundreds of bricks.

### `atlas`

Purpose:
- holds the determinism engine and loombit architecture

Belongs here:
- determinism engine
- loombit architecture
- shard, bank, and dict packing
- heavyweight deterministic payloads
- reproducibility logic tied to Atlas-specific data layout

Does not belong here:
- generic RibbonOS runtime
- kernel mint authority
- the whole brick garden

Atlas is not just another mined concept seam.
It is a first-class substrate and must remain explicit.

### `oradio-gallery`

Purpose:
- holds public `.oradio` artifacts and examples

Belongs here:
- example looms
- public stations
- showcase `.oradio` artifacts
- possibly public descendant kernels that are intended as examples rather than core authority

Does not belong here:
- runtime
- Club implementation
- giant brick inventory
- Atlas banks

This is the friendly browseable repo the Club can point to.

## Ownership boundaries

The clean mental model is:

- `kernel` decides authority
- `ribbon-os` runs artifacts
- `radio-bricks` supplies reusable concepts
- `atlas` supplies determinism substrate
- `oradio-gallery` supplies public artifacts

If a thing answers "who is allowed," it probably belongs to `kernel`.
If a thing answers "how does it open or install," it probably belongs to `ribbon-os`.
If a thing answers "what reusable concept do we have," it probably belongs to `radio-bricks`.
If a thing answers "what makes replay and packing deterministic at scale," it probably belongs to `atlas`.
If a thing answers "what can people download and tune into," it probably belongs to `oradio-gallery`.

## Club package model

The Club should manage packages from multiple repos, not assume one mega-repo.

That means Club should think in packages like:

- `kernel`
- `ribbon-os`
- `radio-bricks`
- `atlas`
- `oradio-gallery`

And install or update them independently.

This keeps the family modular:
- runtime can update without changing kernel law
- brick garden can grow without bloating runtime
- Atlas can stay heavyweight without infecting every repo
- gallery artifacts can proliferate without muddying canon code

## Kernel law

The kernel rule remains:

- any `.oradio` may mint a non-kernel `.oradio`
- only a kernel may mint a kernel
- every minted kernel must carry lineage back to a parent kernel
- the first shipped kernel is the root trust anchor for this family

This makes the kernel repo special without making the whole ecosystem closed.

## What ships where

For the first clean public topology:

- release attachment: `RibbonOS Bootstrap`
- release attachment: `kernel.oradio`
- repo: `kernel`
- repo: `ribbon-os`
- repo: `radio-bricks`
- repo: `atlas`
- repo: `oradio-gallery`

## Immediate implications

- We should stop treating the determinism engine as an implicit seam hidden inside older repos.
- The Club Manager should be treated as a package installer and repo-router, not just a setup screen.
- `bookmark.py` should be treated as kernel-class source, not RibbonOS runtime source.
- `kernel.oradio` should be built and exported from Bookmark, but should live canonically in the `kernel` repo once exported.
- RibbonOS should not try to physically contain every brick or every heavy deterministic payload by default.

## Short version

The family should ship as a small bootstrap pair and live as five clear repos:

- `kernel` for authority
- `ribbon-os` for runtime
- `radio-bricks` for reusable concepts
- `atlas` for determinism
- `oradio-gallery` for public artifacts
