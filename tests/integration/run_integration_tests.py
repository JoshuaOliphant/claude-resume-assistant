#!/usr/bin/env python3
# ABOUTME: Script to run integration tests with real Claude Code SDK
# ABOUTME: Helps verify Claude's actual behavior with file operations

"""Run integration tests for Claude Code SDK."""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Run integration tests with proper setup."""
    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY environment variable not set!")
        print("\nTo run integration tests, you need to:")
        print("1. Copy .env.example to .env")
        print("2. Add your Anthropic API key to .env")
        print("3. Run: source .env")
        print("\nOr set it directly:")
        print("export ANTHROPIC_API_KEY='your-api-key-here'")
        return 1
    
    print("✅ API key found")
    print("\nRunning integration tests with real Claude Code SDK...")
    print("This will make actual API calls and may take a few moments.\n")
    
    # Run pytest with integration marker
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/integration/test_claude_integration.py",
        "-v",
        "-s",  # Show print statements
        "-m", "integration",
        "--tb=short"  # Shorter traceback
    ]
    
    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent.parent.parent)
        return result.returncode
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        return 1

if __name__ == "__main__":
    sys.exit(main())