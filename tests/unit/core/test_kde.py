from __future__ import annotations

import numpy as np
import pytest

from flare_bb.core.config import KdeConfig
from flare_bb.core.kde import compute_kde, create_sample_flux_data, filter_stacked_flux_data


def test_create_sample_flux_data_is_reproducible() -> None:
    first = create_sample_flux_data(10, seed=7)
    second = create_sample_flux_data(10, seed=7)

    np.testing.assert_array_equal(first, second)


def test_compute_kde_returns_expected_shapes() -> None:
    data = create_sample_flux_data(64)
    result = compute_kde(data, KdeConfig(bins=8))

    assert result.points.shape == (64, 2)
    assert result.values.shape == (64,)
    assert result.kde_data.shape == (64, 3)


def test_filter_stacked_flux_data_applies_ranges() -> None:
    data = np.array([[-5.0, -4.0, -3.0], [-6.0, -4.5, -3.0]])
    config = KdeConfig(log_flux_min=-4.5, log_flux_max=-3.5, log_uncertainty_min=-5.0, log_uncertainty_max=-4.0)

    filtered = filter_stacked_flux_data(data, config)

    np.testing.assert_array_equal(filtered, np.array([[-4.0], [-4.5]]))


def test_compute_kde_rejects_bad_shape() -> None:
    with pytest.raises(ValueError, match="shape"):
        compute_kde(np.ones((3, 10)), KdeConfig(bins=8))
