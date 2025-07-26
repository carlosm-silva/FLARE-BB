Scripts and Usage Examples
==========================

The ``scripts/`` directory contains usage scripts that demonstrate the "heavy lifting" calculations
and data processing workflows for KDE generation and analysis. These scripts provide complete examples
of how to use the FLARE-BB library for real-world blazar analysis.

Overview
--------

All implementation details are kept in ``src/``, following the project's design philosophy.
The scripts directory contains:

* **Core Processing Scripts**: Scripts that handle data-intensive operations
* **Data Download Scripts**: Tools for fetching and caching external data
* **Usage Examples**: Complete workflows from data loading to analysis
* **Parameter Exploration**: Tools for systematic parameter sweeps
* **Data Examination**: Utilities for analyzing results

Architecture
~~~~~~~~~~~~

**Design Philosophy**:
- ``src/`` contains all heavy machinery (algorithms, utilities, core logic)
- ``scripts/`` contains heavy lifting (data loading, processing workflows, calculations)
- Clean separation allows easy testing, reuse, and maintenance

KDE Generation Scripts
----------------------

download_lcrs.py
~~~~~~~~~~~~~~~

**Script for downloading Light Curve Repository (LCR) data for all CLEAN sources**

This script downloads light curve data for all sources listed in the 4FGL-DR4 catalog with the CLEAN flag.
It uses the pyLCR library to fetch data from the Fermi database and caches the results locally for efficient
reuse in subsequent analyses.

Usage Examples:

.. code-block:: bash

   # Download with default settings (8 workers, gll_psc_v32.fit catalog)
   python scripts/download_lcrs.py

   # Use 4 workers instead of 8 (useful for slower connections)
   python scripts/download_lcrs.py --workers 4

   # Use a different catalog file
   python scripts/download_lcrs.py --catalog my_catalog.fit

   # Use both custom arguments
   python scripts/download_lcrs.py --workers 16 --catalog new_catalog.fit

   # Get help
   python scripts/download_lcrs.py --help

Command Line Options:

* ``--workers INT`` - Number of worker threads for parallel processing (default: 8)
* ``--catalog STR`` - Name of the catalog file (default: gll_psc_v32.fit)

Data Processing:

The script processes each source through multiple parameter combinations:

* **Cadence**: daily, weekly, monthly
* **Flux Type**: photon, energy
* **Index Type**: fixed, free
* **TS Minimum**: 4

Features:
- **Automatic Caching**: Uses CachedLightCurve for efficient data management
- **Error Handling**: Gracefully handles API errors, empty sources, and network issues
- **Progress Tracking**: Shows download progress with tqdm
- **Parallel Processing**: Configurable number of worker threads
- **Flexible Catalog Support**: Can work with different catalog files

Output:
- Light curve data is cached in ``data/cache/LCRs/`` directory
- Each source gets its own cache file with parameter-encoded naming
- Failed downloads are logged but don't stop the overall process

generate_kde.py
~~~~~~~~~~~~~~~

**Main script for KDE generation with real blazar data**

This script demonstrates the complete workflow from Fermi-LAT catalog loading to KDE generation:

1. **Loads 4FGL catalog** (``gll_psc_v32.fit``)
2. **Identifies blazars** (BLL, FSRQ, BCU classifications)
3. **Processes light curves** using pyLCR sources
4. **Caches data** for efficiency
5. **Applies quality cuts** (TS thresholds, error validation)
6. **Generates KDE** from real flux-error measurements

Usage Examples:

.. code-block:: bash

   # Generate with real blazar data (default)
   python scripts/generate_kde.py

   # Generate with custom parameters
   python scripts/generate_kde.py --bandwidth 0.3 --nbins 1024

   # Generate with sample data (for testing/demo)
   python scripts/generate_kde.py --sample-data

   # Generate multiple parameter combinations
   python scripts/generate_kde.py --batch

   # List existing KDE files
   python scripts/generate_kde.py --list

Command Line Options:

* ``--bandwidth FLOAT`` - Set KDE bandwidth (default: 0.2)
* ``--nbins INT`` - Set grid resolution (default: 512)
* ``--ts-threshold INT`` - Set detection threshold (default: 19)
* ``--flux-type STR`` - Set flux measurement type ('energy' or 'photon')
* ``--sample-data`` - Use sample data instead of real data
* ``--catalog-path PATH`` - Specify catalog directory
* ``--batch`` - Run multiple parameter combinations
* ``--list`` - List existing KDE files

Parameter-Encoded Filenames
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The system automatically generates descriptive filenames that encode all generation parameters:

.. code-block:: text

   kde_bw{bandwidth}_n{nbins}_ts{threshold}_flux-{type}_x{low}to{high}_y{low}to{high}.h5

**Example**: ``kde_bw0.2_n512_ts19_flux-energy_x-4.9to-2.8_y-5.35to-3.25.h5``

Benefits:
- ✅ **No overwrites** - Each parameter set gets a unique file
- ✅ **Self-documenting** - Parameters visible in filename
- ✅ **Easy comparison** - Quick visual identification of different analyses
- ✅ **Parallel processing** - Can run multiple parameter sweeps safely

kde_data_example.py
~~~~~~~~~~~~~~~~~~~

**Script for examining and analyzing existing KDE files**

This script demonstrates how to load, examine, and validate KDE data files:

Usage Examples:

.. code-block:: bash

   # Examine the most recent KDE file
   python scripts/kde_data_example.py

   # Examine a specific file
   python scripts/kde_data_example.py data/cache/kde/kde_bw0.2_n512_ts19_flux-energy_x-4.9to-2.8_y-5.35to-3.25.h5

Features:
- **Data Loading**: Demonstrates proper loading with metadata
- **Parameter Verification**: Compares stored vs expected parameters
- **File Discovery**: Shows how to find files by parameters
- **Data Integrity**: Validates checksums and data consistency
- **Summary Reports**: Provides overview of all KDE files

demo_kde_filenames.py
~~~~~~~~~~~~~~~~~~~~~

**Demonstration script showing filename encoding system**

This script shows how different parameters create different filenames without requiring actual data:

Usage Example:

.. code-block:: bash

   # Show how different parameters create different filenames
   python scripts/demo_kde_filenames.py

Features:
- **No Data Required**: Demonstrates filename system without processing
- **Parameter Variations**: Shows multiple parameter combinations
- **Educational**: Explains the filename encoding system
- **Quick Demo**: Fast way to understand the naming convention

Data Flow
---------

The complete data processing workflow:

.. code-block:: text

   4FGL Catalog → LCR Download → Blazar Filter → Light Curves → Quality Cuts → KDE Generation → HDF5 Output
                                                                      ↓
                                                              Parameter-Encoded Filename

Typical Processing Steps:

1. **Catalog Loading**: Load Fermi-LAT 4FGL catalog
2. **LCR Download**: Download light curve data for all CLEAN sources
3. **Source Classification**: Identify blazars (BLL, FSRQ, BCU)
4. **Light Curve Processing**: Extract flux and error measurements
5. **Quality Filtering**: Apply TS thresholds and error validation
6. **KDE Computation**: Generate 2D kernel density estimation
7. **Data Storage**: Save with comprehensive metadata and checksums

Available Parameters
--------------------

.. list-table:: KDE Generation Parameters
   :widths: 20 40 20 20
   :header-rows: 1

   * - Parameter
     - Description
     - Default
     - Example Values
   * - bandwidth
     - KDE smoothing bandwidth
     - 0.2
     - 0.1, 0.15, 0.3
   * - nbins
     - Grid resolution per dim
     - 512
     - 256, 1024, 2048
   * - ts_threshold
     - Detection significance
     - 19
     - 16, 25, 30
   * - flux_type
     - Type of flux measurement
     - energy
     - energy, photon
   * - x_low
     - Log flux range (low)
     - -4.9
     - Custom ranges
   * - x_high
     - Log flux range (high)
     - -2.8
     - Custom ranges
   * - y_low
     - Log error range (low)
     - -5.35
     - Custom ranges
   * - y_high
     - Log error range (high)
     - -3.25
     - Custom ranges

Data Format
-----------

All KDE files use HDF5 format with comprehensive metadata:

.. code-block:: python

   from data_processing.kde_generator import load_kde_data_with_metadata

   kde_data, points, values, metadata = load_kde_data_with_metadata(filepath)

   # Access generation parameters
   params = metadata['kde_parameters']
   timestamp = metadata['generation_timestamp']
   description = metadata['description']

File Structure:

.. code-block:: text

   KDE_FILE.h5
   ├── data/
   │   ├── kde_data      # Combined array (nbins*nbins, 3)
   │   ├── points        # Grid points (nbins*nbins, 2)
   │   └── values        # Log KDE values (nbins*nbins,)
   └── metadata/
       ├── generation_timestamp
       ├── kde_parameters
       ├── data_shapes
       ├── file_format_version
       ├── description
       └── checksums (kde_data, points, values)

Integration with Core Library
-----------------------------

The scripts demonstrate proper usage patterns:

.. code-block:: python

   # In scripts: Import from src
   sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
   from data_processing.kde_generator import run_kde_generation
   from data_processing.kde_utils import examine_kde_data

   # Heavy lifting: Load and process data
   catalog_df = load_fermi_catalog(args.catalog_path)
   stacked_data = load_blazar_lightcurves(catalog_df)

   # Heavy machinery: Generate KDE using core algorithms
   result = run_kde_generation(stacked_data, custom_params=custom_params)

This architecture keeps the codebase maintainable while making usage patterns clear and accessible.
