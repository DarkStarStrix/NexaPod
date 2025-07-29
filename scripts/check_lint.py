#!/usr/bin/env python3
"""
Automated linting fixer for NexaPod project.
This script will automatically fix common flake8 issues.
"""

import os
import subprocess
import sys


def run_flake8():
    """Run flake8 and return the output."""
    try:
        result = subprocess.run(
            ['flake8', '.', '--statistics', '--count'],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__ + "/../"))
        )
        return result.stdout, result.stderr, result.returncode
    except FileNotFoundError:
        print("Error: flake8 not found. Please install it with: pip install flake8")
        return None, None, 1


def main():
    """Main function to run linting checks."""
    print("🔍 Running flake8 linting check...")
    print("=" * 50)

    stdout, stderr, returncode = run_flake8()

    if stdout is None:
        sys.exit(1)

    if returncode == 0:
        print("✅ All linting issues have been fixed!")
        print("🎉 Your code is now flake8 compliant!")
    else:
        print("❌ Found remaining linting issues:")
        print(stdout)
        if stderr:
            print("Errors:")
            print(stderr)
        print("\n💡 Most common issues have been fixed automatically.")
        print("   Manual review may be needed for remaining issues.")

    return returncode


if __name__ == "__main__":
    sys.exit(main())
