"""Author identity + provenance seed — the one-time questionnaire behind every mint.

Convergence (2026-06-21): oracle-radio is obsessed with provenance. Every non-kernel oradio has a
soulmate, so a LINEAGE forms (kernel -> RadioOS -> ...). Stamping WHO authored each link makes that
lineage traceable cheaply: `kernel.oradio by evengineer1ng <seed>` is far more traceable than a
bare `kernel.oradio`, and it costs almost nothing if we do it now, before the chain grows.

The Club raises a ONE-TIME, 3-question questionnaire on a person's first oradio:

  1. What's your name — how do you identify yourself?   (the display handle; may collide)
  2. Who are you?   (a free-text DECLARATION; we infer nothing — "software engineer" or
                     "fartsxdxdxdxd", we don't care; it's just entropy)
  3. What thread are you trying to pull?   (more entropy)

Each answer is converted PURELY to a seed segment; the three join as `seg.seg.seg` = your personal
**identity seed**. Two people who both type "Bob" for Q1 still differ on their seed (Q2+Q3 are the
disambiguator) — so the handle can collide but the provenance fingerprint best-effort can't, short
of someone intentionally answering all three identically (out of scope for a local app).

This is NOT login / not secure storage — it's a local-first provenance seed. But the schema is
versioned and the raw answers are kept locally, so a healthy later expansion (signing keypair,
federation) can derive from the same seed WITHOUT a refactor of already-minted oradios: an oradio
only ever carries the small `{name, seed, identity_version}` stamp.

Pure/headless (no tkinter, no ffmpeg) — the questionnaire UI lives in the Club/Bookmark shells.
"""

from __future__ import annotations

import hashlib
import json
import re
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

IDENTITY_VERSION = "loom.identity.v1"
_SEGMENT_HEX = 8          # hex chars per answer segment (32-bit each; 96-bit composite)


# ---------------------------------------------------------------------------
# seed derivation (pure)
# ---------------------------------------------------------------------------

def _normalize(answer: str) -> str:
    """Fold an answer to a stable form before hashing: trim, lowercase, collapse whitespace.

    Deliberately light — we want "Bob" and " bob " to seed alike (a person re-answering shouldn't
    drift), but two genuinely different answers to seed apart."""
    return re.sub(r"\s+", " ", (answer or "").strip().lower())


def derive_segment(answer: str) -> str:
    """One answer -> one stable seed segment (sha256 of the normalized text, first 8 hex)."""
    return hashlib.sha256(_normalize(answer).encode("utf-8")).hexdigest()[:_SEGMENT_HEX]


def derive_seed(name: str, who: str, thread: str) -> str:
    """The three answers -> `seg.seg.seg` identity seed. Deterministic + replayable."""
    return ".".join(derive_segment(a) for a in (name, who, thread))


# ---------------------------------------------------------------------------
# the identity (model + local storage)
# ---------------------------------------------------------------------------

@dataclass
class AuthorIdentity:
    """A person's local provenance identity. The raw answers stay local; only `name` + `seed` are
    ever stamped into an oradio."""

    name: str
    who: str
    thread: str
    seed: str
    created_at: str = ""
    version: str = IDENTITY_VERSION

    @classmethod
    def create(cls, name: str, who: str, thread: str) -> "AuthorIdentity":
        return cls(
            name=name.strip(), who=who.strip(), thread=thread.strip(),
            seed=derive_seed(name, who, thread),
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    def to_dict(self) -> Dict[str, object]:
        return {
            "version": self.version,
            "name": self.name,
            "who": self.who,
            "thread": self.thread,
            "seed": self.seed,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, object]) -> "AuthorIdentity":
        return cls(
            name=str(d.get("name", "")),
            who=str(d.get("who", "")),
            thread=str(d.get("thread", "")),
            seed=str(d.get("seed", "")),
            created_at=str(d.get("created_at", "")),
            version=str(d.get("version", IDENTITY_VERSION)),
        )

    def stamp(self) -> Dict[str, object]:
        """The minimal provenance block stamped into a minted oradio (no raw answers leave local)."""
        return {"name": self.name, "seed": self.seed, "identity_version": self.version}


def identity_path(club_dir: str | Path) -> Path:
    return Path(club_dir) / "identity.json"


def has_identity(club_dir: str | Path) -> bool:
    p = identity_path(club_dir)
    if not p.exists():
        return False
    try:
        return bool(json.loads(p.read_text(encoding="utf-8")).get("seed"))
    except Exception:
        return False


def load_identity(club_dir: str | Path) -> Optional[AuthorIdentity]:
    p = identity_path(club_dir)
    if not p.exists():
        return None
    try:
        return AuthorIdentity.from_dict(json.loads(p.read_text(encoding="utf-8")))
    except Exception:
        return None


def save_identity(club_dir: str | Path, identity: AuthorIdentity) -> Path:
    p = identity_path(club_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(identity.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return p


def set_identity(club_dir: str | Path, name: str, who: str, thread: str) -> AuthorIdentity:
    """Answer the questionnaire once and persist it locally. Returns the identity."""
    identity = AuthorIdentity.create(name, who, thread)
    save_identity(club_dir, identity)
    return identity


def author_stamp(club_dir: str | Path) -> Optional[Dict[str, object]]:
    """The current author's provenance stamp for minting, or None if no identity is set yet."""
    identity = load_identity(club_dir)
    return identity.stamp() if identity else None


# ---------------------------------------------------------------------------
# stamping existing bundles (retro-provenance, cheap + in place)
# ---------------------------------------------------------------------------

def read_author(oradio_path: str | Path) -> Optional[Dict[str, object]]:
    """The author stamp already inside a minted .oradio, or None."""
    try:
        with zipfile.ZipFile(oradio_path) as zf:
            m = json.loads(zf.read("manifest.json").decode("utf-8"))
        a = m.get("author")
        return a if isinstance(a, dict) else None
    except Exception:
        return None


def stamp_oradio(oradio_path: str | Path, author: Dict[str, object], *,
                 overwrite: bool = False) -> bool:
    """Add (or replace, if `overwrite`) the `author` provenance block on an already-minted .oradio.

    Rewrites only manifest.json inside the zip; loop.mp4 / anchors are copied verbatim. Returns
    True if the file was (re)stamped, False if it already had an author and overwrite=False. This
    is additive metadata on the mint bundle (not the frozen .loom/descriptor schema)."""
    oradio_path = Path(oradio_path)
    with zipfile.ZipFile(oradio_path) as zf:
        names = zf.namelist()
        manifest = json.loads(zf.read("manifest.json").decode("utf-8"))
        others = {n: zf.read(n) for n in names if n != "manifest.json"}

    if manifest.get("author") and not overwrite:
        return False
    manifest["author"] = author

    tmp = oradio_path.with_suffix(".oradio.tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False))
        for n, data in others.items():
            zf.writestr(n, data)
    tmp.replace(oradio_path)
    return True


def stamp_many(oradio_paths: List[str | Path], author: Dict[str, object]) -> Dict[str, int]:
    """Stamp a batch of unstamped .oradios. Returns {'stamped': n, 'skipped': n}."""
    stamped = skipped = 0
    for p in oradio_paths:
        try:
            if stamp_oradio(p, author):
                stamped += 1
            else:
                skipped += 1
        except Exception:
            skipped += 1
    return {"stamped": stamped, "skipped": skipped}
