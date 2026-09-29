"""Confirmatory experiment, signal-only addendum and descriptive cost summaries.

A root is one initial solution A. In the confirmatory experiment every root was repaired in three
branches: basic feedback (B), basic plus behavioral feedback (C) and basic feedback plus neutral
text of the same character length as C's behavioral block (P). The prespecified diagnostic state
S* contains roots whose initial solution passed the basic diagnostic suite and failed the
behavioral one. In the addendum, every S* root was also repaired with a behavioral failure signal
without details (Q), again of C's character length.

The outcome of a branch is acceptance by the held-out strict suite. Intervals come from a
whole-cluster bootstrap over template clusters.
"""

from __future__ import annotations

import json
import random
from collections import defaultdict
from pathlib import Path

REPLICATES = 20_000
CONFIRMATORY_SEED = 28092027
ADDENDUM_SEED = 28092028
MINIMUM_STATE_ROOTS = 40
SIGNAL_SENTENCE = "A behavioral check failed; no further details are provided. "
BRANCHES = ("A", "B", "C", "P")


def accepted(evaluations, partition, suite):
    matches = [e for e in evaluations if e["partition"] == partition and e["suite"] == suite]
    if len(matches) != 1:
        raise ValueError(f"expected one {partition}/{suite} evaluation")
    return bool(matches[0]["accepted"])


def _branch(directory: Path, reference_code: str | None):
    sample = json.loads((directory / "sample.json").read_text())
    evaluations = json.loads((directory / "evaluations.json").read_text())
    code = (directory / "solution.rb").read_text()
    return (
        dict(
            strict=accepted(evaluations, "holdout", "strict"),
            holdout_base=accepted(evaluations, "holdout", "base"),
            unchanged=None if reference_code is None else code.strip() == reference_code.strip(),
            input_tokens=sample.get("input_tokens") or 0,
            output_tokens=sample.get("output_tokens") or 0,
            usd=sample.get("estimated_api_usd") or 0.0,
        ),
        evaluations,
        code,
    )


def export_roots(confirmatory: Path, addendum: Path | None = None):
    """Compact per-root table from the saved records. Row order follows the sorted record paths."""
    corpus = json.loads((confirmatory / "corpus" / "manifest.json").read_text())
    clusters = {t["id"]: t["template_cluster"] for t in corpus["tasks"]}
    roots = []
    for path in sorted(confirmatory.glob("answers/*/*/*/A/evaluations.json")):
        base = path.parent.parent
        provider, task, repeat = base.parts[-3], base.parts[-2], int(base.parts[-1])
        request = json.loads((base / "A" / "request.json").read_text())
        a, a_evaluations, a_code = _branch(base / "A", None)
        row = dict(
            provider=provider,
            model=request["model"],
            task=task,
            repeat=repeat,
            cluster=clusters[task],
            base_pass=accepted(a_evaluations, "diagnostic", "base"),
            behavior_pass=accepted(a_evaluations, "diagnostic", "behavior"),
            A=a,
        )
        for branch in BRANCHES[1:]:
            row[branch] = _branch(base / branch, a_code)[0]
        if addendum is not None and row["base_pass"] and not row["behavior_pass"]:
            signal = addendum / "answers" / provider / task / str(repeat) / "Q"
            row["Q"] = _branch(signal, a_code)[0]
            prompt = (signal / "prompt.txt").read_text()
            row["Q"]["signal_repetitions"] = prompt.count(SIGNAL_SENTENCE.strip())
            row["Q"]["length_matched"] = json.loads((signal / "request.json").read_text())[
                "signal"
            ]["length_matched"]
        roots.append(row)
    return roots


def export_main_costs(main: Path):
    """Per-root tokens, cost and unchanged-code flags of the main experiment (branches A, B, C)."""
    rows = []
    for path in sorted(main.glob("answers/*/*/*/A/sample.json")):
        base = path.parent.parent
        a, a_evaluations, a_code = _branch(base / "A", None)
        row = dict(
            provider=base.parts[-3],
            task=base.parts[-2],
            repeat=int(base.parts[-1]),
            base_pass=accepted(a_evaluations, "diagnostic", "base"),
            behavior_pass=accepted(a_evaluations, "diagnostic", "behavior"),
            A=a,
        )
        for branch in ("B", "C"):
            row[branch] = _branch(base / branch, a_code)[0]
        rows.append(row)
    return rows


def in_state(root):
    return root["base_pass"] and not root["behavior_pass"]


def _by_cluster(roots):
    groups = defaultdict(list)
    for root in roots:
        groups[root["cluster"]].append(root)
    return groups


def cluster_bootstrap(roots, statistic, seed, replicates=REPLICATES):
    """Percentile interval from resampling whole template clusters with replacement."""
    groups = _by_cluster(roots)
    keys = sorted(groups)
    rng = random.Random(seed)
    values = []
    for _ in range(replicates):
        values.append(statistic([r for k in (rng.choice(keys) for _ in keys) for r in groups[k]]))
    values.sort()
    return values[int(0.025 * replicates)], values[int(0.975 * replicates) - 1]


def mean_difference(x, y):
    def statistic(roots):
        return sum(r[x]["strict"] - r[y]["strict"] for r in roots) / len(roots)

    return statistic


def contrast(roots, x, y, seed):
    lower, upper = cluster_bootstrap(roots, mean_difference(x, y), seed)
    return dict(
        estimate=mean_difference(x, y)(roots),
        lower=lower,
        upper=upper,
        x_only=sum(r[x]["strict"] and not r[y]["strict"] for r in roots),
        y_only=sum(r[y]["strict"] and not r[x]["strict"] for r in roots),
    )


def equal_cell_contrast(roots, x, y, seed=CONFIRMATORY_SEED, replicates=REPLICATES):
    """Mean over (task, configuration) cells; a cluster drawn twice contributes its cells twice."""
    groups = _by_cluster(roots)
    keys = sorted(groups)
    rng = random.Random(seed)

    def statistic(draws):
        cells = defaultdict(list)
        for draw, r in draws:
            cells[(draw, r["task"], r["provider"])].append(r[x]["strict"] - r[y]["strict"])
        return sum(sum(v) / len(v) for v in cells.values()) / len(cells)

    values = []
    for _ in range(replicates):
        draws = [(i, r) for i, k in enumerate(rng.choice(keys) for _ in keys) for r in groups[k]]
        values.append(statistic(draws))
    values.sort()
    estimate = statistic([(0, r) for r in roots])
    return dict(
        estimate=estimate,
        lower=values[int(0.025 * replicates)],
        upper=values[int(0.975 * replicates) - 1],
    )


def _decision(result, state_roots):
    if state_roots < MINIMUM_STATE_ROOTS:
        return "descriptive_only"
    return "confirmed" if result["lower"] > 0 else "not_confirmed"


def _count(roots, branch, key="strict"):
    return sum(bool(r[branch][key]) for r in roots)


def analyze(roots, main_costs=None):
    providers = sorted({r["provider"] for r in roots})
    state = [r for r in roots if in_state(r)]
    result = dict(roots=len(roots), state_roots=len(state))

    confirmatory = dict(
        state_by_provider={p: sum(r["provider"] == p for r in state) for p in providers},
        state_clusters=sorted({r["cluster"] for r in state}),
        repaired_in_state={b: _count(state, b) for b in ("B", "C", "P")},
    )
    for name, (x, y) in {"H1_C_minus_B": ("C", "B"), "H2_C_minus_P": ("C", "P")}.items():
        row = contrast(state, x, y, CONFIRMATORY_SEED)
        row["decision"] = _decision(row, len(state))
        confirmatory[name] = row
    confirmatory["P_minus_B"] = contrast(state, "P", "B", CONFIRMATORY_SEED)
    confirmatory["C_minus_B_by_cluster"] = {
        c: sum(r["C"]["strict"] - r["B"]["strict"] for r in state if r["cluster"] == c)
        for c in confirmatory["state_clusters"]
    }
    confirmatory["all_roots"] = dict(
        accepted={b: _count(roots, b) for b in BRANCHES},
        repairs={
            b: sum(not r["A"]["strict"] and r[b]["strict"] for r in roots) for b in ("B", "C", "P")
        },
        regressions={
            b: sum(r["A"]["strict"] and not r[b]["strict"] for r in roots) for b in ("B", "C", "P")
        },
        initial_failures=sum(not r["A"]["strict"] for r in roots),
        equal_cell={
            f"{x}_minus_{y}": equal_cell_contrast(roots, x, y)
            for x, y in (("C", "B"), ("C", "P"), ("P", "B"))
        },
    )
    confirmatory["by_provider"] = {
        p: dict(
            roots=sum(r["provider"] == p for r in roots),
            state_roots=sum(r["provider"] == p for r in state),
            repaired_in_state={
                b: _count([r for r in state if r["provider"] == p], b) for b in ("B", "C", "P")
            },
        )
        for p in providers
    }
    result["confirmatory"] = confirmatory

    if all("Q" in r for r in state):
        addendum = dict(repaired_in_state={b: _count(state, b) for b in ("B", "C", "P", "Q")})
        h3 = contrast(state, "C", "Q", ADDENDUM_SEED)
        h3["decision"] = _decision(h3, len(state))
        addendum["H3_C_minus_Q"] = h3
        addendum["Q_minus_B"] = contrast(state, "Q", "B", ADDENDUM_SEED)
        addendum["Q_minus_P"] = contrast(state, "Q", "P", ADDENDUM_SEED)
        addendum["C_minus_Q_by_cluster"] = {
            c: sum(r["C"]["strict"] - r["Q"]["strict"] for r in state if r["cluster"] == c)
            for c in confirmatory["state_clusters"]
        }
        addendum["by_provider"] = {
            p: dict(
                repaired={
                    b: _count([r for r in state if r["provider"] == p], b)
                    for b in ("B", "C", "P", "Q")
                },
                unchanged={
                    b: _count([r for r in state if r["provider"] == p], b, "unchanged")
                    for b in ("B", "C", "P", "Q")
                },
            )
            for p in providers
        }
        addendum["signal"] = dict(
            length_matched=all(r["Q"]["length_matched"] for r in state),
            repetitions=[
                min(r["Q"]["signal_repetitions"] for r in state),
                max(r["Q"]["signal_repetitions"] for r in state),
            ],
            input_tokens=dict(
                C=sum(r["C"]["input_tokens"] for r in state),
                Q=sum(r["Q"]["input_tokens"] for r in state),
            ),
            usd=sum(r["Q"]["usd"] for r in state),
        )
        result["addendum"] = addendum

    result["costs"] = dict(confirmatory=cost_summary(roots, ("A", "B", "C", "P")))
    if main_costs is not None:
        result["costs"]["main"] = cost_summary(main_costs, ("A", "B", "C"))
        main_state = [r for r in main_costs if in_state(r)]
        result["costs"]["main"]["unchanged_in_state"] = {
            b: _count(main_state, b, "unchanged") for b in ("B", "C")
        }
    return result


def cost_summary(rows, branches):
    """Descriptive token and estimated API-cost totals (the local model is not priced)."""
    totals = {
        b: dict(
            accepted=_count(rows, b),
            input_tokens=sum(r[b]["input_tokens"] for r in rows),
            output_tokens=sum(r[b]["output_tokens"] for r in rows),
            usd=sum(r[b]["usd"] for r in rows),
        )
        for b in branches
    }
    extra_accepted = totals["C"]["accepted"] - totals["B"]["accepted"]
    extra_usd = totals["C"]["usd"] - totals["B"]["usd"]
    return dict(
        branches=totals,
        total_usd=sum(t["usd"] for t in totals.values()),
        C_vs_B=dict(
            extra_accepted=extra_accepted,
            extra_input_tokens=totals["C"]["input_tokens"] - totals["B"]["input_tokens"],
            extra_usd=extra_usd,
            usd_per_extra_accepted=extra_usd / extra_accepted if extra_accepted > 0 else None,
        ),
    )
