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
# ----------------------------------------------------------------------------------------------------------------------
#
# Utility functions for flux distribution building and management.
#

import datetime
import os
from typing import Any, Dict, List, Optional, Tuple

import h5py
import numpy as np

from .distribution_builder import DistributionResult
from .distribution_config import DEFAULT_CONFIG, DistributionConfig


def create_distribution_filename(
    config: DistributionConfig, kde_metadata: Optional[Dict[str, Any]] = None, prefix: str = "flux_dist"
) -> str:
    """
    Create a descriptive filename for distribution data files.

    Following the repository pattern of parameter-encoded filenames for
    easy identification and avoiding overwrites.

    :param config: Distribution configuration
    :type config: DistributionConfig
    :param kde_metadata: Optional KDE metadata for additional context
    :type kde_metadata: Optional[Dict[str, Any]]
    :param prefix: Filename prefix
    :type prefix: str
    :returns: Formatted filename
    :rtype: str
    """
    # Base parameters from configuration
    parts = [
        f"hd-res{config.high_definition_resolution}",
        f"ml-res{config.marginal_likelihood_resolution}",
        f"ml-interp{config.marginal_likelihood_interp_points}",
        f"bins{config.final_grid_bins}",
        f"flux{config.flux_range_min}to{config.flux_range_max}",
        f"ext{config.marginal_likelihood_range_extension}",
    ]

    # Add KDE information if available
    if kde_metadata and "kde_parameters" in kde_metadata:
        kde_params = kde_metadata["kde_parameters"]
        parts.extend(
            [
                f"kde-bw{kde_params.get('bandwidth', 'unk')}",
                f"n{kde_params.get('nbins', 'unk')}",
                f"ts{kde_params.get('ts_threshold', 'unk')}",
            ]
        )

    # Join with underscores and add extension
    filename = f"{prefix}_{'_'.join(parts)}.h5"

    return filename


def validate_distribution_parameters(config: DistributionConfig) -> Tuple[bool, List[str]]:
    """
    Validate distribution configuration parameters and return detailed results.

    :param config: Configuration to validate
    :type config: DistributionConfig
    :returns: Tuple of (is_valid, list_of_error_messages)
    :rtype: Tuple[bool, List[str]]
    """
    errors = []

    try:
        config.validate()
        return True, []
    except ValueError as e:
        errors.append(str(e))
        return False, errors


def save_distribution_data(
    result: DistributionResult,
    filepath: str,
    kde_metadata: Optional[Dict[str, Any]] = None,
    description: Optional[str] = None,
) -> None:
    """
    Save distribution results to HDF5 file with comprehensive metadata.

    :param result: Distribution calculation results
    :type result: DistributionResult
    :param filepath: Output file path
    :type filepath: str
    :param kde_metadata: Optional metadata from source KDE
    :type kde_metadata: Optional[Dict[str, Any]]
    :param description: Optional description of the calculation
    :type description: Optional[str]
    :raises OSError: If file cannot be written
    """
    # Ensure output directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with h5py.File(filepath, "w") as f:
        # Save main data arrays
        f.create_dataset("posterior_pdf_grid", data=result.posterior_pdf_grid, compression="gzip")
        f.create_dataset("flux_range", data=result.flux_range, compression="gzip")
        f.create_dataset("log_measured_flux_grid", data=result.log_measured_flux_grid, compression="gzip")
        f.create_dataset("log_measured_uncertainty_grid", data=result.log_measured_uncertainty_grid, compression="gzip")
        f.create_dataset("log_posterior_pdf_grid", data=result.log_posterior_pdf_grid, compression="gzip")

        # Save metadata
        metadata_group = f.create_group("metadata")

        # Distribution metadata
        metadata_group.attrs["generation_timestamp"] = datetime.datetime.now().isoformat()
        metadata_group.attrs["file_format_version"] = "1.0"
        metadata_group.attrs["data_type"] = "flux_distributions"

        if description:
            metadata_group.attrs["description"] = description

        # Configuration parameters
        config_group = metadata_group.create_group("distribution_config")
        config_group.attrs["high_definition_resolution"] = result.config.high_definition_resolution
        config_group.attrs["marginal_likelihood_resolution"] = result.config.marginal_likelihood_resolution
        config_group.attrs["marginal_likelihood_interp_points"] = result.config.marginal_likelihood_interp_points
        config_group.attrs["final_grid_bins"] = result.config.final_grid_bins
        config_group.attrs["flux_range_min"] = result.config.flux_range_min
        config_group.attrs["flux_range_max"] = result.config.flux_range_max
        config_group.attrs["marginal_likelihood_range_extension"] = result.config.marginal_likelihood_range_extension
        config_group.attrs["numerical_epsilon"] = result.config.numerical_epsilon
        config_group.attrs["interpolation_method"] = result.config.interpolation_method

        # Source KDE metadata if available
        if kde_metadata:
            kde_group = metadata_group.create_group("source_kde")
            for key, value in kde_metadata.items():
                if isinstance(value, dict):
                    subgroup = kde_group.create_group(key)
                    for subkey, subvalue in value.items():
                        # Handle different data types for HDF5 compatibility
                        if isinstance(subvalue, (str, int, float, bool)):
                            subgroup.attrs[subkey] = subvalue
                        elif isinstance(subvalue, (list, tuple)):
                            # Convert lists/tuples to numpy arrays
                            subgroup.attrs[subkey] = np.array(subvalue)
                        elif isinstance(subvalue, np.ndarray):
                            subgroup.attrs[subkey] = subvalue
                        else:
                            # Convert other types to string representation
                            subgroup.attrs[subkey] = str(subvalue)
                else:
                    # Handle top-level values
                    if isinstance(value, (str, int, float, bool)):
                        kde_group.attrs[key] = value
                    elif isinstance(value, (list, tuple)):
                        kde_group.attrs[key] = np.array(value)
                    elif isinstance(value, np.ndarray):
                        kde_group.attrs[key] = value
                    else:
                        kde_group.attrs[key] = str(value)

        # Data shape information
        shape_group = metadata_group.create_group("data_shapes")
        shape_group.attrs["posterior_pdf_grid_shape"] = result.posterior_pdf_grid.shape
        shape_group.attrs["flux_range_length"] = len(result.flux_range)
        shape_group.attrs["grid_resolution"] = result.log_measured_flux_grid.shape


def load_distribution_data(filepath: str) -> Tuple[DistributionResult, Dict[str, Any]]:
    """
    Load distribution data from HDF5 file with metadata.

    :param filepath: Path to distribution file
    :type filepath: str
    :returns: Tuple of (distribution_result, metadata)
    :rtype: Tuple[DistributionResult, Dict[str, Any]]
    :raises FileNotFoundError: If file doesn't exist
    :raises ValueError: If file format is invalid
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Distribution file not found: {filepath}")

    with h5py.File(filepath, "r") as f:
        # Load main data arrays
        posterior_pdf_grid = f["posterior_pdf_grid"][:]
        flux_range = f["flux_range"][:]
        log_measured_flux_grid = f["log_measured_flux_grid"][:]
        log_measured_uncertainty_grid = f["log_measured_uncertainty_grid"][:]
        log_posterior_pdf_grid = f["log_posterior_pdf_grid"][:]

        # Load metadata
        metadata = {}
        if "metadata" in f:
            metadata_group = f["metadata"]

            # Load attributes
            for key in metadata_group.attrs:
                metadata[key] = metadata_group.attrs[key]

            # Load configuration
            if "distribution_config" in metadata_group:
                config_group = metadata_group["distribution_config"]
                config = DistributionConfig(
                    high_definition_resolution=config_group.attrs["high_definition_resolution"],
                    marginal_likelihood_resolution=config_group.attrs["marginal_likelihood_resolution"],
                    marginal_likelihood_interp_points=config_group.attrs["marginal_likelihood_interp_points"],
                    final_grid_bins=config_group.attrs["final_grid_bins"],
                    flux_range_min=config_group.attrs["flux_range_min"],
                    flux_range_max=config_group.attrs["flux_range_max"],
                    marginal_likelihood_range_extension=config_group.attrs["marginal_likelihood_range_extension"],
                    numerical_epsilon=config_group.attrs["numerical_epsilon"],
                    interpolation_method=(
                        config_group.attrs["interpolation_method"].decode()
                        if isinstance(config_group.attrs["interpolation_method"], bytes)
                        else config_group.attrs["interpolation_method"]
                    ),
                )
            else:
                config = DEFAULT_CONFIG

            # Load source KDE metadata if available
            if "source_kde" in metadata_group:
                kde_metadata = {}
                kde_group = metadata_group["source_kde"]
                for key in kde_group.attrs:
                    value = kde_group.attrs[key]
                    # Convert bytes to string if needed
                    if isinstance(value, bytes):
                        kde_metadata[key] = value.decode()
                    else:
                        kde_metadata[key] = value

                for subgroup_name in kde_group.keys():
                    subgroup = kde_group[subgroup_name]
                    subgroup_dict = {}
                    for attr_key in subgroup.attrs:
                        attr_value = subgroup.attrs[attr_key]
                        # Convert bytes to string if needed
                        if isinstance(attr_value, bytes):
                            subgroup_dict[attr_key] = attr_value.decode()
                        else:
                            subgroup_dict[attr_key] = attr_value
                    kde_metadata[subgroup_name] = subgroup_dict
                metadata["source_kde"] = kde_metadata
        else:
            config = DEFAULT_CONFIG

        # Create result object
        result = DistributionResult(
            posterior_pdf_grid=posterior_pdf_grid,
            flux_range=flux_range,
            log_measured_flux_grid=log_measured_flux_grid,
            log_measured_uncertainty_grid=log_measured_uncertainty_grid,
            log_posterior_pdf_grid=log_posterior_pdf_grid,
            config=config,
        )

        return result, metadata


def list_distribution_files(directory: str = None) -> List[str]:
    """
    List all distribution files in the specified directory.

    :param directory: Directory to search (default: data/cache/distributions)
    :type directory: str, optional
    :returns: List of distribution file paths
    :rtype: List[str]
    """
    if directory is None:
        directory = os.path.join("data", "cache", "distributions")

    if not os.path.exists(directory):
        return []

    distribution_files = []
    for filename in os.listdir(directory):
        if filename.startswith("flux_dist") and filename.endswith(".h5"):
            distribution_files.append(os.path.join(directory, filename))

    return sorted(distribution_files)


def find_distribution_by_parameters(
    target_config: DistributionConfig, directory: str = None, tolerance: float = 1e-6
) -> Optional[str]:
    """
    Find a distribution file matching the specified configuration parameters.

    :param target_config: Configuration to match
    :type target_config: DistributionConfig
    :param directory: Directory to search
    :type directory: str, optional
    :param tolerance: Numerical tolerance for floating-point comparisons
    :type tolerance: float
    :returns: Path to matching file, or None if not found
    :rtype: Optional[str]
    """
    distribution_files = list_distribution_files(directory)

    for filepath in distribution_files:
        try:
            _, metadata = load_distribution_data(filepath)

            if "distribution_config" in metadata:
                file_config = metadata["distribution_config"]

                # Compare key parameters
                if (
                    file_config.get("high_definition_resolution") == target_config.high_definition_resolution
                    and file_config.get("marginal_likelihood_resolution")
                    == target_config.marginal_likelihood_resolution
                    and file_config.get("marginal_likelihood_interp_points")
                    == target_config.marginal_likelihood_interp_points
                    and file_config.get("final_grid_bins") == target_config.final_grid_bins
                    and abs(file_config.get("flux_range_min", 0) - target_config.flux_range_min) < tolerance
                    and abs(file_config.get("flux_range_max", 0) - target_config.flux_range_max) < tolerance
                    and abs(
                        file_config.get("marginal_likelihood_range_extension", 0)
                        - target_config.marginal_likelihood_range_extension
                    )
                    < tolerance
                    and file_config.get("interpolation_method") == target_config.interpolation_method
                ):
                    return filepath

        except (OSError, ValueError, KeyError):
            # Skip files that can't be read or have invalid format
            continue

    return None


def examine_distribution_data(filepath: str) -> Dict[str, Any]:
    """
    Examine and summarize distribution file contents.

    :param filepath: Path to distribution file
    :type filepath: str
    :returns: Summary information about the file
    :rtype: Dict[str, Any]
    :raises FileNotFoundError: If file doesn't exist
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Distribution file not found: {filepath}")

    result, metadata = load_distribution_data(filepath)

    summary = {
        "filepath": filepath,
        "file_size_mb": os.path.getsize(filepath) / (1024 * 1024),
        "data_shapes": {
            "posterior_pdf_grid": result.posterior_pdf_grid.shape,
            "flux_range": result.flux_range.shape,
            "measured_grids": result.log_measured_flux_grid.shape,
        },
        "flux_range_actual": {
            "min": float(result.flux_range.min()),
            "max": float(result.flux_range.max()),
            "points": len(result.flux_range),
        },
        "measured_ranges": {
            "flux": {
                "min": float(result.log_measured_flux_grid.min()),
                "max": float(result.log_measured_flux_grid.max()),
            },
            "uncertainty": {
                "min": float(result.log_measured_uncertainty_grid.min()),
                "max": float(result.log_measured_uncertainty_grid.max()),
            },
        },
        "configuration": {
            "hd_resolution": result.config.high_definition_resolution,
            "marginal_likelihood_resolution": result.config.marginal_likelihood_resolution,
            "final_bins": result.config.final_grid_bins,
            "interpolation": result.config.interpolation_method,
        },
        "metadata": metadata,
    }

    return summary


def get_distribution_summary(directory: str = None) -> Dict[str, Any]:
    """
    Get a summary of all distribution files in the directory.

    :param directory: Directory to search
    :type directory: str, optional
    :returns: Summary of all distribution files
    :rtype: Dict[str, Any]
    """
    distribution_files = list_distribution_files(directory)

    summary = {
        "directory": directory or os.path.join("data", "cache", "distributions"),
        "total_files": len(distribution_files),
        "files": [],
    }

    for filepath in distribution_files:
        try:
            file_summary = examine_distribution_data(filepath)
            summary["files"].append(
                {
                    "filename": os.path.basename(filepath),
                    "size_mb": file_summary["file_size_mb"],
                    "flux_range": file_summary["flux_range_actual"],
                    "grid_resolution": file_summary["configuration"]["final_bins"],
                    "generation_time": file_summary["metadata"].get("generation_timestamp", "Unknown"),
                }
            )
        except (OSError, ValueError):
            # Skip files that can't be read
            summary["files"].append(
                {"filename": os.path.basename(filepath), "status": "error", "error": "Could not read file"}
            )

    return summary


def ensure_distribution_cache_directory(directory: str = None) -> str:
    """
    Ensure the distribution cache directory exists and return its path.

    :param directory: Custom directory path
    :type directory: str, optional
    :returns: Path to the cache directory
    :rtype: str
    """
    if directory is None:
        directory = os.path.join("data", "cache", "distributions")

    os.makedirs(directory, exist_ok=True)
    return directory


def compare_distribution_configs(config1: DistributionConfig, config2: DistributionConfig) -> Dict[str, Any]:
    """
    Compare two distribution configurations and highlight differences.

    :param config1: First configuration
    :type config1: DistributionConfig
    :param config2: Second configuration
    :type config2: DistributionConfig
    :returns: Comparison results
    :rtype: Dict[str, Any]
    """
    comparison = {"identical": True, "differences": []}

    # Define fields to compare
    fields = [
        "high_definition_resolution",
        "marginal_likelihood_resolution",
        "marginal_likelihood_interp_points",
        "final_grid_bins",
        "flux_range_min",
        "flux_range_max",
        "marginal_likelihood_range_extension",
        "numerical_epsilon",
        "interpolation_method",
    ]

    for field in fields:
        val1 = getattr(config1, field)
        val2 = getattr(config2, field)

        if val1 != val2:
            comparison["identical"] = False
            comparison["differences"].append({"field": field, "config1": val1, "config2": val2})

    return comparison
