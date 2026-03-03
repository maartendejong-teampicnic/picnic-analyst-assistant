#!/bin/bash
# Slides Tool Wrapper

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
poetry -C "$SCRIPT_DIR" run python "$SCRIPT_DIR/slides_tool.py" "$@"
