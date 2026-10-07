#!/usr/bin/env bash
# ==============================================================================
# OGGY X Voice Assistant Launcher
# ==============================================================================

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

echo "=================================================="
echo "Starting OGGY X AI Voice Assistant..."
echo "=================================================="

# Check virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    if command -v uv >/dev/null 2>&1; then
        uv venv .venv
        uv pip install --python .venv -r requirements.txt
    else
        python3 -m venv .venv
        .venv/bin/pip install -r requirements.txt
    fi
fi

# Ensure assets are prepared
python3 setup_assets.py 2>/dev/null || true

echo "Starting server on http://localhost:8000 ..."
echo "Open http://localhost:8000 in your browser to meet OGGY X!"
echo "=================================================="

.venv/bin/python server.py
