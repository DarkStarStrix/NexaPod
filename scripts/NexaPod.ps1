# NexaPod CLI Runner (PowerShell)
#
# Runs the CLI without requiring a package installation.
# Usage: .\scripts\NexaPod.ps1 [command]
# Example: .\scripts\NexaPod.ps1 setup

# --- Script Implementation ---
# Exit the script if any command fails.
$ErrorActionPreference = "Stop"

# Get the directory of the current script
$ScriptDir = $PSScriptRoot

# Construct the path to the project root (one level up)
$ProjectRoot = Split-Path -Path $ScriptDir -Parent

# Construct the full path to the main CLI script
$CliMainPath = Join-Path -Path $ProjectRoot -ChildPath "NexaPod_CLI\main.py"

# Check if the main script exists
if (-not (Test-Path -Path $CliMainPath -PathType Leaf)) {
    Write-Error "CLI entrypoint not found at $CliMainPath"
    Write-Error "Please ensure you are running this script from within the NexaPod project structure."
    exit 1
}

# Find a suitable Python executable, preferring 'py', then 'python3', then 'python'.
$PythonExe = Get-Command py, python3, python -ErrorAction SilentlyContinue | Select-Object -First 1

if (-not $PythonExe) {
    Write-Error "Error: Python is not installed or not in your PATH."
    Write-Error "This can happen if Windows is pointing to the Microsoft Store alias. Ensure a full Python version is installed and accessible via your system's PATH, or via the 'py.exe' launcher."
    exit 1
}

# Execute the python script, passing all arguments to it.
# If no arguments are provided, the script will start in interactive mode.
& $PythonExe.Source $CliMainPath $args
