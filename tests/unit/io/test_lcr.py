from __future__ import annotations

from datetime import timedelta
from types import SimpleNamespace

import pytest

from flare_bb.io.lcr import (
    LightCurveRequest,
    MissingPyLcrError,
    download_light_curve,
    find_cached_light_curve,
    import_pylcr,
    is_expired,
    load_cached_light_curve,
)


def test_light_curve_request_cache_stem() -> None:
    request = LightCurveRequest("3C 279", cadence="weekly", flux_type="energy")

    assert request.cache_stem() == "3C 279_weekly_energy_fixed_tsmin4"


def test_light_curve_request_validation() -> None:
    request = LightCurveRequest("missing", cadence="yearly")

    with pytest.raises(ValueError, match="cadence"):
        request.validate()


def test_import_pylcr_missing_dependency() -> None:
    with pytest.raises(MissingPyLcrError):
        import_pylcr()


def test_is_expired(tmp_path) -> None:
    path = tmp_path / "cache.pkl"
    path.write_bytes(b"x")

    assert not is_expired(path, timedelta(days=1))


def test_cached_light_curve_helpers(tmp_path) -> None:
    request = LightCurveRequest("source")
    assert find_cached_light_curve(request, tmp_path) is None

    path = tmp_path / f"{request.cache_stem()}_2026-01-01.pkl"
    path.write_bytes(b"\x80\x04N.")

    assert find_cached_light_curve(request, tmp_path) == path
    assert load_cached_light_curve(path) is None


def test_download_light_curve_returns_valid_object() -> None:
    light_curve = SimpleNamespace(source="source")
    pylcr = SimpleNamespace(sources=["source"], getLightCurve=lambda *args, **kwargs: light_curve)

    result = download_light_curve(LightCurveRequest("source"), pylcr=pylcr, max_attempts=1)

    assert result is light_curve
