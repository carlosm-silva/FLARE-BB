from __future__ import annotations

from flare_bb.core.config import KdeConfig
from flare_bb.core.kde import create_sample_flux_data
from flare_bb.pipeline.kde import find_kde_by_parameters, generate_kde_file, list_kde_files, load_most_recent_kde


def test_generate_and_find_kde_file(tmp_path) -> None:
    config = KdeConfig(bins=8)
    data = create_sample_flux_data(64)

    path = generate_kde_file(data, tmp_path, config=config)
    existing_path = generate_kde_file(data, tmp_path, config=config)
    loaded, metadata, recent_path = load_most_recent_kde(tmp_path)
    found_path = find_kde_by_parameters(tmp_path, {"bins": 8})

    assert path == existing_path
    assert recent_path == path
    assert found_path == path
    assert loaded.config.bins == 8
    assert metadata["kde_parameters"]["bins"] == 8
    assert list_kde_files(tmp_path) == [path]
