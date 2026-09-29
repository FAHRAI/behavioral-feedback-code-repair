"""Verify the distribution and unpack only its declared evidence files."""

import hashlib
import shutil
import tarfile
from pathlib import Path, PurePosixPath

from .data import read


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def safe_path(root: Path, name: str) -> Path:
    parts = PurePosixPath(name)
    if parts.is_absolute() or ".." in parts.parts or "\\" in name or not parts.parts:
        raise ValueError("Unsafe manifest path")
    path = root / name
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("Path escapes the data directory")
    return path


def verify(root: Path) -> int:
    files = read(root / "data/manifest.json")["files"]
    for name, expected in files.items():
        path = safe_path(root, name)
        if path.is_symlink() or not path.is_file() or sha256(path) != expected:
            raise ValueError(f"Changed or missing input: {name}")
    return len(files)


def extract(root: Path, archive: Path, output: Path) -> int:
    expected = read(root / "data/manifest.json")["archive"]
    if sha256(archive) != expected["sha256"]:
        raise ValueError("Evidence archive checksum mismatch")
    records = read(root / "provenance/export.json")
    members = {
        k.removeprefix("evidence/"): v for k, v in records.items() if k.startswith("evidence/")
    }
    if len(members) != expected["members"]:
        raise ValueError("Archive manifest count mismatch")
    output.mkdir(parents=True, exist_ok=False)
    seen = set()
    try:
        with tarfile.open(archive, "r:gz") as stream:
            for member in stream:
                if not member.isfile() or member.name not in members or member.name in seen:
                    raise ValueError("Undeclared, duplicate or non-file archive member")
                if member.size > 100_000_000:
                    raise ValueError("Archive member exceeds size limit")
                target = safe_path(output, member.name)
                target.parent.mkdir(parents=True, exist_ok=True)
                with stream.extractfile(member) as source, target.open("xb") as dest:
                    shutil.copyfileobj(source, dest)
                if sha256(target) != members[member.name]["export_sha256"]:
                    raise ValueError(f"Evidence checksum mismatch: {member.name}")
                seen.add(member.name)
        if seen != set(members):
            raise ValueError("Incomplete evidence archive")
    except Exception:
        shutil.rmtree(output)
        raise
    return len(seen)
