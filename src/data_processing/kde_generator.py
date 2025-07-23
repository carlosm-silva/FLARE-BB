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


"""

import hashlib
import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional

import h5py
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde

# Handle both relative and absolute imports
try:
    from .caching import CachedLightCurve
except ImportError:
    # If relative import fails, try absolute import
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))


# Constants
# Declare the Test Statistic Threshold
TS_THRESHOLD = 19  # ~ 1/13k quantile

# Define the limits for the KDE
X_LOW = -4.9
X_HIGH = -2.8
Y_LOW = -5.35
Y_HIGH = -3.25

# Number of bins for the KDE
N_BINS = 512

# Bandwidth for the KDE
BANDWIDTH = 0.2

# Flux type
FLUX_TYPE = "energy"

# TS minimum
TS_MIN = 4

# Path to the catalogs
catalog_path = os.path.join("data", "cache", "catalog") + os.sep

# Path to the KDE data
KDE_PATH = os.path.join("data", "cache", "kde") + os.sep


def format_src_name(name: bytes) -> str:
    """
    :param name: The source name in bytes.
    :return: The source name in string format.
    """
    s = name.decode()  # 4FGL-DR4 catalog stores sources in binary format
    if s.endswith(
        " "
    ):  # Sometimes, the strings stored also end in a space, which must be removed before the string can be used to query the Fermi database API.
        s = s[:-1]
    return s.strip()  # Remove any extra spaces


def is_blazar(source_name: str, catalog_df: pd.DataFrame) -> bool:
    """
    :param source_name: The name of the source.
    :return: True if the source is a blazar, False otherwise.
    """
    if source_name in catalog_df["Source_Name"].values:
        # Get Source row
        src = catalog_df.loc[catalog_df["Source_Name"] == source_name]
        c1 = src["CLASS1"].values[0]
        c2 = src["CLASS2"].values[0]
        if c1.lower() in ["bll", "fsrq", "bcu"]:
            return True
        elif c2.lower() in ["bll", "fsrq", "bcu"]:
            return True
        return False
    else:
        return False


def compute_kde(
    data: np.ndarray,
    bandwidth: float = BANDWIDTH,
    nbins: int = N_BINS,
    x_low: float = X_LOW,
    x_high: float = X_HIGH,
    y_low: float = Y_LOW,
    y_high: float = Y_HIGH,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Computes a 2D Gaussian KDE over a specified grid.

    :param data: 2D array of shape (2, N) where N is the number of samples.
    :type data: np.ndarray
    :param bandwidth: Bandwidth for the KDE.
    :type bandwidth: float
    :param nbins: Number of bins for the grid in each dimension. Default is 512.
    :type nbins: int, optional
    :param x_low: Lower bound for the x-axis (log10 flux). Default is -4.9.
    :type x_low: float, optional
    :param x_high: Upper bound for the x-axis (log10 flux). Default is -2.8.
    :type x_high: float, optional
    :param y_low: Lower bound for the y-axis (log10 error). Default is -5.35.
    :type y_low: float, optional
    :param y_high: Upper bound for the y-axis (log10 error). Default is -3.25.
    :type y_high: float, optional

    :returns: Tuple containing:
        - points (np.ndarray): Array of grid points, shape (nbins*nbins, 2).
        - values (np.ndarray): Log KDE values at each grid point, shape (nbins*nbins,).
        - concatenated (np.ndarray): Array of shape (nbins*nbins, 3) with [x, y, log_kde_value].
    :rtype: tuple[np.ndarray, np.ndarray, np.ndarray]
    """
    k = gaussian_kde(data, bw_method=bandwidth)
    xi, yi = np.mgrid[x_low : x_high : nbins * 1j, y_low : y_high : nbins * 1j]
    zi = k(np.vstack([xi.flatten(), yi.flatten()]))
    points = np.vstack([xi.flatten(), yi.flatten()]).T
    values = np.log(zi)
    return points, values, np.concatenate([points, values[:, None]], axis=1)


def save_kde_data_with_metadata(
    kde_data: np.ndarray,
    points: np.ndarray,
    values: np.ndarray,
    parameters: Dict[str, Any],
    filepath: str,
    compression: str = "gzip",
) -> None:
    """
    Save KDE data with comprehensive metadata using HDF5 format.

    :param kde_data: Combined KDE data array with shape (nbins*nbins, 3)
    :type kde_data: np.ndarray
    :param points: Grid points array with shape (nbins*nbins, 2)
    :type points: np.ndarray
    :param values: Log KDE values array with shape (nbins*nbins,)
    :type values: np.ndarray
    :param parameters: Dictionary containing all parameters used for KDE generation
    :type parameters: Dict[str, Any]
    :param filepath: Path where to save the HDF5 file
    :type filepath: str
    :param compression: Compression method for HDF5 datasets. Default is "gzip"
    :type compression: str, optional
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with h5py.File(filepath, "w") as f:
        # Create groups for organization
        data_group = f.create_group("data")
        metadata_group = f.create_group("metadata")

        # Save the actual data with compression
        data_group.create_dataset("kde_data", data=kde_data, compression=compression)
        data_group.create_dataset("points", data=points, compression=compression)
        data_group.create_dataset("values", data=values, compression=compression)

        # Save metadata as attributes
        metadata_group.attrs["generation_timestamp"] = datetime.now().isoformat()
        metadata_group.attrs["kde_parameters"] = json.dumps(parameters)
        metadata_group.attrs["data_shapes"] = json.dumps(
            {"kde_data_shape": kde_data.shape, "points_shape": points.shape, "values_shape": values.shape}
        )
        metadata_group.attrs["file_format_version"] = "1.0"
        metadata_group.attrs["description"] = "KDE data for flux-error relationship in blazar light curves"

        # Add data integrity checksums
        metadata_group.attrs["kde_data_checksum"] = hashlib.md5(kde_data.tobytes()).hexdigest()
        metadata_group.attrs["points_checksum"] = hashlib.md5(points.tobytes()).hexdigest()
        metadata_group.attrs["values_checksum"] = hashlib.md5(values.tobytes()).hexdigest()


def load_kde_data_with_metadata(filepath: str) -> tuple[np.ndarray, np.ndarray, np.ndarray, Dict[str, Any]]:
    """
    Load KDE data with metadata from HDF5 file.

    :param filepath: Path to the HDF5 file
    :type filepath: str
    :returns: Tuple containing (kde_data, points, values, metadata)
    :rtype: tuple[np.ndarray, np.ndarray, np.ndarray, Dict[str, Any]]
    :raises FileNotFoundError: If the file doesn't exist
    :raises ValueError: If data integrity check fails
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"KDE data file not found: {filepath}")

    with h5py.File(filepath, "r") as f:
        # Load data
        kde_data = f["data/kde_data"][:]
        points = f["data/points"][:]
        values = f["data/values"][:]

        # Load metadata
        metadata = {}
        for key, value in f["metadata"].attrs.items():
            if key.endswith("_parameters") or key.endswith("_shapes"):
                metadata[key] = json.loads(value)
            else:
                metadata[key] = value

        # Verify data integrity if checksums are available
        if "kde_data_checksum" in metadata:
            if hashlib.md5(kde_data.tobytes()).hexdigest() != metadata["kde_data_checksum"]:
                raise ValueError("KDE data integrity check failed")
        if "points_checksum" in metadata:
            if hashlib.md5(points.tobytes()).hexdigest() != metadata["points_checksum"]:
                raise ValueError("Points data integrity check failed")
        if "values_checksum" in metadata:
            if hashlib.md5(values.tobytes()).hexdigest() != metadata["values_checksum"]:
                raise ValueError("Values data integrity check failed")

    return kde_data, points, values, metadata


def get_kde_generation_parameters() -> Dict[str, Any]:
    """
    Get all parameters used for KDE generation in a structured format.

    :returns: Dictionary containing all KDE generation parameters
    :rtype: Dict[str, Any]
    """
    return {
        "bandwidth": BANDWIDTH,
        "nbins": N_BINS,
        "x_low": X_LOW,
        "x_high": X_HIGH,
        "y_low": Y_LOW,
        "y_high": Y_HIGH,
        "ts_threshold": TS_THRESHOLD,
        "ts_min": TS_MIN,
        "flux_type": FLUX_TYPE,
        "grid_limits": {"x_range": [X_LOW, X_HIGH], "y_range": [Y_LOW, Y_HIGH]},
        "data_filtering": {"flags_filter": 0, "source_type": "blazar", "positive_errors_only": True},
    }


def generate_kde_filename(parameters: Dict[str, Any], base_path: str = KDE_PATH, file_extension: str = ".h5") -> str:
    """
    Generate a descriptive filename that encodes key KDE parameters.

    :param parameters: Dictionary containing KDE generation parameters
    :type parameters: Dict[str, Any]
    :param base_path: Base directory path for the file
    :type base_path: str
    :param file_extension: File extension (default: ".h5")
    :type file_extension: str
    :returns: Full path with descriptive filename
    :rtype: str

    Example filename: kde_bw0.2_n512_ts19_flux-energy_x-4.9to-2.8_y-5.35to-3.25.h5
    """
    # Extract key parameters for filename
    bandwidth = parameters["bandwidth"]
    nbins = parameters["nbins"]
    ts_threshold = parameters["ts_threshold"]
    flux_type = parameters["flux_type"]
    x_low = parameters["x_low"]
    x_high = parameters["x_high"]
    y_low = parameters["y_low"]
    y_high = parameters["y_high"]

    # Create descriptive filename components
    filename_parts = [
        "kde",
        f"bw{bandwidth}",
        f"n{nbins}",
        f"ts{ts_threshold}",
        f"flux-{flux_type}",
        f"x{x_low}to{x_high}",
        f"y{y_low}to{y_high}",
    ]

    # Join with underscores and add extension
    filename = "_".join(filename_parts) + file_extension

    return os.path.join(base_path, filename)


def run_kde_generation(
    stacked_data: np.ndarray, custom_params: Dict[str, Any] = None, output_dir: str = None, verbose: bool = True
) -> Optional[str]:
    """
    Run KDE generation with specified parameters and data.

    :param stacked_data: 2D array of flux-error data, shape (2, N)
    :type stacked_data: np.ndarray
    :param custom_params: Custom parameters to override defaults
    :type custom_params: Dict[str, Any], optional
    :param output_dir: Output directory (default: KDE_PATH)
    :type output_dir: str, optional
    :param verbose: Whether to print progress information
    :type verbose: bool
    :returns: Path to generated file, or None if failed
    :rtype: Optional[str]
    """
    if verbose:
        print("🔬 KDE Generation Workflow")
        print("=" * 60)

    # Get base parameters and apply any customizations
    parameters = get_kde_generation_parameters()
    if custom_params:
        parameters.update(custom_params)
        if verbose:
            print(f"📝 Applied custom parameters: {custom_params}")

    if verbose:
        print("⚙️  Using parameters:")
        for key, value in parameters.items():
            if not isinstance(value, dict):  # Skip nested dictionaries for cleaner output
                print(f"   • {key}: {value}")

    # Generate output filename
    base_path = output_dir if output_dir else KDE_PATH
    output_file = generate_kde_filename(parameters, base_path=base_path)

    if verbose:
        print(f"\n📁 Output file: {os.path.basename(output_file)}")

    # Check if file already exists
    if os.path.exists(output_file):
        if verbose:
            print("⚠️  File already exists - this demonstrates no-overwrite protection!")
        return output_file

    if verbose:
        print(f"\n📊 Processing {stacked_data.shape[1]} data points...")

    # Apply parameter-based filtering
    x_mask = (stacked_data[0] >= parameters["x_low"]) & (stacked_data[0] <= parameters["x_high"])
    y_mask = (stacked_data[1] >= parameters["y_low"]) & (stacked_data[1] <= parameters["y_high"])
    mask = x_mask & y_mask

    filtered_data = stacked_data[:, mask]

    if verbose:
        print(f"   • After range filtering: {filtered_data.shape[1]} points")

    if filtered_data.shape[1] < 10:
        if verbose:
            print("❌ Insufficient data points after filtering!")
        return None

    # Compute KDE
    if verbose:
        print("\n🧮 Computing KDE (this may take a moment)...")
        print(f"   • Grid size: {parameters['nbins']}x{parameters['nbins']}")
        print(f"   • Bandwidth: {parameters['bandwidth']}")

    points, values, kde_data = compute_kde(
        filtered_data,
        bandwidth=parameters["bandwidth"],
        nbins=parameters["nbins"],
        x_low=parameters["x_low"],
        x_high=parameters["x_high"],
        y_low=parameters["y_low"],
        y_high=parameters["y_high"],
    )

    if verbose:
        print("   ✅ KDE computation complete!")
        print(f"   • Output shapes: kde_data{kde_data.shape}, points{points.shape}, values{values.shape}")

    # Save with metadata
    if verbose:
        print("\n💾 Saving KDE data with metadata...")

    save_kde_data_with_metadata(kde_data, points, values, parameters, output_file, compression="gzip")

    if verbose:
        print(f"   ✅ Saved to: {output_file}")
        print("   • File includes complete parameter metadata")
        print("   • Data integrity checksums included")
        print("   • Generation timestamp recorded")

    return output_file


def create_sample_data(n_points: int = 1000) -> np.ndarray:
    """
    Create sample flux-error data for demonstration purposes.
    In real usage, this would come from your blazar analysis pipeline.

    :param n_points: Number of data points to generate
    :type n_points: int
    :returns: 2D array with flux and error data
    :rtype: np.ndarray
    """
    # Generate realistic-looking log flux and log error data
    np.random.seed(42)  # For reproducible results

    # Log flux values (typical range for gamma-ray sources)
    log_flux = np.random.uniform(-4.5, -3.0, n_points)

    # Log errors (correlated with flux but with some scatter)
    log_error = log_flux + np.random.normal(0, 0.3, n_points) - 1.0

    return np.vstack([log_flux, log_error])


# Example usage - can be called from scripts for demonstration
if __name__ == "__main__":
    # This is just for testing the core functions
    print("🧪 Testing KDE generation functions...")

    # Generate sample data
    sample_data = create_sample_data(n_points=500)
    print(f"Created sample data: {sample_data.shape}")

    # Test filename generation
    params = get_kde_generation_parameters()
    filename = generate_kde_filename(params)
    print(f"Generated filename: {os.path.basename(filename)}")

    print("\n💡 For actual KDE generation, use: python scripts/generate_kde.py")
