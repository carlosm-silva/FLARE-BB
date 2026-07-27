from __future__ import annotations

import numpy as np
import pytest

from flare_bb.core.config import DistributionConfig, KdeConfig
from flare_bb.core.distributions import build_flux_distributions, extract_kde_grid
from flare_bb.core.kde import compute_kde, create_sample_flux_data


def test_extract_kde_grid_rejects_non_square_grid() -> None:
    points = np.zeros((3, 2))
    values = np.zeros(3)

    with pytest.raises(ValueError, match="square"):
        extract_kde_grid(points, values)


def test_build_flux_distributions_small_grid() -> None:
    kde_config = KdeConfig(
        bins=6,
        log_flux_min=-4.8,
        log_flux_max=-2.9,
        log_uncertainty_min=-5.4,
        log_uncertainty_max=-3.2,
    )
    kde = compute_kde(create_sample_flux_data(80), config=kde_config)
    config = DistributionConfig(
        high_definition_resolution=8,
        marginal_likelihood_resolution=6,
        marginal_likelihood_interp_points=8,
        final_grid_bins=5,
        log_true_flux_min=-4.4,
        log_true_flux_max=-3.2,
    )

    result = build_flux_distributions(kde.points, kde.values, config=config)

    assert result.posterior_pdf_grid.shape == (5, 5, 5)
    assert result.log_posterior_pdf_grid.shape == (5, 5, 5)
    assert np.all(np.isfinite(result.log_posterior_pdf_grid))
