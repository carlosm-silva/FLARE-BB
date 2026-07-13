"""Generate API reference pages."""

from pathlib import Path

import mkdocs_gen_files

root = Path(__file__).parent.parent
src = root / "src"
title_overrides = {"io": "I/O", "kde": "KDE", "lcr": "LCR", "hdf5": "HDF5"}


def api_title(parts: tuple[str, ...]) -> str:
    """Return the page title for an API module path."""
    name = parts[-1]
    return title_overrides.get(name, name.replace("_", " ").title())


def has_public_child_modules(package_init: Path) -> bool:
    """Return whether a package contains public modules below it."""
    package_dir = package_init.parent
    return any(path.stem != "__init__" and not path.stem.startswith("_") for path in package_dir.rglob("*.py"))


for path in sorted(src.rglob("*.py")):
    if path.stem.startswith("_"):
        continue

    module_path = path.relative_to(src).with_suffix("")
    doc_path = path.relative_to(src).with_suffix(".md")
    full_doc_path = Path("reference", doc_path)
    parts = tuple(module_path.parts)

    if parts[-1] == "__init__":
        if len(parts) > 1 and not has_public_child_modules(path):
            continue
        parts = parts[:-1]
        full_doc_path = full_doc_path.with_name("index.md")
    elif parts[-1] == "__main__":
        continue

    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        fd.write(f"# {api_title(parts)}\n\n::: {'.'.join(parts)}\n")
    mkdocs_gen_files.set_edit_path(full_doc_path, path.relative_to(root))
