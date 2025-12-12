#!/bin/bash
# Run script for ChatDB backend

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Set PYTHONPATH to include project root
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Change to backend directory
cd "$SCRIPT_DIR"

# Run with uv
uv run python -m backend.main "$@"

