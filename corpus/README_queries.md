# Query and freshness scenario families (development)

These eight scenarios were constructed before any new model calls. They are not externally validated, independent random samples of Rails programming, or performance results.

## Query family: m01–m04

- m01 polymorphic resolution batches heterogeneous models, missing/nil targets, and a new target class in H.
- m02 groupwise latest selects by two-level order, retains empty sensors, and adds timestamp ties and a lower-tick reading inserted last in H.
- m03 many-to-many set intersection ignores duplicate memberships/requests, handles empty/unknown requests, and adds untagged projects plus mixed known/unknown requests in H.
- m04 conditional aggregation preserves clients with no qualifying invoices and handles negative and NULL amounts; H adds void-only parents, NULL values, negative-only totals and NULL-only totals.

The query tests compare counts at three sizes of a repeated association shape. They impose no arbitrary fixed cap. They accept batch loading and grouped/set SQL alternatives. They do not measure memory use, indexed query complexity, production latency, PostgreSQL behavior, or every possible output-correct implementation. Constant-query implementations can still be inefficient. References and alternatives deliberately use different strategies; m04 alternatives share preload/grouping techniques seen elsewhere, so tasks are clustered rather than statistically independent.

`m01_polymorphic_feed/controls/synthetic_two_types.rb` is an intentionally limited synthetic implementation: it passes all diagnostic checks but lacks Document resolution exposed by H. This demonstrates H sensitivity and is not observed model behavior. Other query controls are per-parent lazy queries or preloading followed by a fresh per-parent relation query. Both pass functional base and fail query-growth assertions.

## Freshness family: m05–m08

- m05 reuses a parent with an already loaded association across insertion, deletion, transfer and rename.
- m06 reuses a lookup service across absence, insertion, update, deletion/recreation and interleaved keys.
- m07 reuses an aggregate reader across amount/status changes and deletion, preserving wallet isolation.
- m08 reuses a stale model argument across persisted scalar changes, nullable discounts and deletion.

Freshness has no query-count threshold. Database state snapshots around each invocation verify no persistent writes. The controls represent loaded association/relation caches, memoized values, stale input attributes and cached views. `m05_roster_membership/controls/synthetic_cardinality_cache.rb` is deliberately synthetic: a count-keyed cache tracks D insertions/deletions but misses an H rename at unchanged cardinality. This is not observed model behavior.

Each task has its own explicit English contract, separate diagnostic/holdout fixture switches, ordinary happy-path base, stronger behavioral checks, reference, independent alternative, and two broken controls (plus the two synthetic controls across families). Each test sets up its own data; autoincrement ids are not assumed fixed. Manifest expectations must be confirmed by the root Docker audit before freezing.

Limitations: H structures and mutations are authored using these references and controls. H is implementation-hidden feedback, not an untouched external sample. The corpus is developmental; shared ActiveRecord patterns and small in-memory SQLite fixtures reduce independence. Read-only checks compare durable rows; they do not prove absence of transient writes rolled back internally or of model/schema monkey-patching. No API calls or model answers were used to select these cases.

## Cross-review coverage strengthening

Three additional realistic fault controls were added before model generation: m02 `max_id_instead_of_tick.rb` mistakes insertion order for measurement time; m03 `drop_unknown_tags.rb` silently drops unknown members of a mixed tag request; m04 `clamp_negative_total.rb` clips legitimate negative totals. Each is expected to pass diagnostic/base checks and fail holdout behavior/strict checks. These authored controls are not observed model behavior. H also covers a NULL-only posted client separately from a mixed numeric/NULL total. Existing controls remain unchanged. Total: 37 controls (8 references, 8 alternatives, 19 realistic faults, 2 explicitly synthetic controls).
