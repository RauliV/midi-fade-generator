#!/bin/bash

# Wrapper script to run Python with correct environment
# This script tries different Python options to ensure midiutil is available

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/valot_python_backend.py"

# List of Python commands to try, in order of preference
PYTHON_COMMANDS=(
    "/Users/raulivirtanen/Documents/valot/.venv/bin/python"
    "python3"
    "python" 
    "/usr/bin/python3"
    "/opt/homebrew/bin/python3"
)

for python_cmd in "${PYTHON_COMMANDS[@]}"; do
    # Check if the Python command exists and can import midiutil
    if command -v "$python_cmd" >/dev/null 2>&1; then
        if "$python_cmd" -c "import midiutil" >/dev/null 2>&1; then
            echo "Using Python: $python_cmd" >&2
            exec "$python_cmd" "$PYTHON_SCRIPT" "$@"
        else
            echo "Python $python_cmd found but midiutil not available" >&2
        fi
    else
        echo "Python command $python_cmd not found" >&2
    fi
done

echo "Error: No suitable Python with midiutil found" >&2
echo "Please install midiutil with: pip install midiutil" >&2
exit 1