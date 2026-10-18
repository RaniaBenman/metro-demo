# 02 user-CTA: scripts to run so the demo has Replicate in it

I only have **read** access to the Metronome sandbox, and today it only holds leftover Raindrop test data (3 customers, token products). Everything Replicate-specific in the demo must therefore be created by you, with the Python scripts in `03 scripts/`. They use the official Metronome SDK and change nothing outside Metronome.

I checked `~/Documents/Pro/Metronome/02 work/v3_comments_exceptions/scripts` first and left it untouched. Those scripts model Raindrop's token pricing ($20/month package, input/output tokens), so none of them builds what Replicate needs. The new scripts reuse their structure, which proved itself in this sandbox: the SDK calls, the `run_single.sh` runner, get-or-create re-runs and a shared `state.json`.

Every script was run end-to-end, twice, against a local mock of the Metronome API. The first pass checks the payloads, the second checks that re-runs reuse what exists. The first real run against your sandbox is the one thing I could not do myself.

## Requirements (once)

- **Python 3.9 or later**, available as `python3`.
- **A Metronome API token created in the Sandbox environment** (the orange "Sandbox" banner must be visible): Developer → API tokens → create.
- **`metronome-sdk==4.11.1`**, the same pin as the Raindrop scripts and the latest release. You don't install it yourself: on first run, `run_single.sh` creates `Z Misc/.venv` and installs it there.

These two lines move into the scripts folder and give them the token. The token is only kept in this terminal session.

```bash
cd "$HOME/Documents/Pro/Metronome Strategy/03 scripts"
export METRONOME_BEARER_TOKEN="<your sandbox token>"
```

## What to run, in order

Two moments: **A** builds the demo world before I capture the "before" screens. **B** launches the H100 for the "after" screens. `07_check_state.py` and `06_dashboard_links.py` are read-only and safe to run at any time.

| # | When | Command | Parameters | Purpose (one line) |
|---|------|---------|------------|--------------------|
| 1 | A | `./run_single.sh 01_setup_catalog.py` | none | Builds Replicate's catalog: custom-field tags, 1 metric, 1 compute product priced by hardware, 2 support products, 1 rate card with today's 7 machine types, 2 self-serve packages: plain pay-as-you-go that starts with the $10 trial, and the Pro Support upsell. |
| 2 | A | `./run_single.sh 02_provision_customers.py` | `--only self_serve\|pro_support\|prepaid\|postpaid` (optional, default: all four) | Creates the four customers: a free trial, a pay-as-you-go account with Pro Support, and two $100k/3-year enterprise accounts, one prepaid and one postpaid. |
| 3 | A | `./run_single.sh 03_create_alerts.py` | none | Creates 5 threshold notifications: 3 trial alerts covering every customer, 1 commit alert covering every customer, 1 spend budget. **Run before step 4** so they trip as usage lands. |
| 4 | A | `./run_single.sh 04_send_usage.py` | `--only <offering>`, `--print-only` (dry run: prints expected $ per hardware, sends nothing), `--without-roadmap` (skip H100/L40S usage) | Sends about 6,600 per-second compute events, including H100 and L40S usage that has no price yet, as Replicate's platform would on day 0. |
| 5 | A | **wait 5 minutes**, then `./run_single.sh 07_check_state.py` | none | Read-only. Prints balances, draft invoices and alert states, and saves `Z Misc/state_snapshot.json` (I use it for the talk track). |
| 6 | A | `./run_single.sh 06_dashboard_links.py` | none | Read-only. Generates the customer-facing embeddable dashboard URLs and saves them in `Z Misc/state.json`. **The URLs are time-limited**: run it right before I take screenshots, and again on demo day. |
| ⏸ | | **Tell me in the chat that A is done.** | | I capture the "before" screens. Don't run `05_launch_gpu.py` yet. |
| 7 | B | `./run_single.sh 05_launch_gpu.py --hardware gpu-h100` | `--hardware` (default `gpu-h100`), `--name`, `--price-per-hour` (default: list price, $5.49 for H100), `--starting-at` (launch date, default 1st of this month, hour-aligned), `--send-usage` (fallback, sends 10 fresh hours), `--print-only` | Launches the H100 as **one rate** on the rate card. The H100 usage already sent gets priced on the open invoices, with the enterprise discount, commit drawdown and 10% support applied automatically. Then tell me, and I capture the "after" screens. |

`./run.sh` chains steps 1–4, the 5-minute wait, 7 and 6 in one go if you prefer.

All IDs go to `Z Misc/state.json`. Re-running is safe: catalog objects are reused by name, customers by ingest alias, a customer that already has a contract is left alone, alerts are deduplicated by uniqueness key, and events by `transaction_id`.

**Do not launch the L40S.** Its usage is deliberately left unpriced: you'll add its rate live in the Metronome UI during the demo (steps in the demo runbook). If the live moment goes wrong on the day, the fallback is `./run_single.sh 05_launch_gpu.py --hardware gpu-l40s`.

## What each script puts in the demo, and why we show it

| Script | Where it shows up in the demo | Business motive (Replicate's own words) |
|--------|-------------------------------|------------------------------------------|
| 01 | **Act 1, "A new GPU is a rate, not a project".** Billable metric *Compute seconds*, product *Compute hours* (pricing key `hardware`, seconds→hours conversion), rate card *Replicate list prices* with the 7 machine types. **Act 2/3.** Offering → Packages: *Pay-as-you-go ($10 free trial, 30 days)* and *Pay-as-you-go + Pro Support ($500/mo)*. | *"To add another machine type, we have to involve two different engineering teams, which can take weeks."* Your list is growing (H100, H200, L40S, multi-GPU). Each new SKU becomes a price row, with no metric, product, contract or code change. |
| 02 (self_serve) + 03 (trial alerts) + 04 | **Act 2, "A card-free trial that can't leak".** Ada Okafor: the $10 trial credit consumed, its 30-day window, and the trial alerts in alarm. Developer → Notifications: the same alerts apply to every customer. | *"Our systems measure credit usage once a day, and often users use far beyond their free trial credit."* Metronome evaluates thresholds at least every 3 minutes and fires within 5 minutes of the usage being ingested. Sign-up stays card-free; the leak shrinks from up to a day of GPU time to minutes. |
| 02 (pro_support) + 03 (budget) + 04 | **Act 3, "Support tiers you can sell".** Brightframe AI: *Pro Support* $500/month on its contract and scheduled invoice, its usage invoice (one line per machine type), and its $1,500 budget alert. | *"We don't have support tiers because the current billing platform cannot model fixed or percent-based fees."* A fixed tier for growing teams is new revenue on accounts you already have. |
| 02 (prepaid/postpaid) + 03 (commit) + 04 + 06 | **Act 3** (the 10% Enterprise Support line) and **Act 4, "Where am I on my commit?"**. Northwind Media (prepaid: $100k usable over 3 years, invoiced yearly) or Kepler Games (postpaid: $100k minimum, true-up at term end), depending on Replicate's answer to the discovery question. Both show the 15% override, the balance and ledger, the customer-facing embeddable dashboard and the 25%-remaining commit alert. | *"We cannot tell those customers where they are against their commitment without having an engineer pull data from the database."* Customers see their own burn-down in your app, the account team gets a signal before renewal, and no engineer is involved. |
| 05 | **Act 1 finale.** The rate card gains `gpu-h100`; Brightframe's draft invoice gains an H100 line at list price; Northwind's gains one at 15% off, drawn from the commit, plus 10% support. **Live:** you add `gpu-l40s` in the UI and Brightframe's L40S line appears. | Proof, not a promise: the GPU your platform already runs gets billed with one row, with negotiated terms applied by tag. |
| 06 | **Act 4.** The commits & credits dashboard as Northwind would see it inside replicate.com. | The commitment question answers itself in the customer's own UI: "a white-labeled billing experience without building custom UI" (Metronome docs). |
| 07 | Not shown. Gives us the exact numbers for the talk track. | Rehearsal accuracy. |

## Assumptions to know about

- **Personas and amounts are illustrative** (you confirmed the defaults):
  - $10 trial credit valid 30 days.
  - $500/month Pro Support and 10% Enterprise Support.
  - $100k over 3 years at 15% off list.
  - $1,500 budget alert.

  They all live in `replicate_common.py` and `03_create_alerts.py`.
- **Prices are Replicate's published list** (from the brief), stored per hour: $/hour = $/second × 3600 exactly, e.g. A100 80GB $0.001400/s = $5.04/h. Events still carry seconds; the product converts seconds to hours, which is the docs' own GPU-hour pattern. It keeps the rate card readable instead of showing $0.0001-style prices.
- **Hardware IDs:** `cpu`, `gpu-t4`, `gpu-a40-small`, `gpu-a40-large`, `gpu-a100-large`, `gpu-h100` and `gpu-l40s` follow Replicate's own naming. `gpu-a100-small` (A100 40GB) and `gpu-a40-large-8x` are my assumption.
- **Dates:**
  - The Pro Support and enterprise contracts start on the 1st of the current month (so usage lands in the open billing period).
  - The self-serve contract, with its trial credit, starts 3 days before you run step 2.
  - H100/L40S "launch day" defaults to the 1st of the month, so the beta usage already sent is in scope.
- **Not configured on purpose:** Stripe, NetSuite and Salesforce. The sandbox shows Salesforce as "Requires upgrade", NetSuite isn't listed, and the brief says those systems are covered by the architecture slides. The enterprise contracts still carry dummy Salesforce opportunity IDs: one in Metronome's own Salesforce opportunity field (if this environment rejects it, the script retries without it) and one in an `sfdc_opportunity_id` custom field, which step 1 registers.
- **Where this sits vs. the earlier pass:** the previous scripts, README and screenshots were moved to `Z Misc/_superseded (previous pass)/`. Main changes:
  - per-hour display;
  - account-wide, tag-scoped trial alerts (the official trial guide's pattern);
  - packages for self-serve sign-ups;
  - a postpaid enterprise persona;
  - a "launch a GPU" flow with usage already flowing.

## If something fails

- `ERROR: set METRONOME_BEARER_TOKEN`: run the `export` line above in the same terminal.
- `HTTP 401`: the token is wrong or from another environment. Create it while the app shows **Sandbox**.
- `Invalid custom field keys`: step 1 registers them, so run step 1 again, then step 2.
- Anything else: paste me the last 20 lines of output. Every script is safe to re-run once fixed.
