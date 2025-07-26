#!/usr/bin/env python3
"""
Script to build FLARE-BB documentation locally.
"""

import os
import subprocess
import sys
import webbrowser
from pathlib import Path


def main():
    """Build the documentation and optionally open it in a browser."""
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    docs_dir = project_root / "docs"

    print("Building FLARE-BB documentation...")
    print(f"Project root: {project_root}")
    print(f"Docs directory: {docs_dir}")

    # Change to docs directory
    os.chdir(docs_dir)

    try:
        # Build the documentation
        print("\nRunning 'make html'...")
        result = subprocess.run(["make", "html"], check=True, capture_output=True, text=True)
        print("✅ Documentation built successfully!")

        # Get the path to the built documentation
        html_path = docs_dir / "_build" / "html" / "index.html"

        if html_path.exists():
            print(f"\n📚 Documentation built at: {html_path}")

            # Ask if user wants to open in browser
            response = input("\nWould you like to open the documentation in your browser? (y/n): ")
            if response.lower() in ["y", "yes"]:
                print("Opening documentation in browser...")
                webbrowser.open(f"file://{html_path.absolute()}")
        else:
            print("❌ Built documentation not found!")
            return 1

    except subprocess.CalledProcessError as e:
        print(f"❌ Error building documentation: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return 1
    except FileNotFoundError:
        print("❌ 'make' command not found. Please install Sphinx and make sure 'make' is available.")
        print("You can install Sphinx with: pip install sphinx sphinx-rtd-theme")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
