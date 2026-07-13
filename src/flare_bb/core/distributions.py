"""Bayesian flux-distribution algorithms."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any, cast

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import trapezoid
from scipy.interpolate import RegularGridInterpolator, interp1d

from flare_bb.core.config import DEFAULT_DISTRIBUTION_CONFIG, DistributionConfig


@dataclass(frozen=True)
class KdeGrid:
    """Structured KDE grid data.

    Parameters
    ----------
    points : NDArray[np.float64]
        Grid points in log flux/log uncertainty space.
    values : NDArray[np.float64]
        Log KDE values at each point.
    resolution : int
        Number of points per grid axis.
    log_flux_range : tuple[float, float]
        Measured log10 flux range.
    log_uncertainty_range : tuple[float, float]
        Measured log10 uncertainty range.
    """

    points: NDArray[np.float64]
    values: NDArray[np.float64]
    resolution: int
    log_flux_range: tuple[float, float]
    log_uncertainty_range: tuple[float, float]


@dataclass(frozen=True)
class DistributionResult:
    """Posterior flux-distribution result.

    Parameters
    ----------
    posterior_pdf_grid : NDArray[np.float64]
        Posterior PDFs with axes measured flux, measured uncertainty, true flux.
    log_true_flux : NDArray[np.float64]
        True log10 flux coordinates.
    log_measured_flux_grid : NDArray[np.float64]
        Measured log10 flux grid.
    log_measured_uncertainty_grid : NDArray[np.float64]
        Measured log10 uncertainty grid.
    log_posterior_pdf_grid : NDArray[np.float64]
        Log posterior values for stable downstream lookup.
    config : DistributionConfig
        Configuration used to build the distributions.
    """

    posterior_pdf_grid: NDArray[np.float64]
    log_true_flux: NDArray[np.float64]
    log_measured_flux_grid: NDArray[np.float64]
    log_measured_uncertainty_grid: NDArray[np.float64]
    log_posterior_pdf_grid: NDArray[np.float64]
    config: DistributionConfig


ArrayFunction2D = Callable[[NDArray[np.float64], NDArray[np.float64]], NDArray[np.float64]]
ArrayFunction3D = Callable[[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]], NDArray[np.float64]]
KdeInterpolator = Any


def extract_kde_grid(points: NDArray[np.float64], values: NDArray[np.float64]) -> KdeGrid:
    """Extract structured grid metadata from flattened KDE arrays.

    Parameters
    ----------
    points : NDArray[np.float64]
        Flattened grid points with shape ``(n_points, 2)``.
    values : NDArray[np.float64]
        Flattened log KDE values with shape ``(n_points,)``.

    Returns
    -------
    KdeGrid
        Structured grid metadata.
    """
    if points.ndim != 2 or points.shape[1] != 2:
        raise ValueError("KDE points must have shape (n_points, 2).")
    if values.ndim != 1 or values.shape[0] != points.shape[0]:
        raise ValueError("KDE values must have shape (n_points,) matching points.")
    resolution_float = np.sqrt(points.shape[0])
    resolution = int(resolution_float)
    if resolution * resolution != points.shape[0]:
        raise ValueError("KDE points must describe a square grid.")
    if not np.all(np.isfinite(points)) or not np.all(np.isfinite(values)):
        raise ValueError("KDE points and values must be finite.")

    return KdeGrid(
        points=points,
        values=values,
        resolution=resolution,
        log_flux_range=(float(np.min(points[:, 0])), float(np.max(points[:, 0]))),
        log_uncertainty_range=(float(np.min(points[:, 1])), float(np.max(points[:, 1]))),
    )


def normalize_kde(grid: KdeGrid) -> NDArray[np.float64]:
    """Normalize flattened log KDE values to integrate to one.

    Parameters
    ----------
    grid : KdeGrid
        Structured KDE grid data.

    Returns
    -------
    NDArray[np.float64]
        Normalized log KDE values.
    """
    x_coords, y_coords, probability_grid = reshape_kde_grid(grid, np.exp(grid.values))
    total_probability = trapezoid(trapezoid(probability_grid, y_coords, axis=1), x_coords)
    if total_probability <= 0 or not np.isfinite(total_probability):
        raise ValueError("KDE normalization is not positive and finite.")
    return cast("NDArray[np.float64]", grid.values - np.log(total_probability))


def create_kde_interpolator(
    grid: KdeGrid,
    normalized_values: NDArray[np.float64],
    config: DistributionConfig,
) -> KdeInterpolator:
    """Create a regular-grid interpolator for normalized log KDE values.

    Parameters
    ----------
    grid : KdeGrid
        Structured KDE grid data.
    normalized_values : NDArray[np.float64]
        Flattened normalized log KDE values.
    config : DistributionConfig
        Distribution configuration.

    Returns
    -------
    RegularGridInterpolator
        Interpolator over measured log flux and log uncertainty.
    """
    x_coords, y_coords, value_grid = reshape_kde_grid(grid, normalized_values)
    return RegularGridInterpolator(
        (x_coords, y_coords),
        value_grid,
        method=config.interpolation_method,
        bounds_error=False,
        fill_value=-np.inf,
    )


def calculate_high_definition_normalization(
    kde_interpolator: KdeInterpolator,
    grid: KdeGrid,
    config: DistributionConfig,
) -> float:
    """Calculate interpolated KDE normalization on a high-definition grid.

    Parameters
    ----------
    kde_interpolator : RegularGridInterpolator
        Interpolator over normalized log KDE values.
    grid : KdeGrid
        Structured KDE grid data.
    config : DistributionConfig
        Distribution configuration.

    Returns
    -------
    float
        Normalization factor.
    """
    log_flux_min, log_flux_max = grid.log_flux_range
    log_uncertainty_min, log_uncertainty_max = grid.log_uncertainty_range
    log_flux_grid, log_uncertainty_grid = np.mgrid[
        log_flux_min : log_flux_max : config.high_definition_resolution * 1j,
        log_uncertainty_min : log_uncertainty_max : config.high_definition_resolution * 1j,
    ]
    interpolated = kde_interpolator((log_flux_grid.ravel(), log_uncertainty_grid.ravel()))
    density_grid = np.exp(interpolated.reshape(log_flux_grid.shape))
    return float(trapezoid(trapezoid(density_grid, log_uncertainty_grid[0, :], axis=1), log_flux_grid[:, 0]))


def create_kde_prior_pdf(kde_interpolator: KdeInterpolator, normalization: float) -> ArrayFunction2D:
    """Create a prior PDF from a normalized KDE interpolator.

    Parameters
    ----------
    kde_interpolator : RegularGridInterpolator
        Interpolator over normalized log KDE values.
    normalization : float
        Positive normalization factor.

    Returns
    -------
    ArrayFunction2D
        Prior PDF over measured log flux/log uncertainty.
    """
    if normalization <= 0 or not np.isfinite(normalization):
        raise ValueError("KDE prior normalization must be positive and finite.")

    def kde_prior_pdf(
        log_measured_flux: NDArray[np.float64],
        log_measured_uncertainty: NDArray[np.float64],
    ) -> NDArray[np.float64]:
        interpolated = kde_interpolator((log_measured_flux, log_measured_uncertainty))
        return cast("NDArray[np.float64]", np.exp(interpolated) / normalization)

    return kde_prior_pdf


def create_likelihood_pdf(config: DistributionConfig) -> ArrayFunction3D:
    r"""Create the log-normal likelihood PDF $p(F_R \mid F_m, \sigma_m)$.

    Parameters
    ----------
    config : DistributionConfig
        Distribution configuration.

    Returns
    -------
    ArrayFunction3D
        Likelihood PDF over true log flux, measured log flux, and measured log
        uncertainty.
    """
    sqrt_2pi = config.sqrt_2pi

    def likelihood_pdf(
        log_true_flux: NDArray[np.float64],
        log_measured_flux: NDArray[np.float64],
        log_measured_uncertainty: NDArray[np.float64],
    ) -> NDArray[np.float64]:
        measured_flux_linear = 10.0**log_measured_flux
        measured_uncertainty_linear = 10.0**log_measured_uncertainty
        true_flux_linear = 10.0**log_true_flux
        sigma = np.log(measured_flux_linear + measured_uncertainty_linear) - np.log(measured_flux_linear)
        mu = np.log(measured_flux_linear) - 0.5 * sigma**2
        return cast(
            "NDArray[np.float64]",
            np.exp(-((np.log(true_flux_linear) - mu) ** 2) / (2.0 * sigma**2)) / (true_flux_linear * sigma * sqrt_2pi),
        )

    return likelihood_pdf


def calculate_marginal_likelihood(
    likelihood_pdf: ArrayFunction3D,
    kde_prior_pdf: ArrayFunction2D,
    grid: KdeGrid,
    config: DistributionConfig,
) -> Callable[[NDArray[np.float64]], NDArray[np.float64]]:
    r"""Calculate the marginal likelihood $p(F_R)$.

    Parameters
    ----------
    likelihood_pdf : ArrayFunction3D
        Likelihood PDF.
    kde_prior_pdf : ArrayFunction2D
        Prior PDF from KDE data.
    grid : KdeGrid
        Structured KDE grid data.
    config : DistributionConfig
        Distribution configuration.

    Returns
    -------
    Callable[[NDArray[np.float64]], NDArray[np.float64]]
        Vectorized marginal likelihood function.
    """
    log_flux_min, log_flux_max = grid.log_flux_range
    log_uncertainty_min, log_uncertainty_max = grid.log_uncertainty_range
    log_measured_flux_grid, log_measured_uncertainty_grid = np.mgrid[
        log_flux_min : log_flux_max : config.marginal_likelihood_resolution * 1j,
        log_uncertainty_min : log_uncertainty_max : config.marginal_likelihood_resolution * 1j,
    ]
    prior_values = kde_prior_pdf(log_measured_flux_grid, log_measured_uncertainty_grid)

    def marginal_likelihood_for_scalar(log_true_flux: float) -> float:
        log_true_flux_grid = np.full_like(log_measured_flux_grid, log_true_flux)
        likelihood_values = likelihood_pdf(log_true_flux_grid, log_measured_flux_grid, log_measured_uncertainty_grid)
        jacobian = (10.0**log_true_flux) * config.log_10
        integrand = likelihood_values * prior_values * jacobian
        return float(
            trapezoid(trapezoid(integrand, log_measured_uncertainty_grid[0, :], axis=1), log_measured_flux_grid[:, 0])
        )

    def marginal_likelihood(log_true_flux: NDArray[np.float64]) -> NDArray[np.float64]:
        values = [marginal_likelihood_for_scalar(float(value)) for value in np.ravel(log_true_flux)]
        return np.asarray(values, dtype=np.float64).reshape(np.shape(log_true_flux))

    return marginal_likelihood


def create_marginal_likelihood_interpolator(
    marginal_likelihood: Callable[[NDArray[np.float64]], NDArray[np.float64]],
    grid: KdeGrid,
    config: DistributionConfig,
) -> Callable[[NDArray[np.float64]], NDArray[np.float64]]:
    """Create an interpolated marginal-likelihood function.

    Parameters
    ----------
    marginal_likelihood : Callable[[NDArray[np.float64]], NDArray[np.float64]]
        Marginal-likelihood function to tabulate.
    grid : KdeGrid
        Structured KDE grid data.
    config : DistributionConfig
        Distribution configuration.

    Returns
    -------
    Callable[[NDArray[np.float64]], NDArray[np.float64]]
        Interpolated marginal likelihood.
    """
    flux_min, flux_max = config.extended_marginal_likelihood_range(*grid.log_flux_range)
    log_true_flux = np.linspace(flux_min, flux_max, config.marginal_likelihood_interp_points)
    marginal_values = np.maximum(marginal_likelihood(log_true_flux), config.numerical_epsilon)
    interpolator = interp1d(
        log_true_flux,
        np.log(marginal_values),
        kind=config.interpolation_method,
        bounds_error=False,
        fill_value="extrapolate",
    )

    def interpolated_marginal_likelihood(log_true_flux_values: NDArray[np.float64]) -> NDArray[np.float64]:
        return cast("NDArray[np.float64]", np.exp(interpolator(log_true_flux_values)))

    return interpolated_marginal_likelihood


def create_posterior_pdf(
    likelihood_pdf: ArrayFunction3D,
    kde_prior_pdf: ArrayFunction2D,
    marginal_likelihood_pdf: Callable[[NDArray[np.float64]], NDArray[np.float64]],
    config: DistributionConfig,
) -> ArrayFunction3D:
    r"""Create the posterior PDF $p(F_m, \sigma_m \mid F_R)$.

    Parameters
    ----------
    likelihood_pdf : ArrayFunction3D
        Likelihood PDF.
    kde_prior_pdf : ArrayFunction2D
        Prior PDF from KDE data.
    marginal_likelihood_pdf : Callable[[NDArray[np.float64]], NDArray[np.float64]]
        Marginal likelihood PDF.
    config : DistributionConfig
        Distribution configuration.

    Returns
    -------
    ArrayFunction3D
        Posterior PDF.
    """

    def posterior_pdf(
        log_true_flux: NDArray[np.float64],
        log_measured_flux: NDArray[np.float64],
        log_measured_uncertainty: NDArray[np.float64],
    ) -> NDArray[np.float64]:
        likelihood_values = likelihood_pdf(log_true_flux, log_measured_flux, log_measured_uncertainty)
        jacobian = (10.0**log_true_flux) * config.log_10
        prior_values = kde_prior_pdf(log_measured_flux, log_measured_uncertainty)
        marginal_values = np.maximum(marginal_likelihood_pdf(log_true_flux), config.numerical_epsilon)
        return likelihood_values * jacobian * prior_values / marginal_values

    return posterior_pdf


def generate_flux_distributions(
    posterior_pdf: ArrayFunction3D,
    grid: KdeGrid,
    config: DistributionConfig,
    progress: Callable[[Iterable[float]], Iterable[float]] | None = None,
) -> DistributionResult:
    """Generate posterior distributions over the configured true flux range.

    Parameters
    ----------
    posterior_pdf : ArrayFunction3D
        Posterior PDF.
    grid : KdeGrid
        Structured KDE grid data.
    config : DistributionConfig
        Distribution configuration.
    progress : Callable[[Iterable[float]], Iterable[float]] | None
        Optional iterator wrapper for progress reporting.

    Returns
    -------
    DistributionResult
        Posterior distribution grids.
    """
    log_flux_min, log_flux_max = grid.log_flux_range
    log_uncertainty_min, log_uncertainty_max = grid.log_uncertainty_range
    log_true_flux_min, log_true_flux_max = config.log_true_flux_range
    log_true_flux = np.linspace(log_true_flux_min, log_true_flux_max, config.final_grid_bins)
    log_measured_flux_grid, log_measured_uncertainty_grid = np.mgrid[
        log_flux_min : log_flux_max : config.final_grid_bins * 1j,
        log_uncertainty_min : log_uncertainty_max : config.final_grid_bins * 1j,
    ]

    true_flux_iterable = progress(log_true_flux) if progress is not None else log_true_flux
    posterior_slices = []
    measured_flux_flat = log_measured_flux_grid.ravel()
    measured_uncertainty_flat = log_measured_uncertainty_grid.ravel()
    for true_flux_value in true_flux_iterable:
        true_flux_flat = np.full_like(measured_flux_flat, true_flux_value)
        posterior_slice = posterior_pdf(true_flux_flat, measured_flux_flat, measured_uncertainty_flat)
        posterior_slices.append(posterior_slice.reshape(log_measured_flux_grid.shape))

    posterior_pdf_grid = np.moveaxis(np.asarray(posterior_slices, dtype=np.float64), 0, 2)
    log_posterior_pdf_grid = np.log(posterior_pdf_grid + config.numerical_epsilon)
    return DistributionResult(
        posterior_pdf_grid=posterior_pdf_grid,
        log_true_flux=log_true_flux,
        log_measured_flux_grid=log_measured_flux_grid,
        log_measured_uncertainty_grid=log_measured_uncertainty_grid,
        log_posterior_pdf_grid=log_posterior_pdf_grid,
        config=config,
    )


def build_flux_distributions(
    points: NDArray[np.float64],
    values: NDArray[np.float64],
    config: DistributionConfig = DEFAULT_DISTRIBUTION_CONFIG,
    progress: Callable[[Iterable[float]], Iterable[float]] | None = None,
) -> DistributionResult:
    """Build posterior flux distributions from flattened KDE data.

    Parameters
    ----------
    points : NDArray[np.float64]
        Flattened KDE grid points.
    values : NDArray[np.float64]
        Flattened log KDE values.
    config : DistributionConfig
        Distribution configuration.
    progress : Callable[[Iterable[float]], Iterable[float]] | None
        Optional iterator wrapper for progress reporting.

    Returns
    -------
    DistributionResult
        Computed posterior flux distributions.
    """
    config.validate()
    grid = extract_kde_grid(points, values)
    normalized_values = normalize_kde(grid)
    kde_interpolator = create_kde_interpolator(grid, normalized_values, config)
    normalization = calculate_high_definition_normalization(kde_interpolator, grid, config)
    kde_prior_pdf = create_kde_prior_pdf(kde_interpolator, normalization)
    likelihood_pdf = create_likelihood_pdf(config)
    marginal_likelihood = calculate_marginal_likelihood(likelihood_pdf, kde_prior_pdf, grid, config)
    marginal_likelihood_pdf = create_marginal_likelihood_interpolator(marginal_likelihood, grid, config)
    posterior_pdf = create_posterior_pdf(likelihood_pdf, kde_prior_pdf, marginal_likelihood_pdf, config)
    return generate_flux_distributions(posterior_pdf, grid, config, progress=progress)


def reshape_kde_grid(
    grid: KdeGrid, values: NDArray[np.float64]
) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    """Reshape flattened KDE values into a regular grid.

    Parameters
    ----------
    grid : KdeGrid
        Structured KDE grid data.
    values : NDArray[np.float64]
        Flattened values with shape ``(resolution * resolution,)``.

    Returns
    -------
    tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]
        X coordinates, Y coordinates, and reshaped value grid.
    """
    if values.shape != grid.values.shape:
        raise ValueError("Values must have the same shape as the KDE grid values.")
    point_grid = grid.points.reshape(grid.resolution, grid.resolution, 2)
    x_coords = point_grid[:, 0, 0]
    y_coords = point_grid[0, :, 1]
    value_grid = values.reshape(grid.resolution, grid.resolution)
    return x_coords, y_coords, value_grid
