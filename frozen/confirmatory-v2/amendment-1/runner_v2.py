"""Confirmatory v2 runner: new initial solutions, repair branches B, C and length-matched P.

Reuses the unchanged main-experiment functions (research/repair_pilot.py). See protocol.md.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import shutil
import subprocess
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from pathlib import Path

from ruby_llm_eval.config import load_pricing, load_providers
from ruby_llm_eval.evaluate import IMAGE_TAG
from ruby_llm_eval.generate import Sample, build_prompt, strip_code_fences
from ruby_llm_eval.model_client import build_client

from research.pilot_suite import compose_task, load_manifest
from research.repair_pilot import (
    REPAIR_INSTRUCTION,
    diagnostic_feedback,
    evaluation,
    load_keys,
    now,
    price,
    repair_prompt,
    save,
)

HERE = Path(__file__).resolve().parent
CORPUS = Path("results/main-experiment-20260924/corpus")
MODELS = ["anthropic", "gemini", "local"]
FILLER = "No additional diagnostic information is provided in this block. "
FROZEN = {
    "research/repair_pilot.py": "results/main-experiment-20260924/runner.py",
    "research/pilot_suite.py": "results/main-experiment-20260924/composer.py",
    "ruby_llm_eval/model_client.py": "results/main-experiment-20260924/implementation/model_client.py",
    "ruby_llm_eval/evaluate.py": "results/main-experiment-20260924/implementation/evaluate.py",
    "ruby_llm_eval/generate.py": "results/main-experiment-20260924/implementation/generate.py",
}


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def placebo_prompt(task_prompt: str, original: str, evaluations: list[dict]) -> tuple[str, dict]:
    """Branch P: C's prompt with the behavioral object replaced by length-matched neutral filler."""
    real = {"functional": diagnostic_feedback(evaluations, "base"),
            "behavioral": diagnostic_feedback(evaluations, "behavior")}
    target = len(json.dumps(real, ensure_ascii=True))
    fake = {"functional": real["functional"],
            "behavioral": {"status": "not_reported", "accepted": None, "counts": None,
                           "output": "", "output_truncated": False}}
    base_len = len(json.dumps(fake, ensure_ascii=True))
    need = max(0, target - base_len)
    fake["behavioral"]["output"] = (FILLER * (need // len(FILLER) + 1))[:need]
    serialized = json.dumps(fake, ensure_ascii=True)
    prompt = (
        build_prompt(task_prompt)
        + "\n"
        + REPAIR_INSTRUCTION
        + "\n--- ORIGINAL SOLUTION ---\n"
        + original
        + "\n--- AVAILABLE DIAGNOSTIC FEEDBACK ---\n"
        + serialized
        + "\n--- END FEEDBACK ---\nReturn only the complete Ruby source.\n"
    )
    return prompt, {"target_chars": target, "placebo_chars": len(serialized), "length_matched": len(serialized) == target}


def build_schedule(tasks, models, n, seed):
    rng = random.Random(seed)
    schedule = []
    for repeat in range(n):
        ordered = tasks.copy(); rng.shuffle(ordered)
        for task_id in ordered:
            block = []
            ordered_models = models.copy(); rng.shuffle(ordered_models)
            for provider, model in ordered_models:
                branches = ["B", "C", "P"]; rng.shuffle(branches)
                block.append({"task_id": task_id, "repeat": repeat, "provider": provider, "model": model, "branches": branches})
            schedule.append(block)
    return schedule


def run(output: Path, *, n: int, cap: float, schedule_seed: int, offline_smoke: bool = False, resume: bool = False):
    for current, frozen in FROZEN.items():
        if sha(current) != sha(frozen):
            raise SystemExit(f"{current} differs from the frozen main-experiment copy")
    freeze = json.loads((HERE / "freeze.json").read_text()) if (HERE / "freeze.json").exists() else None
    if not offline_smoke:
        if freeze is None:
            raise SystemExit("freeze.json missing: freeze protocol/runner/analysis before real runs")
        allowed = dict(freeze["sha256"])
        amendment = HERE / "amendment_1.json"
        if amendment.exists():
            allowed.update(json.loads(amendment.read_text())["sha256"])
        for name, digest in allowed.items():
            if sha(HERE / name) != digest:
                raise SystemExit(f"{name} changed after freeze/amendment")
    providers = load_providers(Path("configs")); pricing = load_pricing(Path("configs"))
    if not offline_smoke:
        load_keys()
    specs = {s["provider"]: s for s in json.loads(Path("research/main-models.json").read_text())["models"]}
    models = [("offline", "reference-control")] if offline_smoke else [(p, specs[p]["model"]) for p in MODELS]
    options = {p: specs[p]["options"] for p in MODELS}
    options["offline"] = {"temperature": 0.2, "max_tokens": 4096}
    clients = {p: build_client(p, m, providers, api_key="local-only" if p == "local" else None)
               for p, m in models if p != "offline"}
    image_id = subprocess.check_output(["docker", "image", "inspect", IMAGE_TAG, "--format", "{{.Id}}"], text=True).strip()
    snapshot = output / "corpus"
    if resume:
        if not (output / "plan.json").exists():
            raise SystemExit("nothing to resume")
    else:
        output.mkdir(parents=True, exist_ok=False)
        shutil.copytree(CORPUS, snapshot)
    for name in ("protocol.md", "runner_v2.py", "analyze_v2.py"):
        if (HERE / name).exists():
            shutil.copy2(HERE / name, output / name)
    if any(p == "local" for p, _ in models) and not resume:
        prov = {}
        for key, endpoint, body in (("version", "/api/version", None), ("tags", "/api/tags", None),
                                    ("show", "/api/show", {"model": dict(models)["local"]})):
            req = urllib.request.Request("http://127.0.0.1:11434" + endpoint, data=json.dumps(body).encode() if body else None,
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                prov[key] = json.load(resp)
        save(output / "local-provenance.json", prov)
    tasks = [c["id"] for c in load_manifest(snapshot)["tasks"]]
    if offline_smoke:
        tasks, n = tasks[:1], 1
    schedule = build_schedule(tasks, models, n, schedule_seed)
    if resume:
        old = json.loads((output / "plan.json").read_text())
        if old["schedule"] != schedule or old["image_id"] != image_id:
            raise SystemExit("resume must use the identical schedule and sandbox image")
        log = output / "resumptions.jsonl"
        with log.open("a") as fh:
            fh.write(json.dumps({"utc": now(), "previous_state": old.get("state"), "previous_error": old.get("error"),
                                 "runner_sha256": sha(HERE / "runner_v2.py")}) + "\n")
    plan = {"created_at": now(), "state": "running", "offline_smoke": offline_smoke, "image_id": image_id,
            "corpus_version": load_manifest(snapshot)["version"], "n": n, "models": models, "task_ids": tasks,
            "generation_options": {p: options[p] for p, _ in models}, "seed_for_schedule_only": schedule_seed,
            "planned_generations": len(tasks) * len(models) * n * 4, "api_cost_cap_estimate_usd": cap,
            "frozen_implementation_sha256": {k: sha(k) for k in FROZEN}, "freeze": freeze, "schedule": schedule}
    save(output / "plan.json", plan)
    stop = threading.Event(); lock = threading.Lock(); state = {"spent": 0.0, "reserved": 0.0}

    def candidate(job, branch, prompt, pool, extra=None):
        if stop.is_set():
            raise RuntimeError("stopped after an earlier error")
        loc = output / "answers" / job["provider"] / job["task_id"] / str(job["repeat"]) / branch
        if loc.exists():
            req_old = json.loads((loc / "request.json").read_text()) if (loc / "request.json").exists() else {}
            if (loc / "sample.json").exists():
                if req_old.get("prompt_sha256") != hashlib.sha256(prompt.encode()).hexdigest():
                    raise SystemExit(f"saved prompt differs at {loc}")
                saved = json.loads((loc / "sample.json").read_text())
                sample = Sample(saved["index"], saved["code"], saved["input_tokens"], saved["output_tokens"],
                                raw_text=saved.get("raw_text"), metadata=saved.get("metadata"))
                if (loc / "evaluations.json").exists():
                    return sample, json.loads((loc / "evaluations.json").read_text())
                return sample, evaluate_saved(job, sample, loc, pool)
            # no answer was obtained: transport-only retry, keep the failed record
            failed = output / "failed-requests" / f"{job['provider']}__{job['task_id']}__{job['repeat']}__{branch}__{int(time.time())}"
            failed.parent.mkdir(exist_ok=True); shutil.move(str(loc), str(failed))
        loc.mkdir(parents=True, exist_ok=False)
        (loc / "prompt.txt").write_text(prompt)
        rates = pricing.get(job["model"]); gen = options[job["provider"]]
        reserve = (((len(prompt.encode()) + 1024) * max(rates["input"], rates.get("input_cache_write", 0))
                    + gen["max_tokens"] * rates["output"]) / 1e6) if rates else 0
        with lock:
            if state["spent"] + state["reserved"] + reserve > cap:
                stop.set(); raise RuntimeError("API cost guard reached")
            state["reserved"] += reserve
        request = {**job, "branch": branch, "started_at": now(), "state": "in_flight",
                   "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(), "generation_options": gen, **(extra or {})}
        save(loc / "request.json", request)
        started = time.monotonic()
        try:
            if offline_smoke:
                response = {"text": (snapshot / job["task_id"] / "solution_ref.rb").read_text(), "input_tokens": 0, "output_tokens": 0, "metadata": {"offline": True}}
            else:
                response = None
                waits = [30, 60, 120, 240, 300, 300, 300]  # amendment 1: transport-only backoff
                for attempt in range(len(waits) + 1):  # retry only when no answer was obtained
                    try:
                        response = clients[job["provider"]].complete(prompt, **gen); break
                    except Exception as exc:
                        request.setdefault("transport_errors", []).append(f"{type(exc).__name__}: {str(exc)[:300]}")
                        save(loc / "request.json", request)
                        if attempt == len(waits):
                            raise
                        time.sleep(waits[attempt])
            sample = Sample(job["repeat"], strip_code_fences(response["text"]), response["input_tokens"], response["output_tokens"],
                            raw_text=response["text"], metadata=response.get("metadata"))
            saved = asdict(sample); saved["latency_seconds"] = time.monotonic() - started; saved["estimated_api_usd"] = price(saved, rates)
            save(loc / "sample.json", saved); (loc / "solution.rb").write_text(sample.code)
            request.update(state="completed", completed_at=now()); save(loc / "request.json", request)
            with lock:
                state["spent"] += saved["estimated_api_usd"] or 0; state["reserved"] -= reserve
        except Exception as exc:
            request.update(state="transport_or_response_error", error_type=type(exc).__name__, error=str(exc)[:1200], completed_at=now())
            save(loc / "request.json", request); stop.set(); raise
        return sample, evaluate_saved(job, sample, loc, pool)

    def evaluate_saved(job, sample, loc, pool):
        futures = []
        for partition, suite in (("diagnostic", "base"), ("diagnostic", "behavior"), ("holdout", "base"), ("holdout", "strict")):
            task = compose_task(job["task_id"], partition, suite, snapshot)
            (loc / f"{partition}-{suite}.rb").write_text(task.test)
            futures.append(pool.submit(evaluation, task, sample, partition, suite, image_id, output / ".sandbox"))
        evaluations = [f.result() for f in futures]
        save(loc / "evaluations.json", evaluations)
        if any(e["category"] == "infrastructure_error" for e in evaluations):
            stop.set(); raise RuntimeError("Docker infrastructure error")
        return evaluations

    def chain(job, pool):
        task_prompt = (snapshot / job["task_id"] / "prompt.md").read_text()
        original, evals = candidate(job, "A", build_prompt(task_prompt), pool)
        for branch in job["branches"]:
            if branch == "P":
                prompt, meta = placebo_prompt(task_prompt, original.code, evals)
                candidate(job, "P", prompt, pool, extra={"placebo": meta})
            else:
                candidate(job, branch, repair_prompt(task_prompt, original.code, evals, branch), pool)
        print(job["provider"], job["task_id"], job["repeat"], "A/B/C/P saved", flush=True)

    try:
        with ThreadPoolExecutor(max_workers=4) as docker_pool, ThreadPoolExecutor(max_workers=3) as model_pool:
            for i, block in enumerate(schedule):
                for f in [model_pool.submit(chain, job, docker_pool) for job in block]:
                    f.result()
                save(output / "progress.json", {"completed_blocks": i + 1, "total_blocks": len(schedule), "estimated_api_usd": state["spent"], "updated_at": now()})
                print(f"Block {i + 1}/{len(schedule)}; API estimate ${state['spent']:.4f}", flush=True)
    except BaseException as exc:
        stop.set(); plan.update(state="interrupted", error_type=type(exc).__name__, error=str(exc)[:1200]); raise
    else:
        plan["state"] = "completed"
    finally:
        plan.update(finished_at=now(), estimated_api_usd=state["spent"]); save(output / "plan.json", plan)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--n", type=int, default=15)
    ap.add_argument("--cap", type=float, default=15.0)
    ap.add_argument("--schedule-seed", type=int, default=28092026)
    ap.add_argument("--offline-smoke", action="store_true")
    ap.add_argument("--resume", action="store_true")
    a = ap.parse_args()
    run(a.output, n=a.n, cap=a.cap, schedule_seed=a.schedule_seed, offline_smoke=a.offline_smoke, resume=a.resume)


if __name__ == "__main__":
    main()
