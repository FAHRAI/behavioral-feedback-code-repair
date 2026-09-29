# Confirmatory experiment v2: behavioral feedback in the "base-pass / behavior-fail" state, with a length-matched control

Status: written before any v2 generation. Protocol, runner and analysis script are hashed in
`freeze.json` before the first API call. This is an internal commitment, not a public preregistration.

## Background (from the main experiment, 24.09.2026)

In the main experiment (960 roots), adding the behavioral diagnostic block (branch C) to basic
functional feedback (branch B) gave +1.67 pp strict acceptance overall (interval including zero).
An exploratory analysis selected after the results located most of the gain in initial solutions that
passed D.base but failed D.behavior (104 roots: B repaired 12, C repaired 25). The main design could
not separate the content of the added block from its length.

## Questions

H1 (confirmatory): In the state S* = {initial solution A passes D.base and fails D.behavior},
branch C (D.base + D.behavior feedback) is accepted by H.strict more often than branch B (D.base only).

H2 (confirmatory): In S*, branch C is accepted by H.strict more often than branch P, a length-matched
control that receives D.base feedback plus a behavioral block of the same serialized length whose
text contains no diagnostic information.

## Design

- Corpus: the frozen main-experiment corpus snapshot (results/main-experiment-20260924/corpus,
  version main-candidate-0.1.1), 24 tasks, 16 template clusters. Unchanged.
- Implementation: research/repair_pilot.py, research/pilot_suite.py, ruby_llm_eval/{model_client,
  evaluate,generate}.py, byte-identical to the main-experiment frozen copies (hashes in freeze.json).
  Sandbox image sha256:d303858f9658… (same as main). Ollama 0.34.3, model digest af0048e09526 (same as main).
- Configurations: claude-sonnet-5, gemini-3.5-flash-lite, ruby-eval-qwen2.5-coder-7b-pilot with the
  main-experiment options (research/main-models.json). gpt-6-luna is excluded because in the main
  experiment none of its 240 initial solutions fell in S*; this targeting is decided before v2 data.
- Volume: 24 tasks × 3 configurations × 15 new initial solutions = 1,080 roots. Every root gets
  three one-shot repair branches B, C, P in randomized order (schedule seed 28092026); 4,320 generations.
- Branch prompts: B and C are produced by the unchanged main-experiment function repair_prompt.
  P is identical to C except that the "behavioral" object is replaced by
  {"status": "not_reported", "accepted": null, "counts": null, "output": FILLER, "output_truncated": false},
  where FILLER repeats the neutral sentence "No additional diagnostic information is provided in this block. "
  and is cut so that the serialized feedback JSON of P has exactly the same number of characters as that of C.
- Evaluation: the same four suites (D.base, D.behavior, H.base, H.strict), sandbox limits and
  acceptance rule as in the main experiment. H is never shown to models.
- Cost guard: $15 estimated API spend. No re-generation of returned answers; a transport-only retry is
  allowed only when no answer was obtained (same rule as the main amendment).

## Endpoint and analysis (fixed in analyze_v2.py before data)

- Unit: root (one initial solution and its three repairs). Outcome: S = H.strict acceptance of a repair.
- S* is defined from A's diagnostic evaluations: D.base accepted and D.behavior not accepted
  (runtime errors in D.behavior count as not accepted, as in the main analysis).
- Estimates: d1 = mean over S* roots of (S_C − S_B); d2 = mean over S* roots of (S_C − S_P); equal root weights.
- Inference: whole-cluster bootstrap over the template clusters present in S* (roots of a resampled cluster
  kept together), 20,000 replicates, seed 28092027, percentile 95% two-sided intervals.
  Family of two confirmatory one-sided tests, Bonferroni: Hk is confirmed if the lower end of its
  95% two-sided interval (one-sided α = 0.025 each) is above 0.
- Minimum: if S* contains fewer than 40 roots, H1 and H2 are reported descriptively only.
- Secondary, descriptive (95% whole-cluster intervals, no decisions): P − B in S*; C − B, C − P, P − B in all
  roots with equal task–configuration weights; results by configuration; regressions (A accepted by H.strict,
  repair not) and repairs by branch; discordant-pair counts; feedback truncation.
- All results are reported irrespective of outcome. No additional repeats, models or tasks after seeing data.

## Known limitations fixed in advance

Provider models behind the same identifiers may have changed since 24.09.2026. The P filler controls the
character length and the presence of a behavioral object, but not every stylistic property of real test output.
Excluding GPT restricts the confirmatory statements to the three included configurations.
