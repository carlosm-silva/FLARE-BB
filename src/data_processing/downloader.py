"""
SPDX-License-Identifier: GPL-3.0-or-later
FLARE-BB – Bayesian Blocks algorithm for detecting gamma-ray flares
Copyright © 2025 Carlos Márcio de Oliveira e Silva Filho
Copyright © 2025 Ignacio Taboada

This file is part of FLARE-BB.
FLARE-BB is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

FLARE-BB is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this file.  If not, see <https://www.gnu.org/licenses/>.

------------------------------------------------------------------------------------------------------------------------

This script downloads the LCRs for all sources listed in the 4FGL-DR4 catalog with the CLEAN flag.
"""

import os
import sys
from concurrent.futures import ThreadPoolExecutor
from json import JSONDecodeError

import pandas as pd
import pyLCR
from astropy.table import Table
from tqdm import tqdm

# Handle both relative and absolute imports
try:
    from .caching import CachedLightCurve
except ImportError:
    # If relative import fails, try absolute import
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from caching import CachedLightCurve

# The path to the cache folder
cache_folder = os.path.join("data", "cache", "LCRs") + os.sep

# Check if the cache folder exists. If not, create it.
if not os.path.exists(cache_folder):
    os.mkdir(cache_folder)


def format_src_name(name: bytes) -> str:
    """
    The 4FGL-DR4 catalog stores sources in binary format. Sometimes, the strings stored also end in a space, which must
    be removed before the string can be used to query the Fermi database API.
    :param name: The name of the source in binary format.
    :return: The name of the source in string format.
    """
    s = name.decode()
    return s.strip()


def download_cache_source(source: str, c_folder: str = cache_folder) -> None:
    """
    Download all data associated with a source using CachedLightCurve objects.
    The CachedLightCurve class handles caching, retries, and expiration automatically.
    :param source: The name of the source.
    :param c_folder: The path to the cache folder (unused now, but kept for compatibility).
    :return: None
    """
    # Check if source is available in pyLCR.sources
    if source not in pyLCR.sources:
        return

    # Iterate through possible combinations of cadence, flux_type, index_type, and ts_min.
    for cadence in ["daily", "weekly", "monthly"]:
        for flux_type in ["photon", "energy"]:
            for index_type in ["fixed", "free"]:
                for ts_min in [4]:
                    try:
                        # Use CachedLightCurve which handles caching, downloads, and retries automatically
                        CachedLightCurve(
                            source=source,
                            cadence=cadence,
                            flux_type=flux_type,
                            index_type=index_type,
                            ts_min=ts_min,
                            cache_uninitialized=True,
                            online=True,
                        )
                        # If we get here, the light curve was successfully loaded/downloaded and cached

                    except (JSONDecodeError, ValueError) as e:
                        # JSONDecodeError: Invalid request from Fermi API
                        # ValueError: Invalid parameters or source not in pyLCR.sources
                        if "Source not found in pyLCR.sources" in str(e):
                            return  # Source not available, skip all combinations
                        else:
                            break  # Invalid request, skip remaining combinations for this source
                    except IndexError as ie:
                        # Handle the specific case of empty sources
                        if "too many indices for array" in str(ie):
                            print(
                                f"Source {source} {cadence} {flux_type} {index_type} {ts_min} is empty. Skipping...\n",
                                end="",
                            )
                            return  # Source is empty, skip all combinations
                        else:
                            print(
                                f"IndexError for {source} {cadence} {flux_type} {index_type} {ts_min}: {ie}\n", end=""
                            )
                    except (FileNotFoundError, RuntimeError) as e:
                        # FileNotFoundError: Cache not found and online=False
                        # RuntimeError: All download attempts failed
                        print(
                            f"Failed to process {source} for {cadence} {flux_type} {index_type} {ts_min}: {e}\n", end=""
                        )
                    except Exception as e:
                        # Catch any other unexpected exceptions
                        print(
                            f"Unexpected error for {source} {cadence} {flux_type} {index_type} {ts_min}: {e}\n", end=""
                        )


if __name__ == "__main__":
    # Loading the 4FGL-DR4 catalog
    catalog_folder = os.path.join("data", "catalogs") + os.sep
    # Check if the catalog folder exists. If not, raise an error.
    if not os.path.exists(catalog_folder):
        raise FileNotFoundError(f"Catalog folder {catalog_folder} not found.")
    # The name of the catalog file
    catalog_name = "gll_psc_v32.fit"
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
    if not os.path.exists(cache_folder):
        os.mkdir(cache_folder)

    # Download the LCRs for all sources in the dataframe using multi-threading
    # Since ping is the bottleneck, no parallelization is needed.
    with ThreadPoolExecutor(max_workers=8) as executor:
        for _ in tqdm(executor.map(download_cache_source, df["Source_Name"].values), total=len(df["Source_Name"])):
            pass
