from __future__ import annotations

import numpy as np

from flare_bb.core.config import DistributionConfig, KdeConfig
from flare_bb.core.distributions import DistributionResult
from flare_bb.core.kde import compute_kde, create_sample_flux_data
from flare_bb.io.hdf5 import load_distribution_result, load_kde_result, save_distribution_result, save_kde_result


def test_kde_hdf5_round_trip(tmp_path) -> None:
    result = compute_kde(create_sample_flux_data(64), KdeConfig(bins=8))
    path = tmp_path / "kde.h5"

    save_kde_result(result, path)
    loaded, metadata = load_kde_result(path)

    np.testing.assert_allclose(loaded.points, result.points)
    assert loaded.config.bins == 8
    assert metadata["file_format_version"] == "1.0"


def test_distribution_hdf5_round_trip(tmp_path) -> None:
    config = DistributionConfig(final_grid_bins=3)
    result = DistributionResult(
        posterior_pdf_grid=np.ones((3, 3, 3)),
        log_true_flux=np.array([-4.0, -3.5, -3.0]),
        log_measured_flux_grid=np.ones((3, 3)),
        log_measured_uncertainty_grid=np.ones((3, 3)) * -4.0,
        log_posterior_pdf_grid=np.zeros((3, 3, 3)),
        config=config,
    )
    path = tmp_path / "dist.h5"

    save_distribution_result(result, path, kde_metadata={"kde_parameters": {"bandwidth": 0.2}})
    loaded, metadata = load_distribution_result(path)

    np.testing.assert_allclose(loaded.posterior_pdf_grid, result.posterior_pdf_grid)
    assert loaded.config.final_grid_bins == 3
    assert metadata["source_kde"]["kde_parameters"]["bandwidth"] == 0.2
