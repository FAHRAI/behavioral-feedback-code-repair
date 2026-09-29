"""Paired contrast and conditional stratified cluster bootstrap."""

import random
from collections import defaultdict
from statistics import mean


def percentile(values, probability):
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    low = int(position)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def analyze(rows, manifest, *, models, n, bootstrap_replicates=10_000, seed=24092028):
    if n < 1 or bootstrap_replicates < 2:
        raise ValueError("Positive sample count and at least two bootstrap replicates required")
    cases = {case["id"]: case for case in manifest["tasks"]}
    model_ids = sorted(tuple(item) for item in models)
    if not cases or not model_ids or len(set(model_ids)) != len(model_ids):
        raise ValueError("Nonempty corpus and unique configurations required")
    paired = {}
    for row in rows:
        key = row["task_id"], (row["provider"], row["model"]), row["repeat"]
        if key in paired:
            raise ValueError("Duplicate original-answer triple")
        if not all(arm in row for arm in "ABC"):
            raise ValueError("Incomplete A/B/C triple; report missingness before final analysis")
        for arm in "ABC":
            if type(row[arm]["S"]) is not bool:
                raise ValueError("Outcomes must be measured booleans")
            if row[arm].get("category") == "infrastructure_error":
                raise ValueError("Infrastructure failure is not model quality")
        paired[key] = row
    expected = {
        (task, model, repeat) for task in cases for model in model_ids for repeat in range(n)
    }
    if set(paired) != expected:
        raise ValueError(
            "Observed triples do not match the frozen corpus/configuration/repeat plan"
        )

    values = {}
    for task in sorted(cases):
        for model in model_ids:
            values[task, model] = [
                int(paired[task, model, repeat]["C"]["S"])
                - int(paired[task, model, repeat]["B"]["S"])
                for repeat in range(n)
            ]
    task_means = {task: mean(mean(values[task, m]) for m in model_ids) for task in sorted(cases)}
    groups = defaultdict(lambda: defaultdict(list))
    for task, case in sorted(cases.items()):
        groups[case["group"]][case["template_cluster"]].append(task)
    groups = {group: dict(clusters) for group, clusters in sorted(groups.items())}
    weights = {
        g: sum(len(tasks) for tasks in clusters.values()) / len(cases)
        for g, clusters in groups.items()
    }
    rng = random.Random(seed)
    draws = []
    for _ in range(bootstrap_replicates):
        statistic = 0.0
        for group, clusters in groups.items():
            selected = rng.choices(sorted(clusters), k=len(clusters))
            task_draws = []
            for cluster in selected:
                for task in clusters[cluster]:
                    # Drawing a paired difference is equivalent to resampling its
                    # original B/C pair together; never draw arms independently.
                    task_draws.append(
                        mean(mean(rng.choices(values[task, m], k=n)) for m in model_ids)
                    )
            statistic += weights[group] * mean(task_draws)
        draws.append(statistic)
    low, high = percentile(draws, 0.025), percentile(draws, 0.975)
    per_group = []
    for group, clusters in groups.items():
        tasks = [task for members in clusters.values() for task in members]
        per_group.append(
            {
                "group": group,
                "scenarios": len(tasks),
                "clusters": len(clusters),
                "C_minus_B": mean(task_means[task] for task in tasks),
            }
        )
    warnings = [
        "Purposively designed corpus: no population ranking or design-based Rails inference.",
        "Fixed model configurations and fixed requirement families; not randomly sampled models.",
        "The larger C context is part of the intervention, not controlled away.",
    ]
    single_cluster_groups = [g for g, clusters in groups.items() if len(clusters) == 1]
    if single_cluster_groups:
        warnings.append(
            "Single-cluster strata have no estimated scenario-composition variation: "
            + ", ".join(single_cluster_groups)
        )
    if low == high:
        warnings.append(
            "Degenerate bootstrap interval does not establish zero risk or equivalence."
        )
    return {
        "scope": "Descriptive paired contrast; conditional bootstrap sensitivity only.",
        "scenarios": len(cases),
        "clusters": sum(len(c) for c in groups.values()),
        "models": len(model_ids),
        "initial_answers": len(paired),
        "C_minus_B": mean(task_means.values()),
        "bootstrap": {
            "method": "percentile; clusters within fixed families; paired repeats",
            "replicates": bootstrap_replicates,
            "seed": seed,
            "interval_95": [low, high],
            "degenerate": low == high,
        },
        "groups": per_group,
        "leave_one_group_out": {
            group: mean(
                value for task, value in task_means.items() if cases[task]["group"] != group
            )
            for group in groups
            if len(groups) > 1
        },
        "warnings": warnings,
    }
