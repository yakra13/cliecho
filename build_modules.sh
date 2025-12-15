#!/usr/bin/env bash
set -euo pipefail

MODULES_DIR="$(dirname "$0")/modules_working"
OUTPUT_DIR="$(dirname "$0")/modules"

# Check for optional argument
if [ $# -eq 1 ]; then
    MODULES=("$1")
else
    MODULES=()
    # Find all directories inside modules_working
    while IFS= read -r -d '' dir; do
        MODULES+=("$(basename "$dir")")
    done < <(find "$MODULES_DIR" -mindepth 1 -maxdepth 1 -type d -print0)
fi

# Loop through modules and run build.sh
for module in "${MODULES[@]}"; do
    MODULE_PATH="$MODULES_DIR/$module"
    BUILD_SCRIPT="$MODULE_PATH/build.sh"

    if [ ! -x "$BUILD_SCRIPT" ]; then
        echo "[!] Skipping $module: build.sh not found or not executable"
        continue
    fi

    echo "[*] Building module: $module"
    (cd "$MODULE_PATH" && ./build.sh)

    # Copy .whl files to modules folder
    WHL_FILES=("$MODULE_PATH/dist/"*.whl)
    if [ -e "${WHL_FILES[0]}" ]; then
        echo "[*] Copying wheel(s) for $module to modules folder"
        cp "$MODULE_PATH/dist/"*.whl "$OUTPUT_DIR/"
    else
        echo "[!] No wheel found for $module"
    fi
done

echo "[+] All builds complete"