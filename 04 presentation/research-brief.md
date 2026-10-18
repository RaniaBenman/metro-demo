# Research brief: Replicate × Metronome

Background for the deck, the demo and Q&A. Every fact lists its source; anything inferred is marked **(inference)**. Every technical choice comes from the official Metronome documentation (docs.metronome.com), checked on 14 Oct 2026.

## 1. Replicate's business, and the priorities behind the four pains

| Fact | Number | Source |
|---|---|---|
| Developer reach | 2M developers signed up, 30,000 paying customers (Dec 2023) | Replicate's Series B statement, via Orrick (Dec 2023) |
| Catalog | 25k models (Dec 2023) → 50,000+ models (Nov 2025) | Ben's Bites (2023); Cloudflare blog "Replicate joins Cloudflare" (Nov 2025) |
| Ownership | Cloudflare announced the acquisition on 17 Nov 2025 and closed it on 1 Dec 2025. Replicate's "APIs and workflows will continue to work without interruption"; the catalog is coming to Workers AI. | Cloudflare blog; Cloudflare 10-Q (Q1 2026) |
| Pricing model (brief) | Per second of hardware time, 7 machine types (CPU $0.000100/s to 8x A40 Large $0.005800/s) | Prompt |
| Hardware roadmap | Today's replicate.com/pricing lists H100, H200, L40S and multi-GPU variants (2x/4x/8x), 12+ SKUs beyond the brief's 7. We present them as the roadmap (your call). | replicate.com/pricing (14 Oct 2026) |
| Enterprise motion | "Volume discounts for large amounts of spend"; priority support, performance SLAs; "Additional multi-GPU … capacity is available with committed spend contracts" | replicate.com/pricing |
| Quote-to-cash | Stripe (paygo), NetSuite (enterprise), Salesforce (CRM) | Prompt |

**Strategic priorities (inference, to validate in discovery):**
1. **Grow self-serve profitably.** The card-free trial is the top of a funnel of millions of developers, and every leaked trial hour is GPU cost.
2. **Ship hardware faster than competitors.** Hardware launches are how Replicate competes, and billing must not gate them.
3. **Expand enterprise ARPU and retention.** Commits, discounts, support tiers and SLAs.
4. **Free engineers from billing work.** Today it takes two teams per SKU, plus data pulls for commit customers.

**Competitive context (for the "card-free trial is a differentiator" point and the prepaid suggestion):**
- **Together AI:** "does not currently offer free trials"; access needs a $5 minimum credit purchase, with threshold auto-recharge (Together AI support/docs).
- **Fireworks AI:** "Starting July 1st, 2026, Fireworks is moving all self-serve accounts to prepaid billing", with auto reload (Fireworks blog, 15 Jun 2026).
- **OpenAI API:** prepaid billing; auto-reload is on by default at setup (OpenAI Help Center).
- **(inference)** Prepaid credits with auto-recharge is now the industry standard for self-serve AI inference, so a card-free trial is a differentiator worth protecting.

## 2. Metronome: proof points

| Fact | Source |
|---|---|
| Stripe completed the acquisition of Metronome on 14 Jan 2026 (announced Dec 2025). Collison: Metronome's metering engine is already used by "OpenAI, Anthropic and NVIDIA". Stripe intends to integrate it with Stripe Billing. | Stripe newsroom; Stripe blog "Metronome + Stripe: building the future of billing" |
| Price: "Stripe is paying about $1 billion to acquire Metronome, eight sources tell Upstarts." Stripe attached no terms to the announcement, so the figure is **reported**, not disclosed. | Upstarts Media (3 Dec 2025) |
| "OpenAI, Anthropic, Databricks, Confluent, and NVIDIA rely on Metronome"; "Metronome now powers billing for 150M+ end users, processing billions in usage-based revenue." ($50M Series C led by NEA.) | Metronome Series C release, Business Wire (25 Feb 2025) |
| OpenAI: "I can make pricing changes in Metronome's UI in less than an hour with no engineering resources" (Senior Manager of Revenue Operations); in production on Metronome "in less than two weeks". | metronome.com customer story: OpenAI |
| metronome.com now reads "Metronome, a stripe product". Its "Trusted by" logo wall shows, in order: Replicate, OpenAI, Anyscale, Cribl, Thinking Machines, NVIDIA, World Labs, Starburst, DataStax, Confluent, LangChain, CockroachDB, Foursquare, Anthropic, Hugging Face, together.ai. **Databricks is not on it.** Its only public source is the Feb 2025 Series C release. | metronome.com (checked 14–16 Oct 2026) |
| Scale: "up to 110,000 events per second (6.6 million events per minute) without requiring pre-aggregation"; default 5,000/s, raised on request; "billions of events per day" | Docs: Usage events at scale |

## 3. Pain → Metronome capability (all from official docs)

| Pain (Replicate's words) | Capability | Doc evidence |
|---|---|---|
| New machine type = two teams, weeks | One usage product with **pricing group key** `hardware`; the **rate card** holds one rate per machine type; a new GPU is one rate, scheduled for launch day or backdated. **Product tags** make discounts, commits and % fees cover new products automatically. | "Pricing group keys allow you to set different prices for the same product"; "1 billable metric → 1 product → many rates"; "if you know you're launching a product next month, you can schedule a rate change to go into effect on the launch day"; "Add the pertinent product tags to a new product on creation, and any discounts automatically apply" (*Create products*, *Create and manage rate cards*, *Contract edits and overrides*) |
| GPU seconds, published $/hour | Meter seconds, convert with **quantity conversion** (÷3,600) and price per hour | "Configure the associated product's quantity conversion to divide by 3,600 before applying a GPU-hour rate" (*Billing for provisioned throughput*) |
| Credit measured once a day; trials leak | Trial **credit** with an access schedule (amount + window). **Threshold notifications** go account-wide, scoped to trial credits by custom field, delivered by webhook. Trial → paid by **contract transition**. | "A credit with an access schedule bounds both at once"; GPU inference cost → "Amount cap; smaller grants" (*Free trials*); "evaluated at least once every three minutes… fire within 5 minutes of the usage… being ingested" (*Manage your customer lifecycle with Metronome notifications*); "create each one once and leave out `customer_id` to have it apply to everyone" (*Implement a free trial*) |
| No fixed or % fees → no support tiers | **Subscription** product (recurring fixed fee) and **Composite** product (PERCENTAGE rate on tagged products), entitled per contract | "Composite, percentage charge on a group of applicable products… by id or product tag"; "Subscription, a recurring fee billed on a schedule" (*Create products*); PERCENTAGE price "0.1 for 10%" (API *Add a rate*) |
| Commit position needs an engineer | **Prepaid or postpaid commits** (access + invoice schedules, true-up), **multiplier overrides** by tag, real-time **balances & ledgers**, **embeddable dashboards** (commits & credits, usage, invoices), commit threshold alerts, **Salesforce** sync of commits and balances | *Launch an enterprise commit model*; *Apply credits and commits to contracts* ("updates continuously in real time"); *Build API-powered customer dashboards* ("can be displayed through an iframe"); API: "a secure, time-limited URL… white-labeled billing experience without building custom UI"; *Sync into Salesforce* |
| Stripe / NetSuite / Salesforce | Native Stripe invoicing (per-contract billing provider), NetSuite billing or revenue-system sync, Salesforce daily sync, data export | *Invoice with Stripe* (invoice created in Stripe when the Metronome invoice finalizes; multi-entity); *Integrate with NetSuite* (the docs' own example is PLG billed in Stripe and SLG in NetSuite); *Sync into Salesforce* |

The deck's Sources slide links each of these doc pages to its official URL. Each URL was checked on 16 Oct 2026: it returns HTTP 200 and its page title matches.

| Doc page | URL |
|---|---|
| Create and manage rate cards | https://docs.metronome.com/guides/implement-metronome/core-concepts/create-manage-rate-cards |
| Create products | https://docs.metronome.com/guides/implement-metronome/core-concepts/create-products-contracts |
| Launch new pricing | https://docs.metronome.com/guides/pricing-packaging/make-pricing-changes/make-a-pricing-change |
| Billing for provisioned throughput | https://docs.metronome.com/guides/pricing-packaging/billing-model-guides/provisioned-throughput |
| Free trials | https://docs.metronome.com/guides/pricing-packaging/billing-model-guides/free-trials/overview |
| Implement a free trial | https://docs.metronome.com/guides/pricing-packaging/billing-model-guides/free-trials/implement-a-trial |
| Threshold notifications | https://docs.metronome.com/guides/customers-billing/set-up-notifications/threshold-notifications |
| Define subscription pricing | https://docs.metronome.com/guides/pricing-packaging/subscription/define-subscription-pricing |
| Launch an enterprise commit model | https://docs.metronome.com/guides/pricing-packaging/billing-model-guides/enterprise-commit |
| Apply credits and commits to contracts | https://docs.metronome.com/guides/pricing-packaging/apply-credits-and-commits/create-a-pre-paid-commit |
| Offer discounts on commits | https://docs.metronome.com/guides/pricing-packaging/apply-credits-and-commits/discounting-on-commits |
| Build API-powered customer dashboards | https://docs.metronome.com/guides/customers-billing/optimize-customer-experience/customer-dashboards-and-reporting |
| Track the remaining balance of a credit or commit | https://docs.metronome.com/guides/customers-billing/optimize-customer-experience/get-remaining-balance |
| Invoice with Stripe | https://docs.metronome.com/integrations/invoice-integrations/stripe |
| Integrate with NetSuite | https://docs.metronome.com/integrations/invoice-integrations/netsuite |
| Sync into Salesforce | https://docs.metronome.com/integrations/platform-integrations/sfdc-integration |
| Usage events at scale | https://docs.metronome.com/guides/events/high-volume-ingestion |
| Send usage events to /ingest | https://docs.metronome.com/guides/events/send-usage-events |

## 4. Caveats to own if asked (they build trust)

- **Gating stays in Replicate's app.** Metronome is the real-time source of truth and the signal: webhooks within about 5 minutes. Replicate's entitlement flag stops the GPU (docs: "manage entitlement… within your system").
- **Webhooks are at least once,** retried up to 48h and signed. The handler must be idempotent.
- **The Salesforce sync is daily** and "cannot be configured to happen more frequently". Live numbers come from the API, dashboards or webhooks.
- **NetSuite is in Public Beta.** Throughput is up to 25,000 arrears invoices/month, and some features (custom currencies, account hierarchy) are unsupported.
- **Stripe limits:** for non-integer quantities, Metronome sets quantity 1 and puts the true quantity in the description; invoices over 250 lines collapse into one. Neither matters at Replicate's line shape (one line per machine type).
- **Group-key cardinality:** past about 1,000 values per customer (e.g., `model`), talk to Metronome support. `model` is kept for breakdowns, not invoice lines.
- **Usage with no rate isn't billed until the rate exists.** Raw events are kept, and open draft invoices reflect rate changes ("changes are automatically reflected on the invoice"). Finalized invoices are not re-rated, so publish or backdate the rate before period close.

## 5. Discovery questions (to weave into the meeting)

1. Which of the four blockers hurts most this quarter? How long did the last machine type take end to end?
2. How much does trial leakage cost, and is it cost (honest heavy users) or abuse (freejacking)?
3. Commits: **prepaid or postpaid** (minimum + true-up)? Allotted per year, or across the term? Ramps? Rollover at renewal?
4. Support tiers: fixed price, % of spend, or "greater of"? What would customers pay for priority support and SLAs?
5. NetSuite: the system that bills enterprise customers, or only for revenue recognition of Stripe-billed invoices?
6. Event pipeline: where do prediction and instance-hour records live today (queue, warehouse)? Volume per day?
7. Cloudflare: does the integration change billing ownership or systems in the next 12 months?

## 6. Context for the presenter only (do not cite, per your instruction)

- Replicate is publicly a Metronome customer today: first on the metronome.com logo wall, and a case study, "Replicate launches prepaid credits in 2 weeks, significantly reducing fraud", reports prepaid credits with auto-recharge built in 14 days. Replicate's own docs show a $5 minimum threshold and a $15 minimum reload, the same constraints as Metronome's auto-recharge ($5 floor, recharge-to at least $10 above it).
- The role-play treats Replicate as a prospect. The facts above only explain why prepaid with auto-recharge is offered as an option in the appendix.
