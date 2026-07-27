"""Filename helpers for generated FLARE-BB artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from flare_bb.core.config import DistributionConfig, KdeConfig


def kde_filename(config: KdeConfig, suffix: str = ".h5") -> str:
    """Create a parameter-encoded KDE filename.

    Parameters
    ----------
    config : KdeConfig
        KDE generation configuration.
    suffix : str
        Filename suffix.

    Returns
    -------
    str
        Filename encoding the key KDE parameters.
    """
    return (
        f"kde_bw{config.bandwidth}_n{config.bins}_ts{config.ts_threshold}_flux-{config.flux_type}"
        f"_x{config.log_flux_min}to{config.log_flux_max}"
        f"_y{config.log_uncertainty_min}to{config.log_uncertainty_max}{suffix}"
    )


def distribution_filename(
    config: DistributionConfig,
    kde_metadata: dict[str, Any] | None = None,
    prefix: str = "flux_dist",
    suffix: str = ".h5",
) -> str:
    """Create a parameter-encoded distribution filename.

    Parameters
    ----------
    config : DistributionConfig
        Distribution configuration.
    kde_metadata : dict[str, Any] | None
        Optional KDE metadata to include in the filename.
    prefix : str
        Filename prefix.
    suffix : str
        Filename suffix.

    Returns
    -------
    str
        Filename encoding key distribution and KDE parameters.
    """
    parts = [
        f"hd-res{config.high_definition_resolution}",
        f"ml-res{config.marginal_likelihood_resolution}",
        f"ml-interp{config.marginal_likelihood_interp_points}",
        f"bins{config.final_grid_bins}",
        f"flux{config.log_true_flux_min}to{config.log_true_flux_max}",
        f"ext{config.marginal_likelihood_range_extension}",
    ]
    kde_parameters = kde_metadata.get("kde_parameters", {}) if kde_metadata else {}
    if isinstance(kde_parameters, dict) and kde_parameters:
        parts.extend(
            [
                f"kde-bw{kde_parameters.get('bandwidth', 'unk')}",
                f"n{kde_parameters.get('bins', kde_parameters.get('nbins', 'unk'))}",
                f"ts{kde_parameters.get('ts_threshold', 'unk')}",
            ]
        )
    return f"{prefix}_{'_'.join(parts)}{suffix}"


def list_matching_files(directory: Path, pattern: str) -> list[Path]:
    """List files matching a glob pattern in a directory.

    Parameters
    ----------
    directory : Path
        Directory to search.
    pattern : str
        Glob pattern.

    Returns
    -------
    list[Path]
        Sorted matching paths.
    """
    if not directory.exists():
        return []
    return sorted(path for path in directory.glob(pattern) if path.is_file())


def decode_kde_filename(path: Path) -> dict[str, Any]:
    """Decode known parameters from a KDE filename.

    Parameters
    ----------
    path : Path
        KDE file path.

    Returns
    -------
    dict[str, Any]
        Decoded filename parameters.
    """
    if path.name == "log_kde_data.h5":
        return {"format": "legacy"}

    decoded: dict[str, Any] = {"format": "descriptive"}
    for part in path.stem.split("_"):
        if part.startswith("bw"):
            decoded["bandwidth"] = float(part[2:])
        elif part.startswith("n") and part[1:].isdigit():
            decoded["bins"] = int(part[1:])
        elif part.startswith("ts") and part[2:].isdigit():
            decoded["ts_threshold"] = int(part[2:])
        elif part.startswith("flux-"):
            decoded["flux_type"] = part[5:]
        elif part.startswith("x"):
            decoded["log_flux_range"] = part[1:]
        elif part.startswith("y"):
            decoded["log_uncertainty_range"] = part[1:]
    return decoded
