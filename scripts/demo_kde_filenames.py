#!/usr/bin/env python3
"""
SPDX-License-Identifier: GPL-3.0-or-later
FLARE-BB – Bayesian Blocks algorithm for detecting gamma-ray flares
Copyright © 2025 Carlos Márcio de Oliveira e Silva Filho
Copyright © 2025 Ignacio Taboada

Demo script showing how KDE filenames encode parameters to prevent overwrites.
This script demonstrates the filename generation feature without requiring actual data.
"""

import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from data_processing.kde_generator import generate_kde_filename, get_kde_generation_parameters


def main():
    """Main function demonstrating filename generation patterns."""

    print("🎯 KDE Filename Generation Demo")
    print("=" * 60)
    print("This shows how parameter changes create unique filenames to prevent overwrites.\n")

    # Base parameters (current defaults)
    base_params = get_kde_generation_parameters()
    base_filename = generate_kde_filename(base_params, base_path="data/cache/kde")

    print("📋 Base configuration:")
    print(f"  Filename: {os.path.basename(base_filename)}")
    print(
        f"  Parameters: bandwidth={base_params['bandwidth']}, nbins={base_params['nbins']}, "
        f"ts_threshold={base_params['ts_threshold']}, flux_type='{base_params['flux_type']}'"
    )
    print()

    # Show how different parameters create different filenames
    variations = [
        {"name": "Higher Bandwidth", "changes": {"bandwidth": 0.3}, "reason": "Smoother KDE with more averaging"},
        {"name": "Higher Resolution", "changes": {"nbins": 1024}, "reason": "Finer grid resolution"},
        {
            "name": "Stricter TS Threshold",
            "changes": {"ts_threshold": 25},
            "reason": "More conservative detection threshold",
        },
        {
            "name": "Different Flux Type",
            "changes": {"flux_type": "photon"},
            "reason": "Using photon flux instead of energy flux",
        },
        {"name": "Different Grid Range", "changes": {"x_low": -5.0, "x_high": -2.5}, "reason": "Extended flux range"},
        {
            "name": "Multiple Changes",
            "changes": {"bandwidth": 0.15, "nbins": 256, "ts_threshold": 16},
            "reason": "Testing different analysis strategy",
        },
    ]

    print("🔄 Parameter Variations and Their Filenames:")
    print("-" * 60)

    for i, variation in enumerate(variations, 1):
        # Create modified parameters
        modified_params = base_params.copy()
        modified_params.update(variation["changes"])

        # Generate filename
        modified_filename = generate_kde_filename(modified_params, base_path="data/cache/kde")

        print(f"{i}. {variation['name']}:")
        print(f"   Changes: {variation['changes']}")
        print(f"   Reason: {variation['reason']}")
        print(f"   Filename: {os.path.basename(modified_filename)}")
        print()

    print("✅ Benefits of Parameter-Encoded Filenames:")
    print("  • No accidental overwrites when experimenting with parameters")
    print("  • Easy to identify which files correspond to which analysis")
    print("  • Self-documenting file organization")
    print("  • Can run multiple parameter sweeps in parallel")
    print("  • Quick visual comparison of parameter sets")

    print("\n🔍 Filename Format Breakdown:")
    print("  kde_bw{bandwidth}_n{nbins}_ts{threshold}_flux-{type}_x{low}to{high}_y{low}to{high}.h5")
    print("  │   │             │        │             │          │              │")
    print("  │   │             │        │             │          │              └─ Y-axis range")
    print("  │   │             │        │             │          └─ X-axis range")
    print("  │   │             │        │             └─ Flux type")
    print("  │   │             │        └─ TS threshold")
    print("  │   │             └─ Number of bins")
    print("  │   └─ Bandwidth")
    print("  └─ File type prefix")

    print("\n💡 Usage in practice:")
    print("  • Run KDE generator with different parameters")
    print("  • Each run creates a unique file automatically")
    print("  • No risk of overwriting previous results")
    print("  • Easy to compare different parameter combinations")


if __name__ == "__main__":
    main()
