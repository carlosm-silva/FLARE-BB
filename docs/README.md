# FLARE-BB Documentation

This directory contains the Sphinx documentation for FLARE-BB.

## Building Locally

### Prerequisites

1. Install Python dependencies:
   ```bash
   pip install sphinx sphinx-rtd-theme
   pip install -r ../requirements-dev.txt
   ```

2. Make sure you're in the project root directory.

### Building HTML Documentation

```bash
cd docs
make html
```

The built documentation will be available in `docs/_build/html/`.

### Building Other Formats

```bash
# PDF documentation
make latexpdf

# Single HTML file
make singlehtml

# EPUB
make epub
```

## Viewing the Documentation

After building, you can view the documentation by opening `docs/_build/html/index.html` in your web browser.

## GitHub Pages

The documentation is automatically built and deployed to GitHub Pages when changes are pushed to the main branch. The live documentation is available at:

https://carlosm-silva.github.io/FLARE-BB/

## Structure

- `conf.py` - Sphinx configuration
- `index.rst` - Main documentation page
- `api/` - API documentation
- `_static/` - Static assets (CSS, images, etc.)
- `_templates/` - Custom templates
- `_build/` - Built documentation (generated)

## Adding New Documentation

1. Create new `.rst` files in the appropriate directory
2. Add them to the appropriate `toctree` in `index.rst` or other index files
3. Build and test locally
4. Commit and push to trigger automatic deployment 
