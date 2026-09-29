# Reproduction scope

The default analysis uses saved outcomes. It does not contact a model provider,
regenerate solutions, or imply that current API models will produce the same
answers as on 24 and 28 September 2026. Numerical comparison uses the original
random seeds and the recorded task/configuration order; floating-point values are
compared with a relative tolerance of 1e-12 because platform math libraries can
differ in the last digits.

The original evaluation image is
`sha256:d303858f9658f209b24cc22393de9f4bac3c0b1e8114cf07b075a845bf0a9a03`.
It contains Ruby 3.3.11, ActiveRecord/ActionPack 7.2.3.1 and sqlite3 gem 2.9.5.
This is a local Docker image ID, not a published registry digest. The publication
recipe in `runtime/` pins the observed base image digest and the complete installed
gem version/platform inventory. It targets linux/arm64. The original Dockerfile,
which used version ranges, remains in the main evidence archive.

A rebuild has a different image ID. Pass its resolved ID with `--image`; do not
replace the original ID in the collection plan. Build-time operating-system
packages can still change, so the recipe does not promise a byte-identical image.
Acceptance and assertion-count replay checks measure compatibility for the saved
programs actually rerun. Only the build recipe is distributed, not a prebuilt image.

The replay command executes an archived H.strict test file and solution after
checking their exported hashes. It adds explicit capability restrictions to the
container wrapper. The wrapper was rewritten for publication and is not the
original launcher. Scenario aggregation is reproduced directly
from all saved checkpoint pairs. The scenario definitions, executor and all probe
records are retained in the main evidence archive, but the executor's
repository-specific freeze guard is not portable to a new repository. Full
scenario re-execution is not claimed by the current CLI.

Export records in `provenance/` bind each archived file to its original and
exported SHA-256 values. Protocols fixed before data collection are local
commitments, not public preregistrations. Frozen files were not edited.

In the main experiment one Gemini request returned HTTP 503 without a generated
answer; a transport-only amendment allowed retrying that request. The archive
contains all 2,880 answers and 11,520 suite evaluations; no returned solution was
regenerated. The confirmatory experiment had the analogous amendment recorded in
`frozen/confirmatory-v2/amendment-1`; failed requests are kept in its archive.

Paths in archived plans and reports refer to the original workspace layout.
Resolve them relative to the extracted evidence directory. Two metadata files
had personal home-directory prefixes replaced by `$HOME`; the export records
identify those files. Original integrity claims concern original bytes;
distribution checksums concern the exported bytes.
