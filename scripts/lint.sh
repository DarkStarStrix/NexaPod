#!/bin/bash

# Flake8 linting script for NexaPod project
echo "Running flake8 on NexaPod project..."
echo "=================================="

# Run flake8 with configuration
flake8 . --statistics --count

echo ""
echo "Linting complete!"
echo "Check the output above for any remaining issues."
