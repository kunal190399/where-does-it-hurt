# Strict Intersection and Spatial-Frequency Consensus for Annotated Regions: A Synthetic Benchmark and Geometry Audit

**Status:** Working preprint draft for supervisor review; not submission-ready.  
**Data:** Synthetic annotations only for the new experiments.  
**Author list:** To be confirmed with the supervisor and any contributors.  
**Version:** 0.3 — expanded synthetic benchmark and selected geometry tests.

## Abstract

**Background:** Digital pain maps need computational rules for summarising multiple spatial annotations. Strict intersection and thresholded spatial-frequency consensus retain different portions of annotated regions. Pain-frequency mapping has prior literature; this work does not claim to invent frequency maps or consensus mapping.

**Objective:** Compare strict intersection with thresholded spatial-frequency consensus in controlled synthetic settings and test selected geometry functions from the original implementation.

**Methods:** The point/hull experiment generated 360 cases from elliptical ground-truth regions with 3, 5, or 8 noisy point annotations. Convex hulls were rasterised and compared using strict intersection and frequency thresholds from 0.3 to 0.7. A separate mask-level extension generated 1,080 cases across elliptical, irregular, and disconnected regions. Direct tests exercised the original Graham-scan, line-intersection, and Sutherland–Hodgman functions without running the original UI/data pipeline.

**Results:** In the point/hull experiment, threshold-0.5 consensus had mean intersection over union (IoU) 0.787 versus 0.733 for strict intersection; paired mean difference 0.055 (percentile-bootstrap 95% interval 0.043–0.067). Consensus mean recall was 0.978 and precision 0.798; strict-intersection recall was 0.754 and precision 0.965. At noise SD 0.030 and five annotations in the mask-level extension, mean IoU for consensus versus strict intersection was 0.806 versus 0.508 for ellipses, 0.715 versus 0.320 for irregular regions, and 0.649 versus 0.180 for disconnected regions. Direct tests found an IndexError for disjoint polygons and failure for the tested reversed clip-polygon winding.

**Conclusion:** Results show a precision–recall trade-off under the specified synthetic assumptions, not clinical performance. The contribution is a controlled comparison and a focused software audit. The mask-level experiment is not a direct evaluation of the original convex-hull/clipping pipeline.

**Keywords:** digital pain mapping; spatial consensus; strict intersection; synthetic benchmark; polygon clipping; software testing; annotation variability.

## 1. Introduction

Digital body maps are used to collect spatial information about symptoms, including pain. A strict intersection reports only locations included by every annotation. A frequency map records how often each location is marked, and a threshold defines a consensus region. These summaries answer different questions and can differ substantially when annotations vary.

The original *Where Does It Hurt?* prototype reads point coordinates, transforms them to an anatomical image, generates convex hulls, and clips polygons to obtain their shared intersection. The supplied source archive also contains an incomplete refactored module; its existing mock tests do not exercise the actual geometry functions. This motivates a reproducible evaluation separated from the original interactive pipeline.

Pain-frequency mapping has been studied previously. Dixit and Lee (2022) described an algorithm for generating pain frequency maps. Murphy et al. (2025) reviewed 92 digital pain-manikin studies and reported methodological variation. A 2026 scoping review by Eboigbe et al. also describes heterogeneity in pain/symptom-map design and quantification. These works motivate transparent comparisons but mean that pain-frequency mapping itself should not be presented as novel.

## 2. Research question

When multiple noisy annotations approximate the same underlying region, how does thresholded spatial-frequency consensus compare with strict intersection in spatial overlap, precision, and recall?

The exploratory expectation is that strict intersection will be conservative because any annotation omitting a location removes it from the shared region. Frequency consensus may retain more of the ground truth but include some locations outside it. This is a hypothesis about the defined simulation, not a clinical claim.

## 3. Methods

### 3.1 Point/hull benchmark

A randomly positioned, scaled, and rotated ellipse in normalised two-dimensional coordinates served as synthetic ground truth. Each case contained 3, 5, or 8 annotations. Perturbations included global translation, rotation, scale variation, and local coordinate noise at standard deviations 0.005, 0.015, 0.030, and 0.050. Thirty independent cases were generated per noise-by-annotation-count condition (4 × 3 × 30 = 360 cases).

Each point set was converted to a convex hull using an adaptation of the original project's Graham-scan approach. Hulls and ground truth were rasterised on a 100 × 100 grid. Strict intersection included cells present in every annotation. Spatial-frequency consensus included cells marked by at least a chosen fraction of annotations. Threshold sensitivity was assessed at 0.3, 0.4, 0.5, 0.6, and 0.7.

The strict-intersection baseline is a raster-mask analogue of the original polygon intersection, not a direct benchmark of the original Sutherland–Hodgman implementation.

### 3.2 Mask-level shape extension

A separate experiment covered ellipses, irregular simple polygons, and disconnected unions of two elliptical components. Each shape family was evaluated at four perturbation levels, three annotation counts, and 30 replicates per condition (3 × 4 × 3 × 30 = 1,080 paired cases). Annotations were generated using translation, rotation, scaling, and signed buffer perturbation, then rasterised to the common grid. This experiment evaluates mask-level aggregation behaviour; it does not establish that the original hull/clipping pipeline can represent disconnected regions.

### 3.3 Original geometry tests

The original Graham-scan, line-intersection, and Sutherland–Hodgman definitions were isolated from the plotting and file-loading pipeline. Tests covered duplicate/interior/collinear points, crossing and parallel lines, overlapping and disjoint polygons, reversed clip-polygon winding, empty intermediate results, and boundary-touching squares. Known failures were recorded as findings rather than hidden as passing behaviour. This is a focused software audit, not exhaustive proof of geometric correctness.

### 3.4 Metrics

IoU was the primary metric: area(predicted ∩ truth) / area(predicted ∪ truth). Precision and recall were calculated from grid cells. The annotation-frequency map was also assessed with a Brier-style mean squared error against the binary synthetic ground truth. Paired mean IoU difference was estimated across cases with a percentile bootstrap 95% interval. All metrics measure agreement with simulated regions only.

## 4. Results

### 4.1 Primary comparison

Across the 360 point/hull cases, threshold-0.5 consensus achieved mean IoU 0.787 compared with 0.733 for strict intersection. The paired mean difference was 0.055 (bootstrap 95% interval 0.043–0.067). Consensus had mean precision 0.798 and recall 0.978; strict intersection had mean precision 0.965 and recall 0.754. The pattern indicates a precision–recall trade-off: strict intersection is more conservative, while consensus retains more of the synthetic ground-truth region and includes more cells outside it.

### 4.2 Annotation count and noise

With three annotations, mean IoU was 0.775 for consensus and 0.776 for strict intersection. With five annotations, values were 0.804 and 0.757; with eight, 0.783 and 0.666. Across noise SDs 0.005, 0.015, 0.030, and 0.050, consensus mean IoU was 0.955, 0.863, 0.739, and 0.593; strict-intersection mean IoU was 0.928, 0.816, 0.691, and 0.496. Both methods degraded as annotation noise increased. These patterns are specific to this simulation.

### 4.3 Irregular and disconnected regions

At noise SD 0.030 with five annotations in the mask-level experiment, mean IoU for threshold-0.5 consensus versus strict intersection was:

| Shape | Consensus IoU | Strict-intersection IoU |
|---|---:|---:|
| Ellipse | 0.806 | 0.508 |
| Irregular polygon | 0.715 | 0.320 |
| Disconnected region | 0.649 | 0.180 |

These values should not be compared with the point/hull experiment as if only shape complexity changed; the perturbation mechanisms differ.

### 4.4 Threshold sensitivity

Across all annotation counts and perturbation levels, mean IoU was highest at threshold 0.5 for ellipses (0.833), irregular regions (0.766), and disconnected regions (0.710); for disconnected regions, 0.4 was close (0.708). Lower thresholds generally retained recall, while higher thresholds tended to improve precision and reduce recall. This does not establish a universal optimal threshold because threshold performance was assessed on the same family of synthetic models used to generate the results, without independent real-data validation.

### 4.5 Geometry audit

The current automated suite contains 15 tests, including tests that deliberately assert known failure behaviour. The original clipping function handled the tested overlapping counter-clockwise squares, but raised IndexError for disjoint squares when an intermediate result was empty. Reversing the clip polygon's winding produced failure in the tested overlap case. Its strict inside predicate excludes points exactly on clipping boundaries and is orientation-dependent. These are implementation-specific findings, not an exhaustive correctness proof.

## 5. Discussion

Strict intersection and frequency consensus represent different summaries. Strict intersection prioritises the region shared by every annotation and tends toward high precision with lower recall. Thresholded consensus represents agreement frequency and can recover a broader region, but may include cells outside the simulated ground truth. A frequency fraction should not automatically be interpreted as a calibrated probability or clinical uncertainty; its meaning depends on the annotation process and assumptions.

The geometry audit identifies specific edge cases that should be addressed before production use. The original script also couples file reads and visualisation to execution and relies on relative paths. A maintained geometry library or a hardened implementation would be preferable before any deployment.

## 6. Limitations

1. **Synthetic data only:** no performance claim on patient-generated drawings is supported.
2. **Simplified noise model:** shifts, rotation, scale, and local noise may not reflect how people draw on an interface.
3. **Raster approximation:** both experiments use a 100 × 100 grid.
4. **Separate mask-level experiment:** its perturbation mechanism differs and it does not directly test the original hull/clipping pipeline.
5. **Threshold selection:** 0.5 is a baseline, not a universal optimum.
6. **Limited novelty:** pain-frequency mapping has prior literature; the claim is a controlled simulation comparison and software audit.
7. **No clinical validity:** no clinical endpoints or real-patient evaluation were included.
8. **Permissions and provenance:** the professor provided dummy data specifically for the dissertation, according to the author. The new experiments use generated synthetic data and do not include the professor-provided dataset. The original coordinate/demographic files are excluded. Public release still requires confirmation of authorship, university/IP conditions, and reuse rights for project-derived code.

## 7. Conclusion

In this controlled synthetic benchmark, thresholded spatial-frequency consensus achieved higher mean IoU than strict intersection overall, with higher recall and lower precision. The effect varied by annotation count, noise, and shape. These results motivate further method comparison but do not establish clinical usefulness or real-world superiority. Next steps include independent review of the simulation design, robust polygon tests, and—only with appropriate permission—evaluation on properly governed real annotations.

## References

1. Dixit N, Lee J. Quantification of Digital Body Maps for Pain: Development and Application of an Algorithm for Generating Pain Frequency Maps. *JMIR Form Res*. 2022;6(6):e36687. doi:10.2196/36687.
2. Murphy DA, Ali SM, Boudreau SA, Dixon W, Wong D, van der Veer SN. Summary and Analysis of Digital Pain Manikin Data in Adults With Pain Experience: Scoping Review. *J Med Internet Res*. 2025;27:e69360. doi:10.2196/69360.
3. Eboigbe UD, Lawan A, Rushton A, Walton DM. Types, methods, and modes of implementation of pain/symptom maps in musculoskeletal pain rehabilitation: A scoping review. *Musculoskelet Sci Pract*. 2026;86:103664. doi:10.1016/j.msksp.2026.103664.
4. Sutherland IE, Hodgman GW. Reentrant polygon clipping. *Commun ACM*. 1974. doi:10.1145/360767.360802.
5. Polygon Clipping: Analysis and Experiences. 1992. doi:10.1016/B978-0-12-708240-0.50016-2.

## Submission gate

Before submission, verify all bibliographic metadata and numerical outputs against saved CSVs; document literature-search scope/date; add author affiliations and contributions; obtain supervisor/contributor approval; confirm data and code reuse permissions and university/IP conditions; and check the selected repository's current policies. This draft is not submission-ready until these items are resolved.
