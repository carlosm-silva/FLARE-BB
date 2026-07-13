"""Shared pytest fixtures."""

from __future__ import annotations

import numpy as np
import pytest


@pytest.fixture()
def rng() -> np.random.Generator:
    """Return a seeded random generator for reproducible tests."""
    return np.random.default_rng(seed=42)
