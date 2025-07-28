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
# Build flux distributions from KDE data for Bayesian analysis.
#

import argparse
import os
import sys
from typing import Any, Dict

# Add src to path for imports (following repository pattern)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

from data_processing.distribution_builder import build_flux_distributions
from data_processing.distribution_config import DEFAULT_CONFIG, DistributionConfig
from data_processing.distribution_utils import (
    create_distribution_filename,
    ensure_distribution_cache_directory,
    examine_distribution_data,
    find_distribution_by_parameters,
    get_distribution_summary,
    save_distribution_data,
)
from data_processing.kde_generator import load_kde_data_with_metadata
from data_processing.kde_utils import find_kde_by_parameters, list_kde_files


def load_kde_data_for_distributions(
    kde_dir: str = None, target_params: dict = None
) -> tuple[Any, Any, Any, Dict[str, Any]]:
    """
    Load KDE data for distribution building following repository standards.

    :param kde_dir: Directory containing KDE files (default: data/cache/kde)
    :type kde_dir: str, optional
    :param target_params: Specific parameters to match for file selection
    :type target_params: dict, optional
    :returns: Tuple of (kde_data, points, values, metadata)
    :rtype: tuple[Any, Any, Any, Dict[str, Any]]
    :raises FileNotFoundError: If no suitable KDE file is found
    """
    if kde_dir is None:
        kde_dir = os.path.join("data", "cache", "kde")

    if not os.path.exists(kde_dir):
        raise FileNotFoundError(f"KDE directory not found: {kde_dir}")

    # Find KDE file based on parameters
    if target_params:
        filepath = find_kde_by_parameters(target_params, kde_dir)
        if filepath:
            print(f"📁 Found KDE file matching parameters: {os.path.basename(filepath)}")
        else:
            raise FileNotFoundError(f"No KDE file found matching parameters: {target_params}")
    else:
        # Use the most recent KDE file
        kde_files = list_kde_files(kde_dir)
        if not kde_files:
            raise FileNotFoundError(f"No KDE files found in {kde_dir}")

        # Sort by modification time and take the most recent
        kde_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        filepath = kde_files[0]
        print(f"📁 Using most recent KDE file: {os.path.basename(filepath)}")

    # Load the data using the repository's standard function
    kde_data, points, values, metadata = load_kde_data_with_metadata(filepath)

    # Display KDE metadata information
    print("📊 KDE File Metadata:")
    print(f"  • Generation timestamp: {metadata.get('generation_timestamp', 'N/A')}")
    print(f"  • File format version: {metadata.get('file_format_version', 'N/A')}")

    if "kde_parameters" in metadata:
        params = metadata["kde_parameters"]
        print(f"  • Grid size: {params.get('nbins', 'N/A')}×{params.get('nbins', 'N/A')}")
        print(f"  • Bandwidth: {params.get('bandwidth', 'N/A')}")
        print(f"  • TS threshold: {params.get('ts_threshold', 'N/A')}")
        print(f"  • X range: [{params.get('x_low', 'N/A')}, {params.get('x_high', 'N/A')}]")
        print(f"  • Y range: [{params.get('y_low', 'N/A')}, {params.get('y_high', 'N/A')}]")

    return kde_data, points, values, metadata


def create_custom_config(args: argparse.Namespace) -> DistributionConfig:
    """
    Create distribution configuration from command-line arguments.

    :param args: Parsed command-line arguments
    :type args: argparse.Namespace
    :returns: Distribution configuration
    :rtype: DistributionConfig
    """
    config = DistributionConfig(
        high_definition_resolution=args.hd_resolution,
        marginal_likelihood_resolution=args.ml_resolution,
        marginal_likelihood_interp_points=args.ml_interp_points,
        final_grid_bins=args.final_bins,
        flux_range_min=args.flux_min,
        flux_range_max=args.flux_max,
        marginal_likelihood_range_extension=args.range_extension,
        numerical_epsilon=args.epsilon,
        interpolation_method=args.interpolation,
    )

    # Validate configuration
    try:
        config.validate()
        print("✅ Configuration validated successfully")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)

    return config


def process_distributions(
    points: Any, values: Any, kde_metadata: Dict[str, Any], config: DistributionConfig, verbose: bool = True
) -> None:
    """
    Process flux distributions using the core algorithm.

    :param points: KDE grid points
    :type points: Any
    :param values: KDE values
    :type values: Any
    :param kde_metadata: KDE metadata for context
    :type kde_metadata: Dict[str, Any]
    :param config: Distribution configuration
    :type config: DistributionConfig
    :param verbose: Whether to show detailed progress information
    :type verbose: bool
    """
    print("🔬 Building Flux Distributions from KDE Data")
    print("=" * 60)

    # Display configuration
    print("⚙️  Configuration:")
    print(f"  • High-definition resolution: {config.high_definition_resolution}")
    print(f"  • Marginal likelihood resolution: {config.marginal_likelihood_resolution}")
    print(f"  • Marginal likelihood interpolation points: {config.marginal_likelihood_interp_points}")
    print(f"  • Final grid bins: {config.final_grid_bins}")
    print(f"  • Flux range: [{config.flux_range_min}, {config.flux_range_max}]")
    print(f"  • Range extension: {config.marginal_likelihood_range_extension}")
    print(f"  • Interpolation method: {config.interpolation_method}")

    # Check if distribution already exists
    output_dir = ensure_distribution_cache_directory()
    existing_file = find_distribution_by_parameters(config, output_dir)

    if existing_file:
        print(f"📋 Found existing distribution file: {os.path.basename(existing_file)}")

        # Show summary of existing file
        try:
            summary = examine_distribution_data(existing_file)
            print("📊 Existing Distribution Summary:")
            print(f"  • File size: {summary['file_size_mb']:.2f} MB")
            print(
                f"  • Flux range: [{summary['flux_range_actual']['min']:.3f}, {summary['flux_range_actual']['max']:.3f}]"
            )
            print(
                f"  • Grid resolution: {summary['configuration']['final_bins']}×{summary['configuration']['final_bins']}"
            )
            print(f"  • Generation time: {summary['metadata'].get('generation_timestamp', 'Unknown')}")

            response = input("🤔 Use existing file? [y/N]: ").strip().lower()
            if response in ["y", "yes"]:
                print("✅ Using existing distribution file")
        return
            else:
                print("🔄 Proceeding with new calculation...")
        except Exception as e:
            print(f"⚠️  Could not examine existing file: {e}")
            print("🔄 Proceeding with new calculation...")

    # Extract grid information from the data
    print("\n🔍 Analyzing KDE grid structure...")
    resolution = int((points.shape[0]) ** 0.5)
    x_low, x_high = points[:, 0].min(), points[:, 0].max()
    y_low, y_high = points[:, 1].min(), points[:, 1].max()

    print(f"  • KDE grid: {resolution}×{resolution}")
    print(f"  • X range: [{x_low:.3f}, {x_high:.3f}]")
    print(f"  • Y range: [{y_low:.3f}, {y_high:.3f}]")

    # Run the core distribution building algorithm
    print("\n🧮 Running flux distribution calculation...")
    if verbose:
        print("   This process involves several computationally intensive steps:")
        print("   1. Normalizing KDE and creating interpolators")
        print("   2. Calculating likelihood functions")
        print("   3. Computing marginal likelihood (this may take several minutes)")
        print("   4. Building posterior distributions")
        print("   5. Generating flux PDFs for each true flux value")

    try:
        # Call the core algorithm from src/ with progress tracking
        result = build_flux_distributions(points, values, config, verbose=verbose)

        print("✅ Distribution calculation completed successfully!")

        # Display results summary
        print("\n📊 Results Summary:")
        print(f"  • Posterior PDF grid shape: {result.posterior_pdf_grid.shape}")
        print(f"  • True flux range: [{result.flux_range.min():.3f}, {result.flux_range.max():.3f}]")
        print(f"  • Measured flux grid shape: {result.log_measured_flux_grid.shape}")
        print(f"  • Measured uncertainty grid shape: {result.log_measured_uncertainty_grid.shape}")

        # Save results
        print("\n💾 Saving distribution data...")
        filename = create_distribution_filename(config, kde_metadata)
        output_path = os.path.join(output_dir, filename)

        description = (
            f"Flux distributions computed from KDE data using Bayesian analysis. "
            f"Generated with {config.final_grid_bins}×{config.final_grid_bins} grid resolution."
        )

        try:
            save_distribution_data(result, output_path, kde_metadata, description)
            print(f"✅ Results saved to: {filename}")
            print(f"📁 Full path: {output_path}")
            print(f"💽 File size: {os.path.getsize(output_path) / (1024 * 1024):.2f} MB")
        except Exception as save_error:
            print(f"❌ Error saving results: {save_error}")
            print("💡 Attempting to save with minimal metadata...")
            try:
                # Try saving with just basic metadata
                save_distribution_data(result, output_path, None, description)
                print(f"✅ Results saved with minimal metadata to: {filename}")
                print(f"📁 Full path: {output_path}")
                print(f"💽 File size: {os.path.getsize(output_path) / (1024 * 1024):.2f} MB")
            except Exception as final_error:
                print(f"❌ Failed to save even with minimal metadata: {final_error}")
                raise

    except Exception as e:
        print(f"❌ Error during calculation: {e}")
        print("💡 This might be due to:")
        print("   • Insufficient memory for large grid calculations")
        print("   • Invalid KDE data format")
        print("   • Configuration parameter conflicts")
        raise


def list_existing_distributions() -> None:
    """List all existing distribution files with summary information."""
    print("📋 Existing Distribution Files")
    print("=" * 60)

    try:
        summary = get_distribution_summary()

        if summary["total_files"] == 0:
            print("No distribution files found.")
            print("💡 Run the script without --list to generate distributions.")
            return

        print(f"📁 Directory: {summary['directory']}")
        print(f"📊 Total files: {summary['total_files']}")
        print()

        for file_info in summary["files"]:
            if "error" in file_info:
                print(f"❌ {file_info['filename']}: {file_info['error']}")
            else:
                print(f"✅ {file_info['filename']}")
                print(f"   • Size: {file_info['size_mb']:.2f} MB")
                print(f"   • Flux range: [{file_info['flux_range']['min']:.3f}, {file_info['flux_range']['max']:.3f}]")
                print(f"   • Grid resolution: {file_info['grid_resolution']}×{file_info['grid_resolution']}")
                print(f"   • Generated: {file_info['generation_time']}")
                print()

    except Exception as e:
        print(f"❌ Error listing distributions: {e}")


def main():
    """Main function orchestrating the distribution building workflow."""
    parser = argparse.ArgumentParser(
        description="Build flux distributions from KDE data for Bayesian analysis",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Data source options
    parser.add_argument(
        "--kde-dir", type=str, default=None, help="Directory containing KDE files (default: data/cache/kde)"
    )

    # Configuration parameters
    parser.add_argument(
        "--hd-resolution",
        type=int,
        default=DEFAULT_CONFIG.high_definition_resolution,
        help="High-definition grid resolution for normalization",
    )
    parser.add_argument(
        "--ml-resolution",
        type=int,
        default=DEFAULT_CONFIG.marginal_likelihood_resolution,
        help="Grid resolution for marginal likelihood calculations",
    )
    parser.add_argument(
        "--ml-interp-points",
        type=int,
        default=DEFAULT_CONFIG.marginal_likelihood_interp_points,
        help="Number of points for marginal likelihood interpolation",
    )
    parser.add_argument(
        "--final-bins",
        type=int,
        default=DEFAULT_CONFIG.final_grid_bins,
        help="Grid resolution for final distribution calculations",
    )
    parser.add_argument(
        "--flux-min",
        type=float,
        default=DEFAULT_CONFIG.flux_range_min,
        help="Minimum log flux value for distribution range",
    )
    parser.add_argument(
        "--flux-max",
        type=float,
        default=DEFAULT_CONFIG.flux_range_max,
        help="Maximum log flux value for distribution range",
    )
    parser.add_argument(
        "--range-extension",
        type=float,
        default=DEFAULT_CONFIG.marginal_likelihood_range_extension,
        help="Extension factor for marginal likelihood range",
    )
    parser.add_argument(
        "--epsilon",
        type=float,
        default=DEFAULT_CONFIG.numerical_epsilon,
        help="Small epsilon value for numerical stability",
    )
    parser.add_argument(
        "--interpolation",
        type=str,
        default=DEFAULT_CONFIG.interpolation_method,
        choices=["linear", "cubic", "nearest"],
        help="Interpolation method for grid operations",
    )

    # KDE selection parameters
    parser.add_argument("--kde-bandwidth", type=float, help="Select KDE file with specific bandwidth")
    parser.add_argument("--kde-nbins", type=int, help="Select KDE file with specific grid resolution")
    parser.add_argument("--kde-ts-threshold", type=float, help="Select KDE file with specific TS threshold")

    # Workflow options
    parser.add_argument("--list", action="store_true", help="List existing distribution files and exit")
    parser.add_argument(
        "--verbose", action="store_true", help="Show detailed progress information and step-by-step feedback"
    )
    parser.add_argument(
        "--quiet", action="store_true", help="Suppress detailed progress information (opposite of --verbose)"
    )

    args = parser.parse_args()

    # Handle conflicting verbosity options
    if args.verbose and args.quiet:
        print("❌ Error: Cannot specify both --verbose and --quiet")
        sys.exit(1)

    # Determine verbosity level
    if args.quiet:
        verbose = False
    elif args.verbose:
        verbose = True
    else:
        verbose = True  # Default to verbose for better user experience

    # Handle list option
    if args.list:
        list_existing_distributions()
        return

    print("🔬 FLARE-BB Flux Distribution Builder")
    print("=" * 60)

    try:
        # Create configuration from arguments
        config = create_custom_config(args)

        # Build target parameters for KDE selection
        target_params = {}
        if args.kde_bandwidth is not None:
            target_params["bandwidth"] = args.kde_bandwidth
        if args.kde_nbins is not None:
            target_params["nbins"] = args.kde_nbins
        if args.kde_ts_threshold is not None:
            target_params["ts_threshold"] = args.kde_ts_threshold

        # Load KDE data (heavy lifting)
        print("📂 Loading KDE data...")
        kde_data, points, values, metadata = load_kde_data_for_distributions(
            args.kde_dir, target_params if target_params else None
        )

        # Process distributions (heavy lifting)
        process_distributions(points, values, metadata, config, verbose=verbose)

        print("\n🎉 Distribution building complete!")
        print("💡 Use --list to see all available distribution files")

    except FileNotFoundError as e:
        print(f"❌ File Error: {e}")
        print("💡 Make sure KDE data exists. Run 'python scripts/generate_kde.py' first.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
