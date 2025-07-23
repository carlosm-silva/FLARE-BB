KDE Workflow Guide
==================

This guide provides a comprehensive walkthrough of the Kernel Density Estimation (KDE) workflow
for analyzing flux-error relationships in blazar light curves using FLARE-BB.

Overview
--------

The KDE workflow enables sophisticated analysis of the relationship between flux measurements
and their uncertainties in gamma-ray blazar observations. This is essential for understanding
the statistical properties of blazar variability and improving detection algorithms.

**What the KDE Analysis Does:**

1. **Loads Real Data**: Processes Fermi-LAT 4FGL catalog to identify blazars
2. **Extracts Measurements**: Gets flux and error measurements from light curves
3. **Applies Quality Cuts**: Filters data based on detection significance (TS)
4. **Generates 2D KDE**: Creates kernel density estimation in log(flux) vs log(error) space
5. **Saves with Metadata**: Stores results with comprehensive parameter tracking

Prerequisites
-------------

Before starting the KDE workflow, ensure you have:

* **FLARE-BB installed** with all dependencies (``h5py``, ``scipy``)
* **Fermi-LAT 4FGL catalog** in ``data/catalogs/`` directory
* **pyLCR access** for light curve data
* **Sufficient disk space** for cache and results (several GB recommended)

Step-by-Step Workflow
---------------------

Step 1: Basic KDE Generation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Start with the default parameters to generate your first KDE:

.. code-block:: bash

   # Generate KDE with real blazar data
   python scripts/generate_kde.py

This will:

* Load the 4FGL catalog from ``data/catalogs/gll_psc_v32.fit``
* Identify all blazars (BLL, FSRQ, BCU classifications)
* Process their light curves using pyLCR
* Apply quality cuts (TS > 19)
* Generate KDE with default parameters
* Save to ``data/cache/kde/kde_bw0.2_n512_ts19_flux-energy_x-4.9to-2.8_y-5.35to-3.25.h5``

**Expected Output:**

.. code-block:: text

   📖 Loading Fermi-LAT 4FGL catalog...
      ✅ Loaded 6658 sources from catalog
   🌟 Loading blazar light curves...
      ✅ Processed 2341 blazars from 2341 blazar candidates
      • Total data points: 87432
   🔬 KDE Generation Workflow
      ✅ KDE computation complete!
   💾 Saving KDE data with metadata...
      ✅ Saved to: data/cache/kde/kde_bw0.2_n512_ts19_flux-energy_x-4.9to-2.8_y-5.35to-3.25.h5

Step 2: Examine Generated Data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Examine the KDE file to understand the results:

.. code-block:: bash

   # Examine the most recent KDE file
   python scripts/kde_data_example.py

**Output includes:**

* **Data array shapes** and types
* **Generation parameters** used
* **Data ranges** covered
* **Integrity verification** (checksums)
* **Metadata** (timestamp, description)

Step 3: Parameter Exploration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Explore different parameter combinations:

.. code-block:: bash

   # Higher resolution for finer detail
   python scripts/generate_kde.py --nbins 1024

   # Smoother KDE with larger bandwidth
   python scripts/generate_kde.py --bandwidth 0.3

   # More conservative detection threshold
   python scripts/generate_kde.py --ts-threshold 25

   # Different flux type
   python scripts/generate_kde.py --flux-type photon

Each parameter combination creates a unique file with encoded parameters.

Step 4: Batch Processing
~~~~~~~~~~~~~~~~~~~~~~~~

Run systematic parameter sweeps:

.. code-block:: bash

   # Generate multiple parameter combinations automatically
   python scripts/generate_kde.py --batch

This generates KDE files for several pre-defined parameter combinations,
useful for comparative analysis.

Step 5: Data Analysis
~~~~~~~~~~~~~~~~~~~~~

Load and analyze the KDE data in your analysis scripts:

.. code-block:: python

   import numpy as np
   import matplotlib.pyplot as plt
   from data_processing.kde_generator import load_kde_data_with_metadata

   # Load KDE data
   filepath = "data/cache/kde/kde_bw0.2_n512_ts19_flux-energy_x-4.9to-2.8_y-5.35to-3.25.h5"
   kde_data, points, values, metadata = load_kde_data_with_metadata(filepath)

   # Extract grid for plotting
   params = metadata['kde_parameters']
   nbins = params['nbins']

   x = points[:, 0].reshape(nbins, nbins)
   y = points[:, 1].reshape(nbins, nbins)
   z = values.reshape(nbins, nbins)

   # Create contour plot
   plt.figure(figsize=(10, 8))
   plt.contourf(x, y, z, levels=20, cmap='viridis')
   plt.colorbar(label='Log KDE Value')
   plt.xlabel('Log10(Flux)')
   plt.ylabel('Log10(Error)')
   plt.title('Blazar Flux-Error Relationship KDE')
   plt.show()

Parameter Reference
-------------------

Understanding Key Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Bandwidth (``--bandwidth``)**
  Controls smoothing in the KDE. Lower values preserve more detail but may be noisier.

  * ``0.1``: Very detailed, may show noise
  * ``0.2``: Default, good balance
  * ``0.3``: Smoother, emphasizes broad trends

**Grid Resolution (``--nbins``)**
  Sets the resolution of the output grid in each dimension.

  * ``256``: Faster computation, lower detail
  * ``512``: Default, good for most purposes
  * ``1024``: High detail, slower computation

**TS Threshold (``--ts-threshold``)**
  Minimum Test Statistic for including data points.

  * ``16``: More data points, includes marginal detections
  * ``19``: Default, conservative threshold
  * ``25``: Very conservative, only strong detections

**Flux Type (``--flux-type``)**
  Type of flux measurement to use.

  * ``energy``: Energy flux (default)
  * ``photon``: Photon flux

Advanced Usage
--------------

Custom Analysis Workflows
~~~~~~~~~~~~~~~~~~~~~~~~~~

For advanced analysis, you can create custom workflows:

.. code-block:: python

   import sys
   import os
   sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

   from data_processing.kde_generator import run_kde_generation, create_sample_data
   from data_processing.kde_utils import find_kde_by_parameters

   # Generate KDE with custom parameters
   custom_params = {
       'bandwidth': 0.15,
       'nbins': 2048,
       'ts_threshold': 16,
       'flux_type': 'photon'
   }

   # Use sample data for testing
   stacked_data = create_sample_data(n_points=5000)
   result_file = run_kde_generation(stacked_data, custom_params=custom_params)

   # Find existing files with specific parameters
   search_params = {'bandwidth': 0.2, 'flux_type': 'energy'}
   found_file = find_kde_by_parameters(search_params, 'data/cache/kde')

File Management
~~~~~~~~~~~~~~~

**Automatic File Naming**
  Files are automatically named based on parameters to prevent overwrites:

.. code-block:: text

   kde_bw0.2_n512_ts19_flux-energy_x-4.9to-2.8_y-5.35to-3.25.h5
   │   │     │    │   │           │              │
   │   │     │    │   │           │              └─ Y-axis range
   │   │     │    │   │           └─ X-axis range
   │   │     │    │   └─ Flux type
   │   │     │    └─ TS threshold
   │   │     └─ Number of bins
   │   └─ Bandwidth
   └─ File type

**Listing Files**

.. code-block:: bash

   # List all KDE files
   python scripts/generate_kde.py --list

**File Examination**

.. code-block:: bash

   # Examine specific file
   python scripts/kde_data_example.py path/to/specific/file.h5

Troubleshooting
---------------

Common Issues and Solutions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**"No valid blazar data found"**
  * **Check catalog path**: Ensure ``data/catalogs/gll_psc_v32.fit`` exists
  * **Check pyLCR connection**: Verify internet connection for light curve access
  * **Use sample data**: Try ``--sample-data`` flag for testing

**"Insufficient data points after filtering"**
  * **Lower TS threshold**: Use ``--ts-threshold 16`` for more data
  * **Expand ranges**: Modify ``x_low``, ``x_high``, ``y_low``, ``y_high`` parameters
  * **Check data quality**: Some blazars may have limited data

**Memory issues with large grids**
  * **Reduce resolution**: Use ``--nbins 256`` instead of higher values
  * **Process in batches**: Run smaller parameter sets separately
  * **Monitor RAM usage**: High-resolution KDEs require significant memory

**File access errors**
  * **Check permissions**: Ensure write access to ``data/cache/kde/``
  * **Check disk space**: Large KDE files require several MB each
  * **Path issues**: Use absolute paths if relative paths fail

Performance Optimization
~~~~~~~~~~~~~~~~~~~~~~~~

**For Large Datasets:**
  * Start with lower resolution (``--nbins 256``)
  * Use sample data for parameter testing (``--sample-data``)
  * Cache intermediate results when possible

**For Parameter Sweeps:**
  * Use batch mode (``--batch``) for predefined combinations
  * Process overnight for comprehensive sweeps
  * Monitor file sizes and disk usage

**For Analysis:**
  * Load only needed data ranges
  * Use compressed storage (default)
  * Cache frequently accessed results

Next Steps
----------

After generating KDE data, you can:

1. **Statistical Analysis**: Compare different blazar populations
2. **Model Fitting**: Fit theoretical models to KDE distributions
3. **Simulation Studies**: Generate synthetic data matching observed distributions
4. **Detection Optimization**: Use KDE results to improve flare detection algorithms
5. **Publication**: Create publication-quality visualizations and analyses

For more advanced usage, see the API documentation for the full range of available functions and customization options.
