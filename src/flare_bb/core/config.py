"""Configuration objects for FLARE-BB numerical workflows."""

from __future__ import annotations

from dataclasses import dataclass
from math import log, pi, sqrt
from typing import Literal

InterpolationMethod = Literal["linear", "nearest"]


@dataclass(frozen=True)
class KdeConfig:
    """Configuration for two-dimensional KDE generation.

    Parameters
    ----------
    bandwidth : float
        Gaussian KDE bandwidth method passed to SciPy.
    bins : int
        Number of grid bins in each dimension.
    log_flux_min : float
        Lower bound for the measured log10 flux grid.
    log_flux_max : float
        Upper bound for the measured log10 flux grid.
    log_uncertainty_min : float
        Lower bound for the measured log10 uncertainty grid.
    log_uncertainty_max : float
        Upper bound for the measured log10 uncertainty grid.
    ts_threshold : int
        Minimum test statistic used when extracting observed measurements.
    ts_min : int
        Minimum test statistic requested from the Fermi LCR service.
    flux_type : str
        Fermi LCR flux type to use.
    """

    bandwidth: float = 0.2
    bins: int = 512
    log_flux_min: float = -4.9
    log_flux_max: float = -2.8
    log_uncertainty_min: float = -5.35
    log_uncertainty_max: float = -3.25
    ts_threshold: int = 19
    ts_min: int = 4
    flux_type: str = "energy"

    def validate(self) -> None:
        """Validate KDE configuration values.

        Raises
        ------
        ValueError
            If a configuration value is outside the supported range.
        """
        if self.bandwidth <= 0:
            raise ValueError("KDE bandwidth must be positive.")
        if self.bins <= 1:
            raise ValueError("KDE bins must be greater than one.")
        if self.log_flux_min >= self.log_flux_max:
            raise ValueError("log_flux_min must be less than log_flux_max.")
        if self.log_uncertainty_min >= self.log_uncertainty_max:
            raise ValueError("log_uncertainty_min must be less than log_uncertainty_max.")
        if self.ts_threshold < 0:
            raise ValueError("ts_threshold must be non-negative.")
        if self.ts_min < 0:
            raise ValueError("ts_min must be non-negative.")
        if self.flux_type not in {"energy", "photon"}:
            raise ValueError("flux_type must be 'energy' or 'photon'.")

    @property
    def log_flux_range(self) -> tuple[float, float]:
        """Return the measured log10 flux range."""
        return self.log_flux_min, self.log_flux_max

    @property
    def log_uncertainty_range(self) -> tuple[float, float]:
        """Return the measured log10 uncertainty range."""
        return self.log_uncertainty_min, self.log_uncertainty_max


@dataclass(frozen=True)
class DistributionConfig:
    """Configuration for Bayesian flux-distribution construction.

    Parameters
    ----------
    high_definition_resolution : int
        Grid resolution for high-definition KDE normalization.
    marginal_likelihood_resolution : int
        Grid resolution for marginal-likelihood integration.
    marginal_likelihood_interp_points : int
        Number of points used to interpolate the marginal likelihood.
    final_grid_bins : int
        Grid resolution for final posterior distributions.
    log_true_flux_min : float
        Lower bound for true log10 flux values.
    log_true_flux_max : float
        Upper bound for true log10 flux values.
    marginal_likelihood_range_extension : float
        Extension added to each side of the measured flux range when tabulating
        the marginal likelihood.
    numerical_epsilon : float
        Positive floor added before logarithms for numerical stability.
    interpolation_method : InterpolationMethod
        Interpolation method used for regular grids.
    """

    high_definition_resolution: int = 1024
    marginal_likelihood_resolution: int = 128
    marginal_likelihood_interp_points: int = 500
    final_grid_bins: int = 256
    log_true_flux_min: float = -4.75
    log_true_flux_max: float = -3.0
    marginal_likelihood_range_extension: float = 3.0
    numerical_epsilon: float = 1e-300
    interpolation_method: InterpolationMethod = "linear"

    def validate(self) -> None:
        """Validate distribution configuration values.

        Raises
        ------
        ValueError
            If a configuration value is outside the supported range.
        """
        if self.high_definition_resolution <= 1:
            raise ValueError("high_definition_resolution must be greater than one.")
        if self.marginal_likelihood_resolution <= 1:
            raise ValueError("marginal_likelihood_resolution must be greater than one.")
        if self.marginal_likelihood_interp_points <= 1:
            raise ValueError("marginal_likelihood_interp_points must be greater than one.")
        if self.final_grid_bins <= 1:
            raise ValueError("final_grid_bins must be greater than one.")
        if self.log_true_flux_min >= self.log_true_flux_max:
            raise ValueError("log_true_flux_min must be less than log_true_flux_max.")
        if self.marginal_likelihood_range_extension < 0:
            raise ValueError("marginal_likelihood_range_extension must be non-negative.")
        if self.numerical_epsilon <= 0:
            raise ValueError("numerical_epsilon must be positive.")
        if self.interpolation_method not in {"linear", "nearest"}:
            raise ValueError("interpolation_method must be 'linear' or 'nearest'.")

    @property
    def log_true_flux_range(self) -> tuple[float, float]:
        """Return the true log10 flux range."""
        return self.log_true_flux_min, self.log_true_flux_max

    def extended_marginal_likelihood_range(self, log_flux_min: float, log_flux_max: float) -> tuple[float, float]:
        """Return the extended range used to tabulate marginal likelihoods.

        Parameters
        ----------
        log_flux_min : float
            Lower measured log10 flux bound.
        log_flux_max : float
            Upper measured log10 flux bound.

        Returns
        -------
        tuple[float, float]
            Extended lower and upper true log10 flux bounds.
        """
        extension = self.marginal_likelihood_range_extension
        return log_flux_min - extension, log_flux_max + extension

    @property
    def sqrt_2pi(self) -> float:
        r"""Return $\sqrt{2\pi}$."""
        return sqrt(2.0 * pi)

    @property
    def log_10(self) -> float:
        r"""Return $\ln(10)$."""
        return log(10.0)


DEFAULT_KDE_CONFIG = KdeConfig()
DEFAULT_DISTRIBUTION_CONFIG = DistributionConfig()
