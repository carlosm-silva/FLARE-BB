from __future__ import annotations

import pytest

from flare_bb.core import DistributionConfig, KdeConfig


def test_kde_config_rejects_invalid_range() -> None:
    config = KdeConfig(log_flux_min=1.0, log_flux_max=1.0)

    with pytest.raises(ValueError, match="log_flux_min"):
        config.validate()


@pytest.mark.parametrize(
    "config",
    [
        KdeConfig(bandwidth=0.0),
        KdeConfig(bins=1),
        KdeConfig(log_uncertainty_min=1.0, log_uncertainty_max=1.0),
        KdeConfig(ts_threshold=-1),
        KdeConfig(ts_min=-1),
        KdeConfig(flux_type="bad"),
    ],
)
def test_kde_config_rejects_invalid_values(config: KdeConfig) -> None:
    with pytest.raises(ValueError):
        config.validate()


def test_distribution_config_extended_range() -> None:
    config = DistributionConfig(marginal_likelihood_range_extension=2.0)

    assert config.extended_marginal_likelihood_range(-4.0, -3.0) == (-6.0, -1.0)


def test_distribution_config_rejects_cubic_interpolation() -> None:
    config = DistributionConfig(interpolation_method="cubic")  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="interpolation_method"):
        config.validate()


@pytest.mark.parametrize(
    "config",
    [
        DistributionConfig(high_definition_resolution=1),
        DistributionConfig(marginal_likelihood_resolution=1),
        DistributionConfig(marginal_likelihood_interp_points=1),
        DistributionConfig(final_grid_bins=1),
        DistributionConfig(log_true_flux_min=1.0, log_true_flux_max=1.0),
        DistributionConfig(marginal_likelihood_range_extension=-1.0),
        DistributionConfig(numerical_epsilon=0.0),
    ],
)
def test_distribution_config_rejects_invalid_values(config: DistributionConfig) -> None:
    with pytest.raises(ValueError):
        config.validate()
