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
# Configuration parameters for flux distribution building.
#

from dataclasses import dataclass
from typing import Tuple

import numpy as np


@dataclass
class DistributionConfig:
    """
    Configuration parameters for building flux distributions from KDE data.

    This class centralizes all magic numbers and constants used in the distribution
    building process, making them configurable and well-documented.
    """

    # Grid resolution parameters
    high_definition_resolution: int = 1024
    """High-definition grid resolution for normalization calculations."""

    marginal_likelihood_resolution: int = 128
    """Grid resolution for marginal likelihood calculations."""

    marginal_likelihood_interp_points: int = 500
    """Number of points for marginal likelihood interpolation."""

    final_grid_bins: int = 256
    """Grid resolution for final distribution calculations."""

    # Flux range parameters
    flux_range_min: float = -4.75
    """Minimum log flux value for distribution range."""

    flux_range_max: float = -3.0
    """Maximum log flux value for distribution range."""

    marginal_likelihood_range_extension: float = 3.0
    """Extension factor for marginal likelihood range beyond flux bounds."""

    # Numerical parameters
    numerical_epsilon: float = 1e-300
    """Small epsilon value to prevent log(0) in calculations."""

    # Interpolation parameters
    interpolation_method: str = "linear"
    """Method for grid interpolation (linear, cubic, etc.)."""

    # Mathematical constants
    sqrt_2pi: float = np.sqrt(2 * np.pi)
    """Precomputed sqrt(2*pi) for Gaussian calculations."""

    log_10: float = np.log(10)
    """Precomputed ln(10) for log base conversions."""

    def get_flux_range(self) -> Tuple[float, float]:
        """
        Get the flux range as a tuple.

        :returns: Tuple of (min_flux, max_flux)
        :rtype: Tuple[float, float]
        """
        return (self.flux_range_min, self.flux_range_max)

    def get_extended_marginal_likelihood_range(self, x_low: float, x_high: float) -> Tuple[float, float]:
        """
        Get the extended range for marginal likelihood calculations.

        :param x_low: Lower bound of data range
        :type x_low: float
        :param x_high: Upper bound of data range
        :type x_high: float
        :returns: Tuple of (extended_low, extended_high)
        :rtype: Tuple[float, float]
        """
        return (x_low - self.marginal_likelihood_range_extension, x_high + self.marginal_likelihood_range_extension)

    def validate(self) -> bool:
        """
        Validate configuration parameters.

        :returns: True if configuration is valid
        :rtype: bool
        :raises ValueError: If any parameter is invalid
        """
        if self.high_definition_resolution <= 0:
            raise ValueError("High definition resolution must be positive")

        if self.marginal_likelihood_resolution <= 0:
            raise ValueError("Marginal likelihood resolution must be positive")

        if self.marginal_likelihood_interp_points <= 0:
            raise ValueError("Marginal likelihood interpolation points must be positive")

        if self.final_grid_bins <= 0:
            raise ValueError("Final grid bins must be positive")

        if self.flux_range_min >= self.flux_range_max:
            raise ValueError("Flux range minimum must be less than maximum")

        if self.marginal_likelihood_range_extension < 0:
            raise ValueError("Marginal likelihood range extension must be non-negative")

        if self.numerical_epsilon <= 0:
            raise ValueError("Numerical epsilon must be positive")

        if self.interpolation_method not in ["linear", "cubic", "nearest"]:
            raise ValueError("Interpolation method must be 'linear', 'cubic', or 'nearest'")

        return True


# Default configuration instance
DEFAULT_CONFIG = DistributionConfig()
