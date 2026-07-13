"""Boundary adapters for files, metadata, and external data services."""

from flare_bb.io.filenames import decode_kde_filename, distribution_filename, kde_filename, list_matching_files
from flare_bb.io.hdf5 import (
    load_distribution_result,
    load_kde_result,
    save_distribution_result,
    save_kde_result,
    summarize_distribution,
)
from flare_bb.io.lcr import LightCurveRequest, MissingPyLcrError, load_light_curve

__all__ = [
    "LightCurveRequest",
    "MissingPyLcrError",
    "decode_kde_filename",
    "distribution_filename",
    "kde_filename",
    "list_matching_files",
    "load_distribution_result",
    "load_kde_result",
    "load_light_curve",
    "save_distribution_result",
    "save_kde_result",
    "summarize_distribution",
]
