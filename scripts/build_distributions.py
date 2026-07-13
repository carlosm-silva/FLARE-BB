#!/usr/bin/env python3
"""Build flux-distribution artifacts from KDE data."""

from __future__ import annotations

import argparse
from pathlib import Path

from flare_bb.core.config import DistributionConfig
from flare_bb.pipeline.distributions import build_distribution_file, list_distribution_files
from flare_bb.pipeline.kde import load_most_recent_kde


def main() -> None:
    """Run the distribution builder CLI."""
    parser = argparse.ArgumentParser(description="Build FLARE-BB posterior flux distributions from KDE data.")
    parser.add_argument("--kde-path", type=Path)
    parser.add_argument("--kde-dir", type=Path, default=Path("data/cache/kde"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/cache/distributions"))
    parser.add_argument("--hd-resolution", type=int, default=DistributionConfig.high_definition_resolution)
    parser.add_argument("--ml-resolution", type=int, default=DistributionConfig.marginal_likelihood_resolution)
    parser.add_argument("--ml-interp-points", type=int, default=DistributionConfig.marginal_likelihood_interp_points)
    parser.add_argument("--final-bins", type=int, default=DistributionConfig.final_grid_bins)
    parser.add_argument("--flux-min", type=float, default=DistributionConfig.log_true_flux_min)
    parser.add_argument("--flux-max", type=float, default=DistributionConfig.log_true_flux_max)
    parser.add_argument("--range-extension", type=float, default=DistributionConfig.marginal_likelihood_range_extension)
    parser.add_argument("--epsilon", type=float, default=DistributionConfig.numerical_epsilon)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--progress", action="store_true")
    parser.add_argument("--list", action="store_true", help="List existing distribution files and exit.")
    args = parser.parse_args()

    if args.list:
        for path in list_distribution_files(args.output_dir):
            print(path)
        return

    kde_path = args.kde_path
    if kde_path is None:
        _, _, kde_path = load_most_recent_kde(args.kde_dir)

    config = DistributionConfig(
        high_definition_resolution=args.hd_resolution,
        marginal_likelihood_resolution=args.ml_resolution,
        marginal_likelihood_interp_points=args.ml_interp_points,
        final_grid_bins=args.final_bins,
        log_true_flux_min=args.flux_min,
        log_true_flux_max=args.flux_max,
        marginal_likelihood_range_extension=args.range_extension,
        numerical_epsilon=args.epsilon,
    )
    output_path = build_distribution_file(
        kde_path,
        args.output_dir,
        config=config,
        overwrite=args.overwrite,
        show_progress=args.progress,
    )
    print(output_path)


if __name__ == "__main__":
    main()
