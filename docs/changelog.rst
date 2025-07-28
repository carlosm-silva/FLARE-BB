Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

[Unreleased]
------------

Added
~~~~~

* **Flux Distribution Building System**: Complete Bayesian analysis workflow for building flux distributions from KDE data
  * New module `src/data_processing/distribution_config.py` for centralized configuration management
  * New module `src/data_processing/distribution_builder.py` for core Bayesian analysis algorithms
  * New module `src/data_processing/distribution_utils.py` for file management and data utilities
  * New script `scripts/build_distributions.py` for complete workflow orchestration

* **Mathematical Framework Implementation**:
  * Prior distribution p(F_m, σ_m) from KDE data
  * Likelihood function p(F_R | F_m, σ_m) with log-normal uncertainties
  * Marginal likelihood p(F_R) using the Law of Total Probability
  * Posterior distribution p(F_m, σ_m | F_R) using Bayes' theorem

* **Configuration Management**:
  * `DistributionConfig` dataclass with comprehensive parameter management
  * Elimination of magic numbers through centralized configuration
  * Parameter validation with detailed error messages
  * Mathematical constant precomputation for efficiency

* **Core Algorithms**:
  * KDE data extraction and normalization with trapezoidal integration
  * High-definition grid evaluation for accurate normalization
  * Numerical integration for marginal likelihood calculation
  * Interpolated marginal likelihood for efficient evaluation
  * Vectorized posterior PDF generation with progress tracking

* **File Management System**:
  * Parameter-encoded filenames for self-documenting output files
  * Comprehensive HDF5 metadata storage with type-safe handling
  * Robust error recovery with fallback saving mechanisms
  * File discovery and parameter matching capabilities

* **User Experience Improvements**:
  * Comprehensive CLI with all configuration parameters exposed
  * Verbosity control with progress bars and step-by-step feedback
  * Existing file detection with user prompts for reuse
  * Detailed error reporting with helpful hints

* **Documentation**:
  * Complete API documentation for all new modules
  * Comprehensive workflow documentation (`docs/distribution_workflow.rst`)
  * Mathematical framework explanation with LaTeX formulas
  * Usage examples and performance considerations
  * Integration with existing documentation structure

Changed
~~~~~~~

* **Code Quality Improvements**:
  * Refactored `scripts/build_distributions.py` to follow repository design philosophy
  * Separated "heavy lifting" (scripts/) from "heavy machinery" (src/)
  * Eliminated DRY violations and magic numbers
  * Improved variable naming to align with mathematical terminology
  * Added comprehensive type hints throughout

* **Architecture Alignment**:
  * Moved all mathematical algorithms to `src/data_processing/` modules
  * Scripts now focus on CLI parsing, data loading, and workflow orchestration
  * Clear separation of concerns between configuration, algorithms, and utilities
  * Consistent import patterns following repository standards

* **Mathematical Consistency**:
  * Renamed functions and variables to match mathematical framework:
    * `create_pdf_function` → `create_kde_prior_pdf_function`
    * `create_conditional_pdf` → `create_likelihood_pdf`
    * `calculate_prior_distribution` → `calculate_marginal_likelihood`
    * `create_prior_interpolator` → `create_marginal_likelihood_interpolator`
    * `create_final_pdf` → `create_posterior_pdf`
  * Updated parameter names to reflect mathematical context:
    * `prior_calculation_resolution` → `marginal_likelihood_resolution`
    * `prior_interp_points` → `marginal_likelihood_interp_points`
    * `get_extended_prior_range` → `get_extended_marginal_likelihood_range`

Fixed
~~~~~

* **Bug Fixes**:
  * Fixed marginal likelihood calculation using correct resolution parameter
  * Resolved HDF5 saving crashes with robust type handling
  * Eliminated duplicate print statements in workflow output
  * Fixed syntax errors in try/except blocks

* **Numerical Stability**:
  * Added log-space calculations to prevent numerical overflow
  * Implemented epsilon values for log(0) prevention
  * Used high-definition grids for accurate normalization
  * Added interpolation for efficient marginal likelihood evaluation

* **Error Handling**:
  * Comprehensive validation of all configuration parameters
  * Graceful handling of file corruption and format issues
  * Fallback mechanisms for metadata saving failures
  * Detailed error messages with actionable hints

Technical Details
~~~~~~~~~~~~~~~~

* **Performance Optimizations**:
  * Vectorized calculations for efficiency
  * Progress tracking with tqdm for long computations
  * Memory-efficient grid operations
  * Interpolated functions for repeated evaluations

* **Data Structures**:
  * `KDEGridData` dataclass for structured grid information
  * `DistributionResult` dataclass for comprehensive results
  * `DistributionConfig` dataclass for parameter management
  * HDF5 format with compression for efficient storage

* **Integration**:
  * Seamless integration with existing KDE workflow
  * Consistent file naming conventions
  * Compatible metadata structures
  * Backward-compatible API design

This release represents a major enhancement to the FLARE-BB project, adding a complete
Bayesian analysis framework for flux distribution building. The implementation follows
rigorous mathematical principles while maintaining high code quality and user experience
standards.

[1.0.0] - 2025-01-15
---------------------

Initial release with core functionality:

* Basic Bayesian Blocks algorithm implementation
* KDE generation and analysis tools
* Fermi-LAT data processing capabilities
* Core statistical analysis functions
