Data Processing
===============

This module contains tools for downloading, caching, and processing Fermi-LAT light curve data,
including advanced KDE (Kernel Density Estimation) functionality for flux-error analysis and
Bayesian flux distribution building.

Caching Module
--------------

.. automodule:: data_processing.caching
   :members:
   :undoc-members:
   :show-inheritance:

The caching module provides efficient storage and retrieval of light curve data from the
Fermi-LAT Light Curve Repository.

Key Classes
~~~~~~~~~~~

.. autoclass:: data_processing.caching.CachedLightCurve
   :members:
   :special-members: __init__
   :show-inheritance:

Key Functions
~~~~~~~~~~~~~

.. autofunction:: data_processing.caching.check_substr_in_list_v2

Downloader Module
-----------------

.. automodule:: data_processing.downloader
   :members:
   :undoc-members:
   :show-inheritance:

The downloader module handles bulk downloading of light curves from the Fermi-LAT database.

KDE Generator Module
--------------------

.. automodule:: data_processing.kde_generator
   :members:
   :undoc-members:
   :show-inheritance:

The KDE generator module provides sophisticated kernel density estimation for analyzing
flux-error relationships in blazar light curves. It includes comprehensive parameter
management, file naming conventions, and metadata storage.

Key Functions
~~~~~~~~~~~~~

.. autofunction:: data_processing.kde_generator.run_kde_generation

.. autofunction:: data_processing.kde_generator.compute_kde

.. autofunction:: data_processing.kde_generator.save_kde_data_with_metadata

.. autofunction:: data_processing.kde_generator.load_kde_data_with_metadata

.. autofunction:: data_processing.kde_generator.generate_kde_filename

.. autofunction:: data_processing.kde_generator.get_kde_generation_parameters

.. autofunction:: data_processing.kde_generator.create_sample_data

Helper Functions
~~~~~~~~~~~~~~~~

.. autofunction:: data_processing.kde_generator.format_src_name

.. autofunction:: data_processing.kde_generator.is_blazar

KDE Utilities Module
--------------------

.. automodule:: data_processing.kde_utils
   :members:
   :undoc-members:
   :show-inheritance:

The KDE utilities module provides tools for managing, examining, and analyzing KDE data files.
It includes functions for file discovery, parameter comparison, and data integrity checking.

Key Functions
~~~~~~~~~~~~~

.. autofunction:: data_processing.kde_utils.list_kde_files

.. autofunction:: data_processing.kde_utils.examine_kde_data

.. autofunction:: data_processing.kde_utils.find_kde_by_parameters

.. autofunction:: data_processing.kde_utils.compare_parameters

.. autofunction:: data_processing.kde_utils.get_kde_file_summary

.. autofunction:: data_processing.kde_utils.decode_filename

Distribution Configuration Module
--------------------------------

.. automodule:: data_processing.distribution_config
   :members:
   :undoc-members:
   :show-inheritance:

The distribution configuration module centralizes all parameters and constants used in
flux distribution building, following the mathematical framework described in the measurement model.
This module eliminates magic numbers and provides a single source of truth for all configuration
parameters.

Key Classes
~~~~~~~~~~~

.. autoclass:: data_processing.distribution_config.DistributionConfig
   :members:
   :special-members: __init__
   :show-inheritance:

The DistributionConfig class encapsulates all parameters needed for building flux distributions
from KDE data. It includes grid resolution parameters, flux ranges, numerical stability
parameters, and mathematical constants.

Configuration Parameters
^^^^^^^^^^^^^^^^^^^^^^^

.. list-table:: Distribution Configuration Parameters
   :widths: 25 40 15 20
   :header-rows: 1

   * - Parameter
     - Description
     - Default
     - Mathematical Context
   * - high_definition_resolution
     - Grid resolution for normalization calculations
     - 1024
     - Used in high-definition grid evaluation
   * - marginal_likelihood_resolution
     - Grid resolution for marginal likelihood calculations
     - 128
     - Integration grid for p(F_R) calculation
   * - marginal_likelihood_interp_points
     - Points for marginal likelihood interpolation
     - 500
     - Interpolation accuracy for p(F_R)
   * - final_grid_bins
     - Grid resolution for final distributions
     - 256
     - Output resolution for posterior PDFs
   * - flux_range_min
     - Minimum log flux value
     - -4.75
     - Lower bound for F_R range
   * - flux_range_max
     - Maximum log flux value
     - -3.0
     - Upper bound for F_R range
   * - marginal_likelihood_range_extension
     - Extension factor for marginal likelihood range
     - 3.0
     - Range extension beyond flux bounds
   * - numerical_epsilon
     - Small value for numerical stability
     - 1e-300
     - Prevents log(0) in calculations
   * - interpolation_method
     - Method for grid interpolation
     - "linear"
     - Interpolation algorithm choice

Key Methods
^^^^^^^^^^^

.. automethod:: data_processing.distribution_config.DistributionConfig.get_flux_range

.. automethod:: data_processing.distribution_config.DistributionConfig.get_extended_marginal_likelihood_range

.. automethod:: data_processing.distribution_config.DistributionConfig.validate

Distribution Builder Module
---------------------------

.. automodule:: data_processing.distribution_builder
   :members:
   :undoc-members:
   :show-inheritance:

The distribution builder module implements the core mathematical algorithms for building
flux distributions from KDE data, following the Bayesian framework described in the measurement model.
This module contains the "heavy machinery" for probability density function calculations,
numerical integration, and posterior distribution generation.

Key Classes
~~~~~~~~~~~

.. autoclass:: data_processing.distribution_builder.KDEGridData
   :members:
   :special-members: __init__
   :show-inheritance:

Container for KDE grid data and metadata, providing structured access to grid points,
values, resolution, and coordinate ranges.

.. autoclass:: data_processing.distribution_builder.DistributionResult
   :members:
   :special-members: __init__
   :show-inheritance:

Container for flux distribution calculation results, including posterior PDF grids,
flux ranges, measured quantity grids, and configuration information.

Mathematical Framework
^^^^^^^^^^^^^^^^^^^^^

The distribution builder implements the complete Bayesian analysis workflow:

1. **Prior Distribution**: p(F_m, σ_m) from KDE data
2. **Likelihood Function**: p(F_R | F_m, σ_m) with log-normal uncertainties
3. **Marginal Likelihood**: p(F_R) using the Law of Total Probability
4. **Posterior Distribution**: p(F_m, σ_m | F_R) using Bayes' theorem

Key Functions
~~~~~~~~~~~~~

.. autofunction:: data_processing.distribution_builder.build_flux_distributions

Main entry point for the complete distribution building workflow. This function orchestrates
the entire process from KDE data to final probability distributions.

.. autofunction:: data_processing.distribution_builder.extract_kde_grid_data

Extracts structured grid information from KDE points and values.

.. autofunction:: data_processing.distribution_builder.normalize_kde

Normalizes KDE values to form a proper probability distribution using trapezoidal integration.

.. autofunction:: data_processing.distribution_builder.create_kde_interpolator

Creates an interpolator for the normalized KDE using scipy's RegularGridInterpolator.

.. autofunction:: data_processing.distribution_builder.calculate_high_definition_normalization

Calculates normalization factor using high-definition grid evaluation for numerical accuracy.

.. autofunction:: data_processing.distribution_builder.create_kde_prior_pdf_function

Creates the prior probability density function p(F_m, σ_m) from KDE interpolator.

.. autofunction:: data_processing.distribution_builder.create_likelihood_pdf

Creates likelihood probability density function p(F_R | F_m, σ_m) assuming log-normal
measurement uncertainties.

.. autofunction:: data_processing.distribution_builder.calculate_marginal_likelihood

Calculates marginal likelihood p(F_R) using the Law of Total Probability with numerical
integration.

.. autofunction:: data_processing.distribution_builder.create_marginal_likelihood_interpolator

Creates interpolated marginal likelihood function for efficient evaluation.

.. autofunction:: data_processing.distribution_builder.create_posterior_pdf

Creates the posterior probability density function p(F_m, σ_m | F_R) using Bayes' theorem.

.. autofunction:: data_processing.distribution_builder.generate_flux_distributions

Generates flux probability distributions over specified ranges with optional progress tracking.

Distribution Utilities Module
----------------------------

.. automodule:: data_processing.distribution_utils
   :members:
   :undoc-members:
   :show-inheritance:

The distribution utilities module provides tools for managing, saving, loading, and analyzing
flux distribution data files. It includes comprehensive file management, metadata handling,
and data validation capabilities.

Key Functions
~~~~~~~~~~~~~

.. autofunction:: data_processing.distribution_utils.create_distribution_filename

Creates descriptive filenames for distribution data files following the repository's
parameter-encoded naming convention.

.. autofunction:: data_processing.distribution_utils.save_distribution_data

Saves distribution results to HDF5 file with comprehensive metadata and robust type handling.

.. autofunction:: data_processing.distribution_utils.load_distribution_data

Loads distribution data from HDF5 file with metadata and handles type conversions.

.. autofunction:: data_processing.distribution_utils.list_distribution_files

Lists all distribution files in the specified directory.

.. autofunction:: data_processing.distribution_utils.find_distribution_by_parameters

Finds a distribution file matching specified configuration parameters.

.. autofunction:: data_processing.distribution_utils.examine_distribution_data

Examines and summarizes distribution file contents with detailed metadata.

.. autofunction:: data_processing.distribution_utils.get_distribution_summary

Gets a summary of all distribution files in the directory.

.. autofunction:: data_processing.distribution_utils.ensure_distribution_cache_directory

Ensures the distribution cache directory exists and returns its path.

.. autofunction:: data_processing.distribution_utils.compare_distribution_configs

Compares two distribution configurations and highlights differences.

.. autofunction:: data_processing.distribution_utils.validate_distribution_parameters

Validates distribution configuration parameters and returns detailed results.

File Management
^^^^^^^^^^^^^^

The distribution utilities provide robust file management with:

- **Parameter-encoded filenames**: Self-documenting file names that encode all generation parameters
- **Comprehensive metadata**: Full configuration and source information stored with each file
- **Type-safe HDF5 handling**: Robust handling of different data types for HDF5 compatibility
- **Error recovery**: Graceful handling of file corruption and format issues
- **File discovery**: Tools for finding files by parameters and comparing configurations

Example Filename Format:
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   flux_dist_hd-res1024_ml-res128_ml-interp500_bins256_flux-4.75to-3.0_ext3.0_kde-bw0.2_n512_ts19.h5

This filename encodes:
- High-definition resolution: 1024
- Marginal likelihood resolution: 128
- Marginal likelihood interpolation points: 500
- Final grid bins: 256
- Flux range: [-4.75, -3.0]
- Range extension: 3.0
- Source KDE parameters: bandwidth=0.2, nbins=512, ts_threshold=19
