# 02 user-CTA: scripts to run before I capture the demo screens

I can only **read** the Metronome account, so the Replicate-specific objects the demo needs have to be created by you, using these scripts. I checked `~/Documents/Pro/Metronome/02 work/v3_comments_exceptions/scripts` first. Those scripts model Raindrop's token pricing ($20/month package, input and output tokens), so none of them builds what Replicate needs: per-second GPU pricing, support tiers, a trial credit and a multi-year commit. I left that folder untouched. The new scripts in `03 scripts/` follow its structure, comments and runner.

## Requirements (once)

- Python 3.9 or later, available as `python3` on your Mac.
- A Metronome API token for the sandbox account open in Chrome (Metronome → Developer → API tokens).
- `metronome-sdk==4.11.1`, the same pin as the Raindrop scripts. `run_single.sh` installs it automatically into `Z Misc/.venv` on the first run.

```bash
cd "$HOME/Documents/Pro/Metronome Strategy/03 scripts"
export METRONOME_BEARER_TOKEN="<your token>"
```

## What to run, in order

| # | Command | Parameters | Purpose (one line) |
|---|---------|------------|--------------------|
| 1 | `./run_single.sh 01_setup_catalog.py` | none | Builds Replicate's catalog: 1 billable metric, 1 compute product priced by hardware, Pro Support (fixed fee), Enterprise Support (10% composite), trial credit and commit products, 1 rate card with 7 hardware rates. |
| 2 | `./run_single.sh 02_provision_customers.py` | `--only trial\|paygo\|enterprise` (optional, default: all three) | Creates the three personas and their contracts: free trial ($10 credit, 30 days), pay-as-you-go + $500/mo Pro Support, enterprise $100k/3-year prepaid commit with 15% off list and 10% Enterprise Support. |
| 3 | `./run_single.sh 03_create_alerts.py` | none | Creates the threshold notifications: trial credit at $2 and $0, paygo monthly spend over $2,500, enterprise commit balance under $25,000. **Run this before step 4** so the alerts trip as usage arrives. |
| 4 | `./run_single.sh 04_send_usage.py` | `--only <persona>` (optional), `--print-only` (dry run that prints the expected $ amounts) | Sends about 3,100 per-second compute events: trial about $12.59 (goes past the $10 credit), paygo about $2,316, enterprise about $4,367 at list price. |
| 5 | **wait** | | Tell me in the thread once steps 1 to 4 are done. Wait about 5 minutes after step 4 so alerts and draft invoices have caught up. I'll capture the "before" screens. |
| 6 | `./run_single.sh 05_add_machine_type.py --sample-usage` | `--hardware` (default `gpu-h100`), `--name` (default "Nvidia H100 GPU"), `--price-per-sec` (default `0.001525`), `--sample-usage` (adds 10 H100 hours to Lumen Labs), `--print-only` | Launches a new machine type as one rate on the rate card. **Run it only after I've captured the "before" screens.** You can also run it live during the demo. |
| 7 | `./run_single.sh 06_dashboard_links.py` | none | Read-only. Prints the customer-facing embeddable dashboard URLs (enterprise commits and usage, trial credits, paygo invoices) and saves them to `Z Misc/state.json`. Paste me the output. |

`run.sh` chains steps 1, 2, 3, 4 and 7 in one go if you prefer: `./run.sh`.

All IDs are saved to `Z Misc/state.json`. Re-running is safe: catalog objects are reused by name, customers by ingest alias, contracts and alerts by uniqueness key, and events by `transaction_id`.

## Where each script sits in the demo, and why we show it

| Script | Demo act (screens) | Business motive (Replicate's pain) |
|--------|-------------------|-----------------------------------|
| 01 | **Act 1: "One product, one rate per machine"**: billable metric, compute product with the `hardware` pricing key, rate card. | *"Adding a machine type means two engineering teams and weeks."* Replicate's public list has grown from the 7 SKUs in the brief to 19 today (H100, H200, L40S, multi-GPU). Each new SKU is now a pricing row, not a project. |
| 02 (trial) + 03 (trial alerts) + 04 | **Act 2: "Trial without leakage"**: Ada's contract, credit balance and ledger, alerts tripped. | *"We measure credit once a day, and users run far beyond their trial."* Metronome evaluates thresholds at least every 3 minutes and fires within 5 minutes of ingest, by webhook. Sign-up stays card-free, and leakage is capped at minutes of usage, not a day. |
| 02 (paygo + enterprise) + 04 | **Act 3: "Support tiers you can sell"**: Pro Support subscription on Lumen's invoice, Enterprise Support 10% line on Northwind's invoice. | *"We can't model fixed or percent-based fees."* That's new revenue on existing accounts: a fixed tier for growing teams and a % tier that scales with spend for enterprise. |
| 02 (enterprise) + 03 (commit alert) + 04 + 06 | **Act 4: "Commit visibility, self-serve"**: Northwind contract (commit, access schedule, 15% override), balance and ledger, embeddable dashboard, commit alert. | *"An engineer has to pull data so a customer knows where they stand."* Customers see their own burn-down. Sales gets a signal from the alert and the Salesforce sync. Northwind is burning faster than plan, which is an expansion conversation, not a surprise. |
| 05 | **Act 1 finale (live)**: H100 rate appears on the rate card, and the H100 line shows up on Lumen's draft invoice. | Proof, not a promise: a new GPU is billable in one call, and the enterprise discount and % support follow automatically through the `compute` tag. |
| (none) | **Act 5: quote-to-cash**: Developer → Integrations entry screen only (Stripe, NetSuite, Salesforce are not connected in this sandbox, per your call). | Keeps Replicate's stack: Stripe for paygo, NetSuite for enterprise invoices, Salesforce for the account team. |

## Assumptions to know about

- **Personas and amounts are illustrative.** Ada Okafor, Lumen Labs and Northwind Media are made up. The $10 trial, $500/month Pro Support, 10% Enterprise Support, 15% discount and the $2,500/$25,000 alert levels are my picks, so change them in `replicate_common.py` / `03_create_alerts.py` if you want other values. Hardware prices are Replicate's published ones.
- **Alert thresholds are sent in USD cents.** The docs' example ("$100 spend threshold reached" uses `10000`) implies this, but the API reference doesn't state it outright. If the alerts show $100 where you expect $1, divide by 100 in `03_create_alerts.py`.
- **The $0 trial alert** may be rejected if the API wants a threshold above 0. If so, the script stops on that alert; change `cents(0)` to `cents(0.01)` and re-run 03.
- **Contracts for paygo and enterprise start on the 1st of the current month**, and the trial contract starts 3 days before you run 02, so usage lands inside the current billing period.
