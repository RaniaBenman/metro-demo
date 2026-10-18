# Replicate × Metronome — 30-Minute Demo Script

**How to read this document.** Every screen below carries the four elements the
assignment requires: **purpose**, **areas of focus**, **actions in order**.
Screenshots live in `./screenshots/`. Status marks:

- ✅ **captured** — real screenshot of the current sandbox (shows the genuine UI)
- ⏳ **re-capture after data setup** — run the `user-action-needed/` scripts
  first, then re-shoot the same screen; it will show Replicate-branded data
  (GPU SKUs, trial credit, $100k commit) instead of the sandbox's dummy objects

**Demo persona recap (use their words):**

| # | Replicate's pain (verbatim) | Metronome answer | Act |
|---|---|---|---|
| 1 | "Adding another machine type… two engineering teams… weeks" | Pricing is config: one dimensional rate row | 1 |
| 2 | "We measure credit usage once a day… users use far beyond their free trial credit" | Real-time balances + threshold alerts + webhooks | 2 |
| 3 | "The current billing platform cannot model fixed or percent-based fees" | Subscription + Composite product types | 3 |
| 4 | "We cannot tell those customers where they are against their commitment without an engineer" | Commits with live drawdown, customer-facing dashboards, Salesforce sync | 4 |
| — | Stripe (paygo) + NetSuite (enterprise) + Salesforce (CRM) | Native integrations | 5 |

**Timing plan (30–35 min):** Bridge 1′ → Act 1 6′ → Act 2 7′ → Act 3 4′ →
Act 4 7′ → Act 5 4′ → buffer/Q&A 5′. Watch for questions after Acts 1 and 2 —
that is where engineering and product light up.

---

## Bridge — from slides to product (1 min)

Say: *"For the next thirty minutes I want to show you your business running on
Metronome — your pricing page, your free trial, your enterprise contracts.
Everything you see is configuration a billing-ops person owns. No Replicate
engineer was involved in building any of it."*

Open: **Overview** (home). Then straight into Act 1.

---

## Act 1 — Pricing is config, not code (6 min) → Pain #1

### Screen 1.1 — Product catalog ✅ / ⏳

`Offering → Products` · screenshot `01-products-catalog.png`

- **Purpose:** Establish that every sellable thing is a *product* (a line
  item), defined once, reused everywhere.
- **Areas of focus:** The **Type** column — Usage, Subscription, Fixed (and
  Composite, shown next). After data setup this list shows
  `GPU Compute (per second)` plus the three support-tier products.
- **Actions (in order):**
  1. Land on the catalog; let them read the type column.
  2. Say: *"Your whole catalog — every machine type, every support tier — is
     rows in this table."*

### Screen 1.2 — Product creator: the four charge shapes ✅

`Offering → Products → Add` (read-only; **do not Save**) ·
screenshots `02-create-product-modal.png`, `02b-create-product-types.png`

- **Purpose:** The four product types are the four ways a company can charge:
  **Usage** (metered), **Subscription** (recurring fee), **Fixed** (one-time /
  credits / commits), **Composite** (**"charge a percentage of spend on other
  products"** — their words on screen, the Pain #3 unlock).
- **Areas of focus:** The Composite description line; come back to it in Act 3.
- **Actions (in order):**
  1. Open `Add` → welcome screen → **Continue**.
  2. Hover each type; read the Composite line aloud.
  3. **Close with Back/✕ — no save.**

### Screen 1.3 — The rate card = Replicate's pricing page ⏳ (structure ✅)

`Offering → Rate cards → Replicate — Public Pay-per-second` ·
screenshot `03-rate-card-detail.png` (shows the sandbox's dummy card — after
setup this screen shows CPU…8×A40 **+ H100** as dimensional rows)

- **Purpose:** This is the Pain #1 payoff. One rate card holds every price
  from replicate.com/pricing — each machine type is **one dimensional rate
  row** (`hardware: h100 → $0.001525/sec`) on one product.
- **Areas of focus:** `Name & dimensional pricing values` column (the
  `hardware` values); `Starting at` column (rates are *scheduled*, so pricing
  changes ship with effective dates, not deploys); `Entitlement` toggle.
- **Actions (in order):**
  1. Scroll the GPU rows slowly — let them recognize their own pricing table.
  2. Point at the H100 row: *"This SKU was launched by adding this row. No
     event schema change, no billing code, no second team. Your next hardware
     launch looks exactly like this."*
  3. Reference point to drop: OpenAI shipped **10+ pricing changes in a year**
     on Metronome without touching billing code.

### Screen 1.4 — Add a rate (the two-minute motion) ✅

`Rate card → Add a rate` (read-only; **do not Save**) ·
screenshots `04-add-rate-modal.png`, `04b-add-rate-config.png`

- **Purpose:** Show the actual "add a machine type" motion: pick product →
  set dimensional value (`hardware: h100-8x`) → set price + starting_at →
  save. Minutes, owned by ops.
- **Areas of focus:** The sentence *"Rates can be changed on a schedule"*;
  the dimensional-pricing prompt; the `Starting at / Ending before` columns.
- **Actions (in order):**
  1. Open `Add a rate`.
  2. Select `GPU Compute (per second)` in the picker.
  3. Show the dimensional-value + schedule form. Do **not** fill or save.
  4. Close. Ask the room: *"How long would this take in your system today?"*
     (They said: weeks, two teams. Let the silence work.)

---

## Act 2 — The friction-free trial, in real time (7 min) → Pain #2

Narrative: *"Ada signs up — no credit card. She gets $25 of trial credit,
14 days. Watch what Metronome knows about her at every second."*

### Screen 2.1 — Trial customer overview ⏳ (structure ✅)

`Customers → Ada Lovelace → Overview` · screenshot `05-customer-overview.png`
(currently shows dummy customer Jane Doe 2 — same layout)

- **Purpose:** One page = the whole customer relationship: contracts, credit
  balances, invoices.
- **Areas of focus:** The **Commits & credits** card — `Consumed` vs `Total`
  on the trial credit, updating as usage lands.
- **Actions (in order):**
  1. Open the customer; point to the credit card summary.
  2. Say: *"This number is current as of the last prediction she ran. Not as
     of last night's batch."*

### Screen 2.2 — Commits & credits tab: the live balance ⏳ (structure ✅)

`Customers → Ada Lovelace → Commits and credits` ·
screenshot `06-customer-commits-credits.png`

- **Purpose:** The replacement for Replicate's daily measurement: access
  schedule, priority ordering, consumed/total per credit — the same data the
  `customerBalances` API returns to Replicate's own frontend.
- **Areas of focus:** `Access schedule` (the 14-day window); `Priority`
  (trial credit burns before any paid balance); `Consumed / Total`.
- **Actions (in order):**
  1. Open the tab; read the trial-credit row left to right.
  2. Say: *"Your signup flow calls one API for this balance. When it hits
     zero, you ask for the card — at that moment, not tomorrow morning."*

### Screen 2.3 — The draft invoice: drawdown vs. overage ✅

`Customers → Ada Lovelace → Invoices → current DRAFT` ·
screenshots `13-draft-invoice.png`, `13b-draft-invoice-total.png`

- **Purpose:** The money shot for Pain #2: line items carry an **"Applied
  commit or credit"** column — you see exactly which predictions burned trial
  credit and which are already billable overage.
  Bottom of invoice: `Subtotal $25.38 → Credit consumed −$20.00 → Total due
  $5.38` (sandbox data; the shape is what matters).
- **Areas of focus:** The credit column mid-table; the three-line total
  block.
- **Actions (in order):**
  1. Open the draft invoice.
  2. Scroll the charges; pause on a row whose credit column is `—`
     (= already overage).
  3. Scroll to the total; read the three lines aloud.

### Screen 2.4 — Threshold alerts & webhooks: the wake-up call ✅ / ⏳

`Developer → Notifications` (+ `Webhooks` tab) · screenshot `10-notifications.png`

- **Purpose:** How Replicate's app *learns* the credit state: threshold
  alerts (25% remaining → nudge; 3 days left → nudge; **$0 → gate**)
  evaluated **on event ingest**, delivered by webhook in seconds. This is the
  direct answer to "we struggle to know exactly when a user has exhausted
  their free trial credit."
- **Areas of focus:** The system events list (`Credit segment start/end`,
  `Contract end` — the trial lifecycle); the `Add notification` button;
  webhook destinations.
- **Actions (in order):**
  1. Show the notification catalog.
  2. Name the three trial alerts created for Ada and when each fires.
  3. Say: *"Your frontend receives a webhook, you show the card modal. The
     free tier stops leaking the same second it empties."*

### Screen 2.5 — The event stream behind it all ✅

`Usage events` · screenshot `09-usage-events.png`

- **Purpose:** Credibility for engineers: one event per prediction
  (`gpu_inference`, `hardware`, `billed_seconds`), deduplicated by
  transaction ID, backdatable 34 days.
- **Areas of focus:** The event log columns; duplicates counter.
- **Actions (in order):**
  1. Open the stream; filter `event_type = gpu_inference` (after setup).
  2. Click one event; show `hardware` + `billed_seconds`.
  3. Say: *"This is the same event shape your prediction service already
     emits. One line of telemetry becomes rating, credits, alerts, and the
     invoice you just saw."*

---

## Act 3 — Monetizing support: fixed AND percent-based fees (4 min) → Pain #3

Narrative: *"You want to sell support. Your billing can't model the two ways
support is sold. Here are both."*

### Screen 3.1 — Two support products ⏳

`Offering → Products` · (re-use `01`/`02b` screenshots; after setup the
catalog lists `Priority Support` [Subscription] and
`Premium Support (% of usage)` [Composite])

- **Purpose:** Pain #3 verbatim — "cannot model fixed or percent-based fees":
  - **Priority Support** — Subscription type → **$500/mo flat**, on the rate
    card as `entitled: false`, flipped on per contract.
  - **Premium Support** — Composite type → **10% of GPU spend**, computed
    automatically on whatever the customer used.
- **Actions (in order):**
  1. Open each product's detail; linger on the Composite definition
     ("percentage of the total cost of applicable products").
  2. Say: *"Launch a third tier next quarter — say 15% with a dedicated TAM —
     and it's another row, not another billing project."*

### Screen 3.2 — Entitled on the enterprise contract ⏳

`Customers → Acme Robotics → contract → Terms` · (structure in
`08-contract-detail.png`)

- **Purpose:** Both fees appear only on customers who pay for them. The
  subscription bills in-advance monthly; the percentage rides the usage
  invoice. NetSuite-ready as its own line items.
- **Actions (in order):**
  1. Open the contract; find the two support lines under Terms.
  2. Say: *"Enterprise gets Premium, self-serve gets nothing — entitlement is
     per contract."*

---

## Act 4 — The $100k commit everyone can see (7 min) → Pain #4

Narrative: *"Acme Robotics: $100,000 over 3 years, 10% off list in exchange.
Today you'd query the database to answer 'where are we?'. Watch."*

### Screen 4.1 — The contract: the deal, encoded ⏳ (structure ✅)

`Customers → Acme Robotics, Inc. → Contracts → Enterprise — $100k / 3yr` ·
screenshots `08-contract-detail.png`, `08b-contract-rates.png` (structure)

- **Purpose:** The entire signed deal as data:
  - **Commit**: PREPAID $100k — ramped access schedule
    (Y1 $25k / Y2 $35k / Y3 $40k), cash schedule $50k at signature + $50k at
    year 2, **25% rollover** into renewal.
  - **Override**: MULTIPLIER 0.9 on tag `gpu-compute` — the negotiated
    discount, whole term.
  - **Scheduled charge**: $5k solutions engineering, month 3.
  - Net payment terms 30; Salesforce opportunity ID stored on the contract.
- **Areas of focus:** The Terms sections (Commits / Overrides /
  Subscriptions / Scheduled charges); contract length header.
- **Actions (in order):**
  1. Open the contract; scroll Terms top to bottom.
  2. Read the deal aloud from the screen — deal desk will recognize every
     clause.

### Screen 4.2 — Commits & credits: where ARE we against the commit? ⏳ (structure ✅)

`Customers → Acme Robotics → Commits and credits` ·
screenshot `06-customer-commits-credits.png` (structure)

- **Purpose:** **The Pain #4 kill shot**: `Consumed / Total` on the commit,
  per segment, in real time — the exact number that today requires an
  engineer and a SQL query.
- **Areas of focus:** Summary band (active prepaid commits: consumed vs
  remaining); the Commits table (priority, access schedule, invoice
  schedule, total invoiced).
- **Actions (in order):**
  1. Read the summary band aloud: *"Consumed $X of $25,000 Year-1."*
  2. Say: *"And this same number renders inside YOUR product — embeddable
     dashboard or one `customerBalances` call — so Acme's team sees it
     without asking you, and your engineer never runs that query again."*

### Screen 4.3 — The renewal trigger ✅ / ⏳

`Developer → Notifications` · screenshot `10-notifications.png`

- **Purpose:** The 80%-consumed alert on Acme's commit = the account team's
  upsell/renewal alarm, synced to Salesforce via the native connector
  (commit balance, spend by product, usage over time land on the Account).
- **Actions (in order):**
  1. Point at the alert.
  2. Say: *"When Acme crosses 80%, your AE gets the ping in Salesforce with
     the numbers attached. That's the renewal conversation, scheduled by
     usage itself."*

---

## Act 5 — Quote-to-cash without the glue code (4 min) → their stack

### Screen 5.1 — Integrations ✅

`Developer → Integrations` · screenshot `11-integrations.png`

- **Purpose:** Their exact stack, native: **Stripe** (paygo invoices &
  card collection — and Metronome is now part of Stripe), **Salesforce**
  (usage & commit data to the CRM), **NetSuite** (enterprise invoices &
  revenue recognition; API-configured), plus AWS/Azure/GCP marketplaces for
  tomorrow's channel.
- **Actions (in order):**
  1. Open the page; name each tile in their words: paygo, CRM, enterprise.
  2. Say: *"Metronome sits between your product and these systems and
     replaces the glue: one rating engine, three destinations."*

### Screen 5.2 — Reporting & the audit trail ✅

`Reporting` · screenshot `12-reporting.png` · (optionally `Developer →
Audit log` — every change attributable)

- **Purpose:** Finance close: commits & credits by date, revenue
  recognition exports (ASC 606), data export to the warehouse.
- **Actions (in order):**
  1. Open Reporting; name the commits & credits report.
  2. Close the loop: *"The number Acme sees, the number your AE sees, and
     the number Finance books — same number."*

### Close (1 min)

*"In thirty minutes you watched: a machine type launched as config; a free
trial that knows its own balance every second; support sold two new ways; and
a $100k commit everyone can read. Four pains, one platform, zero Replicate
engineering. The question I'd leave you with: which of these do you want
live first?"*

---

## Contingencies & objections (keep in back pocket)

| If they say… | Answer |
|---|---|
| "We already have Stripe for paygo." | Metronome is now part of Stripe (Jan 2026) — this is the Stripe-native path to usage billing; your Stripe contracts get *stronger*, not replaced. |
| "Our event volume is huge." | Metronome meters billions of events/month for OpenAI, Anthropic, NVIDIA, Databricks; 100k+ events/sec ingest, dedup by transaction ID. |
| "Engineering will want to keep the homegrown system." | Keep your prediction pipeline; replace only the billing math. Your engineers stop being the billing department (today they pull commit balances by hand). |
| "What about migration of existing customers?" | Contracts support historical invoices + backdated events (34 days); enterprise deals re-paper at renewal. Typical PLG go-lives in weeks. |
| "Security/compliance?" | RBAC, SSO, audit logs (show Developer → Audit log), SOC 2. |
| Discovery Qs to ask back | "Which team owns adding a SKU today?" · "What % of trial users exceed the allowance before conversion?" · "How many committed deals are in flight right now?" |

## Screenshot index

| File | Screen | Status |
|---|---|---|
| `01-products-catalog.png` | Offering → Products | ✅ (dummy products) — ⏳ re-capture |
| `02-create-product-modal.png` | Product creator — welcome | ✅ final |
| `02b-create-product-types.png` | Product creator — 4 types | ✅ final |
| `03-rate-card-detail.png` | Rate card w/ dimensional rates | ✅ structure — ⏳ re-capture |
| `04-add-rate-modal.png` | Add a rate — picker | ✅ final |
| `04b-add-rate-config.png` | Add a rate — config+schedule | ✅ final |
| `05-customer-overview.png` | Customer overview | ✅ structure — ⏳ re-capture ×2 |
| `06-customer-commits-credits.png` | Commits & credits tab | ✅ structure — ⏳ re-capture ×2 |
| `07-invoices-tab.png` | Invoice history | ✅ structure — ⏳ re-capture |
| `08-contract-detail.png` / `08b-contract-rates.png` | Contract terms & rates | ✅ structure — ⏳ re-capture |
| `09-usage-events.png` | Usage event stream | ✅ structure — ⏳ re-capture |
| `10-notifications.png` | Notifications catalog | ✅ final |
| `11-integrations.png` | Integrations (Stripe/SFDC/…) | ✅ final |
| `12-reporting.png` | Reporting | ✅ final |
| `13-draft-invoice.png` / `13b-…-total.png` | Draft invoice + credit drawdown | ✅ final |
| `14-customer-usage.png` | Customer usage charts | ✅ structure — ⏳ re-capture |
