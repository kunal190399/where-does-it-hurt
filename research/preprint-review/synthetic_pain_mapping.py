"""Reproducible synthetic benchmark for pain-region overlap methods.

All generated annotations and ground-truth regions are synthetic. This module does
not load or use patient coordinate files from the original project.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.path import Path as MplPath
from shapely.geometry import Polygon

GRID_SIZE = 100
NOISE_LEVELS = (0.005, 0.015, 0.03, 0.05)
ANNOTATOR_COUNTS = (3, 5, 8)
CONSENSUS_THRESHOLDS = (0.3, 0.4, 0.5, 0.6, 0.7)


def make_grid(grid_size: int = GRID_SIZE) -> tuple[np.ndarray, np.ndarray]:
    axis = (np.arange(grid_size) + 0.5) / grid_size
    xx, yy = np.meshgrid(axis, axis)
    points = np.column_stack([xx.ravel(), yy.ravel()])
    return axis, points


def ellipse_points(rng: np.random.Generator, n: int = 160) -> np.ndarray:
    """Create a smooth, randomly oriented ellipse strictly inside [0, 1]^2."""
    for _ in range(100):
        cx, cy = rng.uniform(0.35, 0.65, size=2)
        rx, ry = rng.uniform(0.10, 0.19), rng.uniform(0.08, 0.16)
        angle = rng.uniform(0, 2 * np.pi)
        theta = np.linspace(0, 2 * np.pi, n, endpoint=False)
        raw = np.column_stack([rx * np.cos(theta), ry * np.sin(theta)])
        rot = np.array([[np.cos(angle), -np.sin(angle)],
                        [np.sin(angle), np.cos(angle)]])
        pts = raw @ rot.T + [cx, cy]
        if np.all((pts > 0.03) & (pts < 0.97)):
            return pts
    raise RuntimeError("Could not generate an in-bounds ellipse")


def perturb_annotation(truth_points: np.ndarray, rng: np.random.Generator,
                       noise_sd: float, n_points: int = 80) -> np.ndarray:
    """Simulate global translation/scale/rotation plus local coordinate noise."""
    center = truth_points.mean(axis=0)
    centered = truth_points - center
    scale = max(0.5, rng.normal(1.0, noise_sd * 1.5))
    theta = rng.normal(0.0, noise_sd * 1.2)
    rot = np.array([[np.cos(theta), -np.sin(theta)],
                    [np.sin(theta), np.cos(theta)]])
    shifted = centered @ rot.T * scale + center + rng.normal(0, noise_sd, size=2)
    idx = np.linspace(0, len(shifted), n_points, endpoint=False).astype(int)
    return np.clip(shifted[idx] + rng.normal(0, noise_sd * 0.55, size=(n_points, 2)), 0, 1)


def original_graham_scan(points: np.ndarray) -> list[tuple[float, float]]:
    """Graham-scan adaptation used for the synthetic benchmark."""
    from math import atan2

    pts = [tuple(map(float, p)) for p in np.asarray(points)]
    if len(pts) < 3:
        raise ValueError("At least three points are required")

    def cross_product(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    def distance(p1, p2):
        return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2

    start = min(pts, key=lambda point: (point[1], point[0]))
    sorted_points = sorted(pts, key=lambda point: (
        atan2(point[1] - start[1], point[0] - start[0]),
        distance(start, point)))
    unique_angles_points = [sorted_points[0]]
    for point in sorted_points[1:]:
        while (len(unique_angles_points) > 1 and
               cross_product(unique_angles_points[-2], unique_angles_points[-1], point) == 0):
            unique_angles_points.pop()
        unique_angles_points.append(point)

    hull = unique_angles_points[:2]
    for point in unique_angles_points[2:]:
        while len(hull) > 1 and cross_product(hull[-2], hull[-1], point) <= 0:
            hull.pop()
        hull.append(point)
    return hull


def convex_hull(points: np.ndarray) -> Polygon:
    hull_points = original_graham_scan(points)
    geom = Polygon(hull_points)
    if geom.is_empty or not geom.is_valid or geom.geom_type != "Polygon" or geom.area <= 0:
        raise ValueError("Graham scan did not produce a valid positive-area polygon")
    return geom


def rasterize_polygon(poly: Polygon, grid_points: np.ndarray,
                      grid_size: int = GRID_SIZE) -> np.ndarray:
    coords = np.asarray(poly.exterior.coords)
    mask = MplPath(coords, closed=True).contains_points(grid_points)
    return mask.reshape(grid_size, grid_size)


def iou(pred: np.ndarray, truth: np.ndarray) -> float:
    union = np.logical_or(pred, truth).sum()
    return float(np.logical_and(pred, truth).sum() / union) if union else 1.0


def precision_recall(pred: np.ndarray, truth: np.ndarray) -> tuple[float, float]:
    tp = np.logical_and(pred, truth).sum()
    fp = np.logical_and(pred, ~truth).sum()
    fn = np.logical_and(~pred, truth).sum()
    return (float(tp / (tp + fp)) if tp + fp else 1.0,
            float(tp / (tp + fn)) if tp + fn else 1.0)


def run_benchmark(seed: int = 20261029, repetitions: int = 30,
                  grid_size: int = GRID_SIZE) -> tuple[pd.DataFrame, dict]:
    if repetitions < 1:
        raise ValueError("repetitions must be >= 1")
    _, grid_points = make_grid(grid_size)
    rng = np.random.default_rng(seed)
    records: list[dict] = []
    example: dict = {}

    for noise in NOISE_LEVELS:
        for n_annotators in ANNOTATOR_COUNTS:
            for replicate in range(repetitions):
                truth_points = ellipse_points(rng)
                truth_geom = Polygon(truth_points)
                truth_mask = rasterize_polygon(truth_geom, grid_points, grid_size)
                ann_geoms = [convex_hull(perturb_annotation(truth_points, rng, noise))
                             for _ in range(n_annotators)]
                ann_masks = np.stack([rasterize_polygon(g, grid_points, grid_size)
                                      for g in ann_geoms])
                frequency = ann_masks.mean(axis=0)
                strict = ann_masks.all(axis=0)
                for threshold in CONSENSUS_THRESHOLDS:
                    pred = frequency >= threshold
                    p, r = precision_recall(pred, truth_mask)
                    records.append({
                        "noise_sd": noise, "annotators": n_annotators,
                        "replicate": replicate, "method": f"frequency_threshold_{threshold:.1f}",
                        "threshold": threshold, "iou": iou(pred, truth_mask),
                        "precision": p, "recall": r,
                        "predicted_area_fraction": float(pred.mean()),
                        "truth_area_fraction": float(truth_mask.mean()),
                        "brier_score": float(np.mean((frequency - truth_mask.astype(float)) ** 2)),
                    })
                p, r = precision_recall(strict, truth_mask)
                records.append({
                    "noise_sd": noise, "annotators": n_annotators,
                    "replicate": replicate, "method": "strict_intersection",
                    "threshold": np.nan, "iou": iou(strict, truth_mask),
                    "precision": p, "recall": r,
                    "predicted_area_fraction": float(strict.mean()),
                    "truth_area_fraction": float(truth_mask.mean()),
                    "brier_score": np.nan,
                })
                if noise == 0.015 and n_annotators == 5 and replicate == 0:
                    example = {"truth": truth_mask, "annotation_masks": ann_masks,
                               "frequency": frequency, "strict": strict,
                               "consensus": frequency >= 0.5}

    return pd.DataFrame.from_records(records), example


def bootstrap_mean_ci(values: np.ndarray, seed: int = 42,
                      n_boot: int = 5000) -> tuple[float, float, float]:
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    draws = rng.choice(values, size=(n_boot, len(values)), replace=True).mean(axis=1)
    return float(values.mean()), float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))


def write_outputs(out_dir: Path, seed: int = 20261029, repetitions: int = 30) -> pd.DataFrame:
    out_dir.mkdir(parents=True, exist_ok=True)
    raw, example = run_benchmark(seed, repetitions)
    raw.to_csv(out_dir / "synthetic_benchmark_raw.csv", index=False)
    summary = (raw.groupby(["noise_sd", "annotators", "method"], as_index=False)
               .agg(iou_mean=("iou", "mean"), iou_sd=("iou", "std"),
                    precision_mean=("precision", "mean"), recall_mean=("recall", "mean"),
                    predicted_area_mean=("predicted_area_fraction", "mean"),
                    brier_score_mean=("brier_score", "mean")))
    summary.to_csv(out_dir / "synthetic_benchmark_summary.csv", index=False)

    wide = raw.pivot(index=["noise_sd", "annotators", "replicate"],
                     columns="method", values="iou").reset_index()
    wide["iou_difference_consensus_minus_intersection"] = (
        wide["frequency_threshold_0.5"] - wide["strict_intersection"])
    wide.to_csv(out_dir / "paired_case_iou.csv", index=False)
    mean, low, high = bootstrap_mean_ci(wide["iou_difference_consensus_minus_intersection"].to_numpy())
    pd.DataFrame([{"paired_mean_iou_difference": mean, "bootstrap_95_ci_low": low,
                   "bootstrap_95_ci_high": high, "n_paired_cases": len(wide)}]).to_csv(
                       out_dir / "paired_iou_bootstrap_ci.csv", index=False)

    threshold = raw[raw["threshold"].notna()].groupby(
        ["noise_sd", "annotators", "threshold"], as_index=False).agg(
            iou_mean=("iou", "mean"), iou_sd=("iou", "std"),
            precision_mean=("precision", "mean"), recall_mean=("recall", "mean"))
    threshold.to_csv(out_dir / "threshold_sensitivity_summary.csv", index=False)

    fig, axes = plt.subplots(1, 4, figsize=(12, 3.2), constrained_layout=True)
    axes[0].imshow(example["truth"], origin="lower"); axes[0].set_title("Synthetic truth")
    axes[1].imshow(example["frequency"], origin="lower", vmin=0, vmax=1); axes[1].set_title("Frequency map")
    axes[2].imshow(example["consensus"], origin="lower"); axes[2].set_title("Consensus (≥0.5)")
    axes[3].imshow(example["strict"], origin="lower"); axes[3].set_title("Strict intersection")
    for ax in axes: ax.set_xticks([]); ax.set_yticks([])
    fig.savefig(out_dir / "synthetic_method_example.png", dpi=180); plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(11, 3.3), sharey=True, constrained_layout=True)
    for ax, n in zip(axes, ANNOTATOR_COUNTS):
        part = summary[summary["annotators"] == n]
        for method in ["frequency_threshold_0.5", "strict_intersection"]:
            q = part[part["method"] == method].sort_values("noise_sd")
            ax.errorbar(q["noise_sd"], q["iou_mean"], yerr=q["iou_sd"],
                        marker="o", label=method, capsize=2)
        ax.set_title(f"{n} annotations"); ax.set_xlabel("Coordinate noise SD"); ax.grid(True, alpha=.25)
    axes[0].set_ylabel("IoU vs synthetic truth"); axes[-1].legend(fontsize=7)
    fig.savefig(out_dir / "synthetic_iou_comparison.png", dpi=180); plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(11, 3.3), sharey=True, constrained_layout=True)
    for ax, n in zip(axes, ANNOTATOR_COUNTS):
        q = threshold[threshold["annotators"] == n]
        for noise in NOISE_LEVELS:
            s = q[q["noise_sd"] == noise].groupby("threshold", as_index=False)["iou_mean"].mean()
            ax.plot(s["threshold"], s["iou_mean"], marker="o", label=f"noise={noise:g}")
        ax.set_title(f"{n} annotations"); ax.set_xlabel("Consensus threshold"); ax.grid(True, alpha=.25)
    axes[0].set_ylabel("Mean IoU"); axes[-1].legend(fontsize=7)
    fig.savefig(out_dir / "threshold_sensitivity.png", dpi=180); plt.close(fig)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="outputs")
    parser.add_argument("--seed", type=int, default=20261029)
    parser.add_argument("--repetitions", type=int, default=30)
    args = parser.parse_args()
    summary = write_outputs(Path(args.out), args.seed, args.repetitions)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
