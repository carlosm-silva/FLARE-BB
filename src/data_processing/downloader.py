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
import pickle as pkl
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from json import JSONDecodeError
from time import sleep

import pandas as pd
import pyLCR
from astropy.table import Table
from tqdm import tqdm

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
    Download all data associated with a source and save it to a cache folder.
    :param source: The name of the source.
    :param c_folder: The path to the cache folder.
    :return: None
    """
    # Iterate through possible combinations of cadence, flux_type, index_type, and ts_min.
    if source not in pyLCR.sources:
        return
    for cadence in ["daily", "weekly", "monthly"]:
        for flux_type in ["photon", "energy"]:
            for index_type in ["fixed", "free"]:
                for ts_min in [4]:
                    download_attempts = 0
                    while download_attempts < 4:  # Try to download the data 4 times.
                        if download_attempts > 0:  # If the download fails, wait 2^download_attempts seconds.
                            sleep(2**download_attempts)
                        try:
                            lcr = pyLCR.getLightCurve(
                                source, cadence=cadence, flux_type=flux_type, index_type=index_type, ts_min=ts_min
                            )
                            # If pyLCR catches an error, it will return a LightCurve object with source=None.
                            if lcr is not None and lcr.source is not None:
                                file_name = (
                                    "_".join([source, cadence, flux_type, index_type, "tsmin" + str(ts_min)]) + ".pkl"
                                )
                                with open(os.path.join(c_folder, file_name), "wb") as f:
                                    pkl.dump(lcr, f)
                                break
                        except JSONDecodeError:  # JSONDecodeError is raised when the request is invalid.
                            break
                        except IndexError as ie:
                            # The error:
                            # IndexError: too many indices for array: array is 1-dimensional, but 2 were index.
                            # is raised when the source is empty.
                            if "too many indices for array" in str(ie):
                                print(f"Source {source} is empty. Skipping...")
                                break
                            else:
                                raise ie
                        except Exception as e:
                            download_attempts += 1
                            print(
                                f"[{str(datetime.now()).split('.')[0]}]"
                                f"Download failed for {source} for {cadence} {flux_type} {index_type} {ts_min}\n"
                                f"Raised error {e}\n",
                                end="",
                            )
                            # end="" behaves better with multi-threading than \n


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
