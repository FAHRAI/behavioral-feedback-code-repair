from copy import deepcopy

import pytest

from feedback_study.primary import analyze


def fixture():
    models = [["x", "a"], ["y", "b"]]
    cases = [
        {"id": "one", "group": "g1", "template_cluster": "shared"},
        {"id": "two", "group": "g1", "template_cluster": "shared"},
        {"id": "three", "group": "g2", "template_cluster": "other"},
    ]
    rows = [
        {
            "task_id": c["id"],
            "provider": p,
            "model": m,
            "repeat": i,
            "A": {"S": False},
            "B": {"S": False},
            "C": {"S": True},
        }
        for c in cases
        for p, m in models
        for i in range(3)
    ]
    return rows, {"tasks": cases}, models


def test_perfect_paired_effect_does_not_miscount_shared_templates():
    rows, manifest, models = fixture()
    result = analyze(rows, manifest, models=models, n=3, bootstrap_replicates=50)
    assert result["C_minus_B"] == 1
    assert result["scenarios"] == 3
    assert result["clusters"] == 2
    assert result["bootstrap"]["interval_95"] == [1, 1]
    assert result["bootstrap"]["degenerate"]
    assert any("Single-cluster" in warning for warning in result["warnings"])
    assert any("Degenerate" in warning for warning in result["warnings"])


def test_paired_cancellation_and_family_sensitivity():
    rows, manifest, models = fixture()
    for row in rows:
        if row["task_id"] == "three":
            row["B"]["S"] = True
            row["C"]["S"] = False
    result = analyze(rows, manifest, models=models, n=3, bootstrap_replicates=50)
    assert result["C_minus_B"] == pytest.approx(1 / 3)
    assert result["leave_one_group_out"] == {"g1": -1, "g2": 1}


def test_seeded_analysis_is_independent_of_input_order():
    rows, manifest, models = fixture()
    for row in rows:
        row["C"]["S"] = row["repeat"] % 2 == 0
    result = analyze(rows, manifest, models=models, n=3, bootstrap_replicates=50, seed=4)
    assert result == analyze(
        rows[::-1], manifest, models=models[::-1], n=3, bootstrap_replicates=50, seed=4
    )


@pytest.mark.parametrize("defect", ["missing_row", "missing_arm", "duplicate", "infra", "unknown"])
def test_incomplete_or_invalid_evidence_cannot_be_silently_dropped(defect):
    rows, manifest, models = fixture()
    if defect == "missing_row":
        rows.pop()
    elif defect == "missing_arm":
        del rows[0]["C"]
    elif defect == "duplicate":
        rows.append(deepcopy(rows[0]))
    elif defect == "infra":
        rows[0]["C"]["category"] = "infrastructure_error"
    else:
        rows[0]["task_id"] = "outside-plan"
    with pytest.raises(ValueError):
        analyze(rows, manifest, models=models, n=3, bootstrap_replicates=10)
