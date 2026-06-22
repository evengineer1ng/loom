"""Bookmark — the .oradio authoring kernel.

Bookmark composes oradio apps out of *bricks*: small single-responsibility modules
conforming to the ``loom.concept.v1`` contract (see ``brick_kernel``). This package is
the authoring substrate the canvas + mint sit on; it is NOT a runtime for the old
Radio-OS station app.
"""

from .brick_kernel import (
    Brick,
    BrickRegistry,
    Pipeline,
    WireError,
    make_packet,
    discover,
)

__all__ = [
    "Brick",
    "BrickRegistry",
    "Pipeline",
    "WireError",
    "make_packet",
    "discover",
]
