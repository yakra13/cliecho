#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

PYTHON=python3.8
MODULE_NAME=$(basename "$PWD")
echo "[*] Building wheel for $MODULE_NAME using $(python3 --version)"

# Clean old build artifacts
rm -rf dist build *.egg-info

# Make sure build tools are installed
$PYTHON -m pip install --upgrade pip setuptools wheel build

# Build the wheel
$PYTHON -m build --wheel

echo "[+] Build complete! Wheel file(s) in dist/:"
ls -lh dist/*.whl
