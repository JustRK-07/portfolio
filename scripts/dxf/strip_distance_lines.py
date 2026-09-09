#!/usr/bin/env python3
"""
Strip the leftover distance-line geometry from a structural GA DXF.

Background
----------
ISGEC Heavy Engineering DXF exports ship with two parallel sets of
dimension-line artifacts:

    1. `StraightDimension-*` blocks — referenced by `STR_DRAWING` INSERTs
       and rendered as the visible "distance between two points" lines.
    2. `_BLUE_StraightDimension-*` blocks — byte-identical color-override
       mirror copies left over from `SETBYLAYER` / `SETBYBLOCK` macros.

Both block families sit on layer `_BLUE_6` (the DIMLAYER of ISGEC's
dimension style). A prior v1 cleanup pass typically hides the layer in a
layer state but never deletes the geometry, so any tool that walks raw
entity data (ezdxf, dxf.js, several CAD importers) keeps drawing them.

This script strips the geometry at the block-table level so the artifact
is gone, not hidden. It also covers every AutoCAD dimension-block prefix
family in case a future ISGEC export switches styles.

What it removes
---------------
1. Any block definition whose name starts with a recognized AutoCAD
   "exploded-dimension" prefix:

       StraightDimension-*  AlignedDimension-*
       DimAligned-*         LinearDimension-*      DimLinear-*
       AngularDimension-*   DimAngular-*
       RadialDimension-*    DiametricDimension-*
       OrdinateDimension-*  DimOrdinate-*
       ArrowDimension-*

   Plus the `_BLUE_`-prefixed color-override variant of every one.

2. Every INSERT inside the `--container` block (default `STR_DRAWING`)
   that targets one of those blocks.

3. Sets the dimension-only layer `_BLUE_6` OFF in the layer table when it
   exists, as a belt-and-suspenders safety net for downstream renderers
   that walk raw geometry.

What it leaves alone
--------------------
- `MECH_DRAWING` and every entity inside it (mechanical GA is unrelated).
- `STR_DRAWING` itself, plus all `Part-*`, `Bolt-*`, `Connection-*`,
  `GridLine-*` inserts — the real structural members.
- Any block whose name doesn't match a recognized dimension prefix.
- All other layers; only `_BLUE_6` is touched.

Verification
------------
Prints before/after counters for:
  - dimension-family block definitions (any recognized prefix)
  - INSERTs in the container block that target dimension-family blocks
  - LINE entities on layer `_BLUE_6`

Usage
-----
    python3 strip_distance_lines.py <input.dxf> <output.dxf>
    python3 strip_distance_lines.py --container=GADrawing <input.dxf> <output.dxf>

The script never modifies the input file. Output is written to <output.dxf>.

Requires: ezdxf (pip install ezdxf>=1.4)
"""

import argparse
import sys

import ezdxf

# Recognized AutoCAD "exploded-dimension" block-name prefixes.
_BASE_PREFIXES = (
    "StraightDimension-", "AlignedDimension-",
    "DimAligned-", "LinearDimension-", "DimLinear-",
    "AngularDimension-", "DimAngular-",
    "RadialDimension-", "DiametricDimension-",
    "OrdinateDimension-", "DimOrdinate-",
    "ArrowDimension-",
)
DIMENSION_PREFIXES = _BASE_PREFIXES + tuple("_BLUE_" + p for p in _BASE_PREFIXES)


def is_dimension_block(name: str) -> bool:
    return any(name.startswith(p) for p in DIMENSION_PREFIXES)


def collect_dimension_blocks(doc):
    """Return (plain_blocks, blue_blocks) — both lists of BlockLayout."""
    plain, blue = [], []
    for b in doc.blocks:
        if not is_dimension_block(b.name):
            continue
        if b.name.startswith("_BLUE_"):
            blue.append(b)
        else:
            plain.append(b)
    return plain, blue


def count_dimension_blocks(doc):
    """All blocks (plain + _BLUE_) matching any dimension prefix."""
    return sum(1 for b in doc.blocks if is_dimension_block(b.name))


def count_layer_lines(doc, layer: str) -> int:
    return sum(
        1
        for block in doc.blocks
        for e in block
        if e.dxftype() == "LINE" and e.dxf.layer == layer
    )


def count_container_inserts_to(doc, container: str, names: set) -> int:
    block = doc.blocks.get(container)
    if block is None:
        return 0
    return sum(
        1
        for e in block
        if e.dxftype() == "INSERT" and e.dxf.name in names
    )


def main(in_path: str, out_path: str, container: str = "STR_DRAWING") -> int:
    doc = ezdxf.readfile(in_path)

    # ---- 1. Collect dimension-family blocks --------------------------------
    plain_dim_blocks, blue_dim_blocks = collect_dimension_blocks(doc)
    plain_dim_names = {b.name for b in plain_dim_blocks}

    # ---- 2. Baseline counts (before) ---------------------------------------
    before = {
        "dim_blocks_total":     count_dimension_blocks(doc),
        "container_dim_inserts": count_container_inserts_to(doc, container, plain_dim_names),
        "line_on_blue_6":       count_layer_lines(doc, "_BLUE_6"),
    }

    # ---- 3. Strip inserts from the container block ------------------------
    container_block = doc.blocks.get(container)
    removed_inserts = 0
    if container_block is not None:
        to_remove = [
            e for e in container_block
            if e.dxftype() == "INSERT" and e.dxf.name in plain_dim_names
        ]
        for e in to_remove:
            container_block.delete_entity(e)  # type: ignore[attr-defined]
            removed_inserts += 1

    # ---- 4. Purge the block definitions ------------------------------------
    # After deleting the inserts, both block families become orphaned.
    # We also explicitly delete the blue originals because some CAD viewers
    # (and ezdxf itself in some versions) keep "anonymous-style" block
    # entries even after their last reference is removed.
    for b in list(blue_dim_blocks) + list(plain_dim_blocks):
        try:
            doc.blocks.delete_block(b.name)
        except Exception:
            pass  # already gone

    # ---- 5. Turn layer `_BLUE_6` OFF ---------------------------------------
    try:
        layer = doc.layers.get("_BLUE_6")
    except Exception:
        layer = None
    if layer is not None:
        layer.off()

    # ---- 6. Save & report --------------------------------------------------
    doc.saveas(out_path)

    after = {
        "dim_blocks_total":     count_dimension_blocks(doc),
        "container_dim_inserts": count_container_inserts_to(doc, container, plain_dim_names),
        "line_on_blue_6":       count_layer_lines(doc, "_BLUE_6"),
    }

    print("=== before ===")
    for k, v in before.items():
        print(f"  {k:>22}: {v}")
    print("=== after ===")
    for k, v in after.items():
        print(f"  {k:>22}: {v}")
    print(f"\ninserts removed from {container}: {removed_inserts}")
    print(f"output written to: {out_path}")
    return 0


if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description="Strip leftover distance-line geometry from a structural GA DXF.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("input", help="input DXF (never modified)")
    p.add_argument("output", help="output DXF path")
    p.add_argument(
        "--container", default="STR_DRAWING",
        help="name of the block whose INSERTs should be stripped (default: STR_DRAWING)",
    )
    args = p.parse_args()
    sys.exit(main(args.input, args.output, container=args.container))
