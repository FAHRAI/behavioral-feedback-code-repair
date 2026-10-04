# Behavioral test feedback for one-step repair of LLM-generated code

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23130102.svg)](https://doi.org/10.5281/zenodo.23130102)

Data, analysis code and reproduction tools for the paper

> O. Kholodniak, O. Prokhorov. *Behavioral test feedback for one-step repair of LLM-generated code.*
> Manuscript under review, 2026.

## The study in brief

Language models often repair generated code from test feedback, but code can pass basic functional
tests while still violating behavioral requirements of a database-backed application (query growth,
freshness, atomicity, repeated calls, literal input, access scope).

- **Main experiment.** 24 purpose-built Ruby on Rails tasks in 16 template clusters, four model
  configurations (GPT-6 Luna, Claude Sonnet 5, Gemini 3.5 Flash-Lite, Qwen2.5-Coder 7B) and ten
  initial solutions per task and configuration: 960 roots. Each initial solution (A) was repaired once
  with basic feedback (B) and once with basic plus behavioral feedback (C); repairs were judged by
  held-out strict tests. C − B = +1.67 percentage points, 95% interval [−0.42, 3.23].
- **Confirmatory experiment.** 1,080 new roots from three configurations, a neutral control P of the
  same character length as C's behavioral block, and a protocol fixed before any generation. In the
  diagnostic state S* (basic diagnostic tests pass, behavioral ones fail; 150 roots) C repaired 40
  roots, B 18 and P 20: C − B = +14.67 pp [5.36, 19.51], C − P = +13.33 pp [4.46, 20.00]. Both
  hypotheses were confirmed.
- **Signal-only addendum.** A branch Q that only states that a behavioral check failed, again of C's
  length, repaired 42 S* roots: C − Q = −1.33 pp [−2.97, 0.00]; no advantage of the full failure
  details was detected.

The protocols, runners and analysis scripts of the confirmatory experiment and the addendum are in
`frozen/`, together with their SHA-256 freeze records and one transport-only amendment. The frozen
records of the main experiment are available from the authors on request.

## Reproducing the results

The analysis needs Python 3.12 and no network access, credentials or Ruby.

```sh
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install --require-hashes -r requirements-dev.txt
python -m pip install --no-build-isolation --no-deps -e .
feedback-study verify
feedback-study reproduce --output outputs/reproduction
pytest -q
```

`reproduce` recomputes the primary bootstrap, the sensitivity analyses, the scenario tables and the
confirmatory and addendum analyses from `data/`, and compares them with `data/expected/`. Floating
point values may differ between platform math libraries in the last digits, so they are compared with
a relative tolerance of 1e-12; everything else must match exactly. Outputs go to a new directory.

## Evidence archives

Prompts, returned text, generated programs, composed tests and evaluation logs are archived on Zenodo
(https://doi.org/10.5281/zenodo.23129973) in two files whose checksums are recorded in
`data/manifest.json`:

- `evidence-main-v1.0.0.tar.gz`: main experiment, corpus audits and scenario follow-up;
- `evidence-confirmatory-v1.0.0.tar.gz`: confirmatory experiment and signal-only addendum.

```sh
feedback-study extract evidence-main-v1.0.0.tar.gz            # into .evidence/, checksum-verified
feedback-study export-confirmatory confirmatory-v2-20260928 \
    --addendum confirmatory-v3-signal-20260928 --output roots.json   # rebuilds data/confirmatory/roots.json
```

Saved programs can be re-executed in the pinned Ruby container (Docker, linux/arm64):

```sh
docker build --platform linux/arm64 -t behavioral-feedback-study:runtime runtime
STUDY_IMAGE=$(docker image inspect behavioral-feedback-study:runtime --format '{{.Id}}')
feedback-study replay anthropic/m17_literal_prefix/0 --branch C \
  --image "$STUDY_IMAGE" --output outputs/replay-example
```

Replay runs the saved solution against its held-out strict test in a container without network, with a
read-only filesystem, an unprivileged user and resource limits, and checks the outcome and assertion
counts against the archive. See [reproduction scope](docs/reproduction.md).

## Repository contents

| Path | Contents |
| --- | --- |
| `src/feedback_study/` | Analyses, input validation, archive verification and isolated replay |
| `tests/` | Pairing, weighting, archive boundaries, reproduction of reported values |
| `corpus/` | Tasks, fixtures, diagnostic and held-out checks, positive and negative controls |
| `data/main/` | Collection plan, paired outcomes, diagnostic annotations, tokens and costs |
| `data/scenarios/` | All 1,395 checkpoint pairs of the scenario follow-up and original outcomes |
| `data/confirmatory/` | Per-root outcomes, tokens and costs of the confirmatory experiment and addendum |
| `data/expected/` | Reported outputs used for comparison |
| `frozen/` | Confirmatory and addendum protocols, runners and analysis as fixed before data collection |
| `docs/` | Methods, supplement, code structure and reproduction scope |
| `provenance/` | Source and export checksums of every archived file |
| `runtime/` | Pinned Ruby container build recipe |
| `scripts/` | Credential and personal-path scan |

## Citation and license

See `CITATION.cff`. Code: MIT. Data and documentation: CC BY 4.0 (see `DATA-LICENSE.md`).
