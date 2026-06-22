# Onboarding your own brick

A **brick** is one small, single-responsibility capability. Bricks are *bricks* — they may be
**python**, **html**, **json**, or whatever. They all share one contract (`loom.concept.v1`): a
`CONCEPT` describing the brick, plus a way to use it. Bookmark discovers every brick under the
roots in `bookmark/brick_kernel.py` → `BRICK_ROOTS`, gives each a unique **emoji**, and lets you
wire or lay them.

To onboard your own: **drop it under a brick root** (e.g. add a folder to `BRICK_ROOTS`, or place
it in an existing trove). Bookmark picks it up on next load. There are two flavors.

---

## 1. A python brick — `CONCEPT` lives in the file

One `.py` file. It carries the `CONCEPT` dict and at least `inspect()` + `run()`.

```python
CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.stats.mean",        # family.subfamily.name — also the folder path
    "kind": "scorer",
    "lang": "python",               # optional; python is the default
    "version": "1.0.0",
    "deterministic": True,
    "inputs": ["math.series_request.v1"],   # packet types in
    "outputs": ["math.scalar.v1"],          # packet types out
    "requires": [], "provides": ["stats"],  # capabilities for wiring/deps
    "side_effects": [],                      # e.g. ["network_read"]
    "ui_slots": [], "tags": ["stats"],
    "emoji": "📊",                  # optional; auto-assigned (unique) if omitted
    "description": "Arithmetic mean of a numeric series.",
}

def inspect():                      # return the CONCEPT
    return CONCEPT

def run(input_packet, context=None):
    xs = input_packet["payload"]["xs"]
    return {"ok": True, "output_packet": {...}, "receipts": [], "issues": [], "meta": {}}

# validate(input_packet, context=None) and receipts(output_packet) are OPTIONAL.
```

Place at `<root>/math.stats/mean.py` → discovered as `math.stats.mean`.

---

## 2. A non-python brick — `CONCEPT` lives in a sidecar

The brick *is* an asset (an `.html` page, a `.json` data file, …). Since the asset can't hold a
python dict, the **same CONCEPT** travels in a sidecar named `<name>.concept.json` next to it.
Two extra fields matter: `lang` and `asset`.

```
<root>/ui.surface/hello.html
<root>/ui.surface/hello.concept.json
```

```json
{
  "api_version": "loom.concept.v1",
  "id": "ui.surface.hello",
  "kind": "surface",
  "lang": "html",
  "asset": "hello.html",          // relative to the sidecar, or an absolute path
  "version": "1.0.0", "deterministic": true,
  "inputs": [], "outputs": ["surface.html.v1"],
  "requires": [], "provides": ["surface.html"],
  "side_effects": [], "ui_slots": [], "tags": ["html", "surface"],
  "emoji": "👋",
  "description": "A self-contained HTML page brick."
}
```

A non-python brick needs no `inspect`/`run` functions — it's "available" when its CONCEPT is
well-formed and its `asset` exists. `run()` on it returns a **surface descriptor** instead of
executing python; an html brick is realized with `brick_kernel.serve_brick(brick)` (serves it
locally and opens the browser). See the worked example: `html_bricks/bricks/ui.surface/hello.*`,
plus `dbooth`/`decoder` registered against real pages.

---

## Opening an oradio straight to a surface

An `.oradio` can open to an html surface on double-click (not just play its ribbon loop). Set the
manifest's `open` field when minting:

```python
mint_oradio(..., open_with={"kind": "html", "brick": "ui.surface.hello"})
```

Absent → the ribbon loop (the default). With it → the kernel serves that brick's page on open.

---

## Emoji

Every brick gets a **unique emoji** (pin one with `CONCEPT["emoji"]`, or it's auto-assigned).
Send a string of emojis to lay a string of bricks (the "lay by emoji…" input in the brick bar).
Categories stay unique; if we ever exhaust the emoji pool, bricks disambiguate by
`(category_emoji, brick_emoji)` and color-skins.
