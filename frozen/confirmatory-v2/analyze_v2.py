"""Prespecified analysis for confirmatory v2 (protocol.md). Written before any v2 data.

Usage: python -m research.confirmatory_v2.analyze_v2 --output results/confirmatory-v2-YYYYMMDD
"""

from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path

BOOT, SEED, MIN_S = 20000, 28092027, 40


def accepted(evals, partition, suite):
    sel = [e for e in evals if e["partition"] == partition and e["suite"] == suite]
    assert len(sel) == 1
    return bool(sel[0]["accepted"])


def load_roots(out: Path):
    manifest = json.loads((out / "corpus" / "manifest.json").read_text())
    cluster = {t["id"]: t["template_cluster"] for t in manifest["tasks"]}
    roots = []
    for a in sorted(out.glob("answers/*/*/*/A/evaluations.json")):
        base = a.parent.parent
        provider, task, repeat = base.parts[-3], base.parts[-2], int(base.parts[-1])
        ev = {br: json.loads((base / br / "evaluations.json").read_text()) for br in ("A", "B", "C", "P")}
        roots.append(dict(provider=provider, task=task, repeat=repeat, cluster=cluster[task],
                          a_dbase=accepted(ev["A"], "diagnostic", "base"), a_dbeh=accepted(ev["A"], "diagnostic", "behavior"),
                          **{f"S_{br}": accepted(ev[br], "holdout", "strict") for br in ("A", "B", "C", "P")},
                          **{f"F_{br}": accepted(ev[br], "holdout", "base") for br in ("A", "B", "C", "P")}))
    return roots


def cluster_boot(roots, fn, reps=BOOT, seed=SEED):
    """Whole-cluster bootstrap of a root-weighted statistic fn(list_of_roots)."""
    by = defaultdict(list)
    for r in roots:
        by[r["cluster"]].append(r)
    keys = sorted(by); rng = random.Random(seed); vals = []
    for _ in range(reps):
        sample = [r for k in (rng.choice(keys) for _ in keys) for r in by[k]]
        vals.append(fn(sample))
    vals.sort()
    return vals[int(0.025 * reps)], vals[int(0.975 * reps) - 1]


def diff(x, y):
    return lambda rs: sum(r[f"S_{x}"] - r[f"S_{y}"] for r in rs) / len(rs)


def equal_cell(x, y):
    def f(rs):
        cells = defaultdict(list)
        for r in rs:
            cells[(r["task"], r["provider"])].append(r[f"S_{x}"] - r[f"S_{y}"])
        return sum(sum(v) / len(v) for v in cells.values()) / len(cells)
    return f


def summary(roots, fn):
    lo, hi = cluster_boot(roots, fn)
    return dict(estimate=fn(roots), lo95=lo, hi95=hi)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--output", type=Path, required=True)
    out = ap.parse_args().output
    roots = load_roots(out)
    s = [r for r in roots if r["a_dbase"] and not r["a_dbeh"]]
    res = dict(n_roots=len(roots), n_Sstar=len(s),
               n_Sstar_by_provider={p: sum(r["provider"] == p for r in s) for p in sorted({r["provider"] for r in roots})})
    conf = len(s) >= MIN_S
    for name, (x, y) in {"H1_C_minus_B": ("C", "B"), "H2_C_minus_P": ("C", "P")}.items():
        est = summary(s, diff(x, y)) if s else None
        if est:
            est["decision"] = ("confirmed" if est["lo95"] > 0 else "not_confirmed") if conf else "descriptive_only_min_not_met"
            est["discordant"] = dict(x_only=sum(r[f"S_{x}"] and not r[f"S_{y}"] for r in s), y_only=sum(r[f"S_{y}"] and not r[f"S_{x}"] for r in s))
        res[name] = est
    res["Sstar_P_minus_B"] = summary(s, diff("P", "B")) if s else None
    res["Sstar_repaired"] = {br: sum(r[f"S_{br}"] for r in s) for br in ("B", "C", "P")}
    res["all_equal_cell"] = {k: summary(roots, equal_cell(x, y)) for k, (x, y) in {"C_minus_B": ("C", "B"), "C_minus_P": ("C", "P"), "P_minus_B": ("P", "B")}.items()}
    res["by_provider"] = {}
    for p in sorted({r["provider"] for r in roots}):
        rp = [r for r in roots if r["provider"] == p]; sp = [r for r in rp if r["a_dbase"] and not r["a_dbeh"]]
        res["by_provider"][p] = dict(n=len(rp), accepted={br: sum(r[f"S_{br}"] for r in rp) for br in ("A", "B", "C", "P")},
                                     Sstar_n=len(sp), Sstar_repaired={br: sum(r[f"S_{br}"] for r in sp) for br in ("B", "C", "P")})
    res["repairs_regressions"] = {br: dict(repairs=sum((not r["S_A"]) and r[f"S_{br}"] for r in roots),
                                           regressions=sum(r["S_A"] and not r[f"S_{br}"] for r in roots),
                                           initial_failures=sum(not r["S_A"] for r in roots), initial_successes=sum(r["S_A"] for r in roots))
                                  for br in ("B", "C", "P")}
    res["accepted_totals"] = {br: sum(r[f"S_{br}"] for r in roots) for br in ("A", "B", "C", "P")}
    (out / "analysis_v2.json").write_text(json.dumps(res, indent=1))
    print(json.dumps({k: res[k] for k in ("n_roots", "n_Sstar", "n_Sstar_by_provider", "H1_C_minus_B", "H2_C_minus_P")}, indent=1))


if __name__ == "__main__":
    main()
