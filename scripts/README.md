# FLARE-BB Scripts Directory

This directory contains usage scripts that demonstrate the "heavy lifting" calculations and data processing workflows. All implementation details are kept in `src/`, following the project's design philosophy.

## 📁 File Organization

### Core Implementation (`src/`)
- `src/data_processing/kde_generator.py` - Main KDE generation algorithms and core functions
- `src/data_processing/kde_utils.py` - Utility functions for data management and examination
- `src/data_processing/caching.py` - Light curve caching utilities

### Usage Scripts (`scripts/`)
- `generate_kde.py` - **Main script for KDE generation with real blazar data**
- `kde_data_example.py` - Examine and analyze existing KDE files
- `demo_kde_filenames.py` - Demonstrate filename encoding system

## 🚀 Usage Examples

### Generate KDE Data

```bash
# Generate with real blazar data (default)
python scripts/generate_kde.py

# Generate with custom parameters using real data
python scripts/generate_kde.py --bandwidth 0.3 --nbins 1024

# Generate with sample data (for testing/demo)
python scripts/generate_kde.py --sample-data

# Generate multiple parameter combinations
python scripts/generate_kde.py --batch

# List existing KDE files
python scripts/generate_kde.py --list
```

### Examine KDE Files

```bash
# Examine the most recent KDE file
python scripts/kde_data_example.py

# Examine a specific file
python scripts/kde_data_example.py data/cache/kde/kde_bw0.2_n512_ts19_flux-energy_x-4.9to-2.8_y-5.35to-3.25.h5
```

### Demo Filename System

```bash
# Show how different parameters create different filenames
python scripts/demo_kde_filenames.py
```

## 🌟 Real Data Processing

**By default, the script now loads real blazar data from Fermi-LAT 4FGL catalog:**

1. **Loads 4FGL catalog** (`gll_psc_v32.fit`)
2. **Identifies blazars** (BLL, FSRQ, BCU classifications)
3. **Processes light curves** using pyLCR sources
4. **Caches data** for efficiency
5. **Applies quality cuts** (TS thresholds, error validation)
6. **Generates KDE** from real flux-error measurements

### Data Flow:
```
4FGL Catalog → Blazar Filter → Light Curves → Quality Cuts → KDE Generation → HDF5 Output
```

## 📋 Parameter-Encoded Filenames

The system automatically generates descriptive filenames that encode all generation parameters:

```
kde_bw{bandwidth}_n{nbins}_ts{threshold}_flux-{type}_x{low}to{high}_y{low}to{high}.h5
```

**Example**: `kde_bw0.2_n512_ts19_flux-energy_x-4.9to-2.8_y-5.35to-3.25.h5`

### Benefits:
- ✅ **No overwrites** - Each parameter set gets a unique file
- ✅ **Self-documenting** - Parameters visible in filename
- ✅ **Easy comparison** - Quick visual identification of different analyses
- ✅ **Parallel processing** - Can run multiple parameter sweeps safely

## 🔧 Available Parameters

| Parameter | Description | Default | Example Values |
|-----------|-------------|---------|----------------|
| `bandwidth` | KDE smoothing bandwidth | 0.2 | 0.1, 0.15, 0.3 |
| `nbins` | Grid resolution (per dimension) | 512 | 256, 1024, 2048 |
| `ts_threshold` | Detection significance threshold | 19 | 16, 25, 30 |
| `flux_type` | Type of flux measurement | 'energy' | 'energy', 'photon' |
| `x_low`, `x_high` | Log flux range | -4.9, -2.8 | Custom ranges |
| `y_low`, `y_high` | Log error range | -5.35, -3.25 | Custom ranges |

## 🗂️ Command Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `--bandwidth 0.3` | Set KDE bandwidth | Higher = smoother |
| `--nbins 1024` | Set grid resolution | Higher = finer detail |
| `--ts-threshold 25` | Set detection threshold | Higher = more conservative |
| `--flux-type photon` | Set flux measurement type | 'energy' or 'photon' |
| `--sample-data` | Use sample data instead of real data | For testing/demo |
| `--catalog-path PATH` | Specify catalog directory | Custom catalog location |
| `--batch` | Run multiple parameter combinations | Systematic exploration |
| `--list` | List existing KDE files | Check what's available |

## 💾 Data Format

All KDE files use HDF5 format with comprehensive metadata:

```python
from data_processing.kde_generator import load_kde_data_with_metadata

kde_data, points, values, metadata = load_kde_data_with_metadata(filepath)

# Access generation parameters
params = metadata['kde_parameters']
timestamp = metadata['generation_timestamp']
description = metadata['description']
```

## 🔍 Utility Functions

Import utility functions from `src/`:

```python
from data_processing.kde_utils import (
    list_kde_files,           # List all KDE files in directory
    examine_kde_data,         # Load and examine file contents  
    find_kde_by_parameters,   # Find file matching specific parameters
    compare_parameters,       # Compare stored vs expected parameters
    get_kde_file_summary     # Get summary of all files in directory
)

from data_processing.kde_generator import (
    run_kde_generation,       # Core KDE generation function
    create_sample_data,       # Generate sample data for testing
    load_kde_data_with_metadata,  # Load KDE files with metadata
)
```

## 🏗️ Architecture

**Design Philosophy**: 
- `src/` contains all heavy machinery (algorithms, utilities, core logic)
- `scripts/` contains heavy lifting (data loading, processing workflows, calculations)
- Clean separation allows easy testing, reuse, and maintenance

**Import Pattern**:
```python
# In scripts: Import from src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from data_processing.kde_generator import ...
from data_processing.kde_utils import ...
```

**Data Processing Flow**:
```
scripts/generate_kde.py:
├── Load 4FGL catalog (heavy lifting)
├── Process blazar light curves (heavy lifting)
└── Call src functions for KDE generation (heavy machinery)

src/kde_generator.py:
├── run_kde_generation() - Core algorithm
├── compute_kde() - Mathematical computation
└── save_kde_data_with_metadata() - Data persistence
```

This organization keeps the codebase maintainable while making usage patterns clear and accessible. The script handles the data-intensive operations while the src modules provide the computational algorithms. 
