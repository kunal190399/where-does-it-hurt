# Where Does It Hurt? — preprint research review package

**Status: working draft for supervisor review only. Not ready for public release or journal submission.**

This folder contains an exploratory synthetic benchmark and a software audit developed from the original dissertation project. It is intended to help the author and supervisor review the research direction, methods, results, and release conditions.

## Main question
How does thresholded spatial-frequency consensus compare with strict intersection when summarising multiple noisy spatial annotations against a known synthetic ground truth?

## Current evidence
- Point/hull benchmark: 360 paired synthetic cases.
- Mask-level extension: 1,080 paired cases across ellipse, irregular polygon, and disconnected-region families.
- Primary point/hull result: mean IoU 0.787 for consensus threshold 0.5 versus 0.733 for strict intersection; paired difference 0.055, bootstrap 95% interval 0.043–0.067.
- The mask-level experiment found threshold-0.5 consensus IoU of 0.806 vs 0.508 for ellipses, 0.715 vs 0.320 for irregular regions, and 0.649 vs 0.180 for disconnected regions at noise SD 0.030 and five annotations.
- Direct tests identified edge cases in the original polygon clipping implementation, including an IndexError for disjoint polygons and a failure for the tested reversed clip-polygon winding.

These are exploratory results conditional on the simulation assumptions. They are not evidence of clinical validity. The mask-level experiment is not a direct test of the original polygon clipping pipeline.

## Suggested review order
1. `PREPRINT_DRAFT.md` — scientific claims, methods, results, limitations.
2. `RESULTS_SUMMARY.md` — numerical findings.
3. `ORIGINAL_CODE_AUDIT.md` and `ORIGINAL_GEOMETRY_TEST_REPORT.md` — software findings.
4. `LITERATURE_REVIEW.md` — related work and contribution positioning.
5. `PROVENANCE.md` and `AUTHORSHIP_AND_PERMISSION_CHECKLIST.md` — permissions and release gates.

## Reproducibility
The research package uses synthetic annotations only. The professor-provided dummy dataset and original coordinate/demographic files are not included. See the source scripts and tests for the simulation and geometry audit.

## Before any public release
- Confirm authorship and contributor roles.
- Obtain permission to reuse professor-generated dummy data if it will be included or described in more detail.
- Confirm university/IP and original-code reuse conditions.
- Verify references and all reported values against saved outputs.
- Do not include original coordinate or demographic files unless their status and permission are explicitly resolved.
- Do not describe this as clinically validated.
