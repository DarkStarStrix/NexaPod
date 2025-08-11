#!/bin/bash

# NexaPod CLI Runner (Bash)
#
# Runs the CLI without requiring a package installation.
# Usage: ./scripts/NexaPod.sh [command]
# Example: ./scripts/NexaPod.sh setup

# --- Script Implementation ---
set -euo pipefail

# Ensure the script is run with bash, not sh.
if [ -z "$BASH_VERSION" ]; then
    echo "Error: This script must be run with bash, not sh." >&2
    exit 1
fi

# Get the directory where the script is located
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
# Assume the project root is one level up from the script's directory
PROJECT_ROOT=$(dirname "$SCRIPT_DIR")

# Path to the main python script
CLI_MAIN="$PROJECT_ROOT/NexaPod_CLI/main.py"

# Check if the main script exists
if [ ! -f "$CLI_MAIN" ]; then
    echo "Error: CLI entrypoint not found at $CLI_MAIN" >&2
    echo "Please ensure you are running this script from within the NexaPod project structure." >&2
    exit 1
fi

# Find a suitable Python command, preferring 'py' (Windows), then 'python3', then 'python'.
PYTHON_CMD=""
for cmd in py python3 python; do
    if command -v "$cmd" &> /dev/null; then
        PYTHON_CMD="$cmd"
        break
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "Error: Python is not installed or not in your PATH." >&2
    echo "On Windows, ensure Python is installed correctly and not just the Microsoft Store alias." >&2
    exit 1
fi

# Execute the python script, passing all arguments to it.
# If no arguments are provided, the script will start in interactive mode.
"$PYTHON_CMD" "$CLI_MAIN" "$@"
