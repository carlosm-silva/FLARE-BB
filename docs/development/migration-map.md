# Legacy Migration Map

This P0 inventory records the FLARE-BB-relevant material in the ignored
`OLD2/Silva-IceCubeResearch` tree. A status describes its relationship to the
tracked package, not whether the legacy code is safe to run. No entry is a
runtime dependency.

| Legacy component(s) | Status | Successor or disposition |
| --- | --- | --- |
| `bayesian_block_test.py`, `bayesian_tests.ipynb`, `blazar_research/BayesianBlockLC.py` | Pending validation | P1 pure Bayesian-block API. Preserve only behavior characterized by tests; correct the leading-zero statistic and final-edge membership. |
| `blazar_research/CachedLightCurve.py`, `blazar_research/download_lcrs.py`, `blazar_research/FIT files notebook.ipynb` | Pending validation | P2 typed `LightCurveData`, pyLCR adapter, and versioned HDF5 cache. Pickle files are not a public artifact format. |
| `blazar_research/bin_catalog.py`, `blazar_research/Analyzers.py`, `blazar_research/flux_error_problem.py`, `blazar_research/ts0.py` | Pending validation | P2 cleaning-policy and catalog work. Retention rules require documented scientific review. |
| `blazar_research/empirical_distribution.ipynb`, `blazar_research/empirical_distribution_OLD.ipynb`, `blazar_research/empirical_distribution_OLD2.ipynb`, `blazar_research/likelihood_playground.ipynb`, `blazar_research/plot_kde.py`, `blazar_research/plot_flux_hist.py`, `blazar_research/jax_interp_tests.py` | Pending validation | P3 measurement-model audit, bandwidth study, and HDF5-grid validation. |
| `blazar_research/LCR_Simulator/LCRSimulator.py`, `FermiLCSimulation.py`, `FermiLCSTrials.py`, `FermiTrialsCPU.py`, `FermiTrialsGPU.py`, `JAXFermiSimulator.py`, `MeasurementPlayground.ipynb`, `Simulation Playground.ipynb`, `Resolution Power Tests.ipynb`, `Notebook to Plot Old Simulation Algorithm.ipynb`, `red_noise_tests.ipynb` | Pending validation | P4 NumPy reference, P5 JAX backend, and P6 trial engine. Historical global RNG, import-time loading, and fixed-size compilation are not retained contracts. |
| `blazar_research/LCR_Simulator/BayesianBlocksLCRTrials.py`, `blazar_research/OLD_trial_data_analysis.ipynb`, `blazar_research/trial_data_analysis.ipynb`, `blazar_research/fermi_data_analysis.ipynb`, `blazar_research/fermi_data_analysis2.ipynb`, `blazar_research/accuracy_plot_separate.py`, `blazar_research/accuracy_plot_togheter.py` | Pending validation | P6 reproducible trial artifacts, aggregation, and paper-equivalent figures. MongoDB and CSV state are validation evidence only. |
| `blazar_research/BinningClusters.ipynb`, `blazar_research/BinningTests.ipynb`, `blazar_research/hop_scargle_tests.ipynb`, `blazar_research/LCR_Simulator/Classifiers.py` | Exploratory | Longest-block, k-means, HOP, and hard-coded-threshold classification approaches are unvalidated and excluded from production behavior. |
| `blazar_research/Draw Light Curves.ipynb`, `LightCurve Playground.ipynb`, `Photon LightCurve Playground.ipynb`, `Plots for GHC.ipynb`, `Plotting Notebook 2025-01-24.ipynb`, `Simple 4FGL Simulator.ipynb`, `plotter.py`, `stat_utils.py`, `debug_script.py`, `LCR_Simulator/debug_script.py`, `LCR_Simulator/fermi_debug.py` | Exploratory | Retain only as visual or diagnostic references while P1--P6 receive tested interfaces. |
| `blazar_research/LCR_Simulator/csv_to_mongo.py`, `csv_to_mongo2.py`, `fix_mongo_collection.py`, `empirical_sigma_calculator.py` | Unrelated | Local database maintenance and one-off data repair; no package migration planned. |
| `andrew_king_integral/andrewKingIntegral.ipynb`, `meeting1/EffectiveAreaNotebook.ipynb`, `KohtaFigure2Left.ipynb`, `SignalIntegralNotebook.ipynb`, `SignalNumberNotebook.ipynb`, `meeting1/effective_area_calculator.py`, `meeting1/plot_fluence_energy.py` | Unrelated | IceCube and meeting research, outside FLARE-BB. |

The excluded `.ipynb_checkpoints` directory is an editor artifact rather than a
component. The map is updated when a replacement is scientifically validated,
not when a similarly named implementation merely exists.
