# Metronome Strategy Assignment — Replicate.com

One folder, three deliverables, one narrative: **Replicate's four billing
frictions all have the same root cause — pricing logic lives in code — and
Metronome turns it into config.** Everything here is built from their own
words in the assignment brief, their live pricing page, and a real (read-only)
Metronome sandbox.

## The deliverables ↔ the assignment

| Assignment requirement | Where it lives |
|---|---|
| 10-minute presentation with slides and speaker notes (purpose / emphasize / tone per slide) | `03-slides/replicate-metronome/` — 10-slide deck; every `.page` file carries a `notes:` block with PURPOSE / EMPHASIZE / TONE |
| 30-minute demo with every screen documented (purpose / areas of focus / actions in order) + screenshots | `02-demo/demo-script.md` — 16 screens in 5 acts, each with purpose, focus, ordered actions, verbatim talk track, and a screenshot reference |
| Write actions the strategist cannot perform (read-only sandbox) as SDK scripts, commented with goal, position in the demo, and business motive | `user-action-needed/` — five ordered, idempotent Python scripts on the official `metronome-sdk`, plus run instructions |
| Quality of content about Replicate | `01-strategy/strategy-brief.md` — sourced company brief, their four pains in their words, demo mapping, pilot proposal |

## The narrative in one table

| Replicate's pain (their words) | Metronome capability | Proved in |
|---|---|---|
| Adding a machine type takes two engineering teams, weeks | Pricing as config — one dimensional rate row per GPU SKU, schedulable, ops-owned | Slides 6 & 8 → Demo Act 1 |
| Trial credit measured once a day; users overspend silently | Real-time rated balances; threshold alerts (25% / 3 days / $0) fired on ingest, webhook-delivered | Slide 6 → Demo Act 2 |
| Billing cannot model fixed or percent-based fees → no support tiers | Subscription (flat $/mo) + Composite (% of spend) products, entitled per contract | Slide 6 → Demo Act 3 |
| No visibility into a $100k/3yr commit without an engineer | Commits with ramp, installments, rollover, discount overrides; live drawdown; customer dashboard; Salesforce sync | Slide 6 → Demo Act 4 |
| (Their stack: Stripe paygo · NetSuite enterprise · Salesforce CRM) | Native integrations — and Metronome is now part of Stripe | Slides 4 & 5 → Demo Act 5 |

## How to run the whole thing

1. **Read** `01-strategy/strategy-brief.md` (5 min — all the Replicate
   research and the pilot ask).
2. **Present** the deck in `03-slides/replicate-metronome/` (10 min; speaker
   notes are in each page's `notes:` block; QA renders in `03-slides/_qa/`).
3. **Build the demo data** — the sandbox is read-only for the strategist, so
   the write steps are packaged as scripts:
   ```bash
   cd user-action-needed && pip install -r requirements.txt
   export METRONOME_API_TOKEN=<sandbox writer token>
   python3 01_metric_and_products.py   # metric + products
   python3 02_rate_card.py             # 8 GPU rate rows incl. H100
   python3 03_trial_flow.py            # Ada Lovelace, $25/14-day credit, alerts
   python3 04_enterprise_commit.py     # Acme Robotics, $100k/3yr commit
   python3 05_send_usage.py            # ~150 gpu_inference events
   ```
4. **Re-capture** the ⏳-marked screenshots in `02-demo/screenshots/`
   (they currently show the sandbox's genuine UI with dummy data; after the
   scripts run, the same screens show Replicate's GPU SKUs, the trial credit
   drawing down, and the commit balance).
5. **Demo** from `02-demo/demo-script.md` (30–35 min, 5 acts + buffer).

## Demo data at a glance (post-scripts)

- **Ada Lovelace** (self-serve trial): $25 / 14-day credit; her scripted
  usage totals **$26.02** — the demo shows the balance hit $0, the overage
  line on the draft invoice, and the alerts firing in real time.
- **Acme Robotics, Inc.** (enterprise): $100k prepaid commit ramped
  $25k/$35k/$40k over 3 years, 2 installments, 25% rollover, 10% MULTIPLIER
  discount on GPU compute, both support tiers entitled ($500/mo flat + 10% of
  spend), $5k onboarding scheduled charge, 80%-consumed alert. Scripted usage
  draws ~$5,949 (discounted) ≈ 24% of Year-1 commit — a healthy mid-deal
  state, with **H100 events** inside to close the Pain #1 loop.

## File map

```
05 Strategy/
├── Metronome prompt.pdf            # the assignment
├── README.md                       # this file
├── 01-strategy/
│   └── strategy-brief.md           # research, pains, mapping, pilot proposal
├── 02-demo/
│   ├── demo-script.md              # 30-min script, 14 screens, 5 acts
│   └── screenshots/                # 16 real sandbox captures (✅ / ⏳ marked)
├── 03-slides/
│   ├── _qa/                        # rendered pages for quality check
│   └── replicate-metronome/        # 10-slide deck (PPTD source)
│       ├── replicate-metronome.pptd
│       ├── pages/                  # one file per slide, notes included
│       └── media/                  # images used by the deck
└── user-action-needed/             # write actions for the read-only sandbox
    ├── README.md                   # run order, objects created, rationale
    ├── requirements.txt            # metronome-sdk
    ├── replicate_common.py         # shared client, idempotency, state.json
    ├── 01_metric_and_products.py
    ├── 02_rate_card.py
    ├── 03_trial_flow.py
    ├── 04_enterprise_commit.py
    └── 05_send_usage.py
```

*Verified facts worth remembering: USD `price`/`amount` values are in
**cents**; PERCENTAGE rates take a 0–1 decimal (0.10 = 10%); scripts are
idempotent (`state.json` + deterministic `transaction_id`s); nothing touches
the sandbox's pre-existing dummy objects.*
