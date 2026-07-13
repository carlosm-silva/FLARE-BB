"""KDE workflow orchestration."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from flare_bb.core.config import DEFAULT_KDE_CONFIG, KdeConfig
from flare_bb.core.kde import KdeResult, compute_kde
from flare_bb.io.filenames import kde_filename, list_matching_files
from flare_bb.io.hdf5 import load_kde_result, save_kde_result


def generate_kde_file(
    data: NDArray[np.float64],
    output_dir: Path,
    config: KdeConfig = DEFAULT_KDE_CONFIG,
    *,
    overwrite: bool = False,
) -> Path:
    """Generate a KDE file from stacked log flux/error data.

    Parameters
    ----------
    data : NDArray
        Input data with shape ``(2, n_samples)``.
    output_dir : Path
        Output directory.
    config : KdeConfig
        KDE configuration.
    overwrite : bool
        Whether to overwrite an existing parameter-matched file.

    Returns
    -------
    Path
        Generated or existing output path.
    """
    output_path = output_dir / kde_filename(config)
    if output_path.exists() and not overwrite:
        return output_path
    result = compute_kde(data, config=config)
    save_kde_result(result, output_path)
    return output_path


def list_kde_files(directory: Path) -> list[Path]:
    """List KDE files in a directory.

    Parameters
    ----------
    directory : Path
        Directory to inspect.

    Returns
    -------
    list[Path]
        Matching KDE files.
    """
    files = list_matching_files(directory, "kde_*.h5")
    legacy_file = directory / "log_kde_data.h5"
    if legacy_file.exists():
        files.append(legacy_file)
    return sorted(set(files))


def find_kde_by_parameters(directory: Path, parameters: dict[str, object]) -> Path | None:
    """Find a KDE file whose stored parameters match requested values.

    Parameters
    ----------
    directory : Path
        Directory to search.
    parameters : dict[str, object]
        Parameters to match exactly.

    Returns
    -------
    Path | None
        Matching KDE path, if any.
    """
    for path in list_kde_files(directory):
        try:
            _, metadata = load_kde_result(path)
        except (OSError, ValueError, KeyError):
            continue
        stored_parameters = metadata.get("kde_parameters", {})
        if isinstance(stored_parameters, dict) and all(
            stored_parameters.get(key) == value for key, value in parameters.items()
        ):
            return path
    return None


def load_most_recent_kde(directory: Path) -> tuple[KdeResult, dict[str, object], Path]:
    """Load the newest KDE file in a directory.

    Parameters
    ----------
    directory : Path
        Directory to inspect.

    Returns
    -------
    tuple[KdeResult, dict[str, object], Path]
        Loaded KDE, metadata, and source path.
    """
    files = list_kde_files(directory)
    if not files:
        raise FileNotFoundError(f"No KDE files found in {directory}.")
    path = max(files, key=lambda candidate: candidate.stat().st_mtime)
    result, metadata = load_kde_result(path)
    return result, metadata, path
