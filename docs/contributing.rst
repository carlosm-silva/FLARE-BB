Contributing to FLARE-BB
========================

We welcome contributions to FLARE-BB! This guide outlines how to contribute effectively to the project.

Getting Started
---------------

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:

   .. code-block:: bash

      git clone https://github.com/your-username/FLARE-BB.git
      cd FLARE-BB

3. **Set up the development environment**:

   .. code-block:: bash

      python -m venv venv
      source venv/bin/activate  # On Windows: venv\Scripts\activate
      pip install -r requirements-dev.txt
      pip install -e .
      pre-commit install

Types of Contributions
----------------------

Code Contributions
~~~~~~~~~~~~~~~~~~

* **Bug fixes**: Help us identify and fix bugs
* **New features**: Implement new functionality for the Bayesian Blocks algorithm
* **Performance improvements**: Optimize existing code for better performance
* **Documentation**: Improve docstrings, add examples, or fix documentation errors

Scientific Contributions
~~~~~~~~~~~~~~~~~~~~~~~~~

* **Algorithm improvements**: Enhance the Bayesian Blocks implementation
* **Validation studies**: Compare results with other change-point detection methods
* **Example notebooks**: Create Jupyter notebooks demonstrating usage
* **Test datasets**: Contribute synthetic or real gamma-ray light curve datasets

Development Workflow
--------------------

1. **Create a feature branch**:

   .. code-block:: bash

      git checkout -b feature/your-feature-name

2. **Make your changes** following our coding standards:

   * Use **120-character line length**
   * Add **type hints** to all functions
   * Include **Sphinx-style docstrings** with mathematical formulas
   * Add **GPL license headers** to new files

3. **Test your changes**:

   .. code-block:: bash

      # Run formatting and linting
      pre-commit run --all-files

      # Run tests (when available)
      pytest tests/

4. **Commit your changes**:

   .. code-block:: bash

      git add .
      git commit -m "Add descriptive commit message"

5. **Push to your fork**:

   .. code-block:: bash

      git push origin feature/your-feature-name

6. **Create a pull request** on GitHub

Code Standards
--------------

Formatting
~~~~~~~~~~

We use automated code formatting. Before committing, ensure:

.. code-block:: bash

   # Format code
   black src/ tests/ scripts/
   isort src/ tests/ scripts/

   # Check for issues
   ruff check src/ tests/ scripts/
   mypy src/

Documentation
~~~~~~~~~~~~~

All public functions and classes must include docstrings:

.. code-block:: python

   def calculate_fitness(n: int, t: float) -> float:
       """
       Calculate the fitness function for a Bayesian block.

       The fitness function is defined as:

       .. math::

           F(n, t) = \begin{cases}
               n \log n - n & \text{if } n > 0 \\
               0 & \text{if } n = 0
           \end{cases}

       :param n: Number of events in the block.
       :param t: Duration of the block in seconds.
       :return: The fitness value.
       :raises ValueError: If n is negative.
       """

Testing
~~~~~~~

* Write tests for new functionality
* Ensure existing tests pass
* Aim for high test coverage
* Include both unit tests and integration tests

Pull Request Guidelines
-----------------------

Before submitting a pull request:

✅ **Code Quality**
   * All pre-commit hooks pass
   * Code follows project style guidelines
   * No linting errors or warnings

✅ **Documentation**
   * Docstrings added for new functions/classes
   * Mathematical formulas properly formatted
   * Documentation builds without errors

✅ **Testing**
   * Tests added for new functionality
   * All existing tests pass
   * No significant decrease in test coverage

✅ **Licensing**
   * GPL license header added to new files
   * No proprietary or incompatible code included

Review Process
--------------

1. **Automated checks**: GitHub Actions will run formatting, linting, and tests
2. **Code review**: Maintainers will review your code for quality and consistency
3. **Scientific review**: For algorithm changes, we may request scientific validation
4. **Documentation review**: Ensure documentation is clear and complete

Getting Help
------------

* **Questions**: Open a GitHub issue with the "question" label
* **Bugs**: Open a GitHub issue with the "bug" label
* **Feature requests**: Open a GitHub issue with the "enhancement" label
* **Discussion**: Use GitHub Discussions for general conversation

Contact
-------

For major contributions or questions about project direction, contact:

* Carlos Márcio de Oliveira e Silva Filho (cfilho3@gatech.edu)
* Ignacio Taboada (itaboada@gatech.edu)

License
-------

By contributing to FLARE-BB, you agree that your contributions will be licensed under the same
GPL-3.0-or-later license as the project.
