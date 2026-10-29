# Literature review and contribution positioning

## Scope
This short review is a working synthesis to support supervisor discussion, not a systematic review. The full search strategy, search date, and eligibility criteria still need to be documented before publication.

## Digital pain maps and frequency summaries
Dixit and Lee (2022) describe an algorithm for quantifying digital body maps and generating pain-frequency maps. This is important prior art: a preprint should not claim that frequency mapping, automation, or spatial consensus is novel by itself. The defensible question here is narrower: under a declared simulation model, how do thresholded frequency consensus and strict shared-region intersection compare against known synthetic ground truth?

Murphy et al. (2025) reviewed 92 studies using digital pain manikins and reported substantial variation in methods, with limited standardisation across analyses of multiple drawings. A 2026 scoping review by Eboigbe and colleagues similarly describes heterogeneity in the design and quantification of pain/symptom maps. Together, these reviews support transparency and reproducibility as motivations, but do not prove novelty for the current benchmark.

## Polygon clipping and implementation testing
Sutherland and Hodgman (1974) introduced a classic polygon-clipping algorithm. It is established geometry, not a new contribution of this project. The software-audit angle is to test the project's particular implementation for empty intermediate results, polygon winding, and boundary behaviour, and to report these as implementation-specific findings.

## Contribution that may be defensible
- A reproducible simulation-based comparison of strict intersection and thresholded spatial-frequency consensus under specified annotation perturbations.
- Paired evaluation against known synthetic ground truth using IoU, precision, and recall.
- Sensitivity analysis across annotation counts, noise levels, and consensus thresholds.
- A focused audit of selected legacy geometry functions, subject to permission to reuse or redistribute project-derived code.

## Claims to avoid
- Do not claim to invent pain-frequency maps, consensus maps, convex hulls, or polygon clipping.
- Do not claim clinical validation, patient benefit, or real-world superiority from synthetic results.
- Do not imply that the mask-level experiment validates the original point/hull/clipping implementation.
- Do not present a threshold of 0.5 as universally optimal; it is a baseline whose performance depends on the simulation.

## References to verify before submission
1. Dixit N, Lee J. Quantification of Digital Body Maps for Pain: Development and Application of an Algorithm for Generating Pain Frequency Maps. *JMIR Form Res*. 2022;6(6):e36687. doi:10.2196/36687.
2. Murphy DA, Ali SM, Boudreau SA, Dixon W, Wong D, van der Veer SN. Summary and Analysis of Digital Pain Manikin Data in Adults With Pain Experience: Scoping Review. *J Med Internet Res*. 2025;27:e69360. doi:10.2196/69360.
3. Eboigbe UD, Lawan A, Rushton A, Walton DM. Types, methods, and modes of implementation of pain/symptom maps in musculoskeletal pain rehabilitation: A scoping review. *Musculoskelet Sci Pract*. 2026;86:103664. doi:10.1016/j.msksp.2026.103664.
4. Sutherland IE, Hodgman GW. Reentrant polygon clipping. *Commun ACM*. 1974. doi:10.1145/360767.360802.
5. Polygon Clipping: Analysis and Experiences. 1992. doi:10.1016/B978-0-12-708240-0.50016-2.

Confirm every citation's metadata and check repository/publisher requirements before public release.
