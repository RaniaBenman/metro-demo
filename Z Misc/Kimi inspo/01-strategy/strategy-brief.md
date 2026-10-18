# Replicate × Metronome — Strategy Brief

*Prepared by: Strategist, Metronome · Session: 10-min presentation + 30-min demo ·
Objective: drive Replicate to decide Metronome is their billing platform.*

---

## 1. Who we are selling to

**Replicate** — "the GitHub of AI models": run and fine-tune open-source
models behind one API, billed **by the second** of compute.

| Fact | Number / detail | Source |
|---|---|---|
| Founded | 2019, San Francisco (Ben Firshman, CEO) | public record |
| Funding | $40M Series B (Dec 2023) led by a16z, with NVIDIA's NVentures, Sequoia, YC — $57.8M total, ~$350M valuation | replicate.com/blog/series-b |
| Ownership | **Joining Cloudflare** — announced on Cloudflare's blog; APIs and workflows continue uninterrupted | blog.cloudflare.com/replicate-joins-cloudflare |
| Catalog | 50,000+ open-source and fine-tuned models | blog.cloudflare.com/replicate-joins-cloudflare |
| Usage | 30,000 paying customers; 2M+ developers signed up (Series B, Dec 2023) — Replicate does not publish run volumes | replicate.com/blog/series-b |
| Revenue model | Pay-per-second GPU usage; enterprise committed-spend contracts; dedicated/private deployments | replicate.com/pricing |
| Pricing surface | 7+ machine types (CPU → 8×A40), new H100/H200/L40S SKUs appearing — many "available with committed spend contracts" | replicate.com/pricing |
| Quote-to-cash stack | **Stripe** (paygo) · **NetSuite** (enterprise) · **Salesforce** (CRM) | their words (assignment brief) |

**Their strategic priorities, read from the numbers:**

1. **Hardware velocity** — every new GPU generation (H100, H200, L40S…) must
   become a sellable SKU fast; multi-GPU SKUs are gated behind committed-spend
   contracts, i.e. *billing is already gating the product roadmap*.
2. **PLG funnel efficiency** — friction-free trial ("try before credit card")
   is their growth engine; leaking past the trial allowance is direct COGS
   bleed at 45%-ish gross margins.
3. **Moving upmarket** — enterprises want commits, discounts, premium
   support, SLAs; Series B post explicitly says "making it better for
   businesses" is where the money goes.
4. **Monetization expansion** — support tiers, marketplaces, fine-tuning and
   deployments all need fee shapes (fixed, %, commits) their homegrown system
   cannot express.

## 2. Pain → capability map (the spine of the whole session)

| # | Their pain (their words) | Business cost | Metronome capability | Proof in demo |
|---|---|---|---|---|
| 1 | Adding a machine type takes **2 eng teams, weeks** | Billing gates the hardware roadmap; eng opportunity cost | Pricing as **config**: one billable metric + one product with a `hardware` pricing group key → each SKU is **one dimensional rate row**, schedulable (`starting_at`) | Act 1: rate card + Add-a-rate motion; H100 launched live |
| 2 | Trial credit measured **once a day**; users overspend before being asked for a card | GPU COGS bleed on every leaky trial user; conversion prompt mistimed | **Real-time rating** + expiring trial credits + **threshold alerts** (25% left / 3 days left / $0) evaluated **on ingest**, webhook-delivered; spend thresholds post-trial | Act 2: live balance, draft invoice w/ credit drawdown + overage, notifications |
| 3 | Billing **cannot model fixed or percent-based fees** → no support tiers | Unmonetized enterprise demand; support given away | Four product types incl. **Subscription** (flat $/mo) and **Composite** (**% of spend**); entitlement per contract | Act 3: Priority $500/mo + Premium 10% entitled on Acme |
| 4 | **No visibility** into $100k/3yr commits without an engineer pulling the DB | Renewal/upsell blindness; recurring eng interrupt; customer mistrust | **Commits**: ramped access schedule, installments, rollover, MULTIPLIER discount overrides; live Consumed/Remaining; **embeddable customer dashboard** + `customerBalances` API; **Salesforce sync** | Act 4: contract terms, commit drawdown, 80% alert |
| — | Stripe + NetSuite + Salesforce stack held together by glue | Reconciliation drag, rev-rec risk | **Native integrations**: Stripe (Metronome is now part of Stripe), NetSuite, Salesforce; ASC 606 reporting | Act 5: integrations, reporting |

## 3. Why Metronome wins this room (proof points to deploy)

- **Peer proof:** OpenAI, Anthropic, NVIDIA, Databricks, Confluent run
  usage billing on Metronome — Replicate's exact peers and suppliers.
  OpenAI shipped **10+ pricing changes in 12 months** without billing-code
  deploys (the direct rebuttal to Pain #1).
- **Scale proof:** billions of events/month, 100k+ events/sec ingest,
  34-day backdating — orders of magnitude beyond Replicate's event volume.
- **Strategic proof:** **Stripe acquired Metronome (~$1B, closed Jan 2026)** —
  Replicate's paygo rail and its billing layer now come from one vendor;
  de-risked roadmap, no glue to maintain.

## 4. Session strategy

- **Lead with their pricing page, not our product.** Act 1 recreates
  replicate.com/pricing inside Metronome in the first 5 minutes; recognition
  beats explanation.
- **Use their own numbers**: "$100,000 over 3 years" is their example — the
  enterprise demo customer is built to exactly that spec.
- **Make engineering the hero**: every pain removes an *engineering interrupt*
  (SKU launches, DB pulls, daily batch babysitting). The two teams in the
  room (eng + business) both hear their own win.
- **Ask, don't tell**, at three moments (see discovery below); let the
  silence after "how long does this take you today?" do the selling.
- **Time discipline**: hard stops — slides ≤10′, demo ≤35′, buffer 5′.
  If questions run hot after Act 2, compress Act 3 (its content overlaps
  Act 4's contract screen).

**Discovery questions to weave in** (judged criterion):
1. Which team owns adding a SKU today — and what does that calendar look like?
2. What share of trial users exceed the free allowance before converting?
   What is one day of trial overrun worth in GPU cost?
3. How many committed-spend deals are in flight, and how does an AE check
   a commit balance today?
4. If support tiers were free to launch tomorrow, which tier would you sell
   first — flat or %-of-spend?

**Success criteria for the meeting:** agreement on a scoped pilot —
self-serve trial flow (Act 2) + one enterprise commit (Act 4) in a sandbox,
with Replicate's own event stream, within 2–3 weeks.

## 5. Risks / objections and pre-empts

See the objection table at the end of `02-demo/demo-script.md` (Stripe
already in stack, homegrown attachment, volume, migration, security). One
strategic note: post-acquisition, position Metronome as *"the usage-billing
engine of the Stripe you already trust"* — never as "rip out Stripe".
