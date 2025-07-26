Bayesian Blocks
================

This module implements the Bayesian Blocks algorithm for detecting change points in time series data,
specifically optimized for gamma-ray light curves.

.. automodule:: bayesian_blocks
   :members:
   :undoc-members:
   :show-inheritance:

Mathematical Foundation
-----------------------

The Bayesian Blocks algorithm segments time series data by finding the optimal partitioning that
balances model complexity with data fidelity. The algorithm uses a fitness function to evaluate
different segmentations:

.. math::

   F_i = n_i \log n_i - n_i

where :math:`n_i` is the number of events in block :math:`i`.

The total cost function to minimize is:

.. math::

   C = -\sum_{i=1}^{N} F_i + \gamma \cdot N

where :math:`N` is the number of blocks and :math:`\gamma` is a penalty term that controls
the trade-off between model complexity and goodness of fit.

Algorithm Implementation
------------------------

.. note::
   This module will contain the core Bayesian Blocks implementation. The specific classes
   and functions will be documented here once the implementation is complete.
