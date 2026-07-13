# FLARE-BB

FLARE-BB (**F**ermi **L**AT **A**daptive **R**esolution **E**nhancement with **B**ayesian **B**locks) provides tools for modeling Fermi-LAT measured flux/error behavior and building posterior flux distributions for flare analysis.

The package is organized around a modern `src/` layout:

- `flare_bb.core` contains pure numerical KDE and Bayesian distribution code.
- `flare_bb.io` contains HDF5, catalog, and optional Fermi LCR adapters.
- `flare_bb.pipeline` contains workflow orchestration used by command-line scripts.

## Installation

```bash
conda env create -f environment.yml
conda activate flare_bb
pip install -e ".[dev,docs]"
```

## Quick Start

```python
import flare_bb as fbb
from flare_bb.core import KdeConfig, compute_kde, create_sample_flux_data

data = create_sample_flux_data(n_points=500)
result = compute_kde(data, config=KdeConfig(bins=64))

print(fbb.__version__)
print(result.points.shape)
```

## Command-Line Workflows

```bash
python scripts/generate_kde.py --sample-data --bins 128
python scripts/build_distributions.py --final-bins 64 --ml-resolution 32 --hd-resolution 128 --progress
python scripts/inspect_kde.py data/cache/kde/<kde-file>.h5
```

Fermi LAT Light Curve Repository downloads require `pyLCR`. That dependency is intentionally optional until a pinned fork/tag is configured.

## Development

```bash
just check       # lint, format check, mypy, tests with coverage
just test        # tests only
just docs-build  # strict MkDocs build
just fix         # Ruff auto-fix and format
```

## License

FLARE-BB is licensed under GPL-3.0-or-later.
