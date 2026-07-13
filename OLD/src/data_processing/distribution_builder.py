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
# Core algorithms for building flux distributions from KDE data.
#

from dataclasses import dataclass
from typing import Callable, Tuple

import numpy as np
from scipy.integrate import trapezoid
from scipy.interpolate import RegularGridInterpolator, interp1d
from tqdm import tqdm

from .distribution_config import DEFAULT_CONFIG, DistributionConfig


@dataclass
class KDEGridData:
    """Container for KDE grid data and metadata."""

    points: np.ndarray
    """Grid points in 2D space."""

    values: np.ndarray
    """KDE values at grid points."""

    resolution: int
    """Grid resolution (points per dimension)."""

    x_range: Tuple[float, float]
    """Range of x-axis values (x_low, x_high)."""

    y_range: Tuple[float, float]
    """Range of y-axis values (y_low, y_high)."""


@dataclass
class DistributionResult:
    """Container for flux distribution calculation results."""

    posterior_pdf_grid: np.ndarray
    """3D array of posterior probability density functions p(F_m, σ_m | F_R)."""

    flux_range: np.ndarray
    """Array of true flux values F_R."""

    log_measured_flux_grid: np.ndarray
    """Grid of measured flux values F_m (log scale)."""

    log_measured_uncertainty_grid: np.ndarray
    """Grid of measured uncertainty values σ_m (log scale)."""

    log_posterior_pdf_grid: np.ndarray
    """Log-transformed posterior PDF values for numerical stability."""

    config: DistributionConfig
    """Configuration used for generation."""


def extract_kde_grid_data(points: np.ndarray, values: np.ndarray) -> KDEGridData:
    """
    Extract grid information from KDE points and values.

    :param points: Array of 2D grid points
    :type points: np.ndarray
    :param values: Array of KDE values at grid points
    :type values: np.ndarray
    :returns: Structured grid data
    :rtype: KDEGridData
    """
    resolution = int(np.sqrt(points.shape[0]))
    x_low, x_high = points[:, 0].min(), points[:, 0].max()
    y_low, y_high = points[:, 1].min(), points[:, 1].max()

    return KDEGridData(
        points=points, values=values, resolution=resolution, x_range=(x_low, x_high), y_range=(y_low, y_high)
    )


def normalize_kde(grid_data: KDEGridData) -> Tuple[np.ndarray, np.ndarray]:
    """
    Normalize the KDE values to form a proper probability distribution.

    :param grid_data: KDE grid data to normalize
    :type grid_data: KDEGridData
    :returns: Tuple of (normalized_values, grid_coordinates)
    :rtype: Tuple[np.ndarray, np.ndarray]
    """
    resolution = grid_data.resolution
    points = grid_data.points
    values = grid_data.values

    # Extract coordinates and reshape to grid
    x_coords = points[:, 0].reshape((resolution, resolution)).T[0, :]
    y_coords = points[:, 1].reshape((resolution, resolution))[0, :]
    probability_grid = np.exp(values).reshape((resolution, resolution)).T

    # Normalize using trapezoidal integration
    total_probability = trapezoid(trapezoid(probability_grid, x_coords), y_coords)
    normalized_values = values - np.log(total_probability)

    return normalized_values, (x_coords, y_coords)


def create_kde_interpolator(
    grid_data: KDEGridData, normalized_values: np.ndarray, config: DistributionConfig = DEFAULT_CONFIG
) -> RegularGridInterpolator:
    """
    Create an interpolator for the normalized KDE.

    :param grid_data: KDE grid data
    :type grid_data: KDEGridData
    :param normalized_values: Normalized KDE values
    :type normalized_values: np.ndarray
    :param config: Configuration parameters
    :type config: DistributionConfig
    :returns: KDE interpolator function
    :rtype: RegularGridInterpolator
    """
    resolution = grid_data.resolution
    points = grid_data.points

    # Create coordinate grids
    x_grid = points[:, 0].reshape((resolution, resolution))
    y_grid = points[:, 1].reshape((resolution, resolution))

    # Create interpolator
    interpolator = RegularGridInterpolator(
        (x_grid[:, 0], y_grid[0, :]),
        normalized_values.reshape(resolution, resolution),
        method=config.interpolation_method,
    )

    return interpolator


def calculate_high_definition_normalization(
    kde_interpolator: RegularGridInterpolator, grid_data: KDEGridData, config: DistributionConfig = DEFAULT_CONFIG
) -> float:
    """
    Calculate normalization factor using high-definition grid evaluation.

    :param kde_interpolator: KDE interpolator function
    :type kde_interpolator: RegularGridInterpolator
    :param grid_data: Original grid data for range information
    :type grid_data: KDEGridData
    :param config: Configuration parameters
    :type config: DistributionConfig
    :returns: Normalization factor
    :rtype: float
    """
    x_low, x_high = grid_data.x_range
    y_low, y_high = grid_data.y_range
    hd_resolution = config.high_definition_resolution

    # Create high-definition grid
    x_hd, y_hd = np.mgrid[x_low : x_high : hd_resolution * 1j, y_low : y_high : hd_resolution * 1j]

    # Evaluate KDE on high-definition grid
    z_hd = np.exp(kde_interpolator((x_hd.flatten(), y_hd.flatten())).reshape(x_hd.shape))

    # Calculate normalization
    normalization = trapezoid(trapezoid(z_hd, x_hd[:, 0]), y_hd[0, :])

    return normalization


def create_kde_prior_pdf_function(
    kde_interpolator: RegularGridInterpolator, normalization: float
) -> Callable[[np.ndarray, np.ndarray], np.ndarray]:
    """
    Create the prior probability density function p(F_m, σ_m) from KDE interpolator.

    :param kde_interpolator: KDE interpolator function
    :type kde_interpolator: RegularGridInterpolator
    :param normalization: Normalization factor
    :type normalization: float
    :returns: Prior PDF function p(F_m, σ_m)
    :rtype: Callable[[np.ndarray, np.ndarray], np.ndarray]
    """

    def kde_prior_pdf(log_measured_flux: np.ndarray, log_measured_uncertainty: np.ndarray) -> np.ndarray:
        """
        Evaluate the prior probability density function p(F_m, σ_m).

        :param log_measured_flux: Measured flux values F_m (log scale)
        :type log_measured_flux: np.ndarray
        :param log_measured_uncertainty: Measured uncertainty values σ_m (log scale)
        :type log_measured_uncertainty: np.ndarray
        :returns: Prior PDF values p(F_m, σ_m)
        :rtype: np.ndarray
        """
        return np.exp(kde_interpolator((log_measured_flux, log_measured_uncertainty))) / normalization

    return kde_prior_pdf


def create_likelihood_pdf(
    config: DistributionConfig = DEFAULT_CONFIG,
) -> Callable[[np.ndarray, np.ndarray, np.ndarray], np.ndarray]:
    """
    Create likelihood probability density function p(F_R | F_m, σ_m).

    The likelihood models the probability of the true flux F_R given the measured
    flux F_m and uncertainty σ_m, assuming log-normal measurement uncertainties.

    :param config: Configuration parameters
    :type config: DistributionConfig
    :returns: Likelihood PDF function p(F_R | F_m, σ_m)
    :rtype: Callable[[np.ndarray, np.ndarray, np.ndarray], np.ndarray]
    """
    sqrt_2pi = config.sqrt_2pi
    log_10 = config.log_10

    def likelihood_pdf(
        log_true_flux: np.ndarray, log_measured_flux: np.ndarray, log_measured_uncertainty: np.ndarray
    ) -> np.ndarray:
        """
        Evaluate likelihood PDF p(F_R | F_m, σ_m).

        :param log_true_flux: True flux values F_R (log scale)
        :type log_true_flux: np.ndarray
        :param log_measured_flux: Measured flux values F_m (log scale)
        :type log_measured_flux: np.ndarray
        :param log_measured_uncertainty: Measured uncertainty values σ_m (log scale)
        :type log_measured_uncertainty: np.ndarray
        :returns: Likelihood PDF values p(F_R | F_m, σ_m)
        :rtype: np.ndarray
        """
        # Convert to linear scale
        measured_flux_linear = 10**log_measured_flux
        measured_uncertainty_linear = 10**log_measured_uncertainty

        # Calculate log-normal parameters (Equations 3-4 from measurement model)
        sigma = np.log(measured_flux_linear + measured_uncertainty_linear) - np.log(measured_flux_linear)
        mu = np.log(measured_flux_linear) - 0.5 * sigma**2

        # True flux in linear scale
        true_flux_linear = 10**log_true_flux

        # Log-normal PDF (Equation 3 from measurement model)
        return (
            1 / (true_flux_linear * sigma * sqrt_2pi) * np.exp(-((np.log(true_flux_linear) - mu) ** 2) / (2 * sigma**2))
        )

    return likelihood_pdf


def calculate_marginal_likelihood(
    likelihood_pdf: Callable,
    kde_prior_pdf: Callable,
    grid_data: KDEGridData,
    config: DistributionConfig = DEFAULT_CONFIG,
) -> Callable[[np.ndarray], np.ndarray]:
    """
    Calculate marginal likelihood p(F_R) using the Law of Total Probability.

    :param likelihood_pdf: Likelihood PDF function p(F_R | F_m, σ_m)
    :type likelihood_pdf: Callable
    :param kde_prior_pdf: Prior PDF function p(F_m, σ_m) from KDE
    :type kde_prior_pdf: Callable
    :param grid_data: Grid data for integration bounds
    :type grid_data: KDEGridData
    :param config: Configuration parameters
    :type config: DistributionConfig
    :returns: Marginal likelihood function p(F_R)
    :rtype: Callable[[np.ndarray], np.ndarray]
    """
    x_low, x_high = grid_data.x_range
    y_low, y_high = grid_data.y_range
    log_10 = config.log_10

    def marginal_likelihood(log_true_flux: float) -> float:
        """
        Calculate marginal likelihood p(F_R) for a given true flux value.

        :param log_true_flux: True flux value F_R (log scale)
        :type log_true_flux: float
        :returns: Marginal likelihood p(F_R)
        :rtype: float
        """

        def integrand(log_measured_flux: np.ndarray, log_measured_uncertainty: np.ndarray) -> np.ndarray:
            """Integration kernel for marginal likelihood calculation (Equation 5)."""
            return (
                likelihood_pdf(log_true_flux, log_measured_flux, log_measured_uncertainty)
                * kde_prior_pdf(log_measured_flux, log_measured_uncertainty)
                * 10**log_true_flux
                * log_10
            )

        # Create integration grid
        resolution = config.marginal_likelihood_resolution
        log_measured_flux_grid, log_measured_uncertainty_grid = np.mgrid[
            x_low : x_high : resolution * 1j, y_low : y_high : resolution * 1j
        ]

        # Evaluate integrand
        integrand_values = integrand(log_measured_flux_grid, log_measured_uncertainty_grid)

        # Integrate using trapezoidal rule
        return trapezoid(trapezoid(integrand_values, log_measured_flux_grid[:, 0]), log_measured_uncertainty_grid[0, :])

    # Vectorize for array inputs
    return np.vectorize(marginal_likelihood)


def create_marginal_likelihood_interpolator(
    marginal_likelihood_function: Callable, grid_data: KDEGridData, config: DistributionConfig = DEFAULT_CONFIG
) -> Callable[[np.ndarray], np.ndarray]:
    """
    Create interpolated marginal likelihood function for efficient evaluation.

    :param marginal_likelihood_function: Marginal likelihood function p(F_R)
    :type marginal_likelihood_function: Callable
    :param grid_data: Grid data for range determination
    :type grid_data: KDEGridData
    :param config: Configuration parameters
    :type config: DistributionConfig
    :returns: Interpolated marginal likelihood function p(F_R)
    :rtype: Callable[[np.ndarray], np.ndarray]
    """
    x_low, x_high = grid_data.x_range

    # Calculate marginal likelihood values over extended range
    extended_range = config.get_extended_marginal_likelihood_range(x_low, x_high)
    flux_values = np.linspace(extended_range[0], extended_range[1], config.marginal_likelihood_interp_points)
    marginal_likelihood_values = marginal_likelihood_function(flux_values)

    # Create interpolator using log values for better numerical accuracy
    log_marginal_likelihood_values = np.log(marginal_likelihood_values)
    interpolator = interp1d(flux_values, log_marginal_likelihood_values, kind=config.interpolation_method)

    def interpolated_marginal_likelihood(log_true_flux: np.ndarray) -> np.ndarray:
        """
        Evaluate interpolated marginal likelihood p(F_R).

        :param log_true_flux: True flux values F_R (log scale)
        :type log_true_flux: np.ndarray
        :returns: Marginal likelihood values p(F_R)
        :rtype: np.ndarray
        """
        return np.exp(interpolator(log_true_flux))

    return np.vectorize(interpolated_marginal_likelihood)


def create_posterior_pdf(
    likelihood_pdf: Callable,
    kde_prior_pdf: Callable,
    marginal_likelihood_pdf: Callable,
    config: DistributionConfig = DEFAULT_CONFIG,
) -> Callable[[np.ndarray, np.ndarray, np.ndarray], np.ndarray]:
    """
    Create the posterior probability density function p(F_m, σ_m | F_R) using Bayes' theorem.

    :param likelihood_pdf: Likelihood PDF function p(F_R | F_m, σ_m)
    :type likelihood_pdf: Callable
    :param kde_prior_pdf: Prior PDF function p(F_m, σ_m) from KDE
    :type kde_prior_pdf: Callable
    :param marginal_likelihood_pdf: Marginal likelihood function p(F_R)
    :type marginal_likelihood_pdf: Callable
    :param config: Configuration parameters
    :type config: DistributionConfig
    :returns: Posterior PDF function p(F_m, σ_m | F_R)
    :rtype: Callable[[np.ndarray, np.ndarray, np.ndarray], np.ndarray]
    """
    log_10 = config.log_10

    def posterior_pdf(
        log_true_flux: np.ndarray, log_measured_flux: np.ndarray, log_measured_uncertainty: np.ndarray
    ) -> np.ndarray:
        """
        Evaluate the posterior probability density function p(F_m, σ_m | F_R) using Bayes' theorem.

        :param log_true_flux: True flux values F_R (log scale)
        :type log_true_flux: np.ndarray
        :param log_measured_flux: Measured flux values F_m (log scale)
        :type log_measured_flux: np.ndarray
        :param log_measured_uncertainty: Measured uncertainty values σ_m (log scale)
        :type log_measured_uncertainty: np.ndarray
        :returns: Posterior PDF values p(F_m, σ_m | F_R)
        :rtype: np.ndarray
        """
        # Bayes' theorem: p(F_m, σ_m | F_R) = p(F_R | F_m, σ_m) * p(F_m, σ_m) / p(F_R)
        likelihood_value = likelihood_pdf(log_true_flux, log_measured_flux, log_measured_uncertainty)
        jacobian_factor = 10**log_true_flux * log_10

        return (
            likelihood_value
            * jacobian_factor
            * kde_prior_pdf(log_measured_flux, log_measured_uncertainty)
            / marginal_likelihood_pdf(log_true_flux)
        )

    return np.vectorize(posterior_pdf)


def generate_flux_distributions(
    posterior_pdf: Callable, grid_data: KDEGridData, config: DistributionConfig = DEFAULT_CONFIG, verbose: bool = False
) -> DistributionResult:
    """
    Generate flux probability distributions over the specified ranges.

    :param posterior_pdf: Posterior PDF function p(F_m, σ_m | F_R)
    :type posterior_pdf: Callable
    :param grid_data: Grid data for coordinate ranges
    :type grid_data: KDEGridData
    :param config: Configuration parameters
    :type config: DistributionConfig
    :param verbose: Whether to show progress information
    :type verbose: bool
    :returns: Complete distribution results
    :rtype: DistributionResult
    """
    # Get coordinate ranges
    x_low, x_high = grid_data.x_range
    y_low, y_high = grid_data.y_range
    flux_min, flux_max = config.get_flux_range()

    # Create coordinate arrays
    nbins = config.final_grid_bins
    log_measured_flux_coords = np.linspace(x_low, x_high, nbins)
    log_measured_uncertainty_coords = np.linspace(y_low, y_high, nbins)
    log_true_flux_coords = np.linspace(flux_min, flux_max, nbins)

    # Create 2D grids for measured quantities
    log_measured_flux_grid, log_measured_uncertainty_grid = np.mgrid[
        x_low : x_high : nbins * 1j, y_low : y_high : nbins * 1j
    ]

    # Generate posterior PDFs for each true flux value with optional progress tracking
    if verbose:
        print("🔄 Computing posterior PDFs for each true flux value...")

    posterior_pdf_values = []

    flux_iterator = (
        tqdm(log_true_flux_coords, desc="Generating flux PDFs", unit="flux") if verbose else log_true_flux_coords
    )

    for log_true_flux in flux_iterator:
        pdf_values = posterior_pdf(
            log_true_flux, log_measured_flux_grid.flatten(), log_measured_uncertainty_grid.flatten()
        ).reshape(log_measured_flux_grid.shape)
        posterior_pdf_values.append(pdf_values)

    # Convert to numpy array and reorder axes
    posterior_pdf_grid = np.array(posterior_pdf_values)
    posterior_pdf_grid = np.moveaxis(posterior_pdf_grid, 0, 2)  # Move flux axis to last dimension

    # Calculate log values for numerical stability
    log_posterior_pdf_grid = np.log(posterior_pdf_grid + config.numerical_epsilon)

    return DistributionResult(
        posterior_pdf_grid=posterior_pdf_grid,
        flux_range=log_true_flux_coords,
        log_measured_flux_grid=log_measured_flux_grid,
        log_measured_uncertainty_grid=log_measured_uncertainty_grid,
        log_posterior_pdf_grid=log_posterior_pdf_grid,
        config=config,
    )


def build_flux_distributions(
    points: np.ndarray, values: np.ndarray, config: DistributionConfig = DEFAULT_CONFIG, verbose: bool = False
) -> DistributionResult:
    """
    Complete workflow for building flux distributions from KDE data.

    This is the main entry point that orchestrates the entire distribution
    building process from normalized KDE data to final probability distributions.

    :param points: Array of 2D grid points from KDE
    :type points: np.ndarray
    :param values: Array of KDE values at grid points
    :type values: np.ndarray
    :param config: Configuration parameters
    :type config: DistributionConfig
    :param verbose: Whether to show progress information
    :type verbose: bool
    :returns: Complete distribution results
    :rtype: DistributionResult
    :raises ValueError: If configuration is invalid
    """
    # Validate configuration
    config.validate()

    if verbose:
        print("🔧 Step 1/5: Extracting and normalizing KDE data...")
    # Extract and prepare grid data
    grid_data = extract_kde_grid_data(points, values)
    normalized_values, _ = normalize_kde(grid_data)

    if verbose:
        print("🔧 Step 2/5: Creating KDE interpolators...")
    # Create KDE interpolator and calculate normalization
    kde_interpolator = create_kde_interpolator(grid_data, normalized_values, config)
    normalization = calculate_high_definition_normalization(kde_interpolator, grid_data, config)

    if verbose:
        print("🔧 Step 3/5: Setting up probability density functions...")
    # Create PDF functions following Bayes' theorem
    kde_prior_pdf = create_kde_prior_pdf_function(kde_interpolator, normalization)
    likelihood_pdf = create_likelihood_pdf(config)

    if verbose:
        print("🔧 Step 4/5: Computing marginal likelihood (this may take several minutes)...")
    # Calculate marginal likelihood p(F_R) using the Law of Total Probability
    marginal_likelihood_function = calculate_marginal_likelihood(likelihood_pdf, kde_prior_pdf, grid_data, config)
    marginal_likelihood_pdf = create_marginal_likelihood_interpolator(marginal_likelihood_function, grid_data, config)

    if verbose:
        print("🔧 Step 5/5: Building posterior distributions...")
    # Create posterior PDF using Bayes' theorem and generate distributions
    posterior_pdf = create_posterior_pdf(likelihood_pdf, kde_prior_pdf, marginal_likelihood_pdf, config)

    return generate_flux_distributions(posterior_pdf, grid_data, config, verbose=verbose)
