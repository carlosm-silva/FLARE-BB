# Measurement Model

FLARE-BB models each Fermi-LAT observation as a measured flux/error pair $(F_m, \sigma_m)$ conditioned on an underlying true flux $F_R$.

For a detected observation, pyLCR exposes `flux_error` as the endpoints
$(F_m - \sigma_m, F_m + \sigma_m)$. Here $\sigma_m$ is the Fermi-LAT Light
Curve Repository's 1-sigma symmetric Gaussian-equivalent statistical
uncertainty, computed from the inverse Hessian at the optimum of the
log-likelihood surface. It is not a separately constructed 68%
profile-likelihood confidence interval; 68.3% coverage is only the Gaussian
approximation associated with a one-standard-deviation error.

The posterior used by the distribution builder is

$$
p\bigl(F_m,\sigma_m \mid F_R\bigr)
=
\frac{
p\bigl(F_R \mid F_m,\sigma_m\bigr)
p\bigl(F_m,\sigma_m\bigr)
}{
p(F_R)
}.
$$

## Prior

The prior $p(F_m,\sigma_m)$ is estimated empirically from historical blazar light curves. The KDE workflow works in log-log space, using measured log10 flux and measured log10 uncertainty samples after quality cuts.

## Likelihood

The likelihood assumes log-normal measurement uncertainty:

$$
p(x) =
\frac{1}{x\sigma\sqrt{2\pi}}
\exp\left[
-\frac{(\ln x - \mu)^2}{2\sigma^2}
\right].
$$

with

$$
\begin{aligned}
\sigma &\approx \ln(F_m + \sigma_m) - \ln(F_m), \\
\mu &= \ln(F_m) - \frac{\sigma^2}{2}.
\end{aligned}
$$

## Marginal Likelihood

The marginal likelihood integrates over measured flux/error space:

$$
p(F_R) =
\iint_\Omega
p\bigl(F_R \mid f,\varsigma\bigr)
p\bigl(f,\varsigma\bigr)
F_R \ln(10)
\,df\,d\varsigma.
$$

The implementation tabulates this one-dimensional function and interpolates it before generating posterior grids.
