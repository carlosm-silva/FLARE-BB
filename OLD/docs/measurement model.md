### Measurement model
Each Fermi-LAT observation is treated as a sample from a bivariate distribution  

$$
\mathcal{D} \sim (F_m, \sigma_m) \in \mathbb{R}^+ \times \mathbb{R}^+,
$$  
where $F_m$ is the measured energy flux and $\sigma_m$ the uncertainty associated with that measurement.  
We assume $\mathcal{D}$ depends only on the true flux $F_R$ and that measurement uncertainties are log-normally distributed.

Under these assumptions, simulating a light curve consists of evaluating $F_R(t)$ discrete times, then using the obtained values to shape $\mathcal{D}$ and sample the measured flux and error. Sampling is implemented by evaluating the PDF associated to $\mathcal{D}$, hereinafter denoted as $p\big((F_m, \sigma_m) \big| F_R\big)$ through Bayes Theorem:

$$
p\!\bigl((F_m,\sigma_m) \mid F_R\bigr)
\;=\;
\frac{
p\!\bigl(F_R \mid (F_m,\sigma_m)\bigr)\,
p\!\bigl(F_m,\sigma_m\bigr)
}{
p(F_R)
}
\tag{2}
$$
Given Equation (2), evaluating the PDF $p\big((F_m, \sigma_m) \big| F_R )$ can be reduced to evaluating each of the following terms separately:
- The likelihood $p\big(F_R \big| (F_m, \sigma_m)\big)$.
- The prior $p\big((F_m, \sigma_m)\big)$.
- The marginal likelihood $p(F_R)$.
#### Likelihood
Because the uncertainties are log-normal, the likelihood takes the form:
$$
p(x) \;=\;
\frac{1}{x\,\sigma\,\sqrt{2\pi}}\,
\exp\!\left[
-\frac{(\ln x - \mu)^2}{2\sigma^2}
\right]
\tag{3}
$$
Using the definitions of $F_m$ and $\sigma_m$, we approximate:
$$
\sigma \,\approx\, \ln(F_m + \sigma_m) - \ln(F_m),
\qquad
\mu = \ln(F_m) - \tfrac{\sigma^2}{2}.
\tag{4}
$$
#### Prior distribution from historical Fermi-LAT data
The prior $p(F_m, \sigma_m)$ is obtained empirically from the Fermi Large Area Telescope (LAT) Light-Curve Repository (LCR), which contains long-term light curves for more than 1 500 variable sources.  
To ensure clean, well-resolved data for blazars we
* use daily cadence with a fixed spectral index,  
* discard fits that are unconstrained or did not converge, and  
* retain only measurements with a test statistic $\text{TS} \ge 19$.

This yields 77 992 three-day-averaged measurements that define the prior.

Because no simple closed form appears suitable, the prior is modeled with a Gaussian kernel-density estimate (KDE) evaluated in log–log space.  
A bandwidth of ≈ 0.2 decades provides a good balance between bias and variance; variations of ± 0.1 decades have little effect.  
The resulting KDE is pre-computed on a $512 \times 512$ grid covering more than 99 % of Fermi-LAT measurements and stored in a linear-interpolator object for fast lookup.
#### Marginal likelihood
The marginal likelihood $p(F_R)$ follows from the law of total probability:

$$
p(F_R) \;=\;
\iint_{(f,\varsigma)\,\in\,\Omega}
p\!\bigl(F_R \mid (f,\varsigma)\bigr)\;
p\!\bigl(f,\varsigma\bigr)\,
\mathrm{d}f\,\mathrm{d}\varsigma,
\tag{5}
$$

where $\Omega$ is the domain of $(F_m,\sigma_m)$.  
Because $p\!\bigl(F_R \mid (f,\varsigma)\bigr)$ and $p\!\bigl(f,\varsigma\bigr)$ are already defined (Equations 3 – 4 and the KDE prior, respectively), the integral yields a univariate function that depends only on $F_R.$  
It too is evaluated once and stored in a linear-interpolator object for subsequent use.
