"""Execute archived Ruby programs in isolated Docker containers."""

import json
import re
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path

SUMMARY = re.compile(
    r"(\d+) runs?, (\d+) assertions?, (\d+) failures?, (\d+) errors?, (\d+) skips?"
)
PREFIX = "SCENARIO_V1 "


def run(code, test, scratch, *, image, timeout=20):
    """Sentinel distinguishes Ruby load failure from Docker infrastructure failure."""
    scratch = Path(scratch)
    scratch.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(dir=scratch, prefix="scenario_")).resolve()
    container = "scenario_" + uuid.uuid4().hex[:12]
    try:
        (work / "solution.rb").write_text(code)
        (work / "test.rb").write_text(test)
        (work / "entry.rb").write_text(
            'STDOUT.sync=true\nputs "SCENARIO_CONTAINER_STARTED"\nload "/work/test.rb"\n'
        )
        work.chmod(0o755)
        for p in work.iterdir():
            p.chmod(0o644)
        cmd = [
            "docker",
            "run",
            "--rm",
            "--name",
            container,
            "--network",
            "none",
            "--memory",
            "256m",
            "--cpus",
            "1",
            "--pids-limit",
            "128",
            "--read-only",
            "--tmpfs",
            "/tmp:size=64m",
            "-e",
            "HOME=/tmp",
            "-v",
            f"{work}:/work:ro",
            "-w",
            "/work",
            "--pull",
            "never",
            "--user",
            "1000:1000",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges",
            image,
            "timeout",
            f"{timeout}s",
            "ruby",
            "entry.rb",
        ]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 15)
            stdout, stderr, rc = proc.stdout, proc.stderr, proc.returncode
        except subprocess.TimeoutExpired as exc:
            subprocess.run(["docker", "kill", container], capture_output=True, timeout=10)
            return {
                "valid": False,
                "reason": "host_timeout",
                "stdout": (exc.stdout or b"").decode(errors="replace"),
                "stderr": (exc.stderr or b"").decode(errors="replace"),
            }
        if "SCENARIO_CONTAINER_STARTED\n" not in stdout:
            return {
                "valid": False,
                "reason": "infrastructure",
                "returncode": rc,
                "stdout": stdout,
                "stderr": stderr,
            }
        match = SUMMARY.search(stdout)
        counts = list(map(int, match.groups())) if match else None
        status = (
            "timeout"
            if rc == 124
            else (
                "passed"
                if rc == 0 and counts and counts[0] and counts[1]
                else ("failed" if counts else "error")
            )
        )
        events = []
        for line in stdout.splitlines():
            if line.startswith(PREFIX):
                events.append(json.loads(line[len(PREFIX) :]))
        return dict(
            valid=True,
            status=status,
            returncode=rc,
            counts=counts,
            stdout=stdout,
            stderr=stderr,
            events=events,
        )
    finally:
        shutil.rmtree(work)
