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
# This script downloads the LCRs for all sources listed in the 4FGL-DR4 catalog with the CLEAN flag.
#

import argparse
import os
import sys
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
from astropy.table import Table
from tqdm import tqdm

# Add the src directory to the path to import from the package
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from data_processing.downloader import download_cache_source, ensure_cache_folder_exists, format_src_name


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Download LCRs for all sources listed in the 4FGL-DR4 catalog with the CLEAN flag."
    )
    parser.add_argument(
        "--workers", type=int, default=8, help="Number of worker threads for parallel processing (default: 8)"
    )
    parser.add_argument(
        "--catalog", type=str, default="gll_psc_v32.fit", help="Name of the catalog file (default: gll_psc_v32.fit)"
    )
    return parser.parse_args()


def main():
    """Main function to download LCRs for all CLEAN sources in the 4FGL-DR4 catalog."""
    args = parse_arguments()

    # Loading the 4FGL-DR4 catalog
    catalog_folder = os.path.join("data", "catalogs") + os.sep
    # Check if the catalog folder exists. If not, raise an error.
    if not os.path.exists(catalog_folder):
        raise FileNotFoundError(f"Catalog folder {catalog_folder} not found.")
    # The name of the catalog file
    catalog_name = args.catalog
    # Check if the catalog file exists. If not, raise an error.
    if not os.path.exists(os.path.join(catalog_folder, catalog_name)):
        raise FileNotFoundError(f"Catalog file {catalog_name} not found.")
    # Load the catalog as a fits table
    c_table = Table.read(os.path.join(catalog_folder, catalog_name), format="fits", hdu=1)
    # Filter multi-dimensional columns
    column_names = [name for name in c_table.columns if len(c_table[name].shape) <= 1]
    # Convert the table to a pandas dataframe
    df: pd.DataFrame = c_table[column_names].to_pandas()
    # Filter the dataframe to only include sources with the CLEAN flag
    df = df.loc[(df["Flags"] == 0).astype(bool)]
    # Convert the source names to strings
    df["Source_Name"] = df["Source_Name"].apply(format_src_name)

    # Create the cache folder if it does not exist
    ensure_cache_folder_exists()

    # Download the LCRs for all sources in the dataframe using multi-threading
    # Since ping is the bottleneck, no parallelization is needed.
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        for _ in tqdm(executor.map(download_cache_source, df["Source_Name"].values), total=len(df["Source_Name"])):
            pass


if __name__ == "__main__":
    main()
