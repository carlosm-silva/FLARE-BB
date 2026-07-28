# Agentic Coding Delivery Workflow

This document defines how agents should deliver the
[FLARE-BB implementation roadmap](implementation-roadmap.md). The central rule is to organize work around user-facing
milestones while implementing each milestone through small, independently reviewable pull requests.

## Delivery hierarchy

Use four levels of planning:

```text
Roadmap objective
└── GitHub milestone: user-facing capability
    └── Issue: independently reviewable deliverable
        └── Short-lived branch and pull request
            └── Atomic working commits
```

A milestone is not a branch. A milestone may span several pull requests, but each pull request should leave `main`
usable, tested, and scientifically coherent.

## Pull request cadence

For each issue:

1. Create a short-lived `type/short-description` branch from the latest `main`.
2. State the user outcome, acceptance criteria, and explicit non-goals.
3. Characterize relevant legacy behavior with tests before restructuring it.
4. Implement the smallest complete vertical slice.
5. Add or update documentation in the same pull request.
6. Run `just check` and, when documentation changes, `just docs-build`.
7. Review the complete diff for unrelated edits, hidden assumptions, and accidental data or secrets.
8. Open a focused pull request with a Conventional Commit title.
9. Squash-merge only after CI and scientific review pass.
10. Delete the branch and start the next issue from the updated `main`.

Working commits should remain understandable and preferably pass the project gate, but the pull request title and
description deserve the most care because they become the commit on `main`.

## Milestone sequence

### Milestone 1 — Real-light-curve analysis

The first user-facing milestone is complete when a new user can initialize data, load a real Fermi light curve, and
produce its Bayesian-block representation using only the README.

Suggested pull requests:

1. `docs/scientific-contract`
   - Establish terminology, units, paper-backed defaults, and the legacy migration map.
2. `feat/bayesian-block-analysis`
   - Add the pure configuration, result, and analysis API with synthetic and regression tests.
3. `feat/light-curve-data`
   - Add the typed light-curve representation, pyLCR adapter, stable HDF5 schema, and offline fixtures.
4. `feat/cache-initialization`
   - Add initialization and status commands, manifests, checksums, and idempotent caching.
5. `feat/light-curve-analysis-cli`
   - Add the analysis command, visualization, analysis-first quickstart, and real-data tutorial.

### Milestone 2 — Reproducible measurement model

Deliver numerical validation, a versioned artifact schema, runtime spline construction, the bandwidth study, and the
archived `paper-v1` artifact as separate reviewable changes.

Completion means the empirical posterior can be rebuilt or downloaded, verified, loaded, and evaluated reproducibly.

### Milestone 3 — CPU simulation reference

Separate true-flux events, the NumPy conditional sampler, seeded light-curve simulation, simulation-only flare
classification, detection metrics, and the tutorial where practical.

Completion establishes the correctness reference. It does not imply that publication-scale simulation is practical on
the CPU.

### Milestone 4 — JAX and GPU acceleration

Deliver accelerator support incrementally:

1. Backend discovery and diagnostics.
2. JAX PDF evaluation with NumPy parity.
3. JAX sampling with statistical parity.
4. Batched simulation and persistent compilation caching.
5. GPU benchmarking and performance documentation.

Do not combine the JAX dependency, simulation rewrite, and publication-scale trial execution in one pull request. Each
kernel must be validated against the NumPy reference before the next optimization lands.

### Milestone 5 — Trial engine and paper reproduction

Implement checkpointing, sharding, aggregation, plotting, and the final paper profile separately. The final large run
should use already-reviewed and merged software; it should not double as development or debugging.

## Agent task contract

Give an implementation agent one issue at a time. Every task should state:

- the exact user outcome;
- the relevant roadmap objective;
- public interfaces to add or preserve;
- scientific equations, units, terminology, and defaults;
- required tests and numerical acceptance criteria;
- required documentation;
- explicit exclusions; and
- commands that must pass before handoff.

A well-bounded task looks like:

> Implement the pure Bayesian-block numerical API described in P1. Do not add caching, CLI behavior, plotting, or
> flare classification. Match the paper defaults, characterize legacy behavior, correct final-edge membership, and
> make `just check` pass.

Avoid tasks such as “implement Bayesian Blocks and start the simulator,” which combine unrelated decisions and make
scientific review difficult.

## Review responsibilities

Numerical changes require two distinct reviews:

- **Engineering review:** interfaces, typing, tests, error handling, performance, data formats, and maintainability.
- **Scientific review:** equations, transformations, units, defaults, statistical interpretation, and consistency with
  the paper.

For high-risk numerical work, use a fresh review pass that did not participate in the implementation. The reviewer
should inspect the final diff and acceptance evidence rather than relying on the implementing agent's summary.

## Branch and commit policy

- Use lightweight GitHub Flow: branch, pull request, CI, squash-merge, delete branch.
- Keep branches short-lived and limited to one issue.
- Use Conventional Commit titles, such as `feat(analysis): add Bayesian-block segmentation`.
- Stage deliberately; never stage the entire worktree without inspecting it.
- Rebase a stale branch on the latest `origin/main` before final review.
- Do not bypass failing checks, warnings, coverage gates, or strict documentation builds.
- Direct commits to `main` are reserved for genuinely trivial, low-risk corrections.

This workflow keeps the repository usable throughout the migration, preserves clear scientific review boundaries, and
gives agents tasks small enough to implement and verify reliably.
