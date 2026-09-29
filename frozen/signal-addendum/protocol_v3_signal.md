# Addendum v3: failure signal versus failure details (written before any Q generation)

Motivation: independent review noted that, in S*, branches B and P receive no behavioral failure signal while C reports
that a behavioral check failed together with its output. The v2 design cannot separate the value of the failure signal
from the value of the failure details.

## Design
- Roots: the 150 S* roots of results/confirmatory-v2-20260928 (A passed D.base and failed D.behavior), unchanged.
  Their saved initial solutions and diagnostic evaluations are reused; nothing already generated is regenerated.
- New branch Q (one-shot repair, same model and options as the root): identical to C except that the behavioral object is
  {"status": <C's real status>, "accepted": <C's real accepted (false)>, "counts": null,
   "output": FILLER_Q, "output_truncated": false}, where FILLER_Q repeats
  "A behavioral check failed; no further details are provided. " and is cut so that the serialized feedback of Q has
  exactly the same number of characters as that of C. Q thus carries the failure signal but not the failure details.
- Evaluation: same four suites and acceptance rule; outcome S = H.strict acceptance.

## Hypothesis and analysis (fixed before data)
- H3 (confirmatory): in S*, C is accepted more often than Q (failure details add value beyond the failure signal).
- Estimate: mean over the 150 roots of (S_C − S_Q), equal root weights; whole-cluster bootstrap over the S* template clusters,
  20,000 replicates, seed 28092028, percentile 95% two-sided interval. H3 is confirmed if the lower end exceeds 0
  (one-sided α = 0.025; H3 is a new single-hypothesis family).
- Descriptive (95% intervals, no decisions): Q − B, Q − P; results by configuration; unchanged-code counts for Q.
- All results reported irrespective of outcome. No other branches, roots or repeats.

## Limitations fixed in advance
Q is generated on 28.09.2026, some hours after B/C/P; provider models may change within that time. The counts field is
omitted in Q, so Q conveys that a check failed but not how many assertions failed.
