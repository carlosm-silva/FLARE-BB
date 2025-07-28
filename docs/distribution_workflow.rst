Flux Distribution Workflow
==========================

This document describes the complete workflow for building flux distributions from KDE data using
Bayesian analysis, as implemented in the FLARE-BB project.

Overview
--------

The flux distribution workflow implements a complete Bayesian analysis framework for understanding
the relationship between measured flux uncertainties and true flux values in blazar observations.
This process transforms KDE (Kernel Density Estimation) data into comprehensive probability
distributions that can be used for flare detection and analysis.

Mathematical Framework
---------------------

The workflow is based on the mathematical framework described in the measurement model, implementing
the complete Bayesian analysis chain:

Prior Distribution
~~~~~~~~~~~~~~~~~

The prior distribution p(F_m, σ_m) represents our knowledge about the distribution of measured
flux values F_m and their uncertainties σ_m. This is obtained directly from the KDE analysis
of real blazar data:

.. math::

   p(F_m, \sigma_m) = \text{KDE}(F_m, \sigma_m)

The KDE provides a smooth, non-parametric estimate of the empirical distribution of measured
flux-error pairs from the blazar population.

Likelihood Function
~~~~~~~~~~~~~~~~~~

The likelihood function p(F_R | F_m, σ_m) models the probability of observing a true flux F_R
given a measured flux F_m and uncertainty σ_m. This assumes log-normal measurement uncertainties:

.. math::

   p(F_R | F_m, \sigma_m) = \frac{1}{F_R \sigma \sqrt{2\pi}} \exp\left(-\frac{(\ln F_R - \mu)^2}{2\sigma^2}\right)

where:
- σ = ln(F_m + σ_m) - ln(F_m) (log-normal width)
- μ = ln(F_m) - 0.5σ² (log-normal mean)

Marginal Likelihood
~~~~~~~~~~~~~~~~~~

The marginal likelihood p(F_R) is calculated using the Law of Total Probability, integrating
over all possible measured values:

.. math::

   p(F_R) = \int \int p(F_R | F_m, \sigma_m) \cdot p(F_m, \sigma_m) \cdot F_R \ln(10) \, dF_m \, d\sigma_m

This represents the probability of observing a true flux F_R, marginalized over all possible
measurement scenarios.

Posterior Distribution
~~~~~~~~~~~~~~~~~~~~~

The posterior distribution p(F_m, σ_m | F_R) is calculated using Bayes' theorem:

.. math::

   p(F_m, \sigma_m | F_R) = \frac{p(F_R | F_m, \sigma_m) \cdot p(F_m, \sigma_m)}{p(F_R)}

This gives the probability distribution of measured flux-error pairs given a true flux value,
which is the key output for flare detection analysis.

Implementation Architecture
-------------------------

The implementation follows the repository's design philosophy with clear separation of concerns:

Heavy Machinery (src/)
~~~~~~~~~~~~~~~~~~~~~~~

Core mathematical algorithms and data structures:

- **distribution_config.py**: Centralized configuration management
- **distribution_builder.py**: Core Bayesian analysis algorithms
- **distribution_utils.py**: File management and data utilities

Heavy Lifting (scripts/)
~~~~~~~~~~~~~~~~~~~~~~~~~

Workflow orchestration and user interface:

- **build_distributions.py**: Complete workflow script with CLI

Configuration Management
-----------------------

The DistributionConfig class centralizes all parameters:

.. code-block:: python

   @dataclass
   class DistributionConfig:
       # Grid resolution parameters
       high_definition_resolution: int = 1024
       marginal_likelihood_resolution: int = 128
       marginal_likelihood_interp_points: int = 500
       final_grid_bins: int = 256

       # Flux range parameters
       flux_range_min: float = -4.75
       flux_range_max: float = -3.0
       marginal_likelihood_range_extension: float = 3.0

       # Numerical parameters
       numerical_epsilon: float = 1e-300
       interpolation_method: str = "linear"

       # Mathematical constants
       sqrt_2pi: float = np.sqrt(2 * np.pi)
       log_10: float = np.log(10)

Key Parameters:

- **high_definition_resolution**: Grid resolution for normalization calculations
- **marginal_likelihood_resolution**: Grid resolution for marginal likelihood integration
- **final_grid_bins**: Output resolution for posterior PDFs
- **flux_range_min/max**: Range of true flux values to analyze
- **marginal_likelihood_range_extension**: Extension beyond flux bounds for integration

Core Algorithm Workflow
----------------------

The build_flux_distributions function implements the complete workflow:

Step 1: KDE Data Preparation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Extract and normalize KDE data
   grid_data = extract_kde_grid_data(points, values)
   normalized_values, _ = normalize_kde(grid_data)

This step:
- Extracts grid structure from KDE data
- Normalizes KDE values to form proper probability distribution
- Uses trapezoidal integration for accurate normalization

Step 2: Interpolator Creation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Create KDE interpolator and calculate normalization
   kde_interpolator = create_kde_interpolator(grid_data, normalized_values, config)
   normalization = calculate_high_definition_normalization(kde_interpolator, grid_data, config)

This step:
- Creates interpolator for efficient KDE evaluation
- Calculates normalization using high-definition grid
- Ensures numerical accuracy in subsequent calculations

Step 3: PDF Function Setup
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Create PDF functions following Bayes' theorem
   kde_prior_pdf = create_kde_prior_pdf_function(kde_interpolator, normalization)
   likelihood_pdf = create_likelihood_pdf(config)

This step:
- Creates prior PDF function from KDE interpolator
- Creates likelihood PDF function with log-normal uncertainties
- Both functions are vectorized for efficient evaluation

Step 4: Marginal Likelihood Calculation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Calculate marginal likelihood p(F_R) using the Law of Total Probability
   marginal_likelihood_function = calculate_marginal_likelihood(
       likelihood_pdf, kde_prior_pdf, grid_data, config
   )
   marginal_likelihood_pdf = create_marginal_likelihood_interpolator(
       marginal_likelihood_function, grid_data, config
   )

This step:
- Implements numerical integration over measured flux-error space
- Uses trapezoidal integration for accuracy
- Creates interpolated function for efficient evaluation
- This is typically the most computationally intensive step

Step 5: Posterior Distribution Generation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Create posterior PDF using Bayes' theorem and generate distributions
   posterior_pdf = create_posterior_pdf(
       likelihood_pdf, kde_prior_pdf, marginal_likelihood_pdf, config
   )
   return generate_flux_distributions(posterior_pdf, grid_data, config, verbose=verbose)

This step:
- Implements Bayes' theorem to create posterior PDF
- Generates distributions over specified flux ranges
- Includes progress tracking with tqdm
- Returns comprehensive results with metadata

Usage Examples
--------------

Basic Usage
~~~~~~~~~~

.. code-block:: bash

   # Build distributions with default parameters
   python scripts/build_distributions.py

This will:
1. Load the most recent KDE file
2. Use default configuration parameters
3. Run the complete Bayesian workflow
4. Save results with parameter-encoded filename

Custom Configuration
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Build with custom resolution parameters
   python scripts/build_distributions.py \
       --hd-resolution 2048 \
       --ml-resolution 256 \
       --final-bins 512 \
       --flux-min -5.0 \
       --flux-max -2.5

This allows fine-tuning of:
- Grid resolutions for different accuracy requirements
- Flux ranges for specific analysis needs
- Numerical parameters for stability

KDE Selection
~~~~~~~~~~~~

.. code-block:: bash

   # Build using specific KDE file
   python scripts/build_distributions.py \
       --kde-bandwidth 0.2 \
       --kde-nbins 512 \
       --kde-ts-threshold 19

This allows:
- Selection of specific KDE files by parameters
- Comparison of results across different KDE configurations
- Systematic parameter studies

Verbosity Control
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Quiet mode for batch processing
   python scripts/build_distributions.py --quiet

   # Verbose mode for detailed progress
   python scripts/build_distributions.py --verbose

This provides:
- Progress bars for long calculations
- Step-by-step feedback
- Detailed error reporting
- Configurable output levels

File Management
--------------

Parameter-Encoded Filenames
~~~~~~~~~~~~~~~~~~~~~~~~~~

The system generates descriptive filenames that encode all parameters:

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

Benefits:
- ✅ **No overwrites**: Each parameter set gets a unique file
- ✅ **Self-documenting**: Parameters visible in filename
- ✅ **Easy comparison**: Quick visual identification
- ✅ **Parallel processing**: Safe for multiple parameter sweeps

File Structure
~~~~~~~~~~~~~

Distribution files use HDF5 format with comprehensive metadata:

.. code-block:: text

   DISTRIBUTION_FILE.h5
   ├── posterior_pdf_grid      # 3D array (measured_flux, measured_uncertainty, true_flux)
   ├── flux_range              # Array of true flux values
   ├── log_measured_flux_grid  # Grid of measured flux values
   ├── log_measured_uncertainty_grid  # Grid of measured uncertainty values
   ├── log_posterior_pdf_grid  # Log-transformed values for numerical stability
   └── metadata/
       ├── generation_timestamp
       ├── distribution_config  # Complete configuration parameters
       ├── source_kde          # Source KDE metadata
       ├── data_shapes         # Array shape information
       └── description         # Human-readable description

Data Access
~~~~~~~~~~

.. code-block:: python

   from data_processing.distribution_utils import load_distribution_data

   # Load distribution data
   result, metadata = load_distribution_data("path/to/distribution.h5")

   # Access posterior PDFs
   posterior_pdfs = result.posterior_pdf_grid  # Shape: (measured_flux, measured_uncertainty, true_flux)

   # Access coordinate grids
   true_flux_values = result.flux_range
   measured_flux_grid = result.log_measured_flux_grid
   measured_uncertainty_grid = result.log_measured_uncertainty_grid

   # Access configuration
   config = result.config

Performance Considerations
------------------------

Computational Complexity
~~~~~~~~~~~~~~~~~~~~~~~

The workflow has several computationally intensive steps:

1. **Marginal Likelihood Calculation**: O(n² × m) where n is marginal_likelihood_resolution
   and m is the number of flux values
2. **Posterior PDF Generation**: O(p × q × r) where p, q are grid resolutions and r is
   the number of true flux values
3. **High-definition Normalization**: O(hd_resolution²)

Memory Requirements
~~~~~~~~~~~~~~~~~~

Typical memory usage:
- **KDE Data**: ~10-50 MB depending on resolution
- **Marginal Likelihood**: ~100-500 MB for interpolation
- **Posterior PDFs**: ~100-1000 MB depending on grid resolution
- **Total**: 200-1500 MB for typical configurations

Optimization Strategies
~~~~~~~~~~~~~~~~~~~~~~

1. **Grid Resolution Tuning**: Balance accuracy vs. computational cost
2. **Interpolation**: Use interpolated marginal likelihood for efficiency
3. **Progress Tracking**: Monitor long calculations with tqdm
4. **Memory Management**: Use log-space calculations for numerical stability

Error Handling
--------------

The implementation includes comprehensive error handling:

Configuration Validation
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   config.validate()  # Raises ValueError for invalid parameters

This validates:
- Positive resolution parameters
- Valid flux ranges (min < max)
- Valid interpolation methods
- Positive numerical parameters

File Management
~~~~~~~~~~~~~~

- **Graceful degradation**: Fallback saving with minimal metadata
- **Type safety**: Robust HDF5 type handling
- **Error recovery**: Continue processing despite individual file errors
- **Validation**: Comprehensive data integrity checks

Integration with Analysis
------------------------

The generated distributions can be used for:

Flare Detection
~~~~~~~~~~~~~~

.. code-block:: python

   # Compare observed flux-error pair with posterior distribution
   observed_flux = -3.5
   observed_uncertainty = -4.0
   true_flux = -3.2

   # Find corresponding posterior PDF value
   flux_index = np.argmin(np.abs(result.flux_range - true_flux))
   posterior_value = result.posterior_pdf_grid[
       measured_flux_index, measured_uncertainty_index, flux_index
   ]

Uncertainty Quantification
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Calculate confidence intervals
   cumulative_pdf = np.cumsum(posterior_pdf, axis=(0, 1))
   confidence_interval = np.percentile(cumulative_pdf, [5, 95])

Model Validation
~~~~~~~~~~~~~~~

.. code-block:: python

   # Compare with theoretical predictions
   theoretical_pdf = calculate_theoretical_posterior(parameters)
   chi_squared = np.sum((posterior_pdf - theoretical_pdf)**2 / theoretical_pdf)

Future Enhancements
------------------

Planned improvements include:

1. **GPU Acceleration**: CUDA implementation for marginal likelihood calculation
2. **Parallel Processing**: Multi-core integration for large parameter sweeps
3. **Advanced Interpolation**: Higher-order interpolation methods
4. **Memory Optimization**: Streaming calculations for very large grids
5. **Real-time Analysis**: Integration with live data streams

The flux distribution workflow provides a robust, mathematically sound foundation for
Bayesian analysis of blazar flux measurements, enabling sophisticated flare detection
and uncertainty quantification in gamma-ray astronomy.
