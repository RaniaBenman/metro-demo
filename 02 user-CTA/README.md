# 02 user-CTA: build the demo in your Metronome sandbox

I can only read the sandbox, so you create the demo's Replicate data by running the scripts in `03 scripts/`. They write only to the Metronome environment your token belongs to, so use a Sandbox token.

## 1. Once: Python and a Sandbox token

- **Python 3.9+**, available as `python3`. The first run installs `metronome-sdk` into `Z Misc/.venv`, so it needs internet.
- **A Sandbox API token.** In the Metronome app, with the orange **Sandbox** banner visible: **Developer → API tokens → + Add**, role **Writer**, then copy the token (it's shown only once). Writer covers everything the scripts do, and a token's role can't be changed later.

## 2. Build the demo (about 7 minutes)

Do it in the same calendar month as the demo: the usage lands on this month's invoices.

```bash
cd "$HOME/Documents/Pro/Metronome/05 Strategy/03 scripts"
export METRONOME_BEARER_TOKEN="<your sandbox token>"   # kept for this terminal only
./run.sh
```

`run.sh` runs steps 1–4, waits 5 minutes so alerts and draft invoices catch up, then runs steps 7 and 6. **Then tell me**: I capture the "before" screens.

## 3. Launch the L40S (after the "before" screens)

```bash
./run_single.sh 04_send_usage.py --only prepaid   # once, only if you built the demo before 17 Oct
./run_single.sh 05_launch_gpu.py --hardware gpu-l40s
```

The first line sends Northwind's 50 L40S hours, added after your first run; its other events are dropped as duplicates. The second adds the L40S rate, which prices the L40S usage already sent. **Then tell me again**: I capture the "after" screens.

**Don't launch the H100.** You add its rate live in the Metronome UI during the demo. If that fails on the day, run `./run_single.sh 05_launch_gpu.py --hardware gpu-h100` instead.

## 4. On demo day

Run `./run_single.sh 06_dashboard_links.py` shortly before the demo: the customer dashboard URLs expire.

## Each step

Use these to re-run one step on its own. Re-running is safe: existing objects are reused and events are deduplicated. All IDs are saved in `Z Misc/state.json`.

| Step | Command | What it does |
|---|---|---|
| 1 | `./run_single.sh 01_setup_catalog.py` | Builds the catalog: custom field keys, the compute metric and product (priced per `hardware`), Pro and Enterprise Support, the rate card with today's 7 machine types, and the two self-serve packages. |
| 2 | `./run_single.sh 02_provision_customers.py` | Creates one customer per offering: `self_serve` Ada Okafor (free trial), `pro_support` Brightframe AI (pay-as-you-go + Pro Support), `prepaid` Northwind Media ($100k prepaid commit), `postpaid` Kepler Games ($100k postpaid minimum). `--only <offering>` creates just one. |
| 3 | `./run_single.sh 03_create_alerts.py` | Creates 5 alerts: 3 on trial credits, 1 on commits, and Brightframe's $1,500 monthly spend. Run it before step 4 so they trip as usage lands. |
| 4 | `./run_single.sh 04_send_usage.py` | Sends about 6,600 compute events, including H100 and L40S usage that has no price yet. Options: `--only <offering>`; `--print-only` shows the expected $ per machine type and sends nothing; `--without-roadmap` skips the H100/L40S usage. |
| 5 | `./run_single.sh 05_launch_gpu.py --hardware gpu-l40s` | Adds the L40S rate ($3.51/h list) from the 1st of the month, so the L40S usage already sent gets priced, with each contract's discount, commit and support fee. Options: `--price-per-hour`, `--starting-at`, `--send-usage` (10 fresh hours), `--print-only`. |
| 6 | `./run_single.sh 06_dashboard_links.py` | Read-only. Gets the time-limited customer dashboard URLs and saves them in `Z Misc/state.json`. |
| 7 | `./run_single.sh 07_check_state.py` | Read-only. Prints balances, invoices and alerts, and saves them in `Z Misc/state_snapshot.json` for the talk track. |

The demo amounts ($10 trial credit for 30 days, $500/month Pro Support, 10% Enterprise Support, $100k over 3 years at 15% off, $1,500 spend alert) are set in `replicate_common.py` and `03_create_alerts.py`.

## If something fails

- `ERROR: set METRONOME_BEARER_TOKEN in your environment.`: run the `export` line again, in the same terminal.
- `HTTP 401`: the token is wrong, or wasn't created in the Sandbox.
- `HTTP 403`: the token's role can't write. Create a Writer token.
- `Invalid custom field keys`: run step 1 again, then step 2.
- `salesforce_opportunity_id rejected in this environment; retrying without it`: expected when no Salesforce is connected. Nothing to do.
- Anything else: paste me the last 20 lines. Every step is safe to re-run once fixed.

The scripts were tested end to end against a mock of the Metronome API. This is their first run against the real one.
