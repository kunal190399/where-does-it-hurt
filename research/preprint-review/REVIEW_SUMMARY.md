# Supervisor review summary

## Proposed paper
**Working title:** *Strict Intersection and Spatial-Frequency Consensus for Annotated Regions: A Synthetic Benchmark and Geometry Audit*

## Main contribution being tested
A reproducible, simulation-based comparison of strict shared-region intersection and thresholded spatial-frequency consensus, paired with direct tests of selected geometry functions from the original implementation.

This is deliberately not framed as inventing pain-frequency maps. Prior work has described pain-frequency mapping. The proposed contribution is a controlled comparison under explicit synthetic assumptions and a focused software audit.

## Experiments
1. **Point/hull benchmark:** 360 paired cases; 4 coordinate-noise levels × 3 annotation counts × 30 repetitions. Synthetic elliptical regions are annotated with noisy points, converted to convex hulls, rasterised to a common grid, and compared with ground truth.
2. **Mask-level extension:** 1,080 paired cases across ellipses, irregular polygons, and disconnected regions; 4 perturbation levels × 3 annotation counts × 30 repetitions per shape family. This experiment tests aggregation behaviour, not the original polygon clipping implementation.
3. **Original geometry tests:** selected Graham-scan, line-intersection, and Sutherland–Hodgman functions are tested independently of the original plotting/data-loading pipeline.

## Key exploratory findings
- Point/hull benchmark: mean IoU 0.787 for threshold-0.5 consensus vs 0.733 for strict intersection; paired mean difference 0.055 (bootstrap 95% interval 0.043–0.067).
- Point/hull precision/recall: consensus precision 0.798 and recall 0.978; strict intersection precision 0.965 and recall 0.754.
- At noise SD 0.030 and five annotations in the mask-level extension: IoU 0.806 vs 0.508 for ellipses, 0.715 vs 0.320 for irregular regions, and 0.649 vs 0.180 for disconnected regions (consensus vs strict intersection).
- The tested original clipping implementation raises IndexError for disjoint polygons and fails for the tested reversed clip-polygon winding. The tests establish these specific failures, not exhaustive correctness properties.

## Questions for supervisor
1. Is the proposed scope a meaningful and sufficiently distinct contribution beyond the dissertation?
2. Are there any university IP, code ownership, or publication restrictions?
3. May the dummy data created for the dissertation be described or reused in a public preprint? The current synthetic experiments do not require that dataset.
4. Did the supervisor make intellectual contributions to the method, interpretation, or manuscript that should be reflected in the author list?
5. Are the proposed limitations and claims appropriately conservative?

## Release caveats
Synthetic results do not establish clinical validity. The threshold is not universally optimal. The mask-level extension is not a direct test of the original hull/clipping pipeline. Original coordinate and demographic files are excluded. This package should remain under review until authorship, code reuse, and institutional permissions are resolved.
