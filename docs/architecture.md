# Code structure

`primary`, `sensitivity`, `outcomes`, `scenarios` and `confirmatory` contain the calculations. They take
Python data structures and have no provider or container dependencies; `confirmatory` can also rebuild
its per-root table from the extracted evidence archive. The numerical algorithms of the main experiment
were extracted from the original study scripts; only imports and file-loading boundaries were adapted,
and input checks raise `ValueError` so they also run under `python -O`.

`data` validates identities, complete pairing, diagnostic annotations and scenario membership.
`integrity` verifies checksums and validates archive paths before extraction. `cli` connects those
boundaries to the calculations and writes new outputs. `sandbox` is imported only by the replay command.
The package contains no model-generation client or credential loader; the generation code used for the
confirmatory experiment is kept, as frozen, in `frozen/`.

The `src` layout keeps checkout files off the package import path. Tests run against the installed
package.

Keep inputs unchanged. A corrected dataset requires a new version, manifest and an explanation of its
effect on reported results. Expected outputs are comparison targets, not substitutes for recomputation.
Container execution is tested separately from numerical reproduction.
