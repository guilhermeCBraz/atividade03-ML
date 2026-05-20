#!/usr/bin/env python3
"""Generate charts from clustered_eyes.csv.

Usage:
  python scripts/plot_clusters.py --input clustered_eyes.csv --output-dir figures
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot cluster charts.")
    parser.add_argument("--input", required=True, help="Path to clustered_eyes.csv")
    parser.add_argument("--output-dir", default="figures", help="Directory for charts")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_path)
    cols = ["AL", "ACD", "WTW", "K1", "K2"]

    if "cluster" not in df.columns:
        raise SystemExit("Missing column 'cluster' in input file")

    clusters = sorted(df["cluster"].unique())
    colors = ["#4C78A8", "#F58518", "#54A24B", "#B279A2", "#E45756", "#72B7B2"]

    # Cluster sizes
    sizes = df["cluster"].value_counts().sort_index()
    plt.figure(figsize=(6, 4))
    plt.bar([str(c) for c in sizes.index], sizes.values, color=colors[: len(sizes)])
    plt.title("Tamanho dos grupos")
    plt.xlabel("Cluster")
    plt.ylabel("Quantidade de olhos")
    plt.tight_layout()
    plt.savefig(output_dir / "cluster_sizes.png", dpi=200)
    plt.close()

    # Means by cluster
    means = df.groupby("cluster")[cols].mean().loc[clusters]
    x = np.arange(len(cols))
    width = 0.8 / max(1, len(clusters))

    plt.figure(figsize=(8, 4.5))
    for idx, cluster in enumerate(clusters):
        offset = (idx - (len(clusters) - 1) / 2) * width
        plt.bar(
            x + offset,
            means.loc[cluster].values,
            width,
            label=f"Cluster {cluster}",
            color=colors[idx % len(colors)],
        )
    plt.xticks(x, cols)
    plt.ylabel("Media")
    plt.title("Medias por cluster")
    plt.legend()
    plt.grid(axis="y", alpha=0.2)
    plt.tight_layout()
    plt.savefig(output_dir / "cluster_means.png", dpi=200)
    plt.close()

    # Z-score means by cluster
    overall_mean = df[cols].mean()
    overall_std = df[cols].std(ddof=0)
    z_means = (means - overall_mean) / overall_std

    plt.figure(figsize=(8, 4.5))
    for idx, cluster in enumerate(clusters):
        offset = (idx - (len(clusters) - 1) / 2) * width
        plt.bar(
            x + offset,
            z_means.loc[cluster].values,
            width,
            label=f"Cluster {cluster}",
            color=colors[idx % len(colors)],
        )
    plt.axhline(0, color="#333333", linewidth=1)
    plt.xticks(x, cols)
    plt.ylabel("Z-score")
    plt.title("Diferenca padronizada por cluster")
    plt.legend()
    plt.grid(axis="y", alpha=0.2)
    plt.tight_layout()
    plt.savefig(output_dir / "cluster_zscores.png", dpi=200)
    plt.close()

    print("Wrote:", output_dir / "cluster_sizes.png")
    print("Wrote:", output_dir / "cluster_means.png")
    print("Wrote:", output_dir / "cluster_zscores.png")


if __name__ == "__main__":
    main()
