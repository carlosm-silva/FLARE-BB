#!/usr/bin/env python3
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

Script to check that all Python files have the proper GPL license header.
"""

import sys
from pathlib import Path
from typing import List


REQUIRED_HEADER = '''"""
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
along with this file.  If not, see <https://www.gnu.org/licenses/>.'''


def check_license_header(file_path: Path) -> bool:
    """
    Check if a Python file has the required GPL license header.

    :param file_path: Path to the Python file to check.
    :return: True if the header is present and correct, False otherwise.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check if the required header is present at the beginning
        return REQUIRED_HEADER in content[: len(REQUIRED_HEADER) + 100]

    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False


def main() -> int:
    """
    Main function to check license headers in all provided Python files.

    :return: Exit code (0 for success, 1 for failure).
    """
    if len(sys.argv) < 2:
        print("Usage: python check_license_headers.py <file1.py> [file2.py] ...")
        return 1

    files_to_check = [Path(arg) for arg in sys.argv[1:]]
    failed_files: List[Path] = []

    for file_path in files_to_check:
        if not file_path.exists():
            print(f"File not found: {file_path}")
            failed_files.append(file_path)
            continue

        if not file_path.suffix == ".py":
            # Skip non-Python files
            continue

        if not check_license_header(file_path):
            print(f"Missing or incorrect license header in: {file_path}")
            failed_files.append(file_path)

    if failed_files:
        print(f"\n{len(failed_files)} file(s) failed license header check:")
        for file_path in failed_files:
            print(f"  - {file_path}")
        print("\nPlease add the required GPL license header to these files.")
        return 1

    print(f"All {len(files_to_check)} Python files have correct license headers.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
