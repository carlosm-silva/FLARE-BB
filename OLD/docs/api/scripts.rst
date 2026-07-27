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

Flux Distribution Scripts
-------------------------

build_distributions.py
~~~~~~~~~~~~~~~~~~~~~~

**Main script for building flux distributions from KDE data using Bayesian analysis**

This script implements the complete Bayesian workflow for building flux distributions from KDE data,
following the mathematical framework described in the measurement model. It demonstrates the
"heavy lifting" approach by orchestrating the core algorithms from the ``src/`` modules.

Mathematical Framework
^^^^^^^^^^^^^^^^^^^^^

The script implements the complete Bayesian analysis workflow:

1. **Prior Distribution**: p(F_m, σ_m) from KDE data
2. **Likelihood Function**: p(F_R | F_m, σ_m) with log-normal uncertainties
3. **Marginal Likelihood**: p(F_R) using the Law of Total Probability
4. **Posterior Distribution**: p(F_m, σ_m | F_R) using Bayes' theorem

Usage Examples:

.. code-block:: bash

   # Build distributions with default parameters
   python scripts/build_distributions.py

   # Build with custom configuration
   python scripts/build_distributions.py --hd-resolution 2048 --ml-resolution 256

   # Build with specific KDE file
   python scripts/build_distributions.py --kde-bandwidth 0.2 --kde-nbins 512

   # List existing distribution files
   python scripts/build_distributions.py --list

   # Quiet mode (minimal output)
   python scripts/build_distributions.py --quiet

   # Verbose mode (detailed progress)
   python scripts/build_distributions.py --verbose

Command Line Options:

Configuration Parameters:
* ``--hd-resolution INT`` - High-definition grid resolution (default: 1024)
* ``--ml-resolution INT`` - Marginal likelihood grid resolution (default: 128)
* ``--ml-interp-points INT`` - Marginal likelihood interpolation points (default: 500)
* ``--final-bins INT`` - Final grid resolution (default: 256)
* ``--flux-min FLOAT`` - Minimum log flux value (default: -4.75)
* ``--flux-max FLOAT`` - Maximum log flux value (default: -3.0)
* ``--range-extension FLOAT`` - Marginal likelihood range extension (default: 3.0)
* ``--epsilon FLOAT`` - Numerical stability epsilon (default: 1e-300)
* ``--interpolation STR`` - Interpolation method (default: "linear")

KDE Selection Parameters:
* ``--kde-bandwidth FLOAT`` - Select KDE file with specific bandwidth
* ``--kde-nbins INT`` - Select KDE file with specific grid resolution
* ``--kde-ts-threshold FLOAT`` - Select KDE file with specific TS threshold

Workflow Options:
* ``--kde-dir PATH`` - Directory containing KDE files (default: data/cache/kde)
* ``--list`` - List existing distribution files and exit
* ``--verbose`` - Show detailed progress information
* ``--quiet`` - Suppress detailed progress information

Features:
- **Complete Bayesian Workflow**: Implements the full mathematical framework
- **Progress Tracking**: Optional tqdm progress bars and step-by-step feedback
- **Parameter Validation**: Comprehensive validation of all configuration parameters
- **File Management**: Automatic file discovery and parameter matching
- **Error Recovery**: Robust error handling with fallback mechanisms
- **Verbosity Control**: Configurable output levels for different use cases

Output:
- Distribution files saved in ``data/cache/distributions/`` directory
- Parameter-encoded filenames for easy identification
- Comprehensive metadata including source KDE information
- HDF5 format with compression for efficient storage

Example Output:
^^^^^^^^^^^^^^

.. code-block:: text

   🔬 FLARE-BB Flux Distribution Builder
   ============================================================
   📂 Loading KDE data...
   📁 Using most recent KDE file: kde_bw0.2_n512_ts19_flux-energy_x-4.9to-2.8_y-5.35to-3.25.h5
   📊 KDE File Metadata:
     • Generation timestamp: 2025-01-15T10:30:45.123456
     • File format version: 1.0
     • Grid size: 512×512
     • Bandwidth: 0.2
     • TS threshold: 19
     • X range: [-4.9, -2.8]
     • Y range: [-5.35, -3.25]

   🔬 Building Flux Distributions from KDE Data
   ============================================================
   ⚙️  Configuration:
     • High-definition resolution: 1024
     • Marginal likelihood resolution: 128
     • Marginal likelihood interpolation points: 500
     • Final grid bins: 256
     • Flux range: [-4.75, -3.0]
     • Range extension: 3.0
     • Interpolation method: linear

   🔍 Analyzing KDE grid structure...
     • KDE grid: 512×512
     • X range: [-4.900, -2.800]
     • Y range: [-5.350, -3.250]

   🧮 Running flux distribution calculation...
   🔧 Step 1/5: Extracting and normalizing KDE data...
   🔧 Step 2/5: Creating KDE interpolators...
   🔧 Step 3/5: Setting up probability density functions...
   🔧 Step 4/5: Computing marginal likelihood (this may take several minutes)...
   🔧 Step 5/5: Building posterior distributions...
   🔄 Computing posterior PDFs for each true flux value...
   Generating flux PDFs: 100%|██████████| 256/256 [02:15<00:00, 1.89flux/s]

   ✅ Distribution calculation completed successfully!

   📊 Results Summary:
     • Posterior PDF grid shape: (256, 256, 256)
     • True flux range: [-4.750, -3.000]
     • Measured flux grid shape: (256, 256)
     • Measured uncertainty grid shape: (256, 256)

   💾 Saving distribution data...
   ✅ Results saved to: flux_dist_hd-res1024_ml-res128_ml-interp500_bins256_flux-4.75to-3.0_ext3.0_kde-bw0.2_n512_ts19.h5
   📁 Full path: data/cache/distributions/flux_dist_hd-res1024_ml-res128_ml-interp500_bins256_flux-4.75to-3.0_ext3.0_kde-bw0.2_n512_ts19.h5
   💽 File size: 134.22 MB

   🎉 Distribution building complete!
   💡 Use --list to see all available distribution files

Architecture Integration
^^^^^^^^^^^^^^^^^^^^^^^

The script demonstrates proper integration with the repository's architecture:

.. code-block:: python

   # Heavy lifting: CLI parsing, data loading, orchestration
   sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
   from data_processing.distribution_builder import build_flux_distributions
   from data_processing.distribution_config import DistributionConfig
   from data_processing.distribution_utils import save_distribution_data

   # Heavy machinery: Core algorithms from src/
   result = build_flux_distributions(points, values, config, verbose=verbose)
   save_distribution_data(result, output_path, kde_metadata, description)

This separation ensures:
- ✅ **Maintainability**: Core algorithms isolated in src/
- ✅ **Testability**: Individual components can be unit tested
- ✅ **Reusability**: src/ modules can be imported by other scripts
- ✅ **Clear Responsibilities**: Scripts handle workflow, src/ handles algorithms

Data Flow
---------

The complete data processing workflow:

.. code-block:: text

   4FGL Catalog → LCR Download → Blazar Filter → Light Curves → Quality Cuts → KDE Generation → HDF5 Output
                                                                      ↓
                                                              Parameter-Encoded Filename
                                                                      ↓
                                                              Distribution Building → Bayesian Analysis → Posterior PDFs
                                                                      ↓
                                                              Parameter-Encoded Distribution Files

Typical Processing Steps:

1. **Catalog Loading**: Load Fermi-LAT 4FGL catalog
2. **LCR Download**: Download light curve data for all CLEAN sources
3. **Source Classification**: Identify blazars (BLL, FSRQ, BCU)
4. **Light Curve Processing**: Extract flux and error measurements
5. **Quality Filtering**: Apply TS thresholds and error validation
6. **KDE Computation**: Generate 2D kernel density estimation
7. **Distribution Building**: Apply Bayesian analysis to build posterior distributions
8. **Data Storage**: Save with comprehensive metadata and checksums

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

.. list-table:: Distribution Building Parameters
   :widths: 20 40 20 20
   :header-rows: 1

   * - Parameter
     - Description
     - Default
     - Example Values
   * - hd_resolution
     - High-definition grid resolution
     - 1024
     - 512, 2048, 4096
   * - ml_resolution
     - Marginal likelihood resolution
     - 128
     - 64, 256, 512
   * - ml_interp_points
     - Marginal likelihood interpolation points
     - 500
     - 250, 1000, 2000
   * - final_bins
     - Final grid resolution
     - 256
     - 128, 512, 1024
   * - flux_min
     - Minimum log flux value
     - -4.75
     - -5.0, -4.5, -3.5
   * - flux_max
     - Maximum log flux value
     - -3.0
     - -3.5, -2.5, -2.0
   * - range_extension
     - Marginal likelihood range extension
     - 3.0
     - 2.0, 4.0, 5.0
   * - epsilon
     - Numerical stability epsilon
     - 1e-300
     - 1e-200, 1e-400
   * - interpolation
     - Interpolation method
     - linear
     - cubic, nearest

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

Distribution files use a similar HDF5 structure:

.. code-block:: text

   DISTRIBUTION_FILE.h5
   ├── posterior_pdf_grid      # 3D array of posterior PDFs
   ├── flux_range              # Array of true flux values
   ├── log_measured_flux_grid  # Grid of measured flux values
   ├── log_measured_uncertainty_grid  # Grid of measured uncertainty values
   ├── log_posterior_pdf_grid  # Log-transformed posterior PDF values
   └── metadata/
       ├── generation_timestamp
       ├── distribution_config
       ├── source_kde
       ├── data_shapes
       └── description

Integration with Core Library
-----------------------------

The scripts demonstrate proper usage patterns:

.. code-block:: python

   # In scripts: Import from src
   sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
   from data_processing.kde_generator import run_kde_generation
   from data_processing.kde_utils import examine_kde_data
   from data_processing.distribution_builder import build_flux_distributions
   from data_processing.distribution_utils import save_distribution_data

   # Heavy lifting: Load and process data
   catalog_df = load_fermi_catalog(args.catalog_path)
   stacked_data = load_blazar_lightcurves(catalog_df)

   # Heavy machinery: Generate KDE using core algorithms
   result = run_kde_generation(stacked_data, custom_params=custom_params)

   # Heavy machinery: Build distributions using core algorithms
   distribution_result = build_flux_distributions(points, values, config, verbose=verbose)

This architecture keeps the codebase maintainable while making usage patterns clear and accessible.
