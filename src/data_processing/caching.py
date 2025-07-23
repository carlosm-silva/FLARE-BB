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

Warning: The class implemented in this file uses Python's pickle module to cache light curves. Therefore, it is subject
to the same security risks as pickle. See https://docs.python.org/3/library/pickle.html#security-and-pickle for more
info.
"""

import os
import pickle as pkl
from datetime import datetime, timedelta
from json import JSONDecodeError
from time import sleep
from typing import Tuple, Union
from warnings import warn

import pyLCR
from numba import jit
from numba.typed import List as TypedList

# The path to the cache folder
cache_folder = os.path.join("data", "cache", "LCRs") + os.sep


@jit(nopython=True, cache=True)
def check_substr_in_list_v2(substr: str, lst: TypedList[str]) -> Tuple[bool, str]:
    """
    Checks if a substring is in a list of strings. Returns the existence (bool) of the substring and the
    first string in the list that contains the substring, or "" if the substring is not in the list.
    :param substr: The substring to search for.
    :param lst: The list of strings to search.
    :return:
    """
    default_return = (False, "")
    for item in lst:
        if substr in item:
            return True, item
    return default_return


class CachedLightCurve(pyLCR.DataTools.LightCurve):
    """
    Extension of pyLCR.DataTools.LightCurve that adds the ability to cache light curves to disk.
    For more info on pyLCR see https://github.com/dankocevski/pyLCR.
    """

    folder_files = os.listdir(cache_folder)

    def __init__(
        self,
        source: str,
        cadence: str = "daily",
        flux_type: str = "photon",
        index_type: str = "fixed",
        ts_min: int = 4,
        cache_uninitialized: bool = True,
        online: bool = True,
        expires: Union[timedelta, float] = timedelta(days=9e5),
    ):
        """
        Initialize a CachedLightCurve object.
        :param source: The name of the source.
        :param cadence: The cadence of the light curve.
        :param flux_type: The flux type of the light curve.
        :param index_type: The index type of the light curve.
        :param ts_min: The ts_min of the light curve.
        :param cache_uninitialized: Whether to cache the light curve if it has not been cached before.
        :param online: Whether to download the light curve if it has not been downloaded before or if the cache has
        expired.
        :param expires: The time after which the cache expires. If the cache is older than this, it will be deleted.
        """
        super().__init__()

        self.source: str = source
        self.cache_uninitialized: bool = cache_uninitialized
        self.online: bool = online
        self.expires: timedelta = expires if isinstance(expires, timedelta) else timedelta(days=expires)
        # Check if the source is in pyLCR.sources (which are sure to be on the LAT LCR database).
        if online and self.source not in pyLCR.sources:
            raise ValueError("Source not found in pyLCR.sources. It might not be available in the Fermi database.")
        self.cadence: str = cadence
        if online and self.cadence not in ["daily", "weekly", "monthly"]:
            raise ValueError("Invalid cadence. Must be one of 'daily', 'weekly', or 'monthly'.")
        self.flux_type: str = flux_type
        if online and self.flux_type not in ["photon", "energy"]:
            raise ValueError("Invalid flux_type. Must be one of 'photon' or 'energy'.")
        self.index_type: str = index_type
        if online and self.index_type not in ["fixed", "free"]:
            raise ValueError("Invalid index_type. Must be one of 'fixed' or 'free'.")
        self.ts_min: int = ts_min

        self.file_name: str = self.get_cache_filename()
        # noinspection PyTypeChecker
        self.lc: pyLCR.DataTools.LightCurve = None

        # Check if the cache file exists.
        is_cached, self.file_name = check_substr_in_list_v2(self.file_name, TypedList(self.folder_files))
        if not is_cached:
            self.folder_files = os.listdir(cache_folder)
            is_cached, self.file_name = check_substr_in_list_v2(self.file_name, TypedList(self.folder_files))
        if is_cached:
            try:
                self.date = datetime.fromisoformat(self.file_name[-14:-4])
            except ValueError:  # There is no date information in the file name.
                # Get date from file creation time.
                self.date = datetime.fromtimestamp(os.path.getctime(os.path.join(cache_folder, self.file_name)))
            self.load_from_cache()
        elif online:
            self.file_name = self.get_cache_filename() + "_" + datetime.now().strftime("%Y-%m-%d") + ".pkl"
            self.load_from_lat_lcr()
            self.date = datetime.fromisoformat(datetime.now().strftime("%Y-%m-%d"))
        else:
            raise FileNotFoundError("Cache file not found.")

    def get_cache_filename(self) -> str:
        """
        Get the filename of the cache file for this light curve.
        :return: The filename of the cache file for this light curve.
        """
        return "_".join([self.source, self.cadence, self.flux_type, self.index_type, "tsmin" + str(self.ts_min)])

    def load_from_lightcurve(self, lc: pyLCR.DataTools.LightCurve) -> None:
        """
        Load the data from a pyLCR.DataTools.LightCurve object into this CachedLightCurve object.
        :param lc: The pyLCR.DataTools.LightCurve object to load data from.
        :return: None
        """
        self.lc: pyLCR.DataTools.LightCurve = lc
        for field, value in lc.__dict__.items():  # Iterate through all fields in the LightCurve object.
            setattr(self, field, value)

    def load_from_cache(self) -> None:
        """
        Load the data from the cache file into this CachedLightCurve object.
        :return: None
        """
        if self.date + self.expires > datetime.now() or not self.online:  # Check if the cache has expired.
            if not self.online:
                warn(f"Online mode is off, but cache has expired. Using cache anyway. ({self.file_name})", stacklevel=2)
            with open(os.path.join(cache_folder, self.file_name), "rb") as f:
                self.load_from_lightcurve(pkl.load(f))
        else:
            # Delete the cache file if it has expired.
            os.remove(os.path.join(cache_folder, self.file_name))
            self.file_name = self.get_cache_filename() + "_" + datetime.now().strftime("%Y-%m-%d") + ".pkl"
            self.load_from_lat_lcr()
            self.date = datetime.fromisoformat(datetime.now().strftime("%Y-%m-%d"))

    def load_from_lat_lcr(self) -> None:
        """
        Download the light curve from the Fermi LAT LCR database. Retries up to 5 times if the download fails.
        For more information on the Fermi LAT LCR database, see
        https://fermi.gsfc.nasa.gov/ssc/data/access/lat/LightCurveRepository/index.html
        :return: None
        """
        download_attempts = 0
        while download_attempts < 5:
            if download_attempts > 0:
                # Wait a bit in the event of a download failure. Waiting longer accounts for events such as a quick
                # internet outage, connecting to a VPN, etc.
                sleep(2**download_attempts)
            try:
                """
                This try block attempts to download the light curve from the Fermi LAT LCR database. The requests are
                made using pyLCR.getLightCurve, which returns a pyLCR.DataTools.LightCurve object.
                If the pyLCR.getLightCurve call fails, multiple outcomes are possible:
                1. If a JSONDecodeError or IndexError is raised, Fermi LAT LCR raised an error or pyLCR failed to parse
                    the data. In either case, we cannot download the light curve, so there's no point retrying.
                2. If any other exception is raised, the download failed for some other reason. We retry up to 5 times.
                3. If no exception is raised, but the pyLCR.getLightCurve call returns None, or a
                    py.LCR.DataTools.LightCurve object with a None source, one of the following happened: this
                    combination of source, cadence, flux_type, index_type, and ts_min is not available in the Fermi LAT
                    LCR database, or pyLCR caught an exception and decided to print it instead of raising it. Some of
                    the exceptions caught include exceptions related to connection error, therefore we should retry.
                """
                self.lc: pyLCR.DataTools.LightCurve = pyLCR.getLightCurve(
                    self.source,
                    cadence=self.cadence,
                    flux_type=self.flux_type,
                    index_type=self.index_type,
                    ts_min=self.ts_min,
                )
                # pyLCR catches some errors and returns None
                if self.lc is not None and self.lc.source is not None:
                    self.load_from_lightcurve(self.lc)
                    if self.cache_uninitialized:
                        self.save_to_cache()
                    return
                # Raise JsonDecodeError and Index Error. They imply something wrong with the data.
            except (JSONDecodeError, IndexError) as e:
                raise e
            except Exception as e:
                download_attempts += 1
                print(
                    f"[{str(datetime.now()).split('.')[0]}]"
                    f"Download failed for {self.source} for "
                    f"{self.cadence} {self.flux_type} {self.index_type} {self.ts_min}\n"
                    f"Raised error {e}\n",
                    end="",
                )
                # end="" behaves better with multi-threading than \n
        raise RuntimeError(
            f"Download failed for {self.source} for " f"{self.cadence} {self.flux_type} {self.index_type} {self.ts_min}"
        )

    def save_to_cache(self) -> None:
        """
        Save the data to the cache file.
        :return: None
        """
        with open(os.path.join(cache_folder, self.file_name), "wb") as f:
            pkl.dump(self.lc, f)
