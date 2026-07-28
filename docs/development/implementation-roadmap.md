# FLARE-BB Reproducible Scientific Package Roadmap

## Summary

The long-term product will let scientists:

1. Explicitly initialize a verified Fermi-LAT dataset and model cache.
2. Load a real light curve and compute the paper-established Bayesian-block representation.
3. Build or load the empirical measurement model $p((F_m,\sigma_m)\mid F_R)$.
4. Simulate seeded light curves with NumPy for validation or JAX/GPU for production.
5. Run resumable NCP-prior studies and reproduce the paper's figures from archived inputs.

The local `/paper` tree remains ignored and private. Its terminology and equations inform implementation, but stable
conventions will be rewritten into tracked documentation without exposing unpublished paper text.

## Milestone mapping

Milestones describe user-visible delivery progress. The P-numbered sections below are implementation workstreams: a
workstream may contribute to more than one milestone, and P7 supplies documentation and release work throughout.

| Milestone | User-visible outcome | Supporting workstreams | Status |
| --- | --- | --- | --- |
| M0 — Scientific contract | Shared terminology, defaults, and the legacy boundary are tracked. | P0 | Complete |
| M1 — Real-light-curve analysis | A user can initialize, load, and segment a real light curve. | P1, P2, P7 | Active: P1 started |
| M2 — Reproducible measurement model | A validated empirical measurement model can be rebuilt or loaded. | P3, P7 | Planned |
| M3 — CPU simulation reference | Deterministic small-scale simulations are scientifically validated. | P4, P7 | Planned |
| M4 — JAX/GPU acceleration | Accelerated simulation is available with NumPy parity. | P5, P7 | Planned |
| M5 — Trial engine and reproduction | Studies resume safely and archived results are reproducible. | P6, P7 | Planned |
| M6 — Community release | Tutorials, contribution material, releases, and archival references are complete. | P7 | Planned |

## Progress

P0's terminology, units, established defaults, provenance boundary, and `OLD2`
migration inventory are recorded in the tracked [scientific contract](scientific-contract.md)
and [legacy migration map](migration-map.md). The next implementation slice is
P1's pure Bayesian-block numerical API; it must consume this contract without
adding cache, CLI, plotting, or flare-classification behavior.

## Implementation workstreams

### P0 — Scientific contract and migration inventory

Establish the vocabulary, equations, units, defaults, and provenance rules before adding more algorithms.

- Use `true_flux` ($F_R$), `measured_flux` ($F_m$), `measurement_uncertainty` ($\sigma_m$),
  `quiescent_flux` ($F_Q$), `flare_peak_flux` ($F_0$), `flare_center`, `flare_width_days` ($W=2\sigma$), and
  `ncp_prior`.
- Define energy-flux units as $\mathrm{erg\,cm^{-2}\,s^{-1}}$, time as Fermi MET seconds for observed data, and elapsed
  days for simulations.
- Record the paper defaults: daily LCR product (three-day bins), energy flux, fixed spectral index, TS $\geq 19$,
  log-normal Bayesian-block fitness, measurement errors enabled, and NCP prior 10.
- Create a tracked migration map classifying each `OLD2` component as migrated, pending validation, exploratory, or
  unrelated.
- Explicitly mark longest-block, k-means, hard-coded-threshold, and HOP approaches as unvalidated exploratory work.

Completion goals:

- Every public quantity has one canonical Python name, mathematical symbol, unit, and definition.
- Defaults in code, README, tutorials, and generated API reference agree.
- The migration map accounts for all FLARE-BB-relevant `OLD2` scripts and notebooks.
- No production feature depends on `/paper` at runtime or in CI.

### P1 — Analysis-first numerical core

Implement the package's namesake Bayesian-block operation as a pure, typed numerical API.

Public interfaces:

- `BayesianBlocksConfig` with defaults `ncp_prior=10`, `distribution="log_normal"`, and
  `use_measurement_uncertainty=True`.
- `BayesianBlocksResult` containing edges, block means, block standard deviations, sample counts, and per-sample block
  indices.
- `analyze_light_curve(times, measured_flux, measurement_uncertainty, config=...)`.
- A typed `LightCurveData` representation independent of pyLCR internals.

Behavior:

- Apply the paper's log-normal transformation:

  $$
  \begin{aligned}
  \sigma &= \ln(F_m+\sigma_m)-\ln(F_m), \\
  \mu &= \ln(F_m)-\frac{\sigma^2}{2}.
  \end{aligned}
  $$

- Require finite, one-dimensional, equal-length arrays; strictly increasing times; and positive flux and uncertainty
  for log-normal analysis.
- Include a measurement on the final Bayesian-block edge in the final block.
- Return one statistic per block without the legacy leading-zero sentinel.
- Do not automatically label real-data blocks as flares. An explicit user threshold may be plotted, but automatic
  quiescent-level estimation remains out of scope until scientifically validated.

Completion goals:

- Synthetic constant and change-point fixtures produce expected block edges.
- Normal and log-normal modes agree with direct Astropy reference calls.
- Regression fixtures characterize legacy behavior and document intentional corrections.
- A network-free cached real-light-curve fixture can be analyzed and plotted.
- Unit tests cover invalid shapes, ordering, non-finite values, non-positive log inputs, missing errors, and final-edge
  membership.

### P2 — Explicit initialization and stable light-curve cache

Replace ad hoc scripts and pickle-dependent storage with a single, documented initialization workflow.

Public CLI:

```text
flare-bb init
flare-bb init --artifact-set paper-v1
flare-bb init --from-live
flare-bb init --source "4FGL J..."
flare-bb init --warm-jax
flare-bb status
flare-bb analyze "4FGL J..." [--plot output.pdf]
```

Implementation:

- Add a unified `flare-bb` entry point; keep existing scripts temporarily as compatible wrappers.
- Default to a platform-appropriate user cache, overridable by `--cache-dir` and `FLARE_BB_CACHE_DIR`.
- Store standardized light curves in versioned HDF5 rather than pickle. Preserve source, query parameters, MET values,
  measured flux, asymmetric flux bounds, TS, fit-convergence information, and derived $\sigma_m$.
- Make initialization resumable, idempotent, lock-protected, and atomic.
- Verify archive downloads with SHA-256 checksums and byte sizes.
- Provide an archived `paper-v1` snapshot for exact reproduction and an explicitly non-reproducible live rebuild path.
- For live rebuilding, apply a named, documented cleaning policy and verify that the archived paper dataset reproduces
  the expected 77,992 retained measurements.
- Instantiate SciPy interpolators from stored numerical grids at runtime; `--warm-jax` additionally prepares the
  persistent JAX compilation cache.

Completion goals:

- Running `flare-bb init` twice performs no unnecessary download or recomputation.
- Interrupted downloads and builds resume safely.
- Corrupt artifacts are detected before use and replaced only with an explicit repair or reinitialization action.
- `flare-bb status` reports cache location, artifact versions, checksums, query configuration, and readiness for
  analysis and simulation.
- README and getting-started documentation require initialization explicitly before real-data examples.
- No normal public workflow requires repository-local `data/` paths.

### P3 — Measurement-model and spline hardening

Promote the existing KDE and posterior implementation from a working reconstruction to a validated scientific model.

- Audit likelihood, Jacobians, KDE normalization, marginal likelihood, interpolation axes, and posterior normalization
  against the paper.
- Evolve the HDF5 format to store explicit one-dimensional axes, precision, artifact schema version, source-data
  checksum, configuration, package version, and creation timestamp.
- Retain read compatibility with existing format-version-1 artifacts.
- Build a `MeasurementModel` from the distribution artifact, providing PDF evaluation, normalized conditional slices,
  and sampling.
- Reproduce the lost NPZ workflow only as a validation and import tool; the public implementation uses versioned HDF5.
- Re-run the missing KDE bandwidth study at 0.1, 0.2, and 0.3 decades and archive its numerical summary.
- Separate archive-derived artifacts from live-derived artifacts so they can never be mistaken for one another.

Completion goals:

- Prior, marginal-likelihood, and posterior normalization errors meet documented numerical tolerances across the
  configured domain.
- The archived dataset reproduces the expected sample count and paper grid ranges.
- HDF5 round trips preserve arrays, metadata, and checksums.
- Runtime SciPy splines reproduce stored grid values and legacy NPZ interpolation within tolerance.
- The bandwidth claim is supported by a reproducible script, configuration, and result artifact.

### P4 — Reproducible CPU simulation reference

Implement a clear NumPy and SciPy reference simulator before GPU acceleration.

Public interfaces:

- `SimulationConfig`, `QuiescentBackground`, and `GaussianFlare`.
- `simulate_true_flux(times, events)`.
- `MeasurementModel.sample(true_flux, rng=...)`.
- `simulate_light_curve(config, measurement_model, seed, backend="auto")`.
- `DetectionConfig` and simulation-only detection and evaluation results.

Behavior:

- Implement:

  $$
  F_R(t)=F_Q+F_0\exp\left[-\frac{(t-t_0)^2}{2(W/2)^2}\right].
  $$

- Preserve the paper benchmark profile: 1,460 daily samples, the three $F_Q$, $F_0$, and $W$ values, and NCP priors
  5–12.
- Derive the one-standard-deviation detection threshold from moments of $p(F_m,\sigma_m\mid F_Q)$, replacing the
  legacy hard-coded three-value lookup.
- Merge consecutive above-threshold blocks into one detection.
- Count a true positive when a detection contains an injected flare center; count unmatched detections as false
  positives and unmatched injections as false negatives.
- Use explicit seeded `numpy.random.Generator` instances; never use hidden global random state.

Completion goals:

- Identical configuration, artifact checksum, and seed produce byte-identical CPU outputs.
- Gaussian-event values match the analytical equation at the center and selected offsets.
- Conditional samples reproduce reference PDF moments and quantiles within statistical tolerances.
- Detection matching covers boundary centers, consecutive blocks, multiple injected flares, no-flare curves, and
  overlapping detections.
- CPU simulation emits one prominent acceleration warning per process explaining that it is suitable for validation
  and small examples, not paper-scale studies.

### P5 — Optional JAX/GPU backend

Add JAX as an optional accelerator without making scientific correctness depend on it.

- Add an optional JAX dependency extra; document current official CUDA installation separately because GPU wheels are
  platform-specific.
- `backend="auto"` selects JAX only when a GPU device is available; otherwise it selects NumPy and emits
  `AccelerationWarning` once per process.
- Explicit `backend="jax"` may run on CPU but must report the device and emit the same warning when no GPU is present.
- Expose a diagnostic API and CLI showing JAX version, devices, platform, precision, and compilation-cache path.
- Use explicit split JAX PRNG keys, `jit`, `vmap`, chunked batches, and a persistent compilation cache.
- Avoid import-time artifact loading, import-time compilation, fixed 1,460-element function signatures, and repeated
  host and device transfers.
- Default accelerated simulation to float32, record precision in provenance, and validate against the float64 NumPy
  reference.

Completion goals:

- NumPy and JAX evaluate equivalent normalized conditional distributions.
- Statistical sample moments and quantiles agree within defined tolerances.
- Standard CI runs optional JAX tests on CPU; a separate GPU smoke and benchmark workflow runs on designated hardware.
- On the project RTX 3070 Ti, the new sampler reaches at least 80% of the rebuilt legacy JAX sampler's throughput and
  at least 100 times the NumPy reference for the paper-shaped workload.
- README states plainly that the historical implementation observed roughly 1,200 times acceleration, that exact
  speedup is hardware-dependent, and that approximately two million paper-scale simulations are not practical on the
  CPU reference backend.

### P6 — Resumable trial engine and paper reproduction

Build the publication-scale workflow after single simulations are validated.

- Stream simulations in bounded GPU batches and send Bayesian-block analysis to bounded CPU worker pools.
- Generate deterministic seed schedules from a recorded root seed; reuse each simulated light curve across NCP priors
  5–12.
- Store chunked, appendable HDF5 trial results with configuration, seed, artifact checksum, backend and device,
  precision, software versions, completion state, and failure records.
- Support interruption, resume, shard execution, shard merging, and per-configuration progress reporting.
- Aggregate accuracy and error rate with the paper's Beta treatment and false-positive rate with its Gamma or Poisson
  treatment.
- Generate paper-equivalent tables and figures from result artifacts rather than MongoDB or notebook state.
- Freeze the final `paper-v1` trial manifest only after the authors reconcile the paper's “two million light curves”
  statement with the available legacy result archive.

Completion goals:

- A reduced CI profile reproduces the entire workflow deterministically.
- Interrupted and resumed runs equal uninterrupted runs.
- Sharded and unsharded aggregation produce identical summaries.
- The author-approved paper manifest fixes every parameter, seed policy, trial count, artifact checksum, and figure
  recipe.
- All publication figures can be regenerated from an empty output directory using the archived inputs and one
  documented command.

### P7 — Documentation, tutorials, and community release

Develop documentation alongside each functional slice.

- README: installation, mandatory initialization, analysis-first quickstart, cache and status commands, optional JAX
  and GPU setup, CPU warning, project maturity, and links to tutorials.
- Tutorials: initialize data; analyze and plot one real Fermi light curve; rebuild the measurement model; simulate one
  seeded flare; compare NumPy and JAX; run and resume a reduced NCP scan; reproduce archived results.
- Explanation pages: terminology and units; Bayesian-block transformation; measurement model; Gaussian simulation
  convention; detection metrics; artifact provenance; GPU performance limitations.
- Auto-generate API reference from NumPy docstrings and keep hand-written pages focused on scientific reasoning.
- Add contribution guidance, a citation file, release notes, artifact DOI references, and a reproducibility checklist.

Completion goals:

- Every documented command and code example is exercised by automated smoke tests.
- `mkdocs build --strict` passes with no broken references.
- A new user can initialize, analyze a cached source, and produce a Bayesian-block plot using only README instructions.
- A GPU user can verify device selection before launching a trial.
- Documentation never claims automatic real-data flare classification until a validated quiescent estimator exists.

## Test and release gates

- Keep Ruff, formatting, strict mypy, warnings-as-errors, and at least 80% branch coverage as mandatory gates.
- Add unit tests for pure math; golden regression tests for archived fixtures; artifact-schema and corruption tests;
  offline CLI integration tests; statistical sampler tests; CPU and JAX parity tests; and non-blocking hardware
  benchmarks.
- Network access is never required by the standard test suite. Live Fermi tests run separately on a schedule and report
  upstream schema or API drift.
- Test supported Python versions in CI and maintain one environment lock or equivalent resolved dependency record for
  paper reproduction.
- Preserve existing public APIs and format-version-1 readers during the roadmap; deprecations require warnings,
  documentation, and a migration path.

## Immediate agent-facing sequence

1. Implement the pure Bayesian-block core and its regression and edge-case tests.
2. Introduce `LightCurveData` and stable HDF5 light-curve serialization.
3. Add `flare-bb init`, `flare-bb status`, and archive-manifest and checksum handling.
4. Add `flare-bb analyze`, plotting, README initialization instructions, and the first real-data tutorial.
5. Only after that analysis milestone passes all gates, harden the measurement model and begin CPU simulation, followed
   by JAX and GPU acceleration.

## Assumptions

- `/paper` remains ignored and private until the authors decide an arXiv-ready version can be public.
- The authors will provide or approve the DOI-backed `paper-v1` archive and final trial manifest before the
  reproduction release.
- NCP prior 10, log-normal fitness, measurement errors enabled, energy flux, fixed index, and TS $\geq 19$ are the
  established defaults.
- Real-data output is segmentation only; automatic flare labeling is deferred.
- NumPy is the correctness reference, while JAX and GPU are the expected backend for large simulations.
