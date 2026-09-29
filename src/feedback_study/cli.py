"""Commands for checksum verification, saved-data analysis and isolated replay."""

import argparse
import json
import math
import re
from pathlib import Path

from . import confirmatory, integrity, primary, scenarios, sensitivity
from .data import load_scenarios, load_study, read


def matches(actual, expected, rel_tol=1e-12):
    """Structural equality; floats may differ in the last digits between platform math libraries."""
    if isinstance(expected, dict):
        return (
            isinstance(actual, dict)
            and actual.keys() == expected.keys()
            and all(matches(actual[k], expected[k], rel_tol) for k in expected)
        )
    if isinstance(expected, list):
        return (
            isinstance(actual, list)
            and len(actual) == len(expected)
            and all(matches(a, e, rel_tol) for a, e in zip(actual, expected, strict=True))
        )
    if isinstance(expected, float) and isinstance(actual, float):
        return math.isclose(actual, expected, rel_tol=rel_tol, abs_tol=1e-15)
    return type(actual) is type(expected) and actual == expected


def reproduce(root: Path, output: Path):
    integrity.verify(root)
    if output.resolve().is_relative_to((root / "data").resolve()):
        raise ValueError("Analysis output cannot overwrite study inputs")
    rows, manifest, models, annotated, plan = load_study(root)
    p = primary.analyze(rows, manifest, models=models, n=plan["n"])
    s = sensitivity.analyze(rows, {t["id"]: t for t in manifest["tasks"]}, models, annotated, p)
    scenario_rows, original = load_scenarios(root, annotated)
    outputs = {
        "primary": p,
        "sensitivity": s,
        "scenarios": scenarios.analysis(scenario_rows, original),
        "confirmatory": confirmatory.analyze(
            read(root / "data/confirmatory/roots.json"), read(root / "data/main/costs.json")
        ),
    }
    for name, result in outputs.items():
        if not matches(json.loads(json.dumps(result)), read(root / f"data/expected/{name}.json")):
            raise ValueError(f"{name} differs from the archived calculation")
    output.mkdir(parents=True, exist_ok=False)
    for name, result in outputs.items():
        (output / f"{name}.json").write_text(json.dumps(result, indent=2) + "\n")
    return {
        "matched": list(outputs),
        "initial_solutions": len(rows),
        "checkpoint_pairs": len(scenario_rows),
        "confirmatory_roots": outputs["confirmatory"]["roots"],
    }


def replay(root: Path, evidence: Path, identity: str, branch: str, output: Path, image=None):
    from .sandbox import run

    integrity.verify(root)
    rows, _, _, _, plan = load_study(root)
    image = image or plan["image_id"]
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", image):
        raise ValueError("Replay requires an immutable Docker image ID")
    known = {f"{r['provider']}/{r['task_id']}/{r['repeat']}": r for r in rows}
    if identity not in known:
        raise ValueError("Unknown initial solution")
    base = f"results/main-experiment-20260924/answers/{identity}/{branch}"
    records = read(root / "provenance/export.json")

    def saved(name):
        relative = base + "/" + name
        path = integrity.safe_path(evidence, relative)
        if integrity.sha256(path) != records["evidence/" + relative]["export_sha256"]:
            raise ValueError("Changed replay input")
        return path.read_text()

    code, test = saved("solution.rb"), saved("holdout-strict.rb")
    reference = next(
        e
        for e in json.loads(saved("evaluations.json"))
        if e["partition"] == "holdout" and e["suite"] == "strict"
    )
    output.mkdir(parents=True, exist_ok=False)
    result = run(code, test, output / "scratch", image=image)
    result["image_id"] = image
    result["original_image"] = image == plan["image_id"]
    accepted = bool(
        result.get("status") == "passed"
        and result.get("counts")
        and result["counts"][2:] == [0, 0, 0]
    )
    result["matches_archive"] = bool(
        result["valid"]
        and accepted == reference["accepted"]
        and result.get("counts") == reference["counts"]
    )
    (output / "replay.json").write_text(json.dumps(result, indent=2) + "\n")
    if not result["valid"]:
        raise RuntimeError("Container execution failed; see replay.json")
    if not result["matches_archive"]:
        raise ValueError("Replay differs from archived H.strict outcome or counts")
    return {"matches_archive": True, "accepted": accepted, "counts": result["counts"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("verify")
    analysis = commands.add_parser("reproduce")
    analysis.add_argument("--output", type=Path, default=Path("outputs/reproduction"))
    unpack = commands.add_parser("extract")
    unpack.add_argument("archive", type=Path)
    unpack.add_argument("--output", type=Path, default=Path(".evidence"))
    export = commands.add_parser("export-confirmatory")
    export.add_argument("records", type=Path, help="extracted confirmatory records")
    export.add_argument("--addendum", type=Path, help="extracted signal-only addendum records")
    export.add_argument("--output", type=Path, required=True)
    run = commands.add_parser("replay")
    run.add_argument("identity", help="provider/task/repeat")
    run.add_argument("--branch", choices=list("ABC"), required=True)
    run.add_argument("--evidence", type=Path, default=Path(".evidence"))
    run.add_argument("--output", type=Path, required=True)
    run.add_argument("--image", help="Immutable image ID of a separately rebuilt runtime")
    args = parser.parse_args()
    if args.command == "verify":
        result = {"verified_files": integrity.verify(args.root)}
    elif args.command == "reproduce":
        result = reproduce(args.root, args.output)
    elif args.command == "export-confirmatory":
        roots = confirmatory.export_roots(args.records, args.addendum)
        args.output.write_text(json.dumps(roots, indent=1) + "\n")
        result = {"roots": len(roots)}
    elif args.command == "extract":
        result = {"extracted_files": integrity.extract(args.root, args.archive, args.output)}
    else:
        result = replay(
            args.root, args.evidence, args.identity, args.branch, args.output, args.image
        )
    print(json.dumps(result))


if __name__ == "__main__":
    main()
