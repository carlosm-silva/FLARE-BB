# FLARE-BB

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

FLARE-BB (**F**ermi **L**AT **A**daptive **R**esolution **E**nhancement with **B**ayesian **B**locks) provides tools for modeling Fermi-LAT measured flux/error behavior and building posterior flux distributions for flare analysis.

The package is organized around a modern `src/` layout:

- `flare_bb.core` contains pure numerical KDE and Bayesian distribution code.
- `flare_bb.io` contains HDF5, catalog, and Fermi LCR adapters.
- `flare_bb.pipeline` contains workflow orchestration used by command-line scripts.

## Documentation

The full documentation is available at [carlosm-silva.github.io/FLARE-BB](https://carlosm-silva.github.io/FLARE-BB/). It includes usage guidance, the measurement model, and an API reference generated from the package source.

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

Fermi LAT Light Curve Repository downloads use a temporary, commit-pinned dependency on the project's [`pyLCR` fork](https://github.com/carlosm-silva/pyLCR).

## Development

```bash
just check       # lint, format check, mypy, tests with coverage
just test        # tests only
just docs-build  # strict MkDocs build
just fix         # Ruff auto-fix and format
```

## License

FLARE-BB is licensed under the GNU General Public License v3.0 or later. See the [full license](https://github.com/carlosm-silva/FLARE-BB/blob/main/LICENSE) for details.

## Disclaimer

This software is provided "as is" without warranty of any kind. The authors provide no technical support, maintenance, or assistance with this software. Use at your own risk.

## Contact

For questions or inquiries, contact the authors:

- Carlos Márcio de Oliveira e Silva Filho ([cfilho3@gatech.edu](mailto:cfilho3@gatech.edu))
- Ignacio Taboada ([itaboada@gatech.edu](mailto:itaboada@gatech.edu))
