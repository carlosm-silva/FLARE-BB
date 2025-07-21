Development Guide
=================

For detailed development setup instructions, code formatting standards, and contribution guidelines,
please refer to the `DEVELOPMENT.md <../DEVELOPMENT.html>`_ file in the project root.

Quick Reference
---------------

Essential development commands:

.. code-block:: bash

   # Install development dependencies
   pip install -r requirements-dev.txt

   # Set up pre-commit hooks
   pre-commit install

   # Format code
   black src/ tests/ scripts/
   isort src/ tests/ scripts/

   # Check code quality
   ruff check src/ tests/ scripts/
   mypy src/

   # Run all checks
   pre-commit run --all-files

Code Standards
--------------

* **Line length**: 120 characters
* **Indentation**: 4 spaces (no tabs)
* **Docstrings**: Sphinx-style with reStructuredText formatting
* **Type hints**: Required for all function parameters and return values
* **License headers**: GPL-3.0-or-later header in all Python files

Mathematical Documentation
--------------------------

Include LaTeX formulas in docstrings using reStructuredText math directives:

.. code-block:: python

   def fitness_function(n: int) -> float:
       """
       Calculate the fitness function for a block.

       .. math::

           F(n) = n \log n - n

       :param n: Number of events in the block.
       :return: Fitness value.
       """
       return n * np.log(n) - n if n > 0 else 0
