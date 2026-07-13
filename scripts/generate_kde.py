#!/usr/bin/env python3
"""Generate KDE artifacts for FLARE-BB."""

from __future__ import annotations

import argparse
from pathlib import Path

from flare_bb.core.config import KdeConfig
from flare_bb.core.kde import create_sample_flux_data
from flare_bb.io.catalog import extract_blazar_flux_data, load_fermi_catalog
from flare_bb.io.lcr import import_pylcr
from flare_bb.pipeline.kde import generate_kde_file, list_kde_files


def main() -> None:
    """Run the KDE generation CLI."""
    parser = argparse.ArgumentParser(description="Generate KDE data for measured flux/error samples.")
    parser.add_argument("--output-dir", type=Path, default=Path("data/cache/kde"))
    parser.add_argument("--catalog", type=Path, default=Path("data/catalogs/gll_psc_v32.fit"))
    parser.add_argument("--bandwidth", type=float, default=KdeConfig.bandwidth)
    parser.add_argument("--bins", type=int, default=KdeConfig.bins)
    parser.add_argument("--ts-threshold", type=int, default=KdeConfig.ts_threshold)
    parser.add_argument("--flux-type", choices=["energy", "photon"], default=KdeConfig.flux_type)
    parser.add_argument("--sample-data", action="store_true", help="Use deterministic sample data instead of pyLCR.")
    parser.add_argument("--sample-size", type=int, default=2000)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--list", action="store_true", help="List existing KDE files and exit.")
    args = parser.parse_args()

    if args.list:
        for path in list_kde_files(args.output_dir):
            print(path)
        return

    config = KdeConfig(
        bandwidth=args.bandwidth,
        bins=args.bins,
        ts_threshold=args.ts_threshold,
        flux_type=args.flux_type,
    )
    if args.sample_data:
        data = create_sample_flux_data(args.sample_size)
    else:
        pylcr = import_pylcr()
        catalog = load_fermi_catalog(args.catalog)
        data = extract_blazar_flux_data(catalog, list(pylcr.sources), Path("data/cache/LCRs"), config)

    output_path = generate_kde_file(data, args.output_dir, config=config, overwrite=args.overwrite)
    print(output_path)


if __name__ == "__main__":
    main()
