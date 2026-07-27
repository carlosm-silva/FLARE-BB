"""Flux-distribution workflow orchestration."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import cast

from tqdm import tqdm

from flare_bb.core.config import DEFAULT_DISTRIBUTION_CONFIG, DistributionConfig
from flare_bb.core.distributions import DistributionResult, build_flux_distributions
from flare_bb.io.filenames import distribution_filename, list_matching_files
from flare_bb.io.hdf5 import load_distribution_result, load_kde_result, save_distribution_result


def build_distribution_file(
    kde_path: Path,
    output_dir: Path,
    config: DistributionConfig = DEFAULT_DISTRIBUTION_CONFIG,
    *,
    overwrite: bool = False,
    show_progress: bool = False,
) -> Path:
    """Build and save posterior distributions from a KDE file.

    Parameters
    ----------
    kde_path : Path
        Input KDE HDF5 path.
    output_dir : Path
        Output directory.
    config : DistributionConfig
        Distribution configuration.
    overwrite : bool
        Whether to overwrite an existing parameter-matched result.
    show_progress : bool
        Whether to show a tqdm progress bar over true flux values.

    Returns
    -------
    Path
        Generated or existing output path.
    """
    kde_result, kde_metadata = load_kde_result(kde_path)
    output_path = output_dir / distribution_filename(config, kde_metadata)
    if output_path.exists() and not overwrite:
        return output_path

    progress = _progress if show_progress else None
    result = build_flux_distributions(kde_result.points, kde_result.values, config=config, progress=progress)
    description = (
        "Flux distributions computed from KDE data using the FLARE-BB Bayesian measurement model. "
        f"Generated with {config.final_grid_bins}x{config.final_grid_bins} measured-flux grids."
    )
    save_distribution_result(result, output_path, kde_metadata=kde_metadata, description=description)
    return output_path


def list_distribution_files(directory: Path) -> list[Path]:
    """List saved distribution files.

    Parameters
    ----------
    directory : Path
        Directory to inspect.

    Returns
    -------
    list[Path]
        Matching distribution files.
    """
    return list_matching_files(directory, "flux_dist_*.h5")


def find_distribution_by_config(directory: Path, config: DistributionConfig) -> Path | None:
    """Find a distribution file matching a configuration.

    Parameters
    ----------
    directory : Path
        Directory to search.
    config : DistributionConfig
        Target configuration.

    Returns
    -------
    Path | None
        Matching distribution path, if any.
    """
    for path in list_distribution_files(directory):
        try:
            result, _ = load_distribution_result(path)
        except (OSError, ValueError, KeyError):
            continue
        if result.config == config:
            return path
    return None


def load_distribution(path: Path) -> DistributionResult:
    """Load a distribution result from disk.

    Parameters
    ----------
    path : Path
        Distribution file path.

    Returns
    -------
    DistributionResult
        Loaded result.
    """
    result, _ = load_distribution_result(path)
    return result


def _progress(values: Iterable[float]) -> Iterable[float]:
    return cast("Iterable[float]", tqdm(values, desc="Generating flux PDFs", unit="flux"))
