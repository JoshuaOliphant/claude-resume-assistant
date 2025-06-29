#!/usr/bin/env python
# ABOUTME: Main entry point script for the resume customizer CLI
# ABOUTME: Allows running the tool with `python resume_customizer.py` or `./resume_customizer.py`

"""Main entry point for the resume customizer CLI."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from resume_customizer.cli.app import main

if __name__ == "__main__":
    main()