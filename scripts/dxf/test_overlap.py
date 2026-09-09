#!/usr/bin/env python3
"""
Regression harness for `strip_distance_lines.py`.

Builds five synthetic DXF variants, runs the stripper against each, and
verifies the expected before/after counters. Also performs a coordinate
overlap audit against the real ISGEC export pointed to by --real-dxf.

Cases:
  1. regression          — stripper against --real-dxf (an ISGEC export)
  2. non-blue layer      — dimension blocks live on a layer other than _BLUE_6
  3. alt prefix          — AlignedDimension-* instead of StraightDimension-*
  4. already-clean       — DXF with no dimension blocks; no-op test
  5. coordinate overlap  — dimension ↔ grid endpoint audit

Usage:
    python3 test_overlap.py [--real-dxf PATH]
    python3 test_overlap.py --real-dxf /home/rushabh/Downloads/test-a-4.dxf
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

import ezdxf


SCRIPT = str(Path(__file__).resolve().parent / "strip_distance_lines.py")


def run_stripper(in_path: str, out_path: str) -> dict:
    """Run the stripper on a copy and return its before/after counters."""
    r = subprocess.run(
        [sys.executable, SCRIPT, in_path, out_path],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        print("STDERR:", r.stderr)
        raise SystemExit(r.returncode)
    metrics = {}
    for line in r.stdout.splitlines():
        line = line.strip()
        if ":" in line and not line.startswith("===") \
           and "removed" not in line and "output" not in line:
            k, v = line.split(":", 1)
            try:
                metrics[k.strip()] = int(v.strip())
            except ValueError:
                pass
    return metrics


# ---------- synthetic DXF builders -----------------------------------------

def synth_clean_dxf(path: str) -> None:
    """DXF with zero dimension blocks. Used as a no-op test fixture."""
    doc = ezdxf.new("AC1024")
    msp = doc.modelspace()
    msp.add_line((0, 0), (100, 0))
    doc.saveas(path)


def synth_non_blue_layer_dxf(path: str) -> None:
    """Dimension blocks on a DIM layer (not _BLUE_6)."""
    doc = ezdxf.new("AC1024")
    doc.layers.add("DIM")
    doc.layers.add("MAIN")
    str_dwg = doc.blocks.new("STR_DRAWING")

    p1 = doc.blocks.new("Part-A")
    p1.add_line((0, 0), (10, 10), dxfattribs={"layer": "MAIN"})
    str_dwg.add_blockref("Part-A", (0, 0))
    p2 = doc.blocks.new("Part-B")
    p2.add_line((20, 0), (30, 10), dxfattribs={"layer": "MAIN"})
    str_dwg.add_blockref("Part-B", (50, 0))

    d1 = doc.blocks.new("StraightDimension-999999-A")
    d1.add_line((100, 100), (100, 200), dxfattribs={"layer": "DIM"})
    d1.add_line((100, 100), (200, 100), dxfattribs={"layer": "DIM"})
    str_dwg.add_blockref("StraightDimension-999999-A", (0, 0))

    d2 = doc.blocks.new("StraightDimension-999999-B")
    d2.add_line((300, 100), (300, 200), dxfattribs={"layer": "DIM"})
    str_dwg.add_blockref("StraightDimension-999999-B", (50, 0))

    msp = doc.modelspace()
    msp.add_blockref("STR_DRAWING", (0, 0))
    doc.saveas(path)


def synth_alt_prefix_dxf(path: str) -> None:
    """Dimension blocks use AlignedDimension-* (proves broader prefix coverage)."""
    doc = ezdxf.new("AC1024")
    doc.layers.add("DIM")
    str_dwg = doc.blocks.new("STR_DRAWING")
    d = doc.blocks.new("AlignedDimension-12345-X")
    d.add_line((100, 100), (100, 200), dxfattribs={"layer": "DIM"})
    str_dwg.add_blockref("AlignedDimension-12345-X", (0, 0))
    msp = doc.modelspace()
    msp.add_blockref("STR_DRAWING", (0, 0))
    doc.saveas(path)


# ---------- coordinate overlap audit ----------------------------------------

def coordinate_overlap_audit(path: str) -> dict:
    """Count shared endpoints between dimension-family and GridLine blocks."""
    doc = ezdxf.readfile(path)
    dim_pts, grid_pts = set(), set()
    for block in doc.blocks:
        is_dim = any(block.name.startswith(p) for p in
                     ("StraightDimension-", "_BLUE_StraightDimension-"))
        is_grid = block.name.startswith("GridLine-")
        if not (is_dim or is_grid):
            continue
        for e in block:
            if e.dxftype() != "LINE":
                continue
            s, t = e.dxf.start, e.dxf.end
            target = dim_pts if is_dim else grid_pts
            target.add((round(s.x, 2), round(s.y, 2)))
            target.add((round(t.x, 2), round(t.y, 2)))
    return {
        "dim_endpoints":   len(dim_pts),
        "grid_endpoints":  len(grid_pts),
        "shared_endpoints": len(dim_pts & grid_pts),
        "sample_shared":   list(dim_pts & grid_pts)[:5],
    }


# ---------- test cases ------------------------------------------------------

def case_regression(real_dxf: str, workdir: str):
    in_path = os.path.join(workdir, "regression_in.dxf")
    out_path = os.path.join(workdir, "regression_out.dxf")
    shutil.copy(real_dxf, in_path)
    m = run_stripper(in_path, out_path)
    expectations = {"dim_blocks_total": 0, "container_dim_inserts": 0,
                    "line_on_blue_6": 0}
    ok = all(m.get(k) == v for k, v in expectations.items())
    return ok, m, expectations


def case_non_blue_layer(workdir: str):
    in_path = os.path.join(workdir, "non_blue_in.dxf")
    out_path = os.path.join(workdir, "non_blue_out.dxf")
    synth_non_blue_layer_dxf(in_path)
    m = run_stripper(in_path, out_path)
    expectations = {"dim_blocks_total": 0, "container_dim_inserts": 0}
    ok = all(m.get(k) == v for k, v in expectations.items())
    return ok, m, expectations


def case_alt_prefix(workdir: str):
    in_path = os.path.join(workdir, "alt_prefix_in.dxf")
    out_path = os.path.join(workdir, "alt_prefix_out.dxf")
    synth_alt_prefix_dxf(in_path)
    m = run_stripper(in_path, out_path)
    expectations = {"dim_blocks_total": 0, "container_dim_inserts": 0}
    ok = all(m.get(k) == v for k, v in expectations.items())
    return ok, m, expectations


def case_already_clean(workdir: str):
    in_path = os.path.join(workdir, "clean_in.dxf")
    out_path = os.path.join(workdir, "clean_out.dxf")
    synth_clean_dxf(in_path)
    m = run_stripper(in_path, out_path)
    expectations = {"dim_blocks_total": 0, "container_dim_inserts": 0}
    ok = all(m.get(k) == v for k, v in expectations.items())
    return ok, m, expectations


def case_coordinate_overlap(real_dxf: str):
    overlap = coordinate_overlap_audit(real_dxf)
    return overlap["shared_endpoints"] == 0, overlap, None


# ---------- main ------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument(
        "--real-dxf",
        default="/home/rushabh/Downloads/test-a-4.dxf",
        help="path to a real ISGEC DXF export for the regression case "
             "(default: %(default)s)",
    )
    args = p.parse_args()
    real_dxf = args.real_dxf
    if not os.path.exists(real_dxf):
        print(f"error: --real-dxf not found: {real_dxf}", file=sys.stderr)
        sys.exit(2)

    workdir = tempfile.mkdtemp(prefix="dxf-test-")
    print(f"workdir: {workdir}")
    print(f"real DXF: {real_dxf}")

    results = []
    ok, m, exp = case_regression(real_dxf, workdir)
    results.append(("regression", ok, m, exp))

    ok, m, exp = case_non_blue_layer(workdir)
    results.append(("non-blue layer", ok, m, exp))

    ok, m, exp = case_alt_prefix(workdir)
    results.append(("alt prefix (AlignedDimension-*)", ok, m, exp))

    ok, m, exp = case_already_clean(workdir)
    results.append(("already-clean file", ok, m, exp))

    ok, detail, _ = case_coordinate_overlap(real_dxf)
    results.append(("coordinate overlap (dim ↔ grid)", ok, detail, None))

    print()
    print("=" * 78)
    print(f"{'Case':<32} {'Pass':<6} {'Detail'}")
    print("-" * 78)
    for name, ok, detail, _exp in results:
        flag = "PASS" if ok else "FAIL"
        print(f"{name:<32} {flag:<6} {detail}")
    print("=" * 78)


if __name__ == "__main__":
    main()
