#!/bin/bash
# Verification script runner

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
PROJECT_ROOT="$( cd "$BACKEND_DIR/.." && pwd )"

# Set PYTHONPATH to include project root
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Change to backend directory
cd "$BACKEND_DIR"

# Run verification
uv run python scripts/verify.py

