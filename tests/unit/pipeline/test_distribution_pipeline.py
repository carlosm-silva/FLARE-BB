from __future__ import annotations

from flare_bb.core.config import DistributionConfig, KdeConfig
from flare_bb.core.kde import compute_kde, create_sample_flux_data
from flare_bb.io.filenames import kde_filename
from flare_bb.io.hdf5 import save_kde_result
from flare_bb.pipeline.distributions import (
    build_distribution_file,
    find_distribution_by_config,
    list_distribution_files,
)


def test_build_distribution_file_reuses_existing_file(tmp_path) -> None:
    kde = compute_kde(create_sample_flux_data(80), KdeConfig(bins=6))
    kde_path = tmp_path / kde_filename(kde.config)
    save_kde_result(kde, kde_path)
    config = DistributionConfig(
        high_definition_resolution=8,
        marginal_likelihood_resolution=6,
        marginal_likelihood_interp_points=8,
        final_grid_bins=5,
        log_true_flux_min=-4.4,
        log_true_flux_max=-3.2,
    )

    path = build_distribution_file(kde_path, tmp_path, config=config)
    existing_path = build_distribution_file(kde_path, tmp_path, config=config)

    assert existing_path == path
    assert find_distribution_by_config(tmp_path, config) == path
    assert list_distribution_files(tmp_path) == [path]
