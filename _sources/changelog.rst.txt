Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

[1.0.0] - 2025-01-XX
---------------------

Initial release

Added
~~~~~

* **Data Processing Module**: Efficient caching and downloading of Fermi-LAT light curves
* **CachedLightCurve Class**: Smart caching with automatic expiration for LCR data
* **Type Safety**: Full type hints throughout the codebase
* **Documentation**: Comprehensive Sphinx documentation with mathematical formulas
* **Development Tools**: Complete development setup with formatting and linting
* **License Headers**: GPL-3.0-or-later license headers in all source files

Infrastructure
~~~~~~~~~~~~~~

* **Build System**: Modern pyproject.toml-based configuration
* **Code Quality**: Black, isort, Ruff, and MyPy integration
* **Pre-commit Hooks**: Automated code quality checks
* **Documentation**: Sphinx with MathJax support for LaTeX formulas
* **CI/CD Ready**: Configuration files for continuous integration

Unreleased
----------

Planned features for future releases:

* **Bayesian Blocks Algorithm**: Core implementation of the change-point detection algorithm
* **Simulation Tools**: Synthetic light curve generation for testing and validation
* **Utility Functions**: Mathematical and statistical helper functions
* **Performance Optimizations**: Further Numba optimization for computational bottlenecks
* **Visualization Tools**: Plotting utilities for light curves and block segmentation
* **Extended Testing**: Comprehensive test suite with example datasets
