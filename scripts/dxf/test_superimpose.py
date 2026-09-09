#!/usr/bin/env python3
"""
Superimposition + grid-overlap audit.

Run after `strip_distance_lines.py` to verify:

  (A) GRID-OVERLAP CONSISTENCY
      Every surviving GridLine-* LINE forms a consistent orthogonal frame:
      17H + 7V + 0 oblique (typical ISGEC layout).

  (B) GRID vs STRUCTURAL OVERLAP
      Surviving GridLine endpoints share ZERO coordinates with structural
      (Part/Bolt/Connection) endpoints.

  (C) SUPERIMPOSITION FIDELITY
      Re-measure the stripped dim-line endpoints against the cleaned
      drawing's anchor pool (structural + grid endpoints). Every dim
      endpoint must be within a sensible offset of an anchor; none may
      land exactly on an anchor; none may be orphaned (>2500 mm).

Usage:
    python3 test_superimpose.py --cleaned cleaned.dxf --bak original.dxf
    python3 test_superimpose.py  # uses the ISGEC default paths
"""

import argparse
import os
import sys
from collections import Counter

import ezdxf


def collect_line_endpoints(doc, *, block_prefixes, dedup=True, decimals=2):
    pts = []
    for block in doc.blocks:
        if not any(block.name.startswith(p) for p in block_prefixes):
            continue
        for e in block:
            if e.dxftype() == "LINE":
                s, t = e.dxf.start, e.dxf.end
                pts.append((round(s.x, decimals), round(s.y, decimals)))
                pts.append((round(t.x, decimals), round(t.y, decimals)))
    return set(pts) if dedup else pts


def grid_consistency(doc):
    grid_lines = []
    for block in doc.blocks:
        if not block.name.startswith("GridLine-"):
            continue
        for e in block:
            if e.dxftype() == "LINE":
                s, t = e.dxf.start, e.dxf.end
                grid_lines.append(((s.x, s.y), (t.x, t.y)))

    horiz = [(s, t) for s, t in grid_lines if abs(s[1] - t[1]) < 1e-3]
    vert  = [(s, t) for s, t in grid_lines if abs(s[0] - t[0]) < 1e-3]
    oblq  = [(s, t) for s, t in grid_lines
             if abs(s[1] - t[1]) >= 1e-3 and abs(s[0] - t[0]) >= 1e-3]

    all_x = [round(p[0], 2) for s, t in grid_lines for p in (s, t)]
    all_y = [round(p[1], 2) for s, t in grid_lines for p in (s, t)]
    x_span = max(all_x) - min(all_x)
    y_span = max(all_y) - min(all_y)
    distinct_x = sorted({round(p[0], 1) for s, t in grid_lines for p in (s, t)})
    distinct_y = sorted({round(p[1], 1) for s, t in grid_lines for p in (s, t)})

    return {
        "horiz_lines": len(horiz),
        "vert_lines": len(vert),
        "oblique_lines": len(oblq),
        "oblique_is_zero": len(oblq) == 0,
        "x_span": round(x_span, 2),
        "y_span": round(y_span, 2),
        "distinct_x_count": len(distinct_x),
        "distinct_y_count": len(distinct_y),
    }


def grid_vs_structural_overlap(cleaned_path):
    doc = ezdxf.readfile(cleaned_path)
    grid_pts = collect_line_endpoints(doc, block_prefixes=("GridLine-",))
    struct_pts = collect_line_endpoints(
        doc, block_prefixes=("Part-", "Bolt-", "Connection-")
    )
    return {
        "grid_endpoints": len(grid_pts),
        "structural_endpoints": len(struct_pts),
        "shared_endpoints": len(grid_pts & struct_pts),
    }


def superimposition_fidelity(cleaned_path, bak_path):
    cleaned = ezdxf.readfile(cleaned_path)
    bak = ezdxf.readfile(bak_path)

    bak_str = bak.blocks.get("STR_DRAWING")
    reinsert_targets = sum(
        1 for e in bak_str if e.dxftype() == "INSERT" and (
            e.dxf.name.startswith("StraightDimension-")
            or e.dxf.name.startswith("_BLUE_StraightDimension-")
        )
    )

    struct_pts = collect_line_endpoints(
        cleaned, block_prefixes=("Part-", "Bolt-", "Connection-")
    )
    grid_pts = collect_line_endpoints(cleaned, block_prefixes=("GridLine-",))
    anchor_pts = struct_pts | grid_pts

    OFFSET_MAX_OK = 2500.0

    nearest_dists = []
    exact_anchor_collisions = 0
    hard_orphans = 0
    dim_grid_collisions = 0

    for block in bak.blocks:
        if not (block.name.startswith("StraightDimension-")
                or block.name.startswith("_BLUE_StraightDimension-")):
            continue
        for e in block:
            if e.dxftype() != "LINE":
                continue
            for ep in ((e.dxf.start.x, e.dxf.start.y),
                       (e.dxf.end.x, e.dxf.end.y)):
                er = (round(ep[0], 2), round(ep[1], 2))
                if er in grid_pts:
                    dim_grid_collisions += 1
                if not anchor_pts:
                    continue
                nearest = min(
                    anchor_pts,
                    key=lambda p: (p[0] - er[0]) ** 2 + (p[1] - er[1]) ** 2,
                )
                d = ((er[0] - nearest[0]) ** 2 + (er[1] - nearest[1]) ** 2) ** 0.5
                nearest_dists.append(d)
                if d == 0.0:
                    exact_anchor_collisions += 1
                elif d > OFFSET_MAX_OK:
                    hard_orphans += 1

    return {
        "reinsert_targets": reinsert_targets,
        "dim_endpoints_total": len(nearest_dists),
        "dim_grid_exact_collisions": dim_grid_collisions,
        "anchor_exact_collisions": exact_anchor_collisions,
        "orphans_gt_2500": hard_orphans,
        "nearest_dist_min": round(min(nearest_dists), 2) if nearest_dists else None,
        "nearest_dist_max": round(max(nearest_dists), 2) if nearest_dists else None,
        "nearest_dist_median": round(
            sorted(nearest_dists)[len(nearest_dists) // 2], 2
        ) if nearest_dists else None,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--cleaned", default="/home/rushabh/Downloads/test-a-4.dxf",
                   help="path to the cleaned DXF (default: %(default)s)")
    p.add_argument("--bak", default="/home/rushabh/Downloads/test-a-4.dxf.bak",
                   help="path to the pre-strip DXF backup (default: %(default)s)")
    args = p.parse_args()

    for path in (args.cleaned, args.bak):
        if not os.path.exists(path):
            print(f"error: file not found: {path}", file=sys.stderr)
            sys.exit(2)

    print("=" * 78)
    print("(A) GRID OVERLAP CONSISTENCY")
    print("-" * 78)
    cleaned = ezdxf.readfile(args.cleaned)
    g = grid_consistency(cleaned)
    for k, v in g.items():
        print(f"  {k:<24}: {v}")
    a_ok = g["oblique_is_zero"]
    print(f"\n  RESULT: {'PASS' if a_ok else 'FAIL'} — "
          f"grid is {'purely orthogonal' if a_ok else 'NOT orthogonal'}")

    print()
    print("=" * 78)
    print("(B) GRID vs STRUCTURAL OVERLAP")
    print("-" * 78)
    b = grid_vs_structural_overlap(args.cleaned)
    for k, v in b.items():
        print(f"  {k:<26}: {v}")
    b_ok = b["shared_endpoints"] == 0
    print(f"\n  RESULT: {'PASS' if b_ok else 'FAIL'} — "
          f"{'no coordinate collisions' if b_ok else 'OVERLAP DETECTED'}")

    print()
    print("=" * 78)
    print("(C) SUPERIMPOSITION FIDELITY")
    print("-" * 78)
    c = superimposition_fidelity(args.cleaned, args.bak)
    for k, v in c.items():
        print(f"  {k:<28}: {v}")
    c_ok = (
        c["dim_grid_exact_collisions"] == 0
        and c["anchor_exact_collisions"] == 0
        and c["orphans_gt_2500"] == 0
    )
    print(f"\n  RESULT: {'PASS' if c_ok else 'FAIL'} — "
          f"{'all dim endpoints sit on extension lines' if c_ok else 'placement anomaly'}")


if __name__ == "__main__":
    main()
