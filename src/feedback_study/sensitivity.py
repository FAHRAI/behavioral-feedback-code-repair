"""Post hoc sensitivity calculations with fixed task–configuration weights."""

import hashlib
import json
import math
import random
from collections import defaultdict
from statistics import mean

from .outcomes import contrast
from .primary import percentile


def integral(f, left, right, tolerance=1e-12):
    """Adaptive Simpson integration, with a hard convergence failure."""

    def refine(a, b, fa, fb, fm, whole, tol, depth):
        mid = (a + b) / 2
        fl, fr = f((a + mid) / 2), f((mid + b) / 2)
        lower = (mid - a) * (fa + 4 * fl + fm) / 6
        upper = (b - mid) * (fm + 4 * fr + fb) / 6
        error = lower + upper - whole
        if abs(error) <= 15 * tol:
            return lower + upper + error / 15
        if depth == 0:
            raise ArithmeticError("Integration did not converge")
        return refine(a, mid, fa, fm, fl, lower, tol / 2, depth - 1) + refine(
            mid, b, fm, fb, fr, upper, tol / 2, depth - 1
        )

    fa, fb, fm = f(left), f(right), f((left + right) / 2)
    whole = (right - left) * (fa + 4 * fm + fb) / 6
    return refine(left, right, fa, fb, fm, whole, tolerance, 24)


def t_critical(df):
    """0.975 Student-t quantile by integrating its density and bisection."""
    if not math.isfinite(df) or df <= 0:
        raise ValueError("Positive finite degrees of freedom required")
    norm = math.exp(math.lgamma((df + 1) / 2) - math.lgamma(df / 2))
    norm /= math.sqrt(df * math.pi)

    def density(x):
        return norm * (1 + x * x / df) ** (-(df + 1) / 2)

    low, high = 0.0, 2.0
    while integral(density, 0, high) < 0.475:
        high *= 2
        if high > 1e6:
            raise ArithmeticError("Quantile not bracketed")
    for _ in range(55):
        mid = (low + high) / 2
        if integral(density, 0, mid) < 0.475:
            low = mid
        else:
            high = mid
    return (low + high) / 2


def cr2(task_means, clusters):
    """Intercept-only OLS, working I_N, clustered bias-reduced linearization."""
    if len(clusters) < 2:
        raise ValueError("At least two clusters required")
    members = [t for tasks in clusters.values() for t in tasks]
    if len(set(members)) != len(members) or set(members) != set(task_means):
        raise ValueError("Clusters must partition tasks")
    if not all(clusters.values()):
        raise ValueError("Empty cluster")
    total = len(task_means)
    theta = mean(task_means.values())
    weights = [len(tasks) for tasks in clusters.values()]
    variance = (
        sum(
            sum(task_means[t] - theta for t in tasks) ** 2 / (1 - len(tasks) / total)
            for tasks in clusters.values()
        )
        / total**2
    )
    denominator = (
        sum(w**2 / (total - w) ** 2 for w in weights)
        - 2 / total * sum(w**3 / (total - w) ** 2 for w in weights)
        + sum(w**2 / (total - w) for w in weights) ** 2 / total**2
    )
    df = 1 / denominator
    se = math.sqrt(variance)
    critical = t_critical(df)
    critical_g = t_critical(len(clusters) - 1)
    return {
        "estimate": theta,
        "variance": variance,
        "SE": se,
        "df_satterthwaite": df,
        "critical_satterthwaite": critical,
        "interval_95": [theta - critical * se, theta + critical * se],
        "df_G_minus_1": len(clusters) - 1,
        "critical_G_minus_1": critical_g,
        "interval_95_G_minus_1": [theta - critical_g * se, theta + critical_g * se],
        "working_covariance": "I_24 for task-level means; intercept-only OLS",
    }


def selected_mean(task_means, clusters, selected):
    """Keep all tasks of each selected cluster, including multiplicity."""
    return mean(task_means[t] for g in selected for t in clusters[g])


def bootstrap(task_means, clusters, *, seed, replicates=50_000):
    rng = random.Random(seed)
    names = sorted(clusters)
    totals = {g: sum(task_means[t] for t in clusters[g]) for g in names}
    sizes = {g: len(clusters[g]) for g in names}
    draws = []
    for _ in range(replicates):
        selected = rng.choices(names, k=len(names))
        draws.append(sum(totals[g] for g in selected) / sum(sizes[g] for g in selected))
    return {
        "estimate": mean(task_means.values()),
        "interval_95": [percentile(draws, 0.025), percentile(draws, 0.975)],
        "seed": seed,
        "replicates": replicates,
        "units": len(names),
        "within_unit_resampling": False,
        "draws_sha256": hashlib.sha256(json.dumps(draws).encode()).hexdigest(),
    }


def analyze(rows, tasks, models, annotated, primary):
    task_means = {
        t: mean(int(r["C"]["S"]) - int(r["B"]["S"]) for r in rows if r["task_id"] == t)
        for t in sorted(tasks)
    }
    clusters = defaultdict(list)
    for t, case in sorted(tasks.items()):
        clusters[case["template_cluster"]].append(t)
    theta = mean(task_means.values())
    overall = contrast(rows)
    counts = (overall["B"], overall["C"], overall["C_only"], overall["B_only"])
    if counts != (720, 736, 25, 9):
        raise ValueError(f"Unexpected study outcome counts: {counts}")
    if not math.isclose(theta, primary["C_minus_B"], abs_tol=1e-15):
        raise ValueError("Sensitivity estimate differs from the primary estimate")
    if len(clusters) != 16:
        raise ValueError(f"Expected 16 task clusters, found {len(clusters)}")
    leave_cluster = []
    for cluster, members in clusters.items():
        retained = {t: v for t, v in task_means.items() if t not in members}
        leave_cluster.append(
            {
                "removed": cluster,
                "removed_tasks": members,
                "remaining_tasks": len(retained),
                "estimate": mean(retained.values()),
            }
        )
    leave_values = [r["estimate"] for r in leave_cluster]
    center = mean(leave_values)
    jackknife_se = math.sqrt(15 / 16 * sum((v - center) ** 2 for v in leave_values))
    leave_model = []
    for provider, model in models:
        group = [r for r in rows if (r["provider"], r["model"]) != (provider, model)]
        leave_model.append({"removed": [provider, model], **contrast(group)})
    strata = []
    for model_filter in [None, *models]:
        for base in [False, True]:
            for behavior in [False, True]:
                group = [
                    r
                    for r in annotated
                    if r["base_pass"] == base
                    and r["behavior_pass"] == behavior
                    and (model_filter is None or (r["provider"], r["model"]) == model_filter)
                ]
                strata.append(
                    {
                        "configuration": model_filter,
                        "base_pass": base,
                        "behavior_pass": behavior,
                        **contrast(group),
                        "runtime_in_either_D": sum(r["runtime_in_either_D"] for r in group),
                        "truncated_B": sum(r["base_truncated"] for r in group),
                        "truncated_C": sum(
                            r["base_truncated"] or r["behavior_truncated"] for r in group
                        ),
                    }
                )
    special = [r for r in annotated if r["base_pass"] and not r["behavior_pass"]]
    same = set(range(1, 10)) | set(range(12, 17))
    equivalent = {21, 23}
    coverage = defaultdict(list)
    for row in rows:
        number = int(row["task_id"][1:3])
        category = (
            "identical_base"
            if number in same
            else ("equivalent_base" if number in equivalent else "different_base_data")
        )
        coverage[category].append(row)
    return {
        "scope": "Post hoc sensitivity; fixed configurations; purposive corpus",
        "overall": overall,
        "estimate": theta,
        "task_means": task_means,
        "clusters": dict(clusters),
        "primary": primary["bootstrap"],
        "S1": bootstrap(task_means, clusters, seed=250920261),
        "S2": {
            "estimates": leave_cluster,
            "range": [min(leave_values), max(leave_values)],
            "jackknife_SE_descriptive": jackknife_se,
        },
        "S3": leave_model,
        "S4": cr2(task_means, clusters),
        "S5": bootstrap(task_means, {t: [t] for t in task_means}, seed=250920265),
        "strata": strata,
        "signal_stratum_without_local": contrast([r for r in special if r["provider"] != "local"]),
        "base_coverage": [
            {"category": k, "tasks": len({r["task_id"] for r in v}), **contrast(v)}
            for k, v in sorted(coverage.items())
        ],
    }
