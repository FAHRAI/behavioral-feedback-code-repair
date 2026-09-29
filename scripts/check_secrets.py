"""Scan files and archive members; report locations without printing matched values."""

from __future__ import annotations

import argparse
import re
import tarfile
from pathlib import Path

SKIP = {".git", ".venv", "__pycache__", ".pytest_cache", ".ruff_cache", "build", "dist"}
PATTERNS = {
    "provider-key": rb"\bsk-(?:ant-[A-Za-z0-9_-]{20,}|proj-[A-Za-z0-9_-]{20,}|[A-Za-z0-9]{32,})",
    "google-key": rb"\bAIza[0-9A-Za-z_-]{30,}",
    "github-token": rb"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})",
    "aws-key": rb"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b",
    "private-key": rb"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
    "credential-url": rb"https?://[^\s/:]+:[^\s/@]+@",
    "bearer-token": rb"(?i)authorization[\"'\s:]+bearer\s+[A-Za-z0-9._-]{20,}",
    "secret-assignment": (
        rb"(?i)(?:api[_-]?key|access[_-]?token|client[_-]?secret|password)"
        rb"[\"']?\s*[:=]\s*[\"'][A-Za-z0-9_/+=.-]{24,}[\"']"
    ),
}


def known_values(path: Path | None) -> list[bytes]:
    if path is None:
        return []
    values = []
    for line in path.read_text().splitlines():
        name, sep, value = line.partition("=")
        if sep and re.search(r"key|token|secret|password", name, re.I):
            value = value.strip().strip("\"'")
            if len(value) >= 12:
                values.append(value.encode())
    return values


def findings(name: str, content: bytes, secrets: list[bytes]) -> list[dict]:
    hits = [rule for rule, pattern in PATTERNS.items() if re.search(pattern, content)]
    if any(value in content for value in secrets):
        hits.append("known-local-credential")
    parts = Path(name).parts
    if any(p == ".env" or p.startswith(".env.") for p in parts):
        hits.append("environment-file")
    if re.search(rb"/(?:Users|home)/[^/\s]+/", content):
        hits.append("personal-home-path")
    return [{"file": name, "rule": rule} for rule in hits]


def scan(root: Path, secrets: list[bytes] = ()) -> tuple[int, list[dict]]:
    count, issues = 0, []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(part in SKIP for part in relative.parts):
            continue
        if path.is_symlink():
            issues.append({"file": str(relative), "rule": "symlink"})
        elif path.is_file():
            count += 1
            if path.name.endswith(".tar.gz"):
                with tarfile.open(path, "r:gz") as archive:
                    for member in archive:
                        if member.isfile():
                            count += 1
                            content = archive.extractfile(member).read()
                            issues.extend(findings(f"{relative}:{member.name}", content, secrets))
                        else:
                            issues.append(
                                {
                                    "file": f"{relative}:{member.name}",
                                    "rule": "non-file-archive-member",
                                }
                            )
            else:
                issues.extend(findings(str(relative), path.read_bytes(), secrets))
    return count, issues


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, nargs="?", default=Path("."))
    parser.add_argument("--known-env", type=Path)
    args = parser.parse_args()
    count, issues = scan(args.root, known_values(args.known_env))
    for issue in issues:
        print(f"{issue['file']}: {issue['rule']}")
    print(f"Scanned {count} files and archive members; {len(issues)} findings.")
    raise SystemExit(bool(issues))


if __name__ == "__main__":
    main()
