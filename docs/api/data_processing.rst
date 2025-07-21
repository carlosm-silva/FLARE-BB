Data Processing
===============

This module contains tools for downloading, caching, and processing Fermi-LAT light curve data.

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

.. autofunction:: data_processing.caching.check_substr_in_list

Downloader Module
-----------------

.. automodule:: data_processing.downloader
   :members:
   :undoc-members:
   :show-inheritance:

The downloader module handles bulk downloading of light curves from the Fermi-LAT database.
