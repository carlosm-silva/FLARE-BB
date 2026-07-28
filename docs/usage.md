# Usage

## Installation

```bash
conda env create -f environment.yml
conda activate flare_bb
pip install -e ".[dev,docs]"
```

## Python API

Use `flare_bb` as the package name and `fbb` as the local alias when a short name helps readability.

```python
import flare_bb as fbb
from flare_bb.core import KdeConfig, compute_kde, create_sample_flux_data

data = create_sample_flux_data(n_points=1000)
kde = compute_kde(data, KdeConfig(bins=128))

print(fbb.__version__)
print(kde.kde_data.shape)
```

## KDE Generation

For a smoke test that does not require Fermi LCR access:

```bash
python scripts/generate_kde.py --sample-data --bins 128
```

For real Fermi data, place the 4FGL catalog at `data/catalogs/gll_psc_v32.fit`. The project installation includes the commit-pinned `pyLCR` fork required when running without `--sample-data`.

## Flux Distributions

Build posterior distributions from the newest KDE file:

```bash
python scripts/build_distributions.py --final-bins 64 --ml-resolution 32 --hd-resolution 128
```

Generated `.h5` files are data artifacts and are ignored by Git.
