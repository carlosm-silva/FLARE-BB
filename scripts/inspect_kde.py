#!/usr/bin/env python3
"""Inspect a saved FLARE-BB KDE artifact."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from flare_bb.io.filenames import decode_kde_filename
from flare_bb.io.hdf5 import load_kde_result


def main() -> None:
    """Run the KDE inspection CLI."""
    parser = argparse.ArgumentParser(description="Inspect a FLARE-BB KDE HDF5 file.")
    parser.add_argument("path", type=Path)
    args = parser.parse_args()

    result, metadata = load_kde_result(args.path)
    print(f"path: {args.path}")
    print(f"decoded_filename: {decode_kde_filename(args.path)}")
    print(f"kde_data_shape: {result.kde_data.shape}")
    print(f"points_shape: {result.points.shape}")
    print(f"values_shape: {result.values.shape}")
    print(f"log_kde_range: [{np.min(result.values):.6g}, {np.max(result.values):.6g}]")
    print(f"metadata_keys: {sorted(metadata)}")


if __name__ == "__main__":
    main()
