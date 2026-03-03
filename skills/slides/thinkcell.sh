#!/bin/bash
# Think-cell Automation Tool Wrapper
# No Poetry venv needed — stdlib only

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
python3 "$SCRIPT_DIR/thinkcell_tool.py" "$@"
