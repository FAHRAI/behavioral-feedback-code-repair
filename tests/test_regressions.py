import json
import subprocess
import sys
from pathlib import Path

import pytest

from feedback_study import cli, sandbox

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    ("stdout", "stderr", "expected_stdout", "expected_stderr"),
    [(b"partial\xff", b"error\n", "partial\ufffd", "error\n"), (None, None, "", "")],
)
def test_host_timeout_preserves_text(
    tmp_path, monkeypatch, stdout, stderr, expected_stdout, expected_stderr
):
    def timeout(command, **kwargs):
        if command[1] == "run":
            raise subprocess.TimeoutExpired(command, 20, output=stdout, stderr=stderr)
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(sandbox.subprocess, "run", timeout)
    result = sandbox.run("", "", tmp_path, image="sha256:test")
    assert result["valid"] is False
    assert result["reason"] == "host_timeout"
    assert result["stdout"] == expected_stdout
    assert result["stderr"] == expected_stderr
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize(
    ("case", "message"),
    [
        ("scenario_count", "Expected 19 discordant"),
        ("scenario_successes", "Expected 16 C-only"),
        ("outcome_counts", "Unexpected study outcome counts"),
        ("estimate", "differs from the primary estimate"),
        ("clusters", "Expected 16 task clusters"),
    ],
)
def test_study_guards_remain_active_under_optimization(case, message):
    program = r"""import json
import sys
from pathlib import Path
from feedback_study import scenarios, sensitivity
from feedback_study.data import load_study, read

root, case = Path(sys.argv[1]), sys.argv[2]
try:
    if case == "scenario_count":
        scenarios.analysis([], [])
    elif case == "scenario_successes":
        scenarios.analysis([], [{"root": str(i), "B": True, "C": False} for i in range(19)])
    else:
        rows, manifest, models, annotated, _ = load_study(root)
        tasks = {t["id"]: t for t in manifest["tasks"]}
        primary = read(root / "data/expected/primary.json")
        if case == "outcome_counts":
            rows[0]["B"]["S"] = not rows[0]["B"]["S"]
        elif case == "estimate":
            primary["C_minus_B"] += 1
        elif case == "clusters":
            for task in tasks.values():
                task["template_cluster"] = "one"
        sensitivity.analyze(rows, tasks, models, annotated, primary)
except ValueError as error:
    print(json.dumps({"error": str(error)}))
else:
    raise SystemExit("Invalid study input was accepted")
"""
    result = subprocess.run(
        [sys.executable, "-O", "-c", program, str(ROOT), case],
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert result.returncode == 0, result.stderr
    assert message in json.loads(result.stdout)["error"]


def test_reproduction_mismatch_writes_nothing(tmp_path, monkeypatch):
    monkeypatch.setattr(cli.integrity, "verify", lambda root: None)
    monkeypatch.setattr(cli, "load_study", lambda root: ([], {"tasks": []}, [], [], {"n": 10}))
    monkeypatch.setattr(cli, "load_scenarios", lambda root, annotations: ([], []))
    monkeypatch.setattr(cli.primary, "analyze", lambda *args, **kwargs: {})
    monkeypatch.setattr(cli.sensitivity, "analyze", lambda *args: {"changed": True})
    monkeypatch.setattr(cli.scenarios, "analysis", lambda *args: {})
    monkeypatch.setattr(cli.confirmatory, "analyze", lambda *args: {"roots": 0})
    monkeypatch.setattr(cli, "read", lambda path: {})
    output = tmp_path / "output"
    with pytest.raises(ValueError, match="sensitivity differs"):
        cli.reproduce(tmp_path, output)
    assert not output.exists()


def test_numeric_comparison_tolerates_last_digit_differences():
    assert cli.matches({"x": [2.2239945611338943]}, {"x": [2.2239945611338783]})
    assert not cli.matches({"x": [2.224]}, {"x": [2.225]})
    assert not cli.matches({"x": 1}, {"x": 1.0})
