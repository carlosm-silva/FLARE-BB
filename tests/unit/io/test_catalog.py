from __future__ import annotations

import numpy as np
import pandas as pd

from flare_bb.io.catalog import extract_light_curve_flux_data, format_source_name, is_blazar


class DummyLightCurve:
    met = np.array([1.0, 2.0, 3.0])
    met_detections = np.array([1.0, 3.0])
    ts = np.array([20.0, 2.0])
    flux = np.array([1.0, 2.0])
    flux_error = np.array([[0.5, 1.25], [1.5, 2.75]])


def test_format_source_name_handles_bytes_and_strings() -> None:
    assert format_source_name(b"3C 279   ") == "3C 279"
    assert format_source_name(" 3C 279 ") == "3C 279"


def test_is_blazar_uses_catalog_classes() -> None:
    catalog = pd.DataFrame(
        {
            "Source_Name": ["a", "b"],
            "CLASS1": ["BLL", "psr"],
            "CLASS2": ["", "BCU"],
        }
    )

    assert is_blazar("a", catalog)
    assert is_blazar("b", catalog)
    assert not is_blazar("missing", catalog)


def test_extract_light_curve_flux_data_applies_ts_cut() -> None:
    flux, uncertainty = extract_light_curve_flux_data(DummyLightCurve(), ts_threshold=10)

    np.testing.assert_array_equal(flux, np.array([1.0]))
    np.testing.assert_array_equal(uncertainty, np.array([0.25]))
