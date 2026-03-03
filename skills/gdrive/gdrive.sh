#!/bin/bash
# Google Drive Tool Wrapper

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
poetry -C "$SCRIPT_DIR" run python "$SCRIPT_DIR/gdrive_tool.py" "$@"
