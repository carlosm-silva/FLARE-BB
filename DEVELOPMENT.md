# Development Setup for FLARE-BB

This document describes how to set up your development environment to maintain consistent code formatting and quality across the FLARE-BB project.

## Prerequisites

- Python 3.8 or later
- Git
- Cursor/VSCode editor (recommended)

## Initial Setup

### 1. Clone and Set Up the Environment

```bash
# Clone the repository
git clone <repository-url>
cd FLARE-BB

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install project dependencies
pip install -r requirements-dev.txt
pip install -e .
```

### 2. Install Required VSCode/Cursor Extensions

For the best development experience, install these extensions:

- **Python** (ms-python.python)
- **Black Formatter** (ms-python.black-formatter) 
- **Ruff** (charliermarsh.ruff)
- **Python Docstring Generator** (njpwerner.autodocstring)
- **EditorConfig for VS Code** (editorconfig.editorconfig)

### 3. Set Up Pre-commit Hooks

Pre-commit hooks automatically format and check your code before each commit:

```bash
# Install pre-commit hooks
pre-commit install

# Test the hooks (optional)
pre-commit run --all-files
```

## Code Formatting Standards

### Our Standards

- **Line length**: 120 characters
- **Indentation**: 4 spaces (no tabs)
- **Import sorting**: Organized by type (stdlib, third-party, local)
- **Docstrings**: Sphinx-style with reStructuredText formatting
- **Type hints**: Required for all function parameters and return values
- **License headers**: GPL-3.0-or-later header in all Python files

### Docstring Format

Use Sphinx-style docstrings with the following format:

```python
def example_function(param1: str, param2: int) -> bool:
    """
    Brief description of what the function does.
    
    :param param1: Description of the first parameter.
    :param param2: Description of the second parameter.
    :return: Description of what is returned.
    """
    # Implementation here
    return True
```

### Including Mathematical Formulas

For scientific computing projects like FLARE-BB, you can include LaTeX-formatted mathematical formulas in your docstrings:

#### Inline Math
Use single backticks with math directive for inline formulas:

```python
def bayesian_blocks(data: np.ndarray) -> np.ndarray:
    """
    Apply Bayesian Blocks algorithm with fitness function :math:`F = N \log N - N`.
    
    The algorithm minimizes the cost function :math:`C = -F + \gamma` where 
    :math:`\gamma` is the prior penalty term.
    
    :param data: Input time series data.
    :return: Block edges array.
    """
    pass
```

#### Block Math
Use the `.. math::` directive for displayed equations:

```python
def log_likelihood_ratio(n1: int, n2: int, t1: float, t2: float) -> float:
    """
    Calculate the log-likelihood ratio for two adjacent blocks.
    
    The log-likelihood ratio is computed as:
    
    .. math::
        
        \Lambda = 2 \left[ (n_1 + n_2) \log(n_1 + n_2) - n_1 \log n_1 - n_2 \log n_2 \right]
        
    where :math:`n_1` and :math:`n_2` are the photon counts in blocks 1 and 2.
    
    :param n1: Photon count in first block.
    :param n2: Photon count in second block.
    :param t1: Duration of first block.
    :param t2: Duration of second block.
    :return: Log-likelihood ratio value.
    """
    pass
```

#### Multi-line Equations
For complex equations, use proper LaTeX alignment:

```python
def fitness_function(n: int, t: float) -> float:
    """
    Calculate the fitness function for a block.
    
    .. math::
        
        F(n, t) = \begin{cases}
            n \log n - n & \text{if } n > 0 \\
            0 & \text{if } n = 0
        \end{cases}
        
    :param n: Number of events in the block.
    :param t: Duration of the block.
    :return: Fitness value.
    """
    pass
```

**Note**: When building documentation with Sphinx, ensure you have the `sphinx.ext.mathjax` extension enabled in your `conf.py` to properly render mathematical formulas.

### License Header Templates

Python files must include GPL license headers, but the format depends on the file type:

#### For `__init__.py` Files (Comment Format)

Use comment format to avoid cluttering generated documentation:

```python
# SPDX-License-Identifier: GPL-3.0-or-later
# FLARE-BB – Bayesian Blocks algorithm for detecting gamma-ray flares
# Copyright © 2025 Carlos Márcio de Oliveira e Silva Filho
# Copyright © 2025 Ignacio Taboada
#
# This file is part of FLARE-BB.
# FLARE-BB is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# FLARE-BB is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this file.  If not, see <https://www.gnu.org/licenses/>.

"""
Brief module description for documentation.
"""
```

#### For Regular Module Files (Docstring Format)

Use docstring format for individual module files:

```python
"""
SPDX-License-Identifier: GPL-3.0-or-later
FLARE-BB – Bayesian Blocks algorithm for detecting gamma-ray flares
Copyright © 2025 Carlos Márcio de Oliveira e Silva Filho
Copyright © 2025 Ignacio Taboada

This file is part of FLARE-BB.
FLARE-BB is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

FLARE-BB is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this file.  If not, see <https://www.gnu.org/licenses/>.

------------------------------------------------------------------------------------------------------------------------

Brief description of what this file contains.
"""
```

## Manual Code Formatting

While the editor should format code automatically, you can also run formatting tools manually:

### Format Code

```bash
# Format all Python files with Black
black src/ tests/ scripts/

# Sort imports with isort
isort src/ tests/ scripts/

# Format a specific file
black src/data_processing/caching.py
```

### Check Code Quality

```bash
# Run all linting checks
ruff check src/ tests/ scripts/

# Run type checking
mypy src/

# Check license headers (automatically handles both comment and docstring formats)
python scripts/check_license_headers.py src/**/*.py
```

### Run All Checks

```bash
# Run all pre-commit hooks manually
pre-commit run --all-files
```

## Editor Configuration

### Automatic Formatting

With the provided `.vscode/settings.json`, your editor will:

- Format code on save using Black
- Organize imports on save using isort
- Show a ruler at 120 characters
- Use 4-space indentation
- Enable type checking with MyPy
- Generate Sphinx-style docstrings

### Keyboard Shortcuts

Useful keyboard shortcuts in VSCode/Cursor:

- **Ctrl/Cmd + Shift + P**: Command palette
- **Ctrl/Cmd + Shift + I**: Format document
- **Alt + Shift + O**: Organize imports
- **Ctrl/Cmd + .**: Quick fix (code actions)

## Configuration Files

The project includes several configuration files that enforce consistent formatting:

- **`pyproject.toml`**: Main configuration for Black, isort, Ruff, MyPy, and project metadata
- **`.editorconfig`**: Basic editor settings (indentation, line endings, etc.)
- **`.vscode/settings.json`**: VSCode/Cursor-specific settings
- **`.pre-commit-config.yaml`**: Pre-commit hook configuration
- **`requirements-dev.txt`**: Development dependencies

## Troubleshooting

### Common Issues

1. **Format on save not working**: Ensure you have the Black Formatter extension installed and enabled.

2. **Import organization not working**: Check that the Python extension is installed and isort is configured.

3. **Pre-commit hooks failing**: Run `pre-commit run --all-files` to see specific errors.

4. **Type checking errors**: Review MyPy configuration in `pyproject.toml` and add type hints as needed.

### Disabling Checks Temporarily

If you need to disable a specific check for a line:

```python
# Disable MyPy for a line
result = some_function()  # type: ignore

# Disable Ruff for a line  
import unused_module  # noqa: F401
```

## Contributing

Before submitting a pull request:

1. Ensure all pre-commit hooks pass
2. Add type hints to new functions
3. Include Sphinx-style docstrings
4. Add the GPL license header to new files
5. Test your changes with `pytest`

For questions about the development setup, please refer to the main README or contact the project maintainers. 
