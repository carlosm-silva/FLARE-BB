# Scientific Contract

This page is the authoritative P0 vocabulary and default contract for FLARE-BB.
It fixes the meaning of public scientific quantities before the analysis, cache,
and simulation interfaces are introduced. It does not describe automatic flare
classification: real-data analysis is limited to Bayesian-block segmentation
until a quiescent estimator is scientifically validated.

## Canonical quantities

| Python name | Symbol | Definition | Unit |
| --- | --- | --- | --- |
| `true_flux` | $F_R$ | Flux underlying a simulated or measured observation. | $\mathrm{erg\,cm^{-2}\,s^{-1}}$ |
| `measured_flux` | $F_m$ | Flux reported by the Fermi-LAT light-curve product. | $\mathrm{erg\,cm^{-2}\,s^{-1}}$ |
| `measurement_uncertainty` | $\sigma_m$ | LCR 1-sigma symmetric Gaussian-equivalent statistical uncertainty associated with `measured_flux`. | $\mathrm{erg\,cm^{-2}\,s^{-1}}$ |
| `quiescent_flux` | $F_Q$ | Baseline true flux used only in simulation. | $\mathrm{erg\,cm^{-2}\,s^{-1}}$ |
| `flare_peak_flux` | $F_0$ | Peak amplitude above `quiescent_flux` used only in simulation. | $\mathrm{erg\,cm^{-2}\,s^{-1}}$ |
| `flare_center` | $t_0$ | Center time of an injected simulated flare. | elapsed days |
| `flare_width_days` | $W=2\sigma$ | Full flare-width convention for an injected Gaussian flare. | days |
| `ncp_prior` | $\mathrm{ncp\_prior}$ | Bayesian-block change-point penalty. | dimensionless |

Observed `times` are Fermi mission elapsed time (MET) in seconds. Simulated
`times` are elapsed days. APIs must name conversion boundaries explicitly; they
must not silently mix these time coordinates.

## Established defaults

The paper-backed defaults below apply to the production analysis contract. They
supersede incompatible exploratory values in `OLD2`.

| Setting | Default | Scope |
| --- | --- | --- |
| LCR product | daily product with three-day bins | observed light curves |
| `flux_type` | `"energy"` | observed light curves |
| `index_type` | `"fixed"` | observed light curves |
| retained test statistic | $\mathrm{TS} \geq 19$ | measurement-model inputs |
| Bayesian-block distribution | `"log_normal"` | segmentation |
| measurement errors | enabled | segmentation |
| `ncp_prior` | `10` | segmentation |

The LCR request threshold and the retained-measurement threshold are distinct:
the current source request may use `ts_min=4`, while a later named cleaning
policy retains only measurements meeting $\mathrm{TS} \geq 19$. The cache and
analysis APIs must preserve that distinction.

## Scientific conventions

For a detected measurement, pyLCR represents `flux_error` as the endpoints
`(measured_flux - measurement_uncertainty, measured_flux +
measurement_uncertainty)`. FLARE-BB derives `measurement_uncertainty` from the
upper endpoint less `measured_flux`; this is valid only for the symmetric LCR
error representation.

The LCR computes that uncertainty from the inverse Hessian at the optimum of the
log-likelihood surface. It is therefore a 1-sigma symmetric
Gaussian-equivalent statistical uncertainty, not a separately constructed 68%
profile-likelihood confidence interval. The familiar 68.3% coverage statement
applies only under the Gaussian approximation and must not be treated as an
exact interval identity after the log-normal transformation.

For log-normal analysis, the measurement model uses

$$
\begin{aligned}
\sigma &= \ln(F_m + \sigma_m) - \ln(F_m), \\
\mu &= \ln(F_m) - \frac{\sigma^2}{2}.
\end{aligned}
$$

Consequently, log-normal analysis requires positive finite `measured_flux` and
`measurement_uncertainty`. Normal analysis is an explicit alternative, not an
implicit fallback. Future public APIs must validate these assumptions at their
boundaries.

## Provenance boundary

`OLD2` and the private `/paper` tree are reference material only. Production
modules, package tests, and CI must not import from or read either tree. Stable
conventions are documented here and historical components are tracked in the
[migration map](migration-map.md).
