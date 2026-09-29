"""Correction 1 to analyze_v2.py (found after the freeze by independent review).

In the frozen analyze_v2.equal_cell, cells of a cluster drawn more than once in a bootstrap replicate were merged
by (task, provider), so cluster multiplicity was lost for the equal-cell secondary intervals over all roots.
This script recomputes only those secondary intervals with multiplicity preserved. H1/H2 and all root-weighted
S* statistics are unaffected (they average over the concatenated sample). The frozen analysis output is kept.
"""
import argparse, json, random
from collections import defaultdict
from pathlib import Path
from research.confirmatory_v2.analyze_v2 import BOOT, SEED, load_roots


def boot_equal_cell(roots, x, y, reps=BOOT, seed=SEED):
    by = defaultdict(list)
    for r in roots:
        by[r["cluster"]].append(r)
    keys = sorted(by); rng = random.Random(seed)

    def stat(pairs):
        cells = defaultdict(list)
        for draw, r in pairs:
            cells[(draw, r["task"], r["provider"])].append(r[f"S_{x}"] - r[f"S_{y}"])
        return sum(sum(v) / len(v) for v in cells.values()) / len(cells)
    est = stat([(0, r) for r in roots]); vals = []
    for _ in range(reps):
        pairs = [(i, r) for i, k in enumerate(rng.choice(keys) for _ in keys) for r in by[k]]
        vals.append(stat(pairs))
    vals.sort()
    return dict(estimate=est, lo95=vals[int(0.025 * reps)], hi95=vals[int(0.975 * reps) - 1])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--output", type=Path, required=True)
    out = ap.parse_args().output
    roots = load_roots(out)
    res = {"note": __doc__.strip(), "all_equal_cell_corrected": {k: boot_equal_cell(roots, x, y) for k, (x, y) in
           {"C_minus_B": ("C", "B"), "C_minus_P": ("C", "P"), "P_minus_B": ("P", "B")}.items()}}
    s = [r for r in roots if r["a_dbase"] and not r["a_dbeh"]]
    res["Sstar_clusters"] = sorted({r["cluster"] for r in s})
    res["Sstar_extra_C_minus_B_by_cluster"] = {c: sum(r["S_C"] - r["S_B"] for r in s if r["cluster"] == c) for c in res["Sstar_clusters"]}
    (out / "analysis_v2_correction1.json").write_text(json.dumps(res, indent=1)); print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
