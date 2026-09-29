"""Addendum v3 runner: branch Q (failure signal without details) for the S* roots of confirmatory v2.

Usage: python -m research.confirmatory_v2.runner_v3_signal [--offline-smoke] [--analyze]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from pathlib import Path

from ruby_llm_eval.config import load_pricing, load_providers
from ruby_llm_eval.generate import Sample, build_prompt, strip_code_fences
from ruby_llm_eval.model_client import build_client

from research.pilot_suite import compose_task
from research.repair_pilot import REPAIR_INSTRUCTION, diagnostic_feedback, evaluation, load_keys, now, price, save

HERE = Path(__file__).resolve().parent
V2 = Path("results/confirmatory-v2-20260928")
OUT = Path("results/confirmatory-v3-signal-20260928")
FILLER_Q = "A behavioral check failed; no further details are provided. "
BOOT, SEED = 20000, 28092028


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def acc(ev, p, s):
    return bool([e for e in ev if e["partition"] == p and e["suite"] == s][0]["accepted"])


def signal_prompt(task_prompt, original, evaluations):
    real = {"functional": diagnostic_feedback(evaluations, "base"), "behavioral": diagnostic_feedback(evaluations, "behavior")}
    target = len(json.dumps(real, ensure_ascii=True))
    q = {"functional": real["functional"],
         "behavioral": {"status": real["behavioral"]["status"], "accepted": real["behavioral"]["accepted"], "counts": None,
                        "output": "", "output_truncated": False}}
    need = max(0, target - len(json.dumps(q, ensure_ascii=True)))
    q["behavioral"]["output"] = (FILLER_Q * (need // len(FILLER_Q) + 1))[:need]
    ser = json.dumps(q, ensure_ascii=True)
    prompt = (build_prompt(task_prompt) + "\n" + REPAIR_INSTRUCTION + "\n--- ORIGINAL SOLUTION ---\n" + original
              + "\n--- AVAILABLE DIAGNOSTIC FEEDBACK ---\n" + ser + "\n--- END FEEDBACK ---\nReturn only the complete Ruby source.\n")
    return prompt, {"target_chars": target, "q_chars": len(ser), "length_matched": len(ser) == target}


def sstar_roots():
    roots = []
    for a in sorted(V2.glob("answers/*/*/*/A/evaluations.json")):
        ev = json.loads(a.read_text())
        if acc(ev, "diagnostic", "base") and not acc(ev, "diagnostic", "behavior"):
            base = a.parent.parent
            roots.append(dict(provider=base.parts[-3], task=base.parts[-2], repeat=int(base.parts[-1]), base=base))
    return roots


def run(offline_smoke=False):
    if not offline_smoke:
        fr = json.loads((HERE / "freeze_v3.json").read_text())
        for name, digest in fr["sha256"].items():
            if sha(HERE / name) != digest:
                raise SystemExit(f"{name} changed after freeze")
    v2plan = json.loads((V2 / "plan.json").read_text())
    specs = {s["provider"]: s for s in json.loads(Path("research/main-models.json").read_text())["models"]}
    providers = load_providers(Path("configs")); pricing = load_pricing(Path("configs"))
    if not offline_smoke:
        load_keys()
    roots = sstar_roots()
    out = Path("/tmp/v3-smoke") if offline_smoke else OUT
    out.mkdir(parents=True, exist_ok=True)
    if offline_smoke:
        roots = roots[:2]
    clients = {} if offline_smoke else {p: build_client(p, specs[p]["model"], providers, api_key="local-only" if p == "local" else None)
                                        for p in {r["provider"] for r in roots}}
    rng = random.Random(28092029); rng.shuffle(roots)
    save(out / "plan.json", {"created_at": now(), "n_roots": len(roots), "image_id": v2plan["image_id"], "offline_smoke": offline_smoke,
                             "order": [f"{r['provider']}/{r['task']}/{r['repeat']}" for r in roots]})
    snapshot = V2 / "corpus"

    def one(r, pool):
        loc = out / "answers" / r["provider"] / r["task"] / str(r["repeat"]) / "Q"
        if (loc / "evaluations.json").exists():
            return
        loc.mkdir(parents=True, exist_ok=True)
        ev = json.loads((r["base"] / "A" / "evaluations.json").read_text())
        prompt, meta = signal_prompt((snapshot / r["task"] / "prompt.md").read_text(), (r["base"] / "A" / "solution.rb").read_text(), ev)
        (loc / "prompt.txt").write_text(prompt)
        gen = specs[r["provider"]]["options"]; rates = pricing.get(specs[r["provider"]]["model"])
        req = {"provider": r["provider"], "task_id": r["task"], "repeat": r["repeat"], "branch": "Q", "started_at": now(),
               "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(), "generation_options": gen, "signal": meta}
        save(loc / "request.json", req); t0 = time.monotonic()
        if offline_smoke:
            resp = {"text": (snapshot / r["task"] / "solution_ref.rb").read_text(), "input_tokens": 0, "output_tokens": 0}
        else:
            waits = [30, 60, 120, 240, 300, 300, 300]
            for attempt in range(len(waits) + 1):
                try:
                    resp = clients[r["provider"]].complete(prompt, **gen); break
                except Exception as exc:
                    req.setdefault("transport_errors", []).append(f"{type(exc).__name__}: {str(exc)[:300]}"); save(loc / "request.json", req)
                    if attempt == len(waits):
                        raise
                    time.sleep(waits[attempt])
        sample = Sample(r["repeat"], strip_code_fences(resp["text"]), resp["input_tokens"], resp["output_tokens"],
                        raw_text=resp["text"], metadata=resp.get("metadata"))
        saved = asdict(sample); saved["latency_seconds"] = time.monotonic() - t0; saved["estimated_api_usd"] = price(saved, rates)
        save(loc / "sample.json", saved); (loc / "solution.rb").write_text(sample.code)
        req.update(state="completed", completed_at=now()); save(loc / "request.json", req)
        futs = [pool.submit(evaluation, compose_task(r["task"], p, s, snapshot), sample, p, s, v2plan["image_id"], out / ".sandbox")
                for p, s in (("diagnostic", "base"), ("diagnostic", "behavior"), ("holdout", "base"), ("holdout", "strict"))]
        evals = [f.result() for f in futs]; save(loc / "evaluations.json", evals)
        if any(e["category"] == "infrastructure_error" for e in evals):
            raise RuntimeError("Docker infrastructure error")
        print(r["provider"], r["task"], r["repeat"], "Q saved", flush=True)

    by_prov = defaultdict(list)
    for r in roots:
        by_prov[r["provider"]].append(r)
    with ThreadPoolExecutor(max_workers=4) as pool, ThreadPoolExecutor(max_workers=3) as workers:
        futs = [workers.submit(lambda rs: [one(r, pool) for r in rs], rs) for rs in by_prov.values()]
        for f in futs:
            f.result()
    print("done")


def analyze():
    by = defaultdict(list); rows = []
    for r in sstar_roots():
        q = OUT / "answers" / r["provider"] / r["task"] / str(r["repeat"]) / "Q"
        row = {"provider": r["provider"], "task": r["task"]}
        for b in "ABCP":
            row[b] = acc(json.loads((r["base"] / b / "evaluations.json").read_text()), "holdout", "strict")
        row["Q"] = acc(json.loads((q / "evaluations.json").read_text()), "holdout", "strict")
        row["Q_unchanged"] = (q / "solution.rb").read_text().strip() == (r["base"] / "A" / "solution.rb").read_text().strip()
        rows.append(row)
    cl = {t["id"]: t["template_cluster"] for t in json.loads((V2 / "corpus" / "manifest.json").read_text())["tasks"]}
    for row in rows:
        by[cl[row["task"]]].append(row)
    keys = sorted(by)

    def boot(x, y):
        f = lambda rs: sum(r[x] - r[y] for r in rs) / len(rs)
        rng = random.Random(SEED); vals = []
        for _ in range(BOOT):
            vals.append(f([r for k in (rng.choice(keys) for _ in keys) for r in by[k]]))
        vals.sort()
        return {"estimate": f(rows), "lo95": vals[int(0.025 * BOOT)], "hi95": vals[int(0.975 * BOOT) - 1],
                "x_only": sum(r[x] and not r[y] for r in rows), "y_only": sum(r[y] and not r[x] for r in rows)}
    res = {"n": len(rows), "repaired": {b: sum(r[b] for r in rows) for b in "BCPQ"}, "H3_C_minus_Q": boot("C", "Q"),
           "Q_minus_B": boot("Q", "B"), "Q_minus_P": boot("Q", "P"),
           "by_provider": {p: {b: sum(r[b] for r in rows if r["provider"] == p) for b in "BCPQ"} | {"n": sum(r["provider"] == p for r in rows),
                                "Q_unchanged": sum(r["Q_unchanged"] for r in rows if r["provider"] == p)} for p in sorted({r["provider"] for r in rows})}}
    res["H3_C_minus_Q"]["decision"] = "confirmed" if res["H3_C_minus_Q"]["lo95"] > 0 else "not_confirmed"
    (OUT / "analysis_v3.json").write_text(json.dumps(res, indent=1)); print(json.dumps(res, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--offline-smoke", action="store_true"); ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    analyze() if a.analyze else run(a.offline_smoke)
