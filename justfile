# justfile — common tasks for FLARE-BB
# Run `just` or `just --list` to see all available recipes.

# set up the conda environment and pre-commit hooks
bootstrap:
    conda env create -f environment.yml
    conda run -n flare_bb pre-commit install
    @echo "Done. Activate with: conda activate flare_bb"

# update the lock file after editing environment.yml
lock:
    conda env export --no-builds > environment.lock.yml
    @echo "Lock file updated."

# run the full local quality gate (mirrors CI exactly)
check:
    ruff check .
    ruff format --check .
    mypy src/
    pytest --cov=src/flare_bb --cov-report=term-missing

# auto-fix all ruff issues then format
fix:
    ruff check --fix .
    ruff format .

# run tests only (faster feedback loop during development)
test *args:
    pytest {{args}}

# serve docs locally with live reload
docs:
    mkdocs serve --config-file mkdocs.yml

# strict build — fails on broken refs, missing nav entries, or bad math
docs-build:
    mkdocs build --strict --config-file mkdocs.yml
