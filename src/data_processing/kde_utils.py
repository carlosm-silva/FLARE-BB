"""
SPDX-License-Identifier: GPL-3.0-or-later
FLARE-BB – Bayesian Blocks algorithm for detecting gamma-ray flares
Copyright © 2025 Carlos Márcio de Oliveira e Silva Filho
Copyright © 2025 Ignacio Taboada

Utility functions for KDE data management, loading, and examination.
"""

import glob
import os
from pprint import pprint
from typing import Any, Dict, List, Optional

import numpy as np

# Handle both relative and absolute imports
try:
    from .kde_generator import load_kde_data_with_metadata
except ImportError:
    import sys

    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from kde_generator import load_kde_data_with_metadata


def list_kde_files(kde_dir: str, pattern: str = "kde_*.h5") -> List[str]:
    """
    List all KDE data files in a given directory.

    :param kde_dir: The directory to search
    :type kde_dir: str
    :param pattern: The filename pattern to match (default: "kde_*.h5")
    :type pattern: str
    :returns: A list of full paths to the matching files
    :rtype: List[str]
    """
    if not os.path.exists(kde_dir):
        return []

    # Look for both old and new format files
    kde_files = glob.glob(os.path.join(kde_dir, pattern))
    kde_files.extend(glob.glob(os.path.join(kde_dir, "log_kde_data.h5")))  # Legacy format

    return sorted(list(set(kde_files)))  # Remove duplicates and sort


def decode_filename(filepath: str) -> Dict[str, Any]:
    """
    Decode parameters from a KDE filename.

    :param filepath: Path to the KDE file
    :type filepath: str
    :returns: Dictionary of decoded parameters
    :rtype: Dict[str, Any]
    """
    filename = os.path.basename(filepath)
    if filename == "log_kde_data.h5":
        return {"format": "legacy", "note": "Use metadata for parameters"}

    # Remove extension
    name_parts = filename.replace(".h5", "").split("_")

    decoded = {"format": "descriptive"}

    for part in name_parts:
        if part.startswith("bw"):
            decoded["bandwidth"] = float(part[2:])
        elif part.startswith("n") and part[1:].isdigit():
            decoded["nbins"] = int(part[1:])
        elif part.startswith("ts"):
            decoded["ts_threshold"] = int(part[2:])
        elif part.startswith("flux-"):
            decoded["flux_type"] = part[5:]
        elif part.startswith("x"):
            decoded["x_range"] = part[1:]
        elif part.startswith("y"):
            decoded["y_range"] = part[1:]

    return decoded


def find_kde_by_parameters(target_params: Dict[str, Any], kde_dir: str) -> Optional[str]:
    """
    Find a KDE file that matches specific parameters.

    :param target_params: Dictionary of parameters to match
    :type target_params: Dict[str, Any]
    :param kde_dir: Directory to search
    :type kde_dir: str
    :returns: Path to matching file, or None if not found
    :rtype: Optional[str]
    """
    kde_files = list_kde_files(kde_dir)

    for filepath in kde_files:
        try:
            _, _, _, metadata = load_kde_data_with_metadata(filepath)
            stored_params = metadata.get("kde_parameters", {})

            # Check if all target parameters match
            match = True
            for key, value in target_params.items():
                if stored_params.get(key) != value:
                    match = False
                    break

            if match:
                return filepath

        except Exception:
            continue  # Skip files that can't be loaded

    return None


def examine_kde_data(filepath: str, verbose: bool = True) -> Dict[str, Any]:
    """
    Load and examine KDE data with metadata.

    :param filepath: Path to the HDF5 KDE data file
    :type filepath: str
    :param verbose: Whether to print detailed information
    :type verbose: bool
    :returns: Dictionary containing examination results
    :rtype: Dict[str, Any]
    """
    results = {"filepath": filepath, "filename": os.path.basename(filepath), "success": False, "error": None}

    if verbose:
        print(f"Loading KDE data from: {results['filename']}")
        print("=" * 60)

    # Show filename decoding
    decoded = decode_filename(filepath)
    results["decoded_filename"] = decoded

    if verbose and decoded["format"] == "descriptive":
        print("📁 Filename Parameters:")
        for key, value in decoded.items():
            if key != "format":
                print(f"  • {key}: {value}")
        print()

    try:
        kde_data, points, values, metadata = load_kde_data_with_metadata(filepath)

        results.update(
            {
                "success": True,
                "kde_data_shape": kde_data.shape,
                "points_shape": points.shape,
                "values_shape": values.shape,
                "data_types": [kde_data.dtype, points.dtype, values.dtype],
                "metadata": metadata,
                "data_summary": {
                    "kde_values_range": [float(np.min(values)), float(np.max(values))],
                    "points_x_range": [float(np.min(points[:, 0])), float(np.max(points[:, 0]))],
                    "points_y_range": [float(np.min(points[:, 1])), float(np.max(points[:, 1]))],
                },
            }
        )

        if verbose:
            print("📊 Data Arrays:")
            print(f"  • KDE Data shape: {kde_data.shape}")
            print(f"  • Points shape: {points.shape}")
            print(f"  • Values shape: {values.shape}")
            print(f"  • Data types: {kde_data.dtype}, {points.dtype}, {values.dtype}")

            print("\n📋 Metadata:")
            print(f"  • Generation timestamp: {metadata.get('generation_timestamp', 'N/A')}")
            print(f"  • File format version: {metadata.get('file_format_version', 'N/A')}")
            print(f"  • Description: {metadata.get('description', 'N/A')}")

            if "kde_parameters" in metadata:
                print("\n⚙️  Generation Parameters:")
                pprint(metadata["kde_parameters"], indent=4)

            if "data_shapes" in metadata:
                print("\n📐 Original Data Shapes:")
                pprint(metadata["data_shapes"], indent=4)

            print("\n🔍 Data Summary:")
            print(f"  • KDE values range: [{np.min(values):.3f}, {np.max(values):.3f}]")
            print(f"  • Points X range: [{np.min(points[:, 0]):.3f}, {np.max(points[:, 0]):.3f}]")
            print(f"  • Points Y range: [{np.min(points[:, 1]):.3f}, {np.max(points[:, 1]):.3f}]")

            # Data integrity verification
            print("\n✅ Data Integrity:")
            checksum_keys = [k for k in metadata.keys() if k.endswith("_checksum")]
            if checksum_keys:
                print(f"  • {len(checksum_keys)} integrity checksums verified")
            else:
                print("  • No checksums available (older format)")

    except FileNotFoundError:
        error_msg = f"File not found: {filepath}"
        results["error"] = error_msg
        if verbose:
            print(f"❌ Error: {error_msg}")
            print("Make sure you have run the KDE generator first.")
    except ValueError as e:
        error_msg = f"Data integrity error: {e}"
        results["error"] = error_msg
        if verbose:
            print(f"❌ {error_msg}")
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        results["error"] = error_msg
        if verbose:
            print(f"❌ {error_msg}")

    return results


def compare_parameters(filepath: str, expected_params: Dict[str, Any], verbose: bool = True) -> Dict[str, Any]:
    """
    Compare stored parameters with expected values.

    :param filepath: Path to the HDF5 KDE data file
    :type filepath: str
    :param expected_params: Dictionary of expected parameter values
    :type expected_params: Dict[str, Any]
    :param verbose: Whether to print comparison results
    :type verbose: bool
    :returns: Dictionary containing comparison results
    :rtype: Dict[str, Any]
    """
    comparison_results = {"matches": {}, "mismatches": {}, "missing": {}, "success": False}

    try:
        _, _, _, metadata = load_kde_data_with_metadata(filepath)
        stored_params = metadata.get("kde_parameters", {})

        comparison_results["success"] = True

        if verbose:
            print("\n🔄 Parameter Comparison:")
            print("=" * 40)

        for key, expected_value in expected_params.items():
            stored_value = stored_params.get(key, "NOT_FOUND")

            if stored_value == "NOT_FOUND":
                comparison_results["missing"][key] = expected_value
            elif stored_value == expected_value:
                comparison_results["matches"][key] = expected_value
            else:
                comparison_results["mismatches"][key] = {"expected": expected_value, "actual": stored_value}

            if verbose:
                match = "✅" if stored_value == expected_value else "❌"
                print(f"  {match} {key}: {stored_value} (expected: {expected_value})")

    except Exception as e:
        comparison_results["error"] = str(e)
        if verbose:
            print(f"❌ Error comparing parameters: {e}")

    return comparison_results


def get_kde_file_summary(kde_dir: str) -> Dict[str, Any]:
    """
    Get a summary of all KDE files in a directory.

    :param kde_dir: Directory to scan
    :type kde_dir: str
    :returns: Dictionary containing summary information
    :rtype: Dict[str, Any]
    """
    kde_files = list_kde_files(kde_dir)

    summary = {"directory": kde_dir, "total_files": len(kde_files), "files": [], "parameter_variations": set()}

    for filepath in kde_files:
        try:
            file_info = examine_kde_data(filepath, verbose=False)
            if file_info["success"]:
                # Extract key parameters for variation tracking
                metadata = file_info.get("metadata", {})
                params = metadata.get("kde_parameters", {})

                key_params = (
                    params.get("bandwidth"),
                    params.get("nbins"),
                    params.get("ts_threshold"),
                    params.get("flux_type"),
                )
                summary["parameter_variations"].add(key_params)

            summary["files"].append(file_info)

        except Exception:
            summary["files"].append(
                {
                    "filepath": filepath,
                    "filename": os.path.basename(filepath),
                    "success": False,
                    "error": "Could not load file",
                }
            )

    summary["unique_parameter_sets"] = len(summary["parameter_variations"])

    return summary
