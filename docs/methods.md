# Methods

This summary gives the definitions needed to use the data. The paper gives the full rationale.

## Corpus and test partitions

The corpus contains 24 Ruby on Rails tasks, four in each of six requirement families: query growth,
freshness, atomicity, repeated calls, literal input and access scope. Tasks that share a solution
mechanism form a template cluster; the 24 tasks form 16 clusters. Six earlier development tasks were
used only for pipeline development and are excluded.

Each task has a diagnostic partition D and a held-out partition H. D.base checks basic functional
behavior and D.behavior additional requirements of the same contract; H.base and H.strict evaluate the
final solution on other fixtures and boundary conditions. H was never shown to the models. The checks
were validated on 107 control programs (48 intended-correct and 59 intentionally defective).

## Paired repair branches

For every task and configuration, independent initial solutions A were generated. Each A was repaired
once in every branch, from the same prompt and the same initial solution:

| Branch | Feedback given to the model |
| --- | --- |
| B | D.base result |
| C | D.base result and D.behavior result |
| P | D.base result and neutral text of the same character length as C's behavioral block |
| Q | D.base result and a behavioral block that only states that a check failed, of C's length |

The outcome is acceptance by H.strict. A repair is a branch accepted when A was not; a regression is a
branch rejected when A was accepted. The diagnostic state S* holds roots with D.base passed and
D.behavior failed by A.

## Main experiment

Four configurations (GPT-6 Luna, Claude Sonnet 5, Gemini 3.5 Flash-Lite, Qwen2.5-Coder 7B run locally)
× 24 tasks × 10 initial solutions = 960 roots, 2,880 generations and 11,520 evaluations. GPT-6 Luna
and Claude Sonnet 5 used low reasoning effort and a 4,096-token limit; Gemini and the local model used
temperature 0 and the same limit. The primary contrast C − B uses equal weights per task and
configuration and a conditional bootstrap that resamples template clusters within the six families
and repeats within tasks (10,000 replicates, seed 24092028). Sensitivity analyses: whole-cluster and
task bootstraps, a CR2 cluster-robust interval with Satterthwaite degrees of freedom, family contrasts
and leave-one-family-out estimates. The scenario replay of 104 S* roots is post hoc.

## Confirmatory experiment

No GPT-6 Luna solution fell in S*, so the confirmatory experiment used the other three configurations
with the main-experiment options and 15 new initial solutions per task and configuration: 1,080 roots
and 4,320 generations. The protocol, runner and analysis were hashed before the first request
(`frozen/confirmatory-v2`). Hypotheses, if S* held at least 40 roots:

- H1: in S*, C is accepted more often than B;
- H2: in S*, C is accepted more often than P.

Each estimate is the mean paired difference over S* roots with equal weights; intervals come from a
whole-cluster bootstrap over the clusters present in S* (20,000 replicates, seed 28092027). With a
Bonferroni correction for the two one-sided tests, a hypothesis is confirmed if the lower end of its
95% interval exceeds zero. Descriptive analyses over all roots use equal weights per task and
configuration; their bootstrap keeps each drawn cluster separate even when a cluster is drawn more
than once (`frozen/confirmatory-v2/ERRATA.md`).

One HTTP 503 response without a generated answer led to a transport-only amendment (retries with
backoff and resumption); prompts, branches, models, evaluation and analysis were unchanged.

## Signal-only addendum

After the confirmatory results, branch Q was added for the same 150 S* roots, reusing their initial
solutions and diagnostic results. The addendum protocol and runner were hashed before any Q request
(`frozen/signal-addendum`). H3: in S*, C is accepted more often than Q; same bootstrap with 20,000
replicates and seed 28092028. Q repeats the signal sentence and is cut to C's serialized length.

## Costs

Token counts and cost estimates come from the saved responses; the local model is not priced. These
summaries and the unchanged-code counts are post hoc and descriptive.
