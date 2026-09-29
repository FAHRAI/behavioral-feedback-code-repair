# Supplementary Analyses and Execution Notes

## Appendix A Scenario replay and diagnostic linkage

### A1 Selection and measurement

The post hoc follow-up retains all 104 roots for which the initial program A
passed D.base and failed D.behavior. Selection uses only diagnostic outcomes of A, measured before B/C branching;
the stratum was selected for analysis after the primary results were known. It covers nine tasks and all 312 saved A/B/C programs.
The 19 roots with discordant original H.strict outcomes form a separate
outcome-selected case series: 16 C-only and three B-only successes. They are not
a second sample for estimating the primary treatment contrast.

The executable map, fixed controls, exposure annotations and analysis were
committed before the new B/C replay at
`da8248bf4c893bc1584e3ee1b4c2fefc18751752`. The map was authored from corpus
materials, but the principal investigator had seen aggregate outcomes; complete
author blinding is not claimed. The original tasks, primary endpoint and primary
analysis were not changed.

Each probe replays the original prefix within a test method in a fresh isolated
container and stops after the target checkpoint passes. A failure in a preceding
checkpoint leaves the target not reached. An assertion failure, runtime failure
or timeout after target entry counts as failure; pre-entry load or setup failure
leaves it not reached. Infrastructure failures invalidate a record. The three
outcomes are retained in all B/C comparisons, with reasons stored separately.

All 312 full H.strict runs reproduced the archived outcomes and assertion
counts. The 4,185 individual A/B/C probes produced 1,395 paired H observations;
none disagreed with its corresponding full-suite checkpoint outcome. These
checks establish agreement for the saved programs, not completeness of the
oracles or independent information in every checkpoint.

### A2 Finite control validation

A checkpoint enters the group with a validated negative outcome only if the
reference passes and an intended defective program reaches and fails an
assertion in that checkpoint. Prefix failure, runtime error and timeout do not
supply a negative assertion witness. The budget comprised existing corpus
controls plus one additional semantic defect each for m10, m11 and m12: an
incorrect empty no-op, removal of pre-existing deliveries, and omission of
repeated-id changes. No further mutants were added in response to model outcomes.

All 162 reference D/H probes passed. Thirty checkpoints had a negative witness:
13 in D and 17 in H. The remaining 89 H checkpoints are retained separately.
Eighty-eight full control-suite comparisons preserved outcomes and assertion
counts with and without tracing; ten paired emergency-path controls covered
syntax/load/runtime failures, missing expected exceptions and timeouts. These
controls validate selected observable outcomes, not every assertion or defect.

**Table A1. Coverage of H checkpoint controls**

| Task | Roots | H checkpoints | Negative outcome validated |
| --- | ---: | ---: | ---: |
| m03 Tag intersection | 5 | 17 | 2 |
| m10 Collection replacement | 4 | 6 | 2 |
| m11 Publication callbacks | 1 | 7 | 2 |
| m12 Nested savepoint | 16 | 5 | 2 |
| m13 Credit deduplication | 10 | 8 | 1 |
| m15 Idempotency conflict | 10 | 8 | 2 |
| m17 Literal prefix | 23 | 18 | 2 |
| m18 Literal suffix | 25 | 17 | 2 |
| m19 Exact token | 10 | 20 | 2 |
| Total | 104 | 106 | 17 |

### A3 Complete outcome matrices

Each cell counts root–checkpoint pairs, not independent programs or repaired
defects. Rows are B outcomes and columns are C outcomes. The main manuscript's
Table 3 reports directional differences from Table A2, retaining the 104-root
A-selected cohort as the basis of the scenario summary.

**Table A2. All 104 roots and 1,395 pairs**

| B outcome / C outcome | Pass | Fail | Not reached |
| --- | ---: | ---: | ---: |
| Pass | 347 | 6 | 23 |
| Fail | 18 | 84 | 1 |
| Not reached | 151 | 1 | 764 |

**Table A3. Outcome-selected 19-root case series and 249 pairs**

| B outcome / C outcome | Pass | Fail | Not reached |
| --- | ---: | ---: | ---: |
| Pass | 58 | 3 | 21 |
| Fail | 17 | 0 | 0 |
| Not reached | 150 | 0 | 0 |

Almost all C-favoring differences in the full group occur in these 19 roots:
17 of 18 fail/pass observations and 150 of 151 not-reached/pass observations.
That concentration is expected when cases are selected by their known strict
outcomes. The 150 newly reached successes cannot be counted as 150 independently
demonstrated repairs: correcting an earlier failure permits subsequent checks.

### A4 Validation and exposure categories

For each root, exposure annotations use the actual diagnostic output shown in
its saved C prompt, not membership in D alone. A shown-failed label requires
an identifiable corresponding failure message; an aggregate passing summary is
insufficient for shown-passed. Shared checkpoints lacking identifiable evidence
remain unresolved. Mixed checkpoints combine known and added conditions or
histories. H-only means no assigned D counterpart at the map's granularity.

All 208 A diagnostic replays reproduced archived outcomes, assertion counts and
normalized failure sections. Visible failure evidence was linked for all 104
roots, but corresponding H checkpoints were mixed under the map. There were no
pure shown-failed or individually identifiable shown-passed labels. This does
not mean that C received no failures or that no D checkpoint passed.

**Table A4. Behavioral checkpoints with validated negative outcomes in the 19 cases**

| Category | Pairs | Pass/pass | Fail/pass | Not reached/pass | Pass/fail | Pass/not reached |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| H-only | 13 | 6 | 6 | 0 | 0 | 1 |
| Mixed | 18 | 2 | 10 | 4 | 1 | 1 |

B is listed first in each outcome label; the other four cells are zero in both
rows. Three additional functional pairs with validated negative outcomes are
pass/pass. The 16 direct behavioral fail/pass observations occur once in each
C-only root. One further direct difference in Table A3 belongs to a functional
checkpoint without a negative witness.

Among H-only checkpoints without negative validation in the case series,
56 pairs comprise eight pass/pass, two pass/fail, four pass/not reached and
42 not reached/pass observations. None is fail/pass. Those 42 downstream
successes cannot be added to the six direct validated H-only differences.

### A5 The six direct H-only differences

Three Claude repeats of m17 passed the uppercase prefix example ROOT after B
failed it. D already tested case sensitivity with Alpha in the presence of
alpha and alphabet. These are new examples of an already tested rule.

Three Gemini repeats of m12 passed rollback within a caller transaction after B
failed it. D lacked this external-transaction context. This is a descriptive
example involving one task and one configuration, not three independent tasks
or evidence of a general transfer mechanism.

The literal H-only map comprises four query templates at three successive
states, giving 12 checkpoints rather than 12 independent requirements. The
m18 empty suffix is an additional boundary explicitly required by the prompt;
backslash is a new character within an already tested literal-matching rule.
For m19, TAB, FF and VT extend delimiter coverage, while exact case and terminal
token position were already tested in D. The same delimiter families occur in
a mixed checkpoint, so the map does not partition distinct semantic requirements.
These ambiguities were examined after the map was fixed and without access to
model scenario outcomes; the map was not relabeled.

Only ten of the 20 Claude literal-affix roots discussed in the main study belong
to this 104-root follow-up. The annotations here do not cover the other ten.

### A6 Cases favoring basic feedback

All three B-only cases in the 19-root series are Claude outputs whose A programs
failed H.strict. They are distinct from the initially accepted-program regressions
reported in Section 3.4.

In m10, repeat 9, C's recovery after a destroy-callback failure attempts another
deletion and raises TrackFault. B passes the strict suite. The scenario outcomes
contain one B-pass/C-fail and two B-pass/C-not-reached observations.

In m13, repeat 4, C returns applied rather than duplicate on an interleaved
repeat-credit call, whereas B passes. There is one B-pass/C-fail and three
B-pass/C-not-reached observations.

In m19, repeat 3, C includes the uppercase token Maple when matching lowercase
maple, whereas B passes. There is one B-pass/C-fail and 16 B-pass/C-not-reached
observations. Repeat numbers here are the zero-based archive identifiers.

### A7 Additional linkage count specified after the freeze

The following calculation was requested after completion of the frozen scenario
analysis and was not included in its declared analysis plan. It uses the saved
map, exposure annotations and raw diagnostic messages without new execution,
new generations, new controls or relabeling.

Among the ten mixed behavioral B-fail/C-pass observations with validated negative
outcomes in the 19-root case series, all ten have a corresponding D.behavior
failure message visible to C for that same root. The breakdown is three m13
interleaved-repeat observations, six m18 suffix observations and one m19 token
observation. Message inclusion, matching diagnostic IDs, saved C-prompt hashes
and corresponding A replay events were checked directly.

This is consistent with correction of diagnosed behavior under changed inputs
or history. It does not show which information caused the repair, isolate
feedback content from length, or establish that C merely memorized the shown
example. Mixed remains mixed. The count is an additional exploratory description,
not a new confirmatory test or a revision of the frozen sensitivity bounds.

### A8 Sensitivity and interpretation

In the two declared allocations, assigning all mixed checkpoints to shared-design
leaves six direct validated behavioral H-only fail/pass observations; assigning
all mixed to H-only yields 16, plus four not-reached/pass observations. Original
exposure evidence is retained in both calculations. These are bounds on design
attribution, not evidence that mixed checkpoints were actually shown in full.

The analysis supports a narrow example of success in an added transaction context
and a clearer accounting of reachability. It does not provide a stable numerical
estimate of transfer to untested requirements. Post hoc selection, author-defined
mapping, limited negative-control coverage, dependent checkpoints and same-author
H tests limit interpretation. None of these calculations replaces the primary
paired estimate or its uncertainty analysis.

## Appendix B Sensitivity calculations and deletions

### B1 Estimand and uncertainty calculations

All full-sample estimates give each task–configuration pair weight 1/96 and each
of its ten repeats weight 1/10. The point estimate is 16/960, or +1.67 percentage
points. Alternative intervals change the uncertainty calculation, not these
observed weights. The whole-cluster bootstrap samples 16 template clusters with
replacement and normalizes by the number of selected tasks; it does not average
unequal cluster means with equal weights. The task bootstrap samples 24 tasks
with replacement. Each retains all configurations and repeats in a selected
unit. Both use 50,000 replicates, with seeds 250920261 and 250920265 respectively.

For CR2, let y_t be a task's mean paired difference, θ their unweighted mean,
N = 24, and n_g the number of tasks in template cluster g. Define
R_g = Σ(t in g)(y_t − θ). The intercept variance is
V = N⁻² Σ_g [R_g² / (1 − n_g/N)]. Under working covariance I_24, the
Satterthwaite degrees of freedom are the reciprocal of
Σ_g[n_g²/(N − n_g)²] − (2/N)Σ_g[n_g³/(N − n_g)²]
+ N⁻²{Σ_g[n_g²/(N − n_g)]}².
This yields SE = 0.01224753 and degrees of freedom 10.139365. The interval uses
θ ± t(0.975, df)√V; replacing df with 15 gives the separate S4b calculation.
The implementation uses unweighted intercept-only OLS without absorption of
fixed effects. Reference [9] includes its 2023 corrigendum; no general weighted
fixed-effects shortcut is used here. An independent matrix calculation reproduced
the archived variance and degrees of freedom. These checks concern arithmetic
under the stated working model, not guaranteed inferential coverage.

### B2 Composition sensitivity

Deletion estimates renormalize weights over the retained tasks or configurations.
They deliberately change the evaluated set and are not confidence limits for the
unchanged full sample. All deletions below are retained, irrespective of direction.

**Table B1. Leaving out each template cluster**

| Removed tasks | Cluster | Remaining tasks | C−B, pp |
| --- | --- | ---: | ---: |
| m01 | Polymorphic query | 23 | +2.17 |
| m02 | Groupwise maximum | 23 | +1.74 |
| m03 | Tag intersection | 23 | +1.74 |
| m04 | Conditional aggregation | 23 | +1.74 |
| m05 | Association freshness | 23 | +1.74 |
| m06 | Lookup freshness | 23 | +1.74 |
| m07 | Aggregate freshness | 23 | +1.74 |
| m08 | Record freshness | 23 | +1.74 |
| m09, m10, m11, m12 | Transaction boundary | 20 | +1.75 |
| m13, m14, m15, m16 | Persistent repeated state | 20 | +1.75 |
| m17, m18 | Literal affix | 22 | +0.57 |
| m19 | Literal tokenization | 23 | +1.63 |
| m20 | Literal set membership | 23 | +1.74 |
| m21 | Boolean access scope | 23 | +1.74 |
| m22, m24 | Parent access join | 22 | +1.36 |
| m23 | Batch access totality | 23 | +1.74 |

**Table B2. Leaving out each model configuration**

| Removed configuration | Remaining roots | B accepted | C accepted | C−B, pp |
| --- | ---: | ---: | ---: | ---: |
| Claude Sonnet 5 | 720 | 507 | 511 | +0.56 |
| Gemini 3.5 Flash-Lite | 720 | 536 | 548 | +1.67 |
| Qwen2.5-Coder 7B | 720 | 637 | 653 | +2.22 |
| GPT-6 Luna | 720 | 480 | 496 | +2.22 |

The descriptive delete-cluster jackknife SE is 1.23 percentage points. Unequal
cluster sizes and changing corpus composition are reasons not to interpret
it as an additional unchanged-sample interval. References [8–9] are listed
in the main manuscript.

### B3 Interval endpoints

**Table B3. Primary and alternative 95% intervals**

| Analysis | 95% interval for C−B, pp |
| --- | --- |
| Primary: clusters within fixed families and resampled paired repeats | [−0.42, +3.23] |
| S1: unstratified resampling of 16 whole template clusters | [−0.59, +4.23] |
| S4: CR2 with Satterthwaite reference distribution | [−1.06, +4.39] |
| S4b: the same CR2 variance with t(15) | [−0.94, +4.28] |
| S5: unstratified resampling of 24 whole tasks | [−0.21, +3.75] |

Archive labels S1, S4, S4b and S5 identify the interval calculations. S2 and S3
identify cluster and configuration deletions, respectively (Tables B1 and B2).

## Appendix C Transport recovery during collection

A Gemini HTTP 503 interrupted collection after 1,052 answers had been returned.
Their saved artifacts were checked before collection resumed. The amendment
allowed at most three requests for a branch only after an explicit HTTP 503
without an answer; other failures stopped collection. Failed requests were
retained separately and possible charges reserved within the original spending
cap. One failed request was retained, and the affected branch was completed
without regenerating any returned program. This transport amendment was adopted
during collection and was not part of the precollection protocol.
