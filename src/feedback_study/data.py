"""Read the fixed study inputs and reject incomplete or inconsistent records."""

import json
from pathlib import Path


def read(path: Path):
    return json.loads(path.read_text())


def load_study(root: Path):
    plan = read(root / "data/main/plan.json")
    manifest = read(root / "corpus/manifest.json")
    rows = read(root / "data/main/summary.json")["paired_rows"]
    annotated = read(root / "data/main/annotated-pairs.json")
    if plan["state"] != "completed" or plan["offline_smoke"]:
        raise ValueError("A completed model experiment is required")
    tasks = {t["id"]: t for t in manifest["tasks"]}
    models = sorted(tuple(m) for m in plan["models"])
    expected = {(t, *m, r) for t in tasks for m in models for r in range(plan["n"])}

    def index(records):
        result = {}
        for row in records:
            key = tuple(row[k] for k in ("task_id", "provider", "model", "repeat"))
            if key in result:
                raise ValueError("Duplicate initial solution")
            for arm in "ABC":
                if arm not in row or type(row[arm]["S"]) is not bool:
                    raise ValueError("Missing measured outcome")
                if row[arm].get("category") == "infrastructure_error":
                    raise ValueError("Infrastructure failure cannot be a model outcome")
            result[key] = row
        if set(result) != expected:
            raise ValueError("Records do not match the collection plan")
        return result

    paired, annotations = index(rows), index(annotated)
    for key, row in paired.items():
        if any(row[arm] != annotations[key][arm] for arm in "ABC"):
            raise ValueError("Diagnostic annotation changes an outcome")
        if any(type(annotations[key][k]) is not bool for k in ("base_pass", "behavior_pass")):
            raise ValueError("Invalid diagnostic state")
    return rows, manifest, models, annotated, plan


def load_scenarios(root: Path, annotated):
    rows = read(root / "data/scenarios/paired-scenarios.json")
    original = read(root / "data/scenarios/original-outcomes.json")
    cohort = {
        f"{r['provider']}/{r['task_id']}/{r['repeat']}": r
        for r in annotated
        if r["base_pass"] and not r["behavior_pass"]
    }
    originals = {r["root"]: r for r in original}
    if len(originals) != len(original) or set(originals) != set(cohort):
        raise ValueError("Scenario cohort differs from initial diagnostic selection")
    for key, row in originals.items():
        if any(type(row[a]) is not bool or row[a] != cohort[key][a]["S"] for a in "ABC"):
            raise ValueError("Scenario original outcome differs from the main study")
    seen = set()
    for row in rows:
        key = row["root"], row["scenario"]
        if key in seen or row["root"] not in cohort:
            raise ValueError("Duplicate or out-of-cohort checkpoint")
        seen.add(key)
        if any(row[a] not in {"pass", "fail", "not_reached"} for a in "ABC"):
            raise ValueError("Invalid checkpoint outcome")
    if {r["root"] for r in rows} != set(cohort):
        raise ValueError("Missing scenario root")
    return rows, original
