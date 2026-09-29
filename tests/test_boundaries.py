import hashlib
import importlib.util
import io
import json
import subprocess
import tarfile
from pathlib import Path

import pytest

from feedback_study import integrity, sandbox
from feedback_study.scenarios import CELLS, matrix

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("check_secrets", ROOT / "scripts/check_secrets.py")
scanner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scanner)


def test_matrix_keeps_unreached_pairs_and_all_nine_cells():
    rows = [
        {"root": "one", "B": "not_reached", "C": "pass"},
        {"root": "one", "B": "fail", "C": "pass"},
        {"root": "two", "B": "pass", "C": "not_reached"},
    ]
    result = matrix(rows)
    assert set(result["cells"]) == set(CELLS)
    assert sum(result["cells"].values()) == 3
    assert result["roots"] == 2
    assert result["cells"]["not_reached/pass"] == 1
    assert result["C_gain_roots"] == ["one"]


def test_credential_scan_reports_location_without_the_value(tmp_path):
    secret = "sk-proj-" + "x" * 40
    (tmp_path / "response.json").write_text(json.dumps({"key": secret}))
    count, issues = scanner.scan(tmp_path, [secret.encode()])
    assert count == 1
    assert {i["rule"] for i in issues} == {"provider-key", "known-local-credential"}
    assert secret not in json.dumps(issues)


def test_credential_scan_reads_archive_members(tmp_path):
    secret = b"private-value-" + b"z" * 25
    with tarfile.open(tmp_path / "evidence.tar.gz", "w:gz") as archive:
        item = tarfile.TarInfo("nested/response.txt")
        item.size = len(secret)
        archive.addfile(item, io.BytesIO(secret))
    _, issues = scanner.scan(tmp_path, [secret])
    assert issues == [
        {"file": "evidence.tar.gz:nested/response.txt", "rule": "known-local-credential"}
    ]


@pytest.mark.parametrize("path", ["../outside", "/absolute", "a/../../b", "a\\b"])
def test_distribution_paths_cannot_escape_the_root(tmp_path, path):
    with pytest.raises(ValueError):
        integrity.safe_path(tmp_path, path)


def test_checksum_verification_rejects_changed_inputs(tmp_path):
    (tmp_path / "data").mkdir()
    content = tmp_path / "data/outcomes.json"
    content.write_text("original")
    manifest = {"files": {"data/outcomes.json": integrity.sha256(content)}}
    (tmp_path / "data/manifest.json").write_text(json.dumps(manifest))
    assert integrity.verify(tmp_path) == 1
    content.write_text("changed")
    with pytest.raises(ValueError, match="Changed or missing"):
        integrity.verify(tmp_path)


def test_extraction_rejects_links_even_with_correct_archive_checksum(tmp_path):
    (tmp_path / "data").mkdir()
    (tmp_path / "provenance").mkdir()
    archive = tmp_path / "evidence.tar.gz"
    with tarfile.open(archive, "w:gz") as stream:
        link = tarfile.TarInfo("response")
        link.type = tarfile.SYMTYPE
        link.linkname = "../outside"
        stream.addfile(link)
    (tmp_path / "data/manifest.json").write_text(
        json.dumps(
            {
                "archive": {"sha256": integrity.sha256(archive), "members": 1},
            }
        )
    )
    (tmp_path / "provenance/export.json").write_text(
        json.dumps(
            {
                "evidence/response": {"export_sha256": hashlib.sha256(b"").hexdigest()},
            }
        )
    )
    with pytest.raises(ValueError, match="non-file"):
        integrity.extract(tmp_path, archive, tmp_path / "unpacked")
    assert not (tmp_path / "unpacked").exists()


def test_docker_failure_is_not_a_model_failure(tmp_path, monkeypatch):
    commands = []

    def failed(command, **kwargs):
        commands.append(command)
        return subprocess.CompletedProcess(command, 125, "", "daemon unavailable")

    monkeypatch.setattr(sandbox.subprocess, "run", failed)
    result = sandbox.run("", "", tmp_path, image="sha256:test")
    assert result["valid"] is False
    assert result["reason"] == "infrastructure"
    command = commands[0]
    for flag, value in [
        ("--network", "none"),
        ("--pull", "never"),
        ("--user", "1000:1000"),
        ("--cap-drop", "ALL"),
        ("--security-opt", "no-new-privileges"),
    ]:
        assert command[command.index(flag) + 1] == value
    assert "--read-only" in command
    assert list(tmp_path.iterdir()) == []
