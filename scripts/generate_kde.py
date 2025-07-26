#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# FLARE-BB – Bayesian Blocks algorithm for detecting gamma-ray flares
# Copyright © 2025 Carlos Márcio de Oliveira e Silva Filho
# Copyright © 2025 Ignacio Taboada
#
# This file is part of FLARE-BB.
# FLARE-BB is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# FLARE-BB is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this file.  If not, see <https://www.gnu.org/licenses/>.
#
# ------------------------------------------------------------------------------------------------------------------------
#
# Script for generating KDE data with different parameter configurations.
# This script demonstrates the "heavy lifting" - actual data loading and calculations.
#

import argparse
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import numpy as np
import pandas as pd
from astropy.table import Table
from pyLCR import sources
from tqdm import tqdm

from data_processing.caching import CachedLightCurve
from data_processing.kde_generator import (
    FLUX_TYPE,
    TS_MIN,
    TS_THRESHOLD,
    create_sample_data,
    format_src_name,
    is_blazar,
    run_kde_generation,
)
from data_processing.kde_utils import get_kde_file_summary, list_kde_files


def load_fermi_catalog(catalog_path: str) -> pd.DataFrame:
    """
    Load and clean the 4FGL catalog.

    :param catalog_path: Path to the catalog file
    :type catalog_path: str
    :returns: Cleaned catalog DataFrame
    :rtype: pd.DataFrame
    """
    print("📖 Loading Fermi-LAT 4FGL catalog...")

    # Read the catalog
    fits_table = Table.read(catalog_path + "gll_psc_v32.fit", format="fits", hdu=1)
    names = [name for name in fits_table.colnames if len(fits_table[name].shape) <= 1]
    df = fits_table[names].to_pandas()
    df_clean = df.loc[(df["Flags"] == 0).astype(bool)]

    # Remove trailing spaces from the source names and the class names
    df_clean.loc[:, "Source_Name"] = df_clean["Source_Name"].apply(format_src_name)
    df_clean.loc[:, "CLASS1"] = df_clean["CLASS1"].apply(format_src_name)
    df_clean.loc[:, "CLASS2"] = df_clean["CLASS2"].apply(format_src_name)

    print(f"   ✅ Loaded {len(df_clean)} sources from catalog")

    return df_clean


def load_blazar_lightcurves(catalog_df: pd.DataFrame, verbose: bool = True) -> np.ndarray:
    """
    Load and process blazar light curves from pyLCR.

    :param catalog_df: Cleaned 4FGL catalog
    :type catalog_df: pd.DataFrame
    :param verbose: Whether to show progress
    :type verbose: bool
    :returns: Stacked array of log flux and log error data
    :rtype: np.ndarray
    """
    if verbose:
        print("🌟 Loading blazar light curves...")
        print(f"   • Using flux type: {FLUX_TYPE}")
        print(f"   • TS minimum: {TS_MIN}")
        print(f"   • TS threshold for analysis: {TS_THRESHOLD}")

    fluxes = []
    errors = []
    blazar_count = 0
    processed_count = 0

    progress_desc = "Loading Light Curves" if verbose else None
    disable_progress = not verbose

    for lcr in tqdm(sources, desc=progress_desc, disable=disable_progress):
        if not is_blazar(lcr, catalog_df):
            continue

        blazar_count += 1

        try:
            clc = CachedLightCurve(lcr, flux_type=FLUX_TYPE, ts_min=TS_MIN)
            index_dict = {v: i for i, v in enumerate(clc.met)}
            indexes = [index_dict[i] for i in clc.met_detections]
            _ts = clc.ts[indexes]
            _flux = clc.flux
            _flux_error = clc.flux_error[:, 1] - _flux

            # Apply TS threshold
            high_ts_mask = _ts > TS_THRESHOLD
            if np.any(high_ts_mask):
                fluxes.append(clc.flux[high_ts_mask])
                errors.append(_flux_error[high_ts_mask])
                processed_count += 1

        except Exception as e:
            raise e
            if verbose:
                print(f"   ⚠️  Warning: Could not process {lcr}: {e}")
            continue

    if len(fluxes) == 0:
        raise ValueError("No valid blazar data found!")

    # Concatenate all data
    fluxes = np.concatenate(fluxes)
    errors = np.concatenate(errors)

    # Filter out invalid data points
    valid_mask = errors > 0
    fluxes = fluxes[valid_mask]
    errors = errors[valid_mask]

    # Prepare data for KDE (convert to log space)
    xxx = np.log10(fluxes)
    yyy = np.log10(errors)

    stacked_data = np.vstack([xxx, yyy])

    if verbose:
        print(f"   ✅ Processed {processed_count} blazars from {blazar_count} blazar candidates")
        print(f"   • Total data points: {stacked_data.shape[1]}")
        print(f"   • Log flux range: [{np.min(xxx):.2f}, {np.max(xxx):.2f}]")
        print(f"   • Log error range: [{np.min(yyy):.2f}, {np.max(yyy):.2f}]")

    return stacked_data


def main():
    """Main function handling command line arguments and workflow execution."""

    parser = argparse.ArgumentParser(description="Generate KDE data with different parameter configurations")
    parser.add_argument("--bandwidth", type=float, help="KDE bandwidth (default: 0.2)")
    parser.add_argument("--nbins", type=int, help="Number of grid bins (default: 512)")
    parser.add_argument("--ts-threshold", type=int, help="TS threshold (default: 19)")
    parser.add_argument("--flux-type", type=str, help="Flux type: 'energy' or 'photon' (default: 'energy')")
    parser.add_argument("--list", action="store_true", help="List existing KDE files and exit")
    parser.add_argument("--batch", action="store_true", help="Run multiple parameter combinations")
    parser.add_argument(
        "--sample-data", action="store_true", help="Use sample data instead of loading real blazar data"
    )
    parser.add_argument(
        "--catalog-path",
        type=str,
        default=os.path.join("data", "catalogs") + os.sep,
        help="Path to the Fermi catalog directory",
    )

    args = parser.parse_args()

    # Handle list option
    if args.list:
        kde_dir = os.path.join("data", "cache", "kde")
        kde_files = list_kde_files(kde_dir)

        if not kde_files:
            print("📁 No KDE files found in data/cache/kde/")
        else:
            print(f"📁 Found {len(kde_files)} KDE file(s):")
            for i, filepath in enumerate(kde_files, 1):
                print(f"  {i}. {os.path.basename(filepath)}")

            # Show summary
            summary = get_kde_file_summary(kde_dir)
            print(f"\n📊 Summary: {summary['unique_parameter_sets']} unique parameter combinations")

        return

    # Build custom parameters from command line
    custom_params = {}
    if args.bandwidth is not None:
        custom_params["bandwidth"] = args.bandwidth
    if args.nbins is not None:
        custom_params["nbins"] = args.nbins
    if args.ts_threshold is not None:
        custom_params["ts_threshold"] = args.ts_threshold
    if args.flux_type is not None:
        custom_params["flux_type"] = args.flux_type

    # Handle batch processing
    if args.batch:
        print("🚀 Batch Processing Mode")
        print("=" * 60)

        batch_configs = [
            {"bandwidth": 0.15, "nbins": 256},
            {"bandwidth": 0.2, "nbins": 512},  # Default
            {"bandwidth": 0.3, "nbins": 512},
            {"bandwidth": 0.2, "nbins": 1024},
            {"ts_threshold": 25, "bandwidth": 0.2},
        ]

        # Load data once for all batch runs
        if args.sample_data:
            print("📊 Using sample data for batch processing...")
            stacked_data = create_sample_data(n_points=2000)
        else:
            catalog_df = load_fermi_catalog(args.catalog_path)
            stacked_data = load_blazar_lightcurves(catalog_df)

        results = []
        for i, config in enumerate(batch_configs, 1):
            print(f"\n📋 Configuration {i}/{len(batch_configs)}: {config}")
            # Merge custom params with batch config
            batch_params = {**custom_params, **config}
            result = run_kde_generation(stacked_data, custom_params=batch_params)
            results.append(result)

        print("\n✅ Batch processing complete!")
        print(f"Generated {len([r for r in results if r])} KDE files")
        return

    # Load data for single run
    if args.sample_data:
        print("📊 Using sample data...")
        stacked_data = create_sample_data(n_points=2000)
    else:
        print("📊 Loading real blazar data from Fermi-LAT 4FGL catalog...")
        catalog_df = load_fermi_catalog(args.catalog_path)
        stacked_data = load_blazar_lightcurves(catalog_df)

    # Run single KDE generation
    result = run_kde_generation(stacked_data, custom_params=custom_params)

    if result:
        print(f"\n🎉 Success! Generated KDE file: {os.path.basename(result)}")
        print(f"💡 Use 'python scripts/kde_data_example.py {result}' to examine the results")
    else:
        print("\n❌ KDE generation failed")


if __name__ == "__main__":
    main()
