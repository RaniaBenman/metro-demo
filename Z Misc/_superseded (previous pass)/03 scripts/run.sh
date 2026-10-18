#!/bin/bash
# Full demo setup, in order. Needs a Metronome API token:
#   export METRONOME_BEARER_TOKEN="..."
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$HERE/run_single.sh" 01_setup_catalog.py
"$HERE/run_single.sh" 02_provision_customers.py
"$HERE/run_single.sh" 03_create_alerts.py
"$HERE/run_single.sh" 04_send_usage.py
"$HERE/run_single.sh" 06_dashboard_links.py
# 05_add_machine_type.py is run separately (after the "before" screenshots / live in the demo):
#   "$HERE/run_single.sh" 05_add_machine_type.py --sample-usage
