import hashlib
import json
from pathlib import Path

import pytest

FROZEN = Path(__file__).resolve().parents[1] / "frozen"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.mark.parametrize(
    ("record", "directory"),
    [
        ("confirmatory-v2/freeze.json", "confirmatory-v2"),
        ("confirmatory-v2/amendment-1/amendment_1.json", "confirmatory-v2/amendment-1"),
        ("signal-addendum/freeze_v3.json", "signal-addendum"),
    ],
)
def test_frozen_files_match_their_records(record, directory):
    hashes = json.loads((FROZEN / record).read_text())["sha256"]
    for name, expected in hashes.items():
        assert sha256(FROZEN / directory / name) == expected, name


def test_amendment_replaces_the_frozen_runner():
    amendment = json.loads((FROZEN / "confirmatory-v2/amendment-1/amendment_1.json").read_text())
    assert amendment["original_runner_sha256"] == sha256(FROZEN / "confirmatory-v2/runner_v2.py")
