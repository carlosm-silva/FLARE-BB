"""Fermi catalog helpers used by FLARE-BB pipelines."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import numpy as np
from numpy.typing import NDArray
import pandas as pd

from flare_bb.core.config import KdeConfig
from flare_bb.io.lcr import LightCurveRequest, load_light_curve

BLAZAR_CLASSES = frozenset({"bll", "fsrq", "bcu"})


def format_source_name(name: bytes | str) -> str:
    """Normalize source names from FITS byte strings or regular strings.

    Parameters
    ----------
    name : bytes | str
        Source name value.

    Returns
    -------
    str
        Stripped source name.
    """
    if isinstance(name, bytes):
        return name.decode().strip()
    return name.strip()


def is_blazar(source_name: str, catalog: pd.DataFrame) -> bool:
    """Return whether a catalog source is classified as a blazar.

    Parameters
    ----------
    source_name : str
        Source name.
    catalog : pd.DataFrame
        Catalog containing ``Source_Name``, ``CLASS1``, and ``CLASS2``.

    Returns
    -------
    bool
        True if the source is a BLL, FSRQ, or BCU object.
    """
    source_rows = catalog.loc[catalog["Source_Name"] == source_name]
    if source_rows.empty:
        return False
    source = source_rows.iloc[0]
    class_1 = str(source["CLASS1"]).lower()
    class_2 = str(source["CLASS2"]).lower()
    return class_1 in BLAZAR_CLASSES or class_2 in BLAZAR_CLASSES


def load_fermi_catalog(path: Path) -> pd.DataFrame:
    """Load and clean a Fermi-LAT 4FGL catalog.

    Parameters
    ----------
    path : Path
        FITS catalog path.

    Returns
    -------
    pd.DataFrame
        Clean source catalog restricted to rows with ``Flags == 0``.
    """
    try:
        from astropy.table import Table
    except ImportError as error:  # pragma: no cover - exercised only without optional dependency
        raise ImportError("astropy is required to load Fermi catalog FITS files.") from error

    table = Table.read(path, format="fits", hdu=1)
    column_names = [name for name in table.colnames if len(table[name].shape) <= 1]
    catalog = table[column_names].to_pandas()
    clean_catalog = catalog.loc[(catalog["Flags"] == 0).astype(bool)].copy()
    for column in ("Source_Name", "CLASS1", "CLASS2"):
        clean_catalog[column] = clean_catalog[column].apply(format_source_name)
    return cast("pd.DataFrame", clean_catalog)


def extract_blazar_flux_data(
    catalog: pd.DataFrame,
    sources: list[str],
    cache_dir: Path,
    config: KdeConfig,
) -> NDArray[np.float64]:
    """Extract stacked log flux/error data for blazar light curves.

    Parameters
    ----------
    catalog : pd.DataFrame
        Clean Fermi source catalog.
    sources : list[str]
        pyLCR source names to consider.
    cache_dir : Path
        Light-curve cache directory.
    config : KdeConfig
        KDE configuration controlling flux type and TS cuts.

    Returns
    -------
    NDArray[np.float64]
        Stacked log flux/error data with shape ``(2, n_samples)``.
    """
    fluxes: list[NDArray[np.float64]] = []
    uncertainties: list[NDArray[np.float64]] = []
    for source in sources:
        if not is_blazar(source, catalog):
            continue
        light_curve = load_light_curve(
            LightCurveRequest(source=source, flux_type=config.flux_type, ts_min=config.ts_min),
            cache_dir=cache_dir,
        )
        source_fluxes, source_uncertainties = extract_light_curve_flux_data(light_curve, config.ts_threshold)
        if source_fluxes.size > 0:
            fluxes.append(source_fluxes)
            uncertainties.append(source_uncertainties)

    if not fluxes:
        raise ValueError("No valid blazar flux data found.")
    flux = np.concatenate(fluxes)
    uncertainty = np.concatenate(uncertainties)
    positive_uncertainty = uncertainty > 0
    return np.vstack([np.log10(flux[positive_uncertainty]), np.log10(uncertainty[positive_uncertainty])]).astype(
        np.float64
    )


def extract_light_curve_flux_data(
    light_curve: Any, ts_threshold: int
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Extract flux and upper uncertainty values from a pyLCR light curve.

    Parameters
    ----------
    light_curve : Any
        pyLCR light-curve object.
    ts_threshold : int
        Minimum test statistic to retain.

    Returns
    -------
    tuple[NDArray[np.float64], NDArray[np.float64]]
        Flux and uncertainty arrays.
    """
    met_index = {value: index for index, value in enumerate(light_curve.met)}
    detection_indexes = np.asarray([met_index[value] for value in light_curve.met_detections], dtype=int)
    full_test_statistic = np.asarray(light_curve.ts, dtype=np.float64)
    test_statistic = (
        full_test_statistic[detection_indexes]
        if full_test_statistic.shape[0] != detection_indexes.shape[0]
        else full_test_statistic
    )
    full_flux = np.asarray(light_curve.flux, dtype=np.float64)
    flux_error = np.asarray(light_curve.flux_error, dtype=np.float64)
    flux = full_flux[detection_indexes] if full_flux.shape[0] != detection_indexes.shape[0] else full_flux
    selected_flux_error = (
        flux_error[detection_indexes] if flux_error.shape[0] != detection_indexes.shape[0] else flux_error
    )
    upper_uncertainty = selected_flux_error[:, 1] - flux
    high_ts_mask = test_statistic > ts_threshold
    return flux[high_ts_mask], upper_uncertainty[high_ts_mask]
