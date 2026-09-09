# ISGEC DXF Cleanup

Three scripts that fix a recurring artifact in ISGEC Heavy Engineering DXF
exports and verify the fix didn't break anything else.

## The problem

ISGEC exports ship every structural GA drawing with a **distance-line
artifact**:

- 94 `StraightDimension-*` blocks, each containing 5 LINE entities that
  draw extension lines + tick marks + dimension lines.
- 94 `_BLUE_StraightDimension-*` orphan blocks (byte-identical
  color-override copies left over from `SETBYLAYER` / `SETBYBLOCK`).
- All 980 LINEs sit on layer `_BLUE_6` (ISGEC's DIMLAYER).

A prior cleanup pass typically hides the layer in a layer state but never
deletes the geometry. The lines stay visible in any tool that walks raw
entity data (ezdxf, dxf.js, several CAD importers).

## The fix

```bash
python3 strip_distance_lines.py <input.dxf> <output.dxf>
```

5 seconds per file. The script:

1. Deletes every dimension-family block (`StraightDimension-*`,
   `AlignedDimension-*`, `DimAligned-*`, `LinearDimension-*`,
   `AngularDimension-*`, `RadialDimension-*`, `DiametricDimension-*`,
   `OrdinateDimension-*`, `ArrowDimension-*`, plus every `_BLUE_` variant).
2. Removes the INSERTs in `STR_DRAWING` that referenced them.
3. Sets layer `_BLUE_6` OFF (safety net).

The input file is never modified. Output goes to `<output.dxf>`.

For non-standard container names (e.g. `GA_DRAWING`):

```bash
python3 strip_distance_lines.py --container=GA_DRAWING <input.dxf> <output.dxf>
```

## The audits

```bash
# Regression: stripper works on real ISGEC exports + 3 synthetic variants
python3 test_overlap.py --real-dxf /path/to/test-a-4.dxf

# Post-strip: grid consistency + structural overlap + dimension placement
python3 test_superimpose.py --cleaned cleaned.dxf --bak original.dxf
```

Both take < 10 s total. Run them on every new ISGEC export before trusting
the cleaned output.

## Verified results (test-a-3.dxf and test-a-4.dxf, ISGEC 2026)

```
=== before ===
         dim_blocks_total: 188
    container_dim_inserts: 94
            line_on_blue_6: 980
=== after ===
         dim_blocks_total: 0
    container_dim_inserts: 0
            line_on_blue_6: 0
```

Plus 8 audit checks across grid consistency, structural overlap, and
dimension placement — all PASS.

## Requirements

```
pip install ezdxf>=1.4
```

## Files

| File | Purpose |
|---|---|
| `strip_distance_lines.py` | The fix |
| `test_overlap.py` | Regression harness (5 cases) |
| `test_superimpose.py` | Post-strip audit (3 cases) |

The stripper is non-destructive to the input and idempotent on already-clean
files. Safe to run on any DXF without checking first.
