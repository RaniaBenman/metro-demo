#!/bin/bash
# Full demo setup, in order. Needs a Metronome API token (Sandbox):
#   export METRONOME_BEARER_TOKEN="..."
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$HERE/run_single.sh" 01_setup_catalog.py
"$HERE/run_single.sh" 02_provision_customers.py
"$HERE/run_single.sh" 03_create_alerts.py
"$HERE/run_single.sh" 04_send_usage.py
echo ">> waiting 5 minutes so threshold notifications and draft invoices catch up"
sleep 300
"$HERE/run_single.sh" 07_check_state.py
"$HERE/run_single.sh" 06_dashboard_links.py
# Run separately, AFTER the "before" screenshots:
#   "$HERE/run_single.sh" 05_launch_gpu.py --hardware gpu-l40s
