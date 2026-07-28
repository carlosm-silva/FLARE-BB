"""Fermi LAT Light Curve Repository integration."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
import pickle
from time import sleep
from typing import Any


class MissingPyLcrError(ImportError):
    """Raised when the pyLCR runtime dependency is unavailable."""


@dataclass(frozen=True)
class LightCurveRequest:
    """Parameters identifying a Fermi LCR light curve.

    Parameters
    ----------
    source : str
        Source name accepted by pyLCR.
    cadence : str
        LCR cadence.
    flux_type : str
        LCR flux type.
    index_type : str
        LCR index type.
    ts_min : int
        Minimum test statistic requested from pyLCR.
    """

    source: str
    cadence: str = "daily"
    flux_type: str = "photon"
    index_type: str = "fixed"
    ts_min: int = 4

    def cache_stem(self) -> str:
        """Return the stable cache filename stem for this request."""
        return "_".join([self.source, self.cadence, self.flux_type, self.index_type, f"tsmin{self.ts_min}"])

    def validate(self, sources: Iterable[str] | None = None) -> None:
        """Validate request values.

        Parameters
        ----------
        sources : Iterable[str] | None
            Optional valid source collection from pyLCR.
        """
        if sources is not None and self.source not in sources:
            raise ValueError("Source not found in pyLCR.sources. It might not be available in the Fermi database.")
        if self.cadence not in {"daily", "weekly", "monthly"}:
            raise ValueError("cadence must be 'daily', 'weekly', or 'monthly'.")
        if self.flux_type not in {"photon", "energy"}:
            raise ValueError("flux_type must be 'photon' or 'energy'.")
        if self.index_type not in {"fixed", "free"}:
            raise ValueError("index_type must be 'fixed' or 'free'.")
        if self.ts_min < 0:
            raise ValueError("ts_min must be non-negative.")


def load_light_curve(
    request: LightCurveRequest,
    cache_dir: Path,
    *,
    online: bool = True,
    cache_uninitialized: bool = True,
    expires: timedelta = timedelta(days=900_000),
    max_attempts: int = 5,
) -> Any:
    """Load a light curve from cache or pyLCR.

    Parameters
    ----------
    request : LightCurveRequest
        Light-curve request parameters.
    cache_dir : Path
        Directory for pickled pyLCR light-curve objects.
    online : bool
        Whether downloading from pyLCR is allowed.
    cache_uninitialized : bool
        Whether downloaded curves should be cached.
    expires : timedelta
        Cache expiration age.
    max_attempts : int
        Maximum pyLCR download attempts.

    Returns
    -------
    Any
        pyLCR light-curve object.
    """
    cached_path = find_cached_light_curve(request, cache_dir)
    if cached_path is not None and (not online or not is_expired(cached_path, expires)):
        return load_cached_light_curve(cached_path)
    if cached_path is not None and online:
        cached_path.unlink()
    if not online:
        raise FileNotFoundError(f"Cache file not found for {request.cache_stem()}.")

    pylcr = import_pylcr()
    request.validate(sources=pylcr.sources)
    light_curve = download_light_curve(request, pylcr=pylcr, max_attempts=max_attempts)
    if cache_uninitialized:
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_path = cache_dir / f"{request.cache_stem()}_{datetime.now(tz=UTC).date().isoformat()}.pkl"
        with cache_path.open("wb") as file:
            pickle.dump(light_curve, file)
    return light_curve


def find_cached_light_curve(request: LightCurveRequest, cache_dir: Path) -> Path | None:
    """Find a cached light curve matching a request.

    Parameters
    ----------
    request : LightCurveRequest
        Light-curve request parameters.
    cache_dir : Path
        Cache directory.

    Returns
    -------
    Path | None
        Matching cache path, if any.
    """
    if not cache_dir.exists():
        return None
    matches = sorted(cache_dir.glob(f"{request.cache_stem()}*.pkl"))
    return matches[-1] if matches else None


def load_cached_light_curve(path: Path) -> Any:
    """Load a cached pyLCR light curve.

    Parameters
    ----------
    path : Path
        Pickle path.

    Returns
    -------
    Any
        Cached light-curve object.
    """
    with path.open("rb") as file:
        return pickle.load(file)


def is_expired(path: Path, expires: timedelta) -> bool:
    """Return whether a cache file is older than the expiration age.

    Parameters
    ----------
    path : Path
        Cache path.
    expires : timedelta
        Expiration age.

    Returns
    -------
    bool
        True when expired.
    """
    modified_at = datetime.fromtimestamp(path.stat().st_mtime, tz=UTC)
    return modified_at + expires <= datetime.now(tz=UTC)


def download_light_curve(request: LightCurveRequest, *, pylcr: Any, max_attempts: int = 5) -> Any:
    """Download a light curve with retries.

    Parameters
    ----------
    request : LightCurveRequest
        Light-curve request parameters.
    pylcr : Any
        Imported pyLCR module.
    max_attempts : int
        Maximum download attempts.

    Returns
    -------
    Any
        pyLCR light-curve object.
    """
    request.validate(sources=pylcr.sources)
    for attempt in range(max_attempts):
        if attempt > 0:
            sleep(2**attempt)
        light_curve = pylcr.getLightCurve(
            request.source,
            cadence=request.cadence,
            flux_type=request.flux_type,
            index_type=request.index_type,
            ts_min=request.ts_min,
        )
        if light_curve is not None and getattr(light_curve, "source", None) is not None:
            return light_curve
    raise RuntimeError(
        "Download failed for "
        f"{request.source} {request.cadence} {request.flux_type} {request.index_type} {request.ts_min}."
    )


def import_pylcr() -> Any:
    """Import pyLCR or raise a clear dependency error.

    Returns
    -------
    Any
        Imported pyLCR module.
    """
    try:
        import pyLCR
    except ImportError as error:
        raise MissingPyLcrError(
            "pyLCR is required for Fermi LCR download/caching features. "
            "Reinstall FLARE-BB to restore its pinned pyLCR dependency."
        ) from error
    return pyLCR
