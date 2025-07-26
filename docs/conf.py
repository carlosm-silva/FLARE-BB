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

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath("../src"))

# Change to project root directory for proper relative path resolution
original_cwd = os.getcwd()
project_root = os.path.abspath("..")
os.chdir(project_root)

project = "FLARE-BB"
copyright = "2025, Carlos Márcio de Oliveira e Silva Filho, Ignacio Taboada"
author = "Carlos Márcio de Oliveira e Silva Filho, Ignacio Taboada"
release = "1.0.0"
version = "1.0.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",  # Automatically document from docstrings
    "sphinx.ext.autosummary",  # Generate summary tables
    "sphinx.ext.viewcode",  # Add source code links
    "sphinx.ext.napoleon",  # Support for NumPy and Google style docstrings
    "sphinx.ext.mathjax",  # Render mathematical formulas
    "sphinx.ext.intersphinx",  # Link to other documentation
    "sphinx.ext.todo",  # Support for TODOs
    "sphinx.ext.coverage",  # Coverage checker for documentation
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_title = f"{project} v{version}"
html_short_title = project

# GitHub Pages configuration
html_baseurl = "https://carlosm-silva.github.io/FLARE-BB/"

# Read the Docs theme options
html_theme_options = {
    "canonical_url": html_baseurl,
    "analytics_id": "",  # Google Analytics ID
    "analytics_anonymize_ip": False,
    "logo_only": False,
    "display_version": True,
    "prev_next_buttons_location": "bottom",
    "style_external_links": False,
    "vcs_pageview_mode": "",
    "style_nav_header_background": "#2980B9",
    # Toc options
    "collapse_navigation": False,
    "sticky_navigation": True,
    "navigation_depth": 4,
    "includehidden": True,
    "titles_only": False,
}

# -- Options for autodoc extension -------------------------------------------

autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
}

# Mock imports for modules that have runtime dependencies
autodoc_mock_imports = [
    "pyLCR",
]

# Configure autodoc to handle import errors gracefully
autodoc_typehints = "description"
autodoc_typehints_description_target = "documented"

# Create mock environment for problematic imports
import sys


# Mock the problematic filesystem operations
def setup_mocks():
    """Set up mocks for modules that have filesystem dependencies at import time."""

    # Mock os.listdir to return empty list for the cache folder
    original_listdir = os.listdir

    def mock_listdir(path):
        if "cache" in path and "LCRs" in path:
            return []  # Return empty list for cache folder
        return original_listdir(path)

    # Apply the mock
    os.listdir = mock_listdir


# Set up mocks before importing modules
setup_mocks()

# Generate autosummary automatically
autosummary_generate = True

# -- Options for Napoleon extension ------------------------------------------

napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# -- Options for MathJax extension -------------------------------------------

mathjax3_config = {
    "tex": {
        "inlineMath": [["$", "$"], ["\\(", "\\)"]],
        "displayMath": [["$$", "$$"], ["\\[", "\\]"]],
        "processEscapes": True,
        "processEnvironments": True,
    },
    "options": {"ignoreHtmlClass": "tex2jax_ignore", "processHtmlClass": "tex2jax_process"},
}

# -- Options for intersphinx extension ---------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "pandas": ("https://pandas.pydata.org/docs/", None),
    "astropy": ("https://docs.astropy.org/en/stable/", None),
}

# -- Options for todo extension ----------------------------------------------

todo_include_todos = True

# -- Additional options -------------------------------------------------------

# The suffix(es) of source filenames.
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# Custom CSS
html_css_files = [
    "custom.css",
]

# Output file base name for HTML help builder.
htmlhelp_basename = "FLAREBBdoc"

# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    "papersize": "letterpaper",
    # The font size ('10pt', '11pt' or '12pt').
    "pointsize": "10pt",
    # Additional stuff for the LaTeX preamble.
    "preamble": r"""
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{amsfonts}
""",
    # Latex figure (float) alignment
    "figure_align": "htbp",
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, "FLARE-BB.tex", "FLARE-BB Documentation", author, "manual"),
]

# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(master_doc, "flare-bb", "FLARE-BB Documentation", [author], 1)]

# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        master_doc,
        "FLARE-BB",
        "FLARE-BB Documentation",
        author,
        "FLARE-BB",
        "Bayesian Blocks algorithm for detecting gamma-ray flares",
        "Miscellaneous",
    ),
]
