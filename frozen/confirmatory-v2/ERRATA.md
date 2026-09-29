# Errata to the frozen confirmatory v2 materials (the frozen files are not modified)

1. protocol.md, "Design", Implementation: component hashes are recorded in results/confirmatory-v2-20260928/plan.json
   ("frozen_implementation_sha256"), not in freeze.json; freeze.json holds the hashes of protocol.md, runner_v2.py and analyze_v2.py.
2. analyze_v2.py, equal_cell: cluster multiplicity was lost for the equal-cell secondary intervals over all roots.
   Corrected in analyze_v2_correction1.py (output analysis_v2_correction1.json). H1/H2 and S* statistics are unaffected.
3. runner_v2.py progress counter: after the resume, the running cost estimate restarted at zero and omitted the first eight
   generations ($0.0106); the total recomputed from sample.json files is $6.2747.
