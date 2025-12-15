#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

MODULE_NAME=$(basename "$PWD")
echo "[*] Building wheel for $MODULE_NAME using python3.8"

# Clean old build artifacts
rm -rf dist build *.egg-info

# Make sure build tools are installed
python3.8 -m pip install --upgrade pip setuptools wheel build

# Build the wheel
python3.8 -m build --wheel

echo "[+] Build complete! Wheel file(s) in dist/:"
ls -lh dist/*.whl
