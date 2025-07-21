FLARE-BB Documentation
======================

**F**\ ermi **L**\ AT **A**\ daptive **R**\ esolution **E**\ nhancement with **B**\ ayesian **B**\ locks

A Bayesian Blocks Algorithm for Detecting Gamma-Ray Flares in Fermi-LAT Light Curves

.. image:: https://img.shields.io/badge/License-GPLv3-blue.svg
   :target: https://www.gnu.org/licenses/gpl-3.0
   :alt: License: GPL v3

Overview
--------

FLARE-BB is a scientific Python package that implements the Bayesian Blocks algorithm for detecting gamma-ray flares
in Fermi-LAT light curves. The package provides tools for:

* **Data Processing**: Efficient caching and downloading of Fermi-LAT Light Curve Repository data
* **Bayesian Analysis**: Implementation of the Bayesian Blocks algorithm for change-point detection
* **Statistical Methods**: Advanced statistical tools for gamma-ray astronomy
* **Simulation**: Tools for generating and analyzing synthetic light curves

Key Features
------------

* **High Performance**: Optimized with Numba for fast computation
* **Flexible Caching**: Smart caching system for Fermi-LAT data with automatic expiration
* **Type Safety**: Full type hints for better code reliability
* **Scientific Documentation**: LaTeX-formatted mathematical formulas in docstrings
* **GPL Licensed**: Open source with strong copyleft protection

Quick Start
-----------

.. code-block:: python

   from src.data_processing.caching import CachedLightCurve

   # Load a light curve with caching
   lc = CachedLightCurve(
       source="3C 279",
       cadence="daily",
       flux_type="photon"
   )

   # Access the light curve data
   print(f"Source: {lc.source}")
   print(f"Number of data points: {len(lc.met)}")

Mathematical Foundation
-----------------------

The Bayesian Blocks algorithm is based on the fitness function:

.. math::

   F(n, t) = \begin{cases}
       n \log n - n & \text{if } n > 0 \\
       0 & \text{if } n = 0
   \end{cases}

where :math:`n` is the number of events in a block and :math:`t` is the block duration.

The algorithm minimizes the global cost function:

.. math::

   C = -\sum_{i} F_i + \gamma \cdot N_{blocks}

where :math:`\gamma` is the prior penalty term and :math:`N_{blocks}` is the number of blocks.

API Documentation
-----------------

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api/data_processing
   api/bayesian_blocks
   api/simulation
   api/utils

.. toctree::
   :maxdepth: 1
   :caption: Development:

   development
   changelog
   contributing

Installation
------------

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/carlosm-silva/FLARE-BB.git
   cd FLARE-BB

   # Install in development mode
   pip install -e .

   # Install development dependencies
   pip install -r requirements-dev.txt

Dependencies
~~~~~~~~~~~~

* Python 3.8+
* NumPy
* Numba
* Pandas
* Astropy
* pyLCR
* tqdm

Development Setup
-----------------

For development setup including code formatting, linting, and testing configuration,
see the :doc:`development` guide.

Authors and License
-------------------

**Authors:**

* Carlos Márcio de Oliveira e Silva Filho (cfilho3@gatech.edu)
* Ignacio Taboada (itaboada@gatech.edu)

**License:**
This project is licensed under the GNU General Public License v3.0 or later.
See the `LICENSE <https://github.com/your-repo/FLARE-BB/blob/main/LICENSE>`_ file for details.

Disclaimer
----------

This software is provided "as is" without warranty of any kind. The authors provide no technical support,
maintenance, or assistance with this software. Use at your own risk.

Citation
--------

If you use FLARE-BB in your research, please cite:

.. code-block:: bibtex

   @software{flare_bb_2025,
     author = {Silva Filho, Carlos Márcio de Oliveira e and Taboada, Ignacio},
     title = {FLARE-BB: Bayesian Blocks Algorithm for Detecting Gamma-Ray Flares},
     url = {https://github.com/carlosm-silva/FLARE-BB},
     version = {1.0.0},
     year = {2025}
   }

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
