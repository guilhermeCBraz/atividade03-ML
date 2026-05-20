#!/usr/bin/env python3
"""Cluster eye profiles from AL, ACD, WTW, K1, K2.

Usage:
  python scripts/cluster_eyes.py --input barrettII_eyes_clustering.xlsx

Outputs (default in same folder as input):
  - clustered_eyes.csv
  - cluster_profiles_mean.csv
  - cluster_profiles_std.csv
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value).lower())


def resolve_columns(df: pd.DataFrame) -> list[str]:
    norm_map = {norm(c): c for c in df.columns}
    required = ["al", "acd", "wtw", "k1", "k2"]
    missing = [c for c in required if c not in norm_map]
    if missing:
        raise ValueError(
            "Missing columns (normalized): "
            + ", ".join(missing)
            + " | Found: "
            + ", ".join([str(c) for c in df.columns])
        )
    return [norm_map[c] for c in required]


def pick_k(x_scaled, min_k: int, max_k: int, seed: int) -> tuple[int, list[tuple[int, float, float]]]:
    max_k = min(max_k, max(2, x_scaled.shape[0] - 1))
    min_k = min(min_k, max_k)

    results: list[tuple[int, float, float]] = []
    for k in range(min_k, max_k + 1):
        km = KMeans(n_clusters=k, n_init=20, random_state=seed)
        labels = km.fit_predict(x_scaled)
        sil = silhouette_score(x_scaled, labels)
        results.append((k, sil, km.inertia_))

    best_k = max(results, key=lambda item: item[1])[0]
    return best_k, results


def main() -> None:
    parser = argparse.ArgumentParser(description="Cluster eye profiles.")
    parser.add_argument("--input", required=True, help="Path to Excel file")
    parser.add_argument("--output-dir", default=None, help="Directory for outputs")
    parser.add_argument("--min-k", type=int, default=2, help="Minimum k to test")
    parser.add_argument("--max-k", type=int, default=8, help="Maximum k to test")
    parser.add_argument("--k", type=int, default=None, help="Force a specific k")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")

    output_dir = Path(args.output_dir) if args.output_dir else input_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_excel(input_path)
    cols = resolve_columns(df)
    x = df[cols].copy()

    for col in cols:
        x[col] = pd.to_numeric(x[col], errors="coerce")

    before = len(x)
    x = x.dropna(axis=0, how="any")
    dropped = before - len(x)

    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(x.values)

    if args.k:
        best_k = args.k
        results: list[tuple[int, float, float]] = []
    else:
        best_k, results = pick_k(x_scaled, args.min_k, args.max_k, args.seed)

    if results:
        print("k, silhouette, inertia")
        for k, sil, inertia in results:
            print(k, round(sil, 4), round(inertia, 2))
        print("Best k by silhouette:", best_k)

    km = KMeans(n_clusters=best_k, n_init=50, random_state=args.seed)
    labels = km.fit_predict(x_scaled)

    x_with = x.copy()
    x_with["cluster"] = labels

    profile_mean = x_with.groupby("cluster")[cols].mean()
    profile_std = x_with.groupby("cluster")[cols].std()

    df_out = df.loc[x_with.index].copy()
    df_out["cluster"] = labels

    clustered_path = output_dir / "clustered_eyes.csv"
    mean_path = output_dir / "cluster_profiles_mean.csv"
    std_path = output_dir / "cluster_profiles_std.csv"

    df_out.to_csv(clustered_path, index=False)
    profile_mean.to_csv(mean_path)
    profile_std.to_csv(std_path)

    print("Rows, Cols:", df.shape)
    print("Using columns:", cols)
    print("Dropped rows with NA:", dropped)
    print("Cluster sizes:")
    print(x_with["cluster"].value_counts().sort_index())
    print("Wrote:", clustered_path)
    print("Wrote:", mean_path)
    print("Wrote:", std_path)


if __name__ == "__main__":
    main()
