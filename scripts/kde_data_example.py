#!/usr/bin/env python3
"""
SPDX-License-Identifier: GPL-3.0-or-later
FLARE-BB – Bayesian Blocks algorithm for detecting gamma-ray flares
Copyright © 2025 Carlos Márcio de Oliveira e Silva Filho
Copyright © 2025 Ignacio Taboada

Example script demonstrating how to use the KDE data examination functionality.
This script shows usage patterns for the KDE utilities.
"""

import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from data_processing.kde_utils import (
    compare_parameters,
    examine_kde_data,
    find_kde_by_parameters,
    get_kde_file_summary,
    list_kde_files,
)


def main():
    """Main function demonstrating KDE data examination workflows."""

    print("🔬 KDE Data Examination Tool")
    print("=" * 60)

    # Set up paths
    kde_dir = os.path.join("data", "cache", "kde")

    # List available KDE files
    kde_files = list_kde_files(kde_dir)

    if not kde_files:
        print("❌ No KDE files found in data/cache/kde/")
        print("Run the KDE generator first to create data files.")
        return

    print(f"📁 Found {len(kde_files)} KDE file(s):")
    for i, filepath in enumerate(kde_files, 1):
        print(f"  {i}. {os.path.basename(filepath)}")
    print()

    # Handle command line arguments
    if len(sys.argv) > 1:
        kde_file = sys.argv[1]
        if not os.path.exists(kde_file):
            print(f"❌ File not found: {kde_file}")
            return
    else:
        # Use the most recent file by default
        kde_file = kde_files[-1]
        print(f"🎯 Examining most recent file: {os.path.basename(kde_file)}")
        print()

    # Examine the selected file
    examination_result = examine_kde_data(kde_file, verbose=True)

    if examination_result["success"]:
        # Use the actual file's parameters for comparison and search
        file_params = examination_result["metadata"].get("kde_parameters", {})

        # Example parameter comparison using actual values
        expected_params = {
            "bandwidth": file_params.get("bandwidth"),
            "nbins": file_params.get("nbins"),
            "ts_threshold": file_params.get("ts_threshold"),
            "flux_type": file_params.get("flux_type"),
        }

        print("\n🔄 Verifying file parameters match expectations...")
        compare_parameters(kde_file, expected_params)

        # Demonstrate finding files by parameters (use subset of actual params)
        print("\n🔍 Finding files by parameters:")
        search_params = {"bandwidth": file_params.get("bandwidth"), "flux_type": file_params.get("flux_type")}
        found_file = find_kde_by_parameters(search_params, kde_dir)
        if found_file:
            print(f"  ✅ Found file matching {search_params}: {os.path.basename(found_file)}")
        else:
            print(f"  ❌ No file found matching {search_params}")

        # Also demonstrate searching for a different parameter set
        print("\n🔍 Searching for files with different parameters:")
        alt_search_params = {"bandwidth": 0.15, "flux_type": "energy"}
        alt_found_file = find_kde_by_parameters(alt_search_params, kde_dir)
        if alt_found_file:
            print(f"  ✅ Found file matching {alt_search_params}: {os.path.basename(alt_found_file)}")
        else:
            print(f"  ❌ No file found matching {alt_search_params}")
    else:
        print("\n⚠️  Could not examine file successfully, using default parameter comparison...")
        # Fallback to hardcoded params if file can't be loaded
        expected_params = {"bandwidth": 0.2, "nbins": 512, "ts_threshold": 19, "flux_type": "energy"}
        compare_parameters(kde_file, expected_params)

    # Show summary of all files
    print("\n📊 Directory Summary:")
    summary = get_kde_file_summary(kde_dir)
    print(f"  • Total files: {summary['total_files']}")
    print(f"  • Unique parameter sets: {summary['unique_parameter_sets']}")

    # Show successful vs failed files
    successful_files = sum(1 for f in summary["files"] if f["success"])
    print(f"  • Successfully loaded: {successful_files}/{summary['total_files']}")

    print("\n" + "=" * 60)
    print("💡 Usage examples:")
    print("  • Load data: kde_data, points, values, metadata = load_kde_data_with_metadata(filepath)")
    print("  • Access parameters: params = metadata['kde_parameters']")
    print("  • Check generation time: timestamp = metadata['generation_timestamp']")
    print("  • List files: python scripts/kde_data_example.py")
    print("  • Examine specific file: python scripts/kde_data_example.py path/to/file.h5")


if __name__ == "__main__":
    main()
