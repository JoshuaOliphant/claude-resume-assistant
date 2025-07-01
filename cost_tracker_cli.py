#!/usr/bin/env python3
"""
Standalone Cost Tracker CLI for Resume Customizer

This script provides cost tracking and budget management functionality
for the Resume Customizer tool. Addresses GitHub issue #8.

Usage:
    python cost_tracker_cli.py status
    python cost_tracker_cli.py set-budget --daily 5.00
    python cost_tracker_cli.py export csv costs.csv
"""

import sys
import os
from pathlib import Path

# Add src directory to path so we can import the modules
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    from resume_customizer.cli.cost_cli import main
except ImportError as e:
    print(f"❌ Error importing cost tracking modules: {e}")
    print("Make sure you're running this script from the project root directory.")
    sys.exit(1)

if __name__ == "__main__":
    main()