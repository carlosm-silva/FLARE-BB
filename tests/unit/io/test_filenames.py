from __future__ import annotations

from pathlib import Path

from flare_bb.core.config import DistributionConfig, KdeConfig
from flare_bb.io.filenames import decode_kde_filename, distribution_filename, kde_filename


def test_kde_filename_encodes_parameters() -> None:
    config = KdeConfig(bandwidth=0.3, bins=128, ts_threshold=25, flux_type="photon")

    assert kde_filename(config).startswith("kde_bw0.3_n128_ts25_flux-photon")


def test_decode_kde_filename() -> None:
    decoded = decode_kde_filename(Path("kde_bw0.2_n512_ts19_flux-energy_x-4.9to-2.8_y-5.35to-3.25.h5"))

    assert decoded["bandwidth"] == 0.2
    assert decoded["bins"] == 512
    assert decoded["flux_type"] == "energy"


def test_distribution_filename_includes_kde_metadata() -> None:
    filename = distribution_filename(
        DistributionConfig(final_grid_bins=16),
        {"kde_parameters": {"bandwidth": 0.2, "bins": 32, "ts_threshold": 19}},
    )

    assert "bins16" in filename
    assert "kde-bw0.2" in filename
