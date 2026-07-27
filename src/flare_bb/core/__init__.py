"""Numerical core for FLARE-BB."""

from flare_bb.core.config import DEFAULT_DISTRIBUTION_CONFIG, DEFAULT_KDE_CONFIG, DistributionConfig, KdeConfig
from flare_bb.core.distributions import DistributionResult, KdeGrid, build_flux_distributions
from flare_bb.core.kde import KdeResult, compute_kde, create_sample_flux_data

__all__ = [
    "DEFAULT_DISTRIBUTION_CONFIG",
    "DEFAULT_KDE_CONFIG",
    "DistributionConfig",
    "DistributionResult",
    "KdeConfig",
    "KdeGrid",
    "KdeResult",
    "build_flux_distributions",
    "compute_kde",
    "create_sample_flux_data",
]
