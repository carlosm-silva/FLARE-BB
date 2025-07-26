Data Processing
===============

This module contains tools for downloading, caching, and processing Fermi-LAT light curve data,
including advanced KDE (Kernel Density Estimation) functionality for flux-error analysis.

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
