"""HDF5 persistence for FLARE-BB KDE and distribution artifacts."""

from __future__ import annotations

from dataclasses import asdict
from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path
from typing import Any

import h5py
import numpy as np
from numpy.typing import NDArray

from flare_bb.core.config import DistributionConfig, KdeConfig
from flare_bb.core.distributions import DistributionResult
from flare_bb.core.kde import KdeResult

KDE_FORMAT_VERSION = "1.0"
DISTRIBUTION_FORMAT_VERSION = "1.0"


def save_kde_result(result: KdeResult, path: Path, compression: str = "gzip") -> None:
    """Save a KDE result to HDF5 with metadata and checksums.

    Parameters
    ----------
    result : KdeResult
        KDE result to save.
    path : Path
        Output HDF5 path.
    compression : str
        HDF5 compression strategy.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with h5py.File(path, "w") as file:
        data_group = file.create_group("data")
        metadata_group = file.create_group("metadata")
        data_group.create_dataset("kde_data", data=result.kde_data, compression=compression)
        data_group.create_dataset("points", data=result.points, compression=compression)
        data_group.create_dataset("values", data=result.values, compression=compression)
        metadata_group.attrs["generation_timestamp"] = _timestamp()
        metadata_group.attrs["kde_parameters"] = json.dumps(asdict(result.config))
        metadata_group.attrs["data_shapes"] = json.dumps(
            {
                "kde_data": result.kde_data.shape,
                "points": result.points.shape,
                "values": result.values.shape,
            }
        )
        metadata_group.attrs["file_format_version"] = KDE_FORMAT_VERSION
        metadata_group.attrs["description"] = "KDE data for the measured flux/error relation in blazar light curves"
        metadata_group.attrs["kde_data_checksum"] = _array_checksum(result.kde_data)
        metadata_group.attrs["points_checksum"] = _array_checksum(result.points)
        metadata_group.attrs["values_checksum"] = _array_checksum(result.values)


def load_kde_result(path: Path) -> tuple[KdeResult, dict[str, Any]]:
    """Load a KDE result from HDF5.

    Parameters
    ----------
    path : Path
        Input HDF5 path.

    Returns
    -------
    tuple[KdeResult, dict[str, Any]]
        Loaded result and metadata.
    """
    if not path.exists():
        raise FileNotFoundError(f"KDE data file not found: {path}")
    with h5py.File(path, "r") as file:
        kde_data = np.asarray(file["data/kde_data"][:], dtype=np.float64)
        points = np.asarray(file["data/points"][:], dtype=np.float64)
        values = np.asarray(file["data/values"][:], dtype=np.float64)
        metadata = _read_metadata_group(file["metadata"]) if "metadata" in file else {}

    _validate_checksum(metadata, "kde_data_checksum", kde_data)
    _validate_checksum(metadata, "points_checksum", points)
    _validate_checksum(metadata, "values_checksum", values)
    parameters = metadata.get("kde_parameters", {})
    config = _kde_config_from_metadata(parameters) if isinstance(parameters, dict) else KdeConfig()
    return KdeResult(kde_data=kde_data, points=points, values=values, config=config), metadata


def save_distribution_result(
    result: DistributionResult,
    path: Path,
    kde_metadata: dict[str, Any] | None = None,
    description: str | None = None,
    compression: str = "gzip",
) -> None:
    """Save a posterior distribution result to HDF5.

    Parameters
    ----------
    result : DistributionResult
        Distribution result to save.
    path : Path
        Output HDF5 path.
    kde_metadata : dict[str, Any] | None
        Optional source KDE metadata.
    description : str | None
        Optional artifact description.
    compression : str
        HDF5 compression strategy.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with h5py.File(path, "w") as file:
        file.create_dataset("posterior_pdf_grid", data=result.posterior_pdf_grid, compression=compression)
        file.create_dataset("log_true_flux", data=result.log_true_flux, compression=compression)
        file.create_dataset("flux_range", data=result.log_true_flux, compression=compression)
        file.create_dataset("log_measured_flux_grid", data=result.log_measured_flux_grid, compression=compression)
        file.create_dataset(
            "log_measured_uncertainty_grid",
            data=result.log_measured_uncertainty_grid,
            compression=compression,
        )
        file.create_dataset("log_posterior_pdf_grid", data=result.log_posterior_pdf_grid, compression=compression)
        metadata_group = file.create_group("metadata")
        metadata_group.attrs["generation_timestamp"] = _timestamp()
        metadata_group.attrs["file_format_version"] = DISTRIBUTION_FORMAT_VERSION
        metadata_group.attrs["data_type"] = "flux_distributions"
        if description is not None:
            metadata_group.attrs["description"] = description
        _write_mapping(metadata_group.create_group("distribution_config"), asdict(result.config))
        if kde_metadata:
            _write_mapping(metadata_group.create_group("source_kde"), kde_metadata)


def load_distribution_result(path: Path) -> tuple[DistributionResult, dict[str, Any]]:
    """Load a posterior distribution result from HDF5.

    Parameters
    ----------
    path : Path
        Input HDF5 path.

    Returns
    -------
    tuple[DistributionResult, dict[str, Any]]
        Loaded result and metadata.
    """
    if not path.exists():
        raise FileNotFoundError(f"Distribution file not found: {path}")
    with h5py.File(path, "r") as file:
        posterior_pdf_grid = np.asarray(file["posterior_pdf_grid"][:], dtype=np.float64)
        log_true_flux_key = "log_true_flux" if "log_true_flux" in file else "flux_range"
        log_true_flux = np.asarray(file[log_true_flux_key][:], dtype=np.float64)
        log_measured_flux_grid = np.asarray(file["log_measured_flux_grid"][:], dtype=np.float64)
        log_measured_uncertainty_grid = np.asarray(file["log_measured_uncertainty_grid"][:], dtype=np.float64)
        log_posterior_pdf_grid = np.asarray(file["log_posterior_pdf_grid"][:], dtype=np.float64)
        metadata = _read_metadata_group(file["metadata"]) if "metadata" in file else {}

    config_metadata = metadata.get("distribution_config", {})
    config = (
        _distribution_config_from_metadata(config_metadata)
        if isinstance(config_metadata, dict)
        else DistributionConfig()
    )
    return (
        DistributionResult(
            posterior_pdf_grid=posterior_pdf_grid,
            log_true_flux=log_true_flux,
            log_measured_flux_grid=log_measured_flux_grid,
            log_measured_uncertainty_grid=log_measured_uncertainty_grid,
            log_posterior_pdf_grid=log_posterior_pdf_grid,
            config=config,
        ),
        metadata,
    )


def summarize_distribution(path: Path) -> dict[str, Any]:
    """Summarize a saved distribution file.

    Parameters
    ----------
    path : Path
        Distribution HDF5 path.

    Returns
    -------
    dict[str, Any]
        Summary suitable for CLI display or tests.
    """
    result, metadata = load_distribution_result(path)
    return {
        "path": path,
        "file_size_mb": path.stat().st_size / (1024 * 1024),
        "posterior_pdf_grid_shape": result.posterior_pdf_grid.shape,
        "log_true_flux_min": float(np.min(result.log_true_flux)),
        "log_true_flux_max": float(np.max(result.log_true_flux)),
        "final_grid_bins": result.config.final_grid_bins,
        "generation_timestamp": metadata.get("generation_timestamp"),
    }


def _timestamp() -> str:
    return datetime.now(tz=UTC).isoformat()


def _array_checksum(array: NDArray[np.float64]) -> str:
    return hashlib.md5(array.tobytes()).hexdigest()


def _validate_checksum(metadata: dict[str, Any], key: str, array: NDArray[np.float64]) -> None:
    expected = metadata.get(key)
    if expected is not None and expected != _array_checksum(array):
        raise ValueError(f"{key} integrity check failed.")


def _read_metadata_group(group: Any) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    for key, value in group.attrs.items():
        metadata[key] = _decode_metadata_value(value)
    for name, item in group.items():
        if isinstance(item, h5py.Group):
            metadata[name] = _read_metadata_group(item)
    return metadata


def _decode_metadata_value(value: Any) -> Any:
    if isinstance(value, bytes):
        return value.decode()
    if isinstance(value, str):
        if value.startswith(("{", "[")):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return value
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    return value


def _write_mapping(group: Any, mapping: dict[str, Any]) -> None:
    for key, value in mapping.items():
        if isinstance(value, dict):
            _write_mapping(group.create_group(key), value)
        elif isinstance(value, (str, int, float, bool, np.ndarray)):
            group.attrs[key] = value
        elif isinstance(value, (list, tuple)):
            group.attrs[key] = np.asarray(value)
        else:
            group.attrs[key] = str(value)


def _kde_config_from_metadata(parameters: dict[str, Any]) -> KdeConfig:
    return KdeConfig(
        bandwidth=float(parameters.get("bandwidth", 0.2)),
        bins=int(parameters.get("bins", parameters.get("nbins", 512))),
        log_flux_min=float(parameters.get("log_flux_min", parameters.get("x_low", -4.9))),
        log_flux_max=float(parameters.get("log_flux_max", parameters.get("x_high", -2.8))),
        log_uncertainty_min=float(parameters.get("log_uncertainty_min", parameters.get("y_low", -5.35))),
        log_uncertainty_max=float(parameters.get("log_uncertainty_max", parameters.get("y_high", -3.25))),
        ts_threshold=int(parameters.get("ts_threshold", 19)),
        ts_min=int(parameters.get("ts_min", 4)),
        flux_type=str(parameters.get("flux_type", "energy")),
    )


def _distribution_config_from_metadata(parameters: dict[str, Any]) -> DistributionConfig:
    return DistributionConfig(
        high_definition_resolution=int(parameters.get("high_definition_resolution", 1024)),
        marginal_likelihood_resolution=int(parameters.get("marginal_likelihood_resolution", 128)),
        marginal_likelihood_interp_points=int(parameters.get("marginal_likelihood_interp_points", 500)),
        final_grid_bins=int(parameters.get("final_grid_bins", 256)),
        log_true_flux_min=float(parameters.get("log_true_flux_min", parameters.get("flux_range_min", -4.75))),
        log_true_flux_max=float(parameters.get("log_true_flux_max", parameters.get("flux_range_max", -3.0))),
        marginal_likelihood_range_extension=float(parameters.get("marginal_likelihood_range_extension", 3.0)),
        numerical_epsilon=float(parameters.get("numerical_epsilon", 1e-300)),
        interpolation_method=str(parameters.get("interpolation_method", "linear")),  # type: ignore[arg-type]
    )
