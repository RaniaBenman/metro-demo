#!/bin/bash
# Reproducible runner for the Replicate x Metronome demo scripts.
#
# Usage (from anywhere):
#   "03 scripts/run_single.sh" 01_setup_catalog.py
#   METRONOME_BEARER_TOKEN=... "03 scripts/run_single.sh" 04_send_usage.py --print-only
#
# Bootstraps "Z Misc/.venv" from requirements.txt on first use,
# then runs the requested step script with that interpreter.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"   # .../Metronome/05 Strategy/03 scripts
VENV="$(cd "$HERE/.." && pwd)/Z Misc/.venv"             # .../Metronome/05 Strategy/Z Misc/.venv

if [ ! -x "$VENV/bin/python" ]; then
    echo ">> creating $VENV"
    mkdir -p "$(dirname "$VENV")"
    python3 -m venv "$VENV"
fi

# Install on first run, and whenever requirements.txt changes.
STAMP="$VENV/.requirements.sha1"
if [ ! -f "$STAMP" ] || ! shasum -a 1 --check --status "$STAMP" 2>/dev/null; then
    echo ">> installing dependencies from requirements.txt"
    "$VENV/bin/pip" install -r "$HERE/requirements.txt"
    shasum -a 1 "$HERE/requirements.txt" > "$STAMP"
fi

exec "$VENV/bin/python" "$HERE/${1:?usage: run_single.sh <script.py> [args...]}" "${@:2}"
