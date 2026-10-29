# Where Does It Hurt? — Synthetic Research Extension

**Status: draft for supervisor review. Not submission-ready.**

This directory contains a research extension to the original *Where Does It Hurt?* dissertation project. The purpose is to make the proposed research question, experimental setup, findings, limitations, and review requirements understandable to a supervisor or future collaborator.

## 1. Project overview

The original project processes spatial points representing a marked region, transforms those points to an image coordinate system, builds a convex hull, and uses polygon clipping to calculate the region shared by annotations.

This extension asks a narrower research question:

> When several noisy annotations represent the same underlying region, how does strict intersection compare with thresholded spatial-frequency consensus against known synthetic ground truth?

- **Strict intersection** keeps only grid cells included in every annotation. It is conservative: a cell omitted by one annotator disappears from the result.
- **Spatial-frequency consensus** counts how often each cell is included and keeps cells whose frequency reaches a chosen threshold (for example, 0.5 means at least half the annotations include that cell).

The work compares these aggregation rules in controlled simulations and separately audits selected edge cases in the legacy geometry implementation. It does **not** claim to invent pain-frequency mapping, and it does **not** establish clinical validity.

## 2. What is in this folder?

| File | Purpose |
|---|---|
| `PREPRINT_DRAFT.md` | Working manuscript: question, methods, results, discussion, limitations and references |
| `REVIEW_SUMMARY.md` | Short summary and questions for the supervisor |
| `RESULTS_SUMMARY.md` | Numerical results and threshold sensitivity summary |
| `synthetic_pain_mapping.py` | Reproducible point/convex-hull synthetic benchmark |
| `extended_shape_benchmark.py` | Separate mask-level benchmark for ellipse, irregular and disconnected shapes |
| `test_synthetic_pain_mapping.py` | Basic automated tests for the main synthetic benchmark |
| `requirements.txt` | Python package dependencies |
| `LITERATURE_REVIEW.md` | Related work and contribution positioning |
| `ORIGINAL_CODE_AUDIT.md` | Summary of selected legacy geometry findings |
| `PROVENANCE.md` | Data provenance and scope notes |
| `AUTHORSHIP_AND_PERMISSION_CHECKLIST.md` | Publication, authorship, IP and permission checklist |

The professor-provided dummy dataset and original coordinate/demographic files are intentionally not included. Project-derived geometry source and executable tests against it are also withheld from this branch pending confirmation of reuse permissions.

## 3. Experiments

### A. Point/hull benchmark

- 360 synthetic cases: four coordinate-noise levels × three annotation counts × 30 repetitions.
- Synthetic regions are elliptical. Noisy points are converted to convex hulls and rasterised on a common grid.
- Compares strict intersection with frequency thresholds 0.3, 0.4, 0.5, 0.6 and 0.7.
- Metrics include intersection over union (IoU), precision, recall and a Brier-style score for the frequency map.

### B. Mask-level shape extension

- 1,080 synthetic cases across ellipse, irregular-polygon and disconnected-region families.
- Tests how the aggregation rules behave when the ground-truth mask has different shapes.
- This uses a different perturbation model from the point/hull experiment. It is **not** a direct test of the original convex-hull/polygon-clipping pipeline.

### C. Legacy geometry audit

Selected original geometry functions were tested separately from file loading and visualisation. The reported tests found specific edge cases, including an `IndexError` for disjoint polygons and failure in the tested reversed clip-polygon winding case. These are findings for the tested cases, not an exhaustive proof of all possible failures.

## 4. Main exploratory findings

In the point/hull experiment, mean IoU was 0.787 for frequency consensus at threshold 0.5 and 0.733 for strict intersection. Consensus had higher mean recall (0.978) but lower mean precision (0.798) than strict intersection (recall 0.754; precision 0.965). This illustrates a precision–recall trade-off under the chosen simulation assumptions.

In the mask-level experiment, at perturbation SD 0.030 and five annotations, mean IoU for consensus versus strict intersection was 0.806 vs 0.508 for ellipses, 0.715 vs 0.320 for irregular regions, and 0.649 vs 0.180 for disconnected regions.

These numbers are exploratory and must be checked against generated outputs before submission. Synthetic results do not establish performance on real drawings, patient outcomes, or clinical usefulness. A threshold that performs well in one simulation is not necessarily optimal for another dataset.

## 5. Reproduce the experiments

Use Python 3.10+ in a virtual environment. From this directory:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Run the point/hull benchmark:

```bash
python synthetic_pain_mapping.py --out outputs --seed 20261029 --repetitions 30
```

Run the mask-level extension:

```bash
python extended_shape_benchmark.py --out outputs --seed 20261029 --repetitions 30
```

Run the available tests:

```bash
pytest -q
```

The scripts write CSV summaries and figures to the chosen output directory. Full runs may take longer than a quick smoke test. For a faster check, use `--repetitions 1`; do not use that reduced run to reproduce the manuscript's reported 30-repetition results.

## 6. Suggested reading order for the supervisor

1. Start with `REVIEW_SUMMARY.md` for the research question and review questions.
2. Read `PREPRINT_DRAFT.md` for the proposed manuscript.
3. Check `RESULTS_SUMMARY.md` and reproduce the experiments.
4. Review `LITERATURE_REVIEW.md` and `ORIGINAL_CODE_AUDIT.md`.
5. Resolve all items in `AUTHORSHIP_AND_PERMISSION_CHECKLIST.md` before public release.

## 7. Publication and permissions

Before public release or journal submission:

- Confirm the author list, contributions, affiliations and acknowledgements with the supervisor.
- Confirm university intellectual-property rules and permission to redistribute any project-derived code.
- Confirm whether the professor-provided dummy data may be reused or described in a public paper; it is not needed by the new synthetic experiments.
- Verify all references and reported numbers against the generated outputs.
- Document the literature-search method and date.
- Keep the claims limited to the experiments actually performed and state clearly that there is no clinical validation.

**Current status:** a working research package for discussion and revision, not a validated clinical tool or submission-ready manuscript.
