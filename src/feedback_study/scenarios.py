"""Descriptive scenario comparisons retaining all nine paired outcomes."""

from collections import Counter, defaultdict

STATES = ("pass", "fail", "not_reached")
CELLS = [f"{a}/{b}" for a in STATES for b in STATES]


def matrix(rows):
    counts = Counter(f"{r['B']}/{r['C']}" for r in rows)
    return {
        "pairs": len(rows),
        "roots": len({r["root"] for r in rows}),
        "cells": {c: counts[c] for c in CELLS},
        "C_gain_roots": sorted({r["root"] for r in rows if r["C"] == "pass" and r["B"] != "pass"}),
        "B_gain_roots": sorted({r["root"] for r in rows if r["B"] == "pass" and r["C"] != "pass"}),
    }


def tables(rows):
    grouped = defaultdict(list)
    for r in rows:
        grouped[(r["validation"], r["feedback_source"], r["exposure"])].append(r)
    return [
        {"validation": k[0], "source": k[1], "exposure": k[2], **matrix(v)}
        for k, v in sorted(grouped.items())
    ]


def analysis(rows, original):
    original = {r["root"]: r for r in original}
    discordants = [k for k, v in original.items() if v["B"] != v["C"]]
    if len(discordants) != 19:
        raise ValueError(f"Expected 19 discordant scenario roots, found {len(discordants)}")
    if sum(original[k]["C"] for k in discordants) != 16:
        raise ValueError("Expected 16 C-only successes among discordant scenario roots")
    case_rows = [r for r in rows if r["root"] in discordants]
    sensitivity = {}
    sensitivity_exposure_detail = {}
    for assignment in ("shared-design", "H-only"):
        mapped = []
        for r in case_rows:
            category = r["design_relation"]
            if category == "mixed":
                category = assignment
            elif category == "shared":
                category = "shared-design"
            mapped.append({**r, "original_exposure": r["exposure"], "exposure": category})
        sensitivity[assignment] = tables(mapped)
        # The broad design totals above deliberately aggregate the evidence
        # axis; this companion table preserves it, including unresolved rows.
        sensitivity_exposure_detail[assignment] = tables(
            [{**r, "exposure": r["exposure"] + " / " + r["original_exposure"]} for r in mapped]
        )
    cases = []
    for root in sorted(discordants):
        rr = [r for r in case_rows if r["root"] == root]
        gains = [r for r in rr if (r["B"] == "pass") != (r["C"] == "pass")]
        cases.append(
            {
                "root": root,
                "original": original[root],
                "all_scenarios": matrix(rr),
                "gain_scenarios": gains,
                "tables": tables(rr),
            }
        )
    return {
        "all_104": matrix(rows),
        "all_tables": tables(rows),
        "discordant_roots": len(discordants),
        "discordant_tables": tables(case_rows),
        "discordant_total": matrix(case_rows),
        "cases": cases,
        "mixed_sensitivity": sensitivity,
        "mixed_sensitivity_exposure_detail": sensitivity_exposure_detail,
        "context_disagreements": [r for r in rows if r["probe_full_disagreement"]],
    }
