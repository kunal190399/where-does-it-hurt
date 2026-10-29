import numpy as np
from shapely.geometry import Polygon

from synthetic_pain_mapping import (
    bootstrap_mean_ci, convex_hull, make_grid, rasterize_polygon, run_benchmark,
)


def test_convex_hull_is_valid_and_contains_points():
    points = np.array([[0, 0], [1, 0], [1, 1], [0, 1], [0.5, 0.5]])
    hull = convex_hull(points)
    assert hull.is_valid
    assert abs(hull.area - 1.0) < 1e-9


def test_synthetic_generation_is_reproducible():
    a = run_benchmark(seed=17, repetitions=1)[0]
    b = run_benchmark(seed=17, repetitions=1)[0]
    assert a.equals(b)


def test_benchmark_has_expected_case_count_and_methods():
    df, example = run_benchmark(seed=3, repetitions=2)
    assert df[["noise_sd", "annotators", "replicate"]].drop_duplicates().shape[0] == 24
    assert df.shape[0] == 24 * 6
    assert "frequency" in example and "truth" in example


def test_bootstrap_ci_contains_sample_mean_for_constant_values():
    mean, low, high = bootstrap_mean_ci(np.ones(10), n_boot=200)
    assert mean == 1.0
    assert low == 1.0 and high == 1.0


def test_rasterization_has_positive_area():
    points = np.array([[0.2, 0.2], [0.8, 0.2], [0.8, 0.8], [0.2, 0.8]])
    mask = rasterize_polygon(Polygon(points), make_grid()[1])
    assert mask.sum() > 0
