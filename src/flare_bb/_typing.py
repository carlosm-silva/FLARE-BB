"""Shared type aliases for FLARE-BB.

Other modules import from here with:
    from test_physics_repo._typing import ArrayLike, NDArray
"""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray

__all__ = ["ArrayLike", "NDArray", "np"]
