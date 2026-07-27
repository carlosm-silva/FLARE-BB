#!/usr/bin/env python3
"""Download and cache Fermi LCR light curves for clean catalog sources."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from tqdm import tqdm

from flare_bb.io.catalog import load_fermi_catalog
from flare_bb.io.lcr import LightCurveRequest, load_light_curve


def main() -> None:
    """Run the LCR downloader CLI."""
    parser = argparse.ArgumentParser(description="Download Fermi LCR light curves for sources in a clean catalog.")
    parser.add_argument("--catalog", type=Path, default=Path("data/catalogs/gll_psc_v32.fit"))
    parser.add_argument("--cache-dir", type=Path, default=Path("data/cache/LCRs"))
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()

    catalog = load_fermi_catalog(args.catalog)
    sources = list(catalog["Source_Name"].values)

    def download_source(source: str) -> None:
        for cadence in ("daily", "weekly", "monthly"):
            for flux_type in ("photon", "energy"):
                for index_type in ("fixed", "free"):
                    request = LightCurveRequest(source, cadence=cadence, flux_type=flux_type, index_type=index_type)
                    try:
                        load_light_curve(request, args.cache_dir)
                    except (RuntimeError, ValueError):
                        continue

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        for _ in tqdm(executor.map(download_source, sources), total=len(sources)):
            pass


if __name__ == "__main__":
    main()
