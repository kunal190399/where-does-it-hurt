# Results summary

These are exploratory results from synthetic data only. They are conditional on the chosen shapes, noise model, grid resolution, and threshold definitions.

## Primary point/hull benchmark
- Design: 4 coordinate-noise SDs (0.005, 0.015, 0.030, 0.050) × 3 annotation counts (3, 5, 8) × 30 replicates = 360 paired cases.
- Mean IoU: frequency consensus at threshold 0.5 = 0.787; strict intersection = 0.733.
- Paired mean IoU difference: 0.055; percentile-bootstrap 95% interval 0.043–0.067.
- Mean precision: consensus 0.798; strict intersection 0.965.
- Mean recall: consensus 0.978; strict intersection 0.754.

### By annotation count
| Annotations | Consensus mean IoU | Strict-intersection mean IoU |
|---:|---:|---:|
| 3 | 0.775 | 0.776 |
| 5 | 0.804 | 0.757 |
| 8 | 0.783 | 0.666 |

### By coordinate-noise SD
| Noise SD | Consensus mean IoU | Strict-intersection mean IoU |
|---:|---:|---:|
| 0.005 | 0.955 | 0.928 |
| 0.015 | 0.863 | 0.816 |
| 0.030 | 0.739 | 0.691 |
| 0.050 | 0.593 | 0.496 |

## Extended mask-level benchmark
- Design: 3 shape families (ellipse, irregular polygon, disconnected region) × 4 perturbation levels × 3 annotation counts × 30 replicates = 1,080 paired cases.
- At noise SD 0.030 and five annotations:
| Shape | Consensus IoU (threshold 0.5) | Strict-intersection IoU |
|---|---:|---:|
| Ellipse | 0.806 | 0.508 |
| Irregular polygon | 0.715 | 0.320 |
| Disconnected region | 0.649 | 0.180 |

### Threshold sensitivity, averaged across noise levels and annotation counts
| Shape | Threshold 0.3 | Threshold 0.4 | Threshold 0.5 | Threshold 0.6 | Threshold 0.7 |
|---|---:|---:|---:|---:|---:|
| Ellipse | 0.790 | 0.825 | 0.833 | 0.820 | 0.725 |
| Irregular polygon | 0.737 | 0.763 | 0.766 | 0.754 | 0.634 |
| Disconnected region | 0.689 | 0.708 | 0.710 | 0.689 | 0.539 |

Threshold 0.5 had the highest mean IoU among tested thresholds for these shape families, although 0.4 was close for disconnected regions. This does not establish a universal optimum.

## Interpretation
Consensus retained more of the simulated ground-truth region, while strict intersection was more conservative. Results do not establish performance on real annotations or clinical usefulness. The point/hull and mask-level experiments use different perturbation mechanisms and should not be treated as a controlled comparison of shape complexity alone.
