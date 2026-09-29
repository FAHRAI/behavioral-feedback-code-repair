# Literal input and access-scope scenarios (m17–m24)

Eight designed scenarios; not model results, not yet a statistical population.
These controls intentionally isolate plausible semantic errors without exceptions.
Each strict suite includes ordinary tests. SQL and Ruby-filter reference alternatives
are both valid because these tasks impose no query budget; no claim of scalability.

Literal affix tasks share a template cluster; token/set membership have separate
clusters. Parent join and nested lookup share parent-authorization structure.
Report results by cluster as well as by task; do not treat these as eight entirely
independent mechanisms. Ordinary m21 reconstructs a benign single-tenant fixture;
its diagnostic and holdout behavior fixtures contain the cross-tenant contrasts.

H adds state changes and combinations rather than only renaming fixture strings.
H for m18 omits no contract information: empty suffix matches all was explicit in
the prompt but absent from D tests. m23 similarly introduces the explicit empty
batch boundary. Their diagnostic_overfit controls are SYNTHETIC sensitivity checks,
not observed model failures. Positive results do not prove robust generalization.

No concurrency, timing or efficiency claims are tested here. Matching is explicitly case-sensitive ASCII; affix tasks m17–m18 exclude NUL
(U+0000) while allowing other ASCII whitespace. The token and term-set tasks
m19–m20 do not add that exclusion. There is no implicit Unicode normalization
contract. Returned records in m23–m24 must be persisted and expose the current
listed attributes, checked against the database snapshot.
