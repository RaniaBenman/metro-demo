# user-action-needed/

The demo account is **READ-only** for the strategist. These scripts perform the
WRITE actions required to build the Replicate demo environment, exactly as the
assignment prescribes. Each script is commented with its **goal**, its
**position in the demo narrative**, and the **business motive** behind showing
it.

## Run me

```bash
cd "05 Strategy/user-action-needed"
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt          # metronome-sdk (official Python SDK)
export METRONOME_API_TOKEN=<sandbox token>   # Developer → API tokens → + Add (Writer role suffices)

python3 01_metric_and_products.py
python3 02_rate_card.py
python3 03_trial_flow.py
python3 04_enterprise_commit.py
python3 05_send_usage.py
```

Order matters (each step depends on IDs created by the previous one). All
scripts are **idempotent**: IDs are persisted to `state.json`, and usage events
carry deterministic `transaction_id`s, so re-running any script is safe.

## What gets built, and why

| Script | Objects created | Pain it answers | Demo act |
|---|---|---|---|
| `01_metric_and_products.py` | Billable metric `Replicate GPU Seconds` (SUM of `billed_seconds`, grouped by `hardware`); usage product `GPU Compute (per second)` with `hardware` pricing group key + `gpu-compute` tag; support products (SUBSCRIPTION / COMPOSITE / FIXED); credit & commit carrier products | #1 — pricing is config, not code | Act 1 |
| `02_rate_card.py` | Rate card `Replicate — Public Pay-per-second` (alias `replicate-paygo`) with 8 dimensional GPU rates (CPU…8×A40 **plus the new H100**), Priority Support $500/mo FLAT, Premium Support 10% PERCENTAGE | #1 (H100 = one rate row) · #3 (fixed & %-fees) | Acts 1 & 3 |
| `03_trial_flow.py` | Trial custom-field keys; customer `Ada Lovelace`; trial contract with **$25 / 14-day credit**; three real-time alerts (25% remaining, 3 days left, balance = $0) | #2 — real-time trial exhaustion | Act 2 |
| `04_enterprise_commit.py` | Customer `Acme Robotics, Inc.` (Salesforce join key); 3-yr contract: **$100k PREPAID commit** (ramped $25k/$35k/$40k, $50k×2 installments, 25% rollover), **10% MULTIPLIER discount** on `gpu-compute`, both support tiers entitled, $5k onboarding scheduled charge; 80%-consumed commit alert | #4 (commit visibility) · #3 | Acts 3 & 4 |
| `05_send_usage.py` | ~150 `gpu_inference` events: Ada burns through her $25 (+ small overage); Acme draws ~¼ of Year-1 commit incl. **H100** events | makes every screen live | Acts 1, 2, 4 |

## After running

1. Open the app and re-capture the screens marked ⏳ *pending data* in
   `02-demo/demo-script.md` (rate card, product catalog, both customers).
2. The Alerts created with `evaluate_on_create=False` arm silently and fire on
   the usage sent by script 05 — wire a webhook under
   **Developer → Notifications → Webhooks** to show the payload live.
3. Nothing here touches the pre-existing dummy objects (Raindrop/Jane Doe).

Unit note: for the USD credit type, all `price`/`amount` values are **cents**
(verified against the sandbox's existing rate card and the prior project).
