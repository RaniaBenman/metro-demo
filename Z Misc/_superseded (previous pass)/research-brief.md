# Research brief: Replicate × Metronome

Background for the deck, the demo and Q&A. Each fact lists its source. Anything inferred is marked **(inference)**.

## Replicate: the business

| Fact | Number | Source |
|---|---|---|
| Model catalog | 50,000+ containerized models | SiliconANGLE, 17 Nov 2025 (Cloudflare acquisition) |
| Ownership | Cloudflare announced the acquisition of Replicate on 17 Nov 2025; terms undisclosed. Plan: run Replicate on Cloudflare's infrastructure and fold its catalog into Workers AI and AI Gateway. | SiliconANGLE; Help Net Security; SD Times |
| Funding before acquisition | $23M+ (YC, Sequoia), plus a $40M Series B led by a16z (2023) | SiliconANGLE; Voicebot.ai |
| Pricing model | Per second of hardware time, "billed by the second… scales to zero" | Prompt / replicate.com/pricing |
| Hardware SKUs | **7 in the brief → 19 on replicate.com/pricing today** (CPU Small, L40S ×1/2/4/8, A100 80GB ×1/2/4/8, H100 ×1/2/4/8, H200 ×1/2/4/8, T4…) | replicate.com/pricing (fetched 14 Oct 2026) |
| Enterprise motion | "Enterprise & volume discounts… volume discounts for large amounts of spend"; priority support, SLAs; multi-GPU capacity "available with committed spend contracts" | replicate.com/pricing |
| Quote-to-cash | Stripe (paygo), NetSuite (enterprise), Salesforce (CRM) | Prompt |

**So what (inference):** the SKU catalog almost tripled. With a weeks-long, two-team process per SKU, the billing system becomes the bottleneck on launching new GPUs, and launching GPUs is how Replicate competes. Now that Replicate is part of Cloudflare, the expected scale goes up and the bar for billing correctness rises with it.

## Metronome: proof points

| Fact | Source |
|---|---|
| Stripe acquired Metronome (announced 2 Dec 2025, completed since). Collison: Metronome "already serves OpenAI, Anthropic, and NVIDIA". To be integrated with Stripe Billing. | stripe.com/newsroom "Stripe completes Metronome acquisition"; PYMNTS |
| Website logos: OpenAI, HubSpot, Fly.io, Astronomer, Cribl, Starburst | metronome.com |

**So what (inference):** Replicate already runs paygo collection on Stripe. Metronome is the metering and pricing layer that belongs to the same company, so this is not a rip-and-replace of payments.

## Pain → Metronome capability (all from official docs)

| Pain (Replicate's words) | Capability | Doc evidence |
|---|---|---|
| New machine type = 2 teams, weeks | One usage product with a **pricing group key** `hardware`; a new SKU is one rate on the **rate card** | "Pricing group keys allow you to set different prices for the same product". "Rate cards… one change propagates" (*Create products*, *How Metronome works*) |
| Credit measured once a day, trials leak | **Contract credit** with access schedule (amount + end date) + **threshold notifications** via webhook | Threshold "evaluated at least once every three minutes… will fire within 5 minutes of the usage… being ingested" (*Notifications*); "a credit with an access schedule bounds both at once" (*Create a free trial*) |
| No fixed or % fees → no support tiers | **Subscription** product (fixed monthly fee) and **Composite** product (PERCENTAGE rate on tagged products) | "Composite: percentage charge on a group of applicable products" (*Create products*); PERCENTAGE rate "0.1 for 10%" (API ref) |
| Commit position needs an engineer | **Prepaid/postpaid commits** with access + invoice schedules, **overrides** for discount, **embeddable dashboards** (commits & credits), **balances API**, commit alerts, Salesforce sync | *Enterprise commit guide*; *Build API-powered customer dashboards* ("can be displayed through an iframe") |
| Stripe / NetSuite / Salesforce | Native Stripe invoicing (charge_automatically / send_invoice), NetSuite invoice sync (Public Beta), Salesforce daily sync of contracts, commits (current balance), invoices | *Invoice with Stripe*; *Integrate with NetSuite*; *Sync into Salesforce* |

## Caveats to own if asked (honesty builds trust)

- **Notification latency is minutes, not milliseconds.** Thresholds fire within about 5 minutes of ingest. For a hard stop at exactly $0, Replicate's own gateway acts on the webhook. Metronome is the source of truth for the balance, not an inline rate-limiter.
- **The Salesforce sync runs daily** ("cannot be configured to happen more frequently"). Real-time numbers come from the embeddable dashboard or the balances API.
- **The NetSuite integration is in Public Beta.** Tax is not calculated by Metronome. Up to 25,000 arrears invoices per month.
- **Stripe limits:** invoices over 250 line items collapse into one, and charges above $999,999.99 error out. Neither is a concern at Replicate's line-item shape (one line per hardware SKU).
- **Webhook delivery is at least once,** retried for up to 48h. Make the handler idempotent.
