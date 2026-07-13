"""KDE algorithms for measured flux and uncertainty samples."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
from numpy.typing import NDArray
from scipy.stats import gaussian_kde

from flare_bb.core.config import DEFAULT_KDE_CONFIG, KdeConfig


@dataclass(frozen=True)
class KdeResult:
    """Computed KDE grid and generation metadata.

    Parameters
    ----------
    kde_data : NDArray[np.float64]
        Concatenated array with columns ``log_flux``, ``log_uncertainty``, and
        ``log_kde_value``.
    points : NDArray[np.float64]
        Grid points with shape ``(bins * bins, 2)``.
    values : NDArray[np.float64]
        Log KDE values at ``points``.
    config : KdeConfig
        Configuration used for generation.
    """

    kde_data: NDArray[np.float64]
    points: NDArray[np.float64]
    values: NDArray[np.float64]
    config: KdeConfig

    @property
    def metadata(self) -> dict[str, object]:
        """Return serializable metadata for the KDE result."""
        return {
            "kde_parameters": asdict(self.config),
            "data_shapes": {
                "kde_data": self.kde_data.shape,
                "points": self.points.shape,
                "values": self.values.shape,
            },
        }


def compute_kde(data: NDArray[np.float64], config: KdeConfig = DEFAULT_KDE_CONFIG) -> KdeResult:
    """Compute a 2D Gaussian KDE in log flux/log uncertainty space.

    Parameters
    ----------
    data : NDArray[np.float64]
        Input array with shape ``(2, n_samples)``.
    config : KdeConfig
        KDE generation configuration.

    Returns
    -------
    KdeResult
        Computed grid points, log-density values, and metadata.
    """
    config.validate()
    validate_stacked_flux_data(data)
    filtered_data = filter_stacked_flux_data(data, config)
    if filtered_data.shape[1] < 2:
        raise ValueError("At least two samples are required after KDE range filtering.")

    kernel = gaussian_kde(filtered_data, bw_method=config.bandwidth)
    log_flux_grid, log_uncertainty_grid = np.mgrid[
        config.log_flux_min : config.log_flux_max : config.bins * 1j,
        config.log_uncertainty_min : config.log_uncertainty_max : config.bins * 1j,
    ]
    points = np.vstack([log_flux_grid.ravel(), log_uncertainty_grid.ravel()]).T.astype(np.float64)
    densities = np.maximum(
        kernel(np.vstack([log_flux_grid.ravel(), log_uncertainty_grid.ravel()])), np.finfo(float).tiny
    )
    values = np.log(densities).astype(np.float64)
    kde_data = np.concatenate([points, values[:, np.newaxis]], axis=1)
    return KdeResult(kde_data=kde_data, points=points, values=values, config=config)


def filter_stacked_flux_data(data: NDArray[np.float64], config: KdeConfig) -> NDArray[np.float64]:
    """Filter stacked log flux/error data to the KDE grid range.

    Parameters
    ----------
    data : NDArray[np.float64]
        Input array with shape ``(2, n_samples)``.
    config : KdeConfig
        KDE generation configuration.

    Returns
    -------
    NDArray[np.float64]
        Filtered data with shape ``(2, n_filtered_samples)``.
    """
    validate_stacked_flux_data(data)
    log_flux = data[0]
    log_uncertainty = data[1]
    flux_mask = (log_flux >= config.log_flux_min) & (log_flux <= config.log_flux_max)
    uncertainty_mask = (log_uncertainty >= config.log_uncertainty_min) & (log_uncertainty <= config.log_uncertainty_max)
    return data[:, flux_mask & uncertainty_mask]


def validate_stacked_flux_data(data: NDArray[np.float64]) -> None:
    """Validate stacked log flux/error data.

    Parameters
    ----------
    data : NDArray[np.float64]
        Input array expected to have shape ``(2, n_samples)``.

    Raises
    ------
    ValueError
        If the array shape or contents are invalid.
    """
    if data.ndim != 2 or data.shape[0] != 2:
        raise ValueError("KDE input data must have shape (2, n_samples).")
    if data.shape[1] == 0:
        raise ValueError("KDE input data must contain at least one sample.")
    if not np.all(np.isfinite(data)):
        raise ValueError("KDE input data must contain only finite values.")


def create_sample_flux_data(n_points: int = 1000, seed: int = 42) -> NDArray[np.float64]:
    """Create deterministic sample log flux/error data for tests and examples.

    Parameters
    ----------
    n_points : int
        Number of samples to generate.
    seed : int
        Seed for the NumPy random generator.

    Returns
    -------
    NDArray[np.float64]
        Array with shape ``(2, n_points)``.
    """
    if n_points <= 0:
        raise ValueError("n_points must be positive.")
    rng = np.random.default_rng(seed)
    log_flux = rng.uniform(-4.5, -3.0, n_points)
    log_uncertainty = log_flux + rng.normal(0.0, 0.3, n_points) - 1.0
    return np.vstack([log_flux, log_uncertainty]).astype(np.float64)
