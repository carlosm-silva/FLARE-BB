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
* **KDE Analysis**: Advanced Kernel Density Estimation for flux-error relationship analysis in blazar light curves
* **Bayesian Analysis**: Implementation of the Bayesian Blocks algorithm for change-point detection
* **Statistical Methods**: Advanced statistical tools for gamma-ray astronomy
* **Simulation**: Tools for generating and analyzing synthetic light curves
* **Usage Scripts**: Complete workflows and examples for real-world blazar analysis

Key Features
------------

* **High Performance**: Optimized with Numba for fast computation
* **Flexible Caching**: Smart caching system for Fermi-LAT data with automatic expiration
* **KDE Processing**: Sophisticated kernel density estimation with parameter-encoded filenames
* **Real Data Integration**: Seamless integration with Fermi-LAT 4FGL catalog and pyLCR
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

KDE Analysis Quick Start
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Generate KDE data from real blazar light curves
   python scripts/generate_kde.py

   # Examine the generated KDE file
   python scripts/kde_data_example.py

   # Explore parameter combinations
   python scripts/generate_kde.py --batch

.. code-block:: python

   # Load KDE data with metadata
   from data_processing.kde_generator import load_kde_data_with_metadata

   kde_data, points, values, metadata = load_kde_data_with_metadata(filepath)
   params = metadata['kde_parameters']

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

KDE Mathematical Foundation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The KDE analysis uses Gaussian kernel density estimation for 2D flux-error relationships:

.. math::

   \hat{f}(x, y) = \frac{1}{nh^2} \sum_{i=1}^{n} K\left(\frac{x - x_i}{h}, \frac{y - y_i}{h}\right)

where :math:`K` is the Gaussian kernel, :math:`h` is the bandwidth, and :math:`(x_i, y_i)` are the flux-error data points in log space.

API Documentation
-----------------

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api/data_processing
   api/bayesian_blocks
   api/simulation
   api/utils
   api/scripts

.. toctree::
   :maxdepth: 1
   :caption: User Guides:

   kde_workflow

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
* h5py (for KDE data storage)
* scipy (for KDE computation)

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
