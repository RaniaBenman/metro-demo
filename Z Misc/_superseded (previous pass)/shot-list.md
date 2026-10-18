# Demo shot list (for the local screenshot session)

Metronome is **READ-ONLY**: navigate, open, expand, hover, scroll. Never click Create / Add / Edit / Save / Archive / Delete / Submit, and never fill a form.
The scripts in `03 scripts/` are run by R, never by the session.

Save screens to `04 presentation/screens/` as `NN_actX_short-purpose.png`, where NN is the order of appearance in the demo.
Document every screen in `04 presentation/screens/README.md` using the template at the bottom.

## Narrative (30-minute demo, 5 acts)

The thread is Replicate's four pains, in their own words. Each act ends on "this is the pain you told us about, and this is it solved".

| Act | Time | Pain answered | Personas / objects (created by R's scripts) |
|---|---|---|---|
| 0 Orientation | 2 min | Set context: one event, one metric, one product, one rate card | Metronome home |
| 1 New machine types | 7 min | "Adding a machine type takes two teams and weeks" | Billable metric **Compute Seconds**, product **Compute (per second)** (pricing group key `hardware`), rate card **Replicate Public Pricing**; live: H100 added by `05_add_machine_type.py` |
| 2 Trial without leakage | 6 min | "We measure credit once a day; users run far past their trial" | Customer **Ada Okafor (free trial)**: $10 Free Trial Credit, alerts at $2 and $0 |
| 3 Support tiers | 5 min | "We can't model fixed or percent-based fees" | **Lumen Labs**: Pro Support $500/mo subscription. **Northwind Media**: Enterprise Support 10% (composite) |
| 4 Commit visibility | 8 min | "An engineer must pull data so customers know where they stand vs their commit" | **Northwind Media (enterprise commit)**: $100k / 3-yr prepaid commit, 15% override, balance + ledger, embeddable dashboard, commit alert |
| 5 Quote-to-cash | 2 min | Stripe (paygo), NetSuite (enterprise), Salesforce (CRM) | Developer → Integrations **entry screen only** (not connected) |

## Shots (in demo order)

### Phase A: can be captured now (no scripts needed)
| NN | File | What to show |
|---|---|---|
| 00 | `00_act0_metronome-home.png` | Landing page after login: the navigation (Customers, Offering/Pricing, Developer…) |
| 18 | `18_act5_integrations-entry.png` | Developer → Integrations: available integrations list showing Stripe, NetSuite, Salesforce |
| 19 | `19_act5_webhooks-entry.png` | Developer → Webhooks (or Notifications): where alert webhooks are configured. If absent, skip it and note that. |

### Phase B: after R has run steps 1 to 4 and 7 (before 05)
| NN | File | What to show |
|---|---|---|
| 01 | `01_act1_billable-metric-compute-seconds.png` | Billable metric "Compute Seconds": event type `compute_seconds`, SUM of `seconds`, group keys hardware / kind / model |
| 02 | `02_act1_product-compute-per-second.png` | Product "Compute (per second)": type Usage, pricing group key `hardware`, presentation key, tag `compute` |
| 03 | `03_act1_rate-card-7-machine-types.png` | Rate card "Replicate Public Pricing": the 7 hardware rates (+ Pro Support, Enterprise Support 10% not entitled) |
| 06 | `06_act2_ada-customer-overview.png` | Customer Ada Okafor (free trial): contract "Free trial", dates |
| 07 | `07_act2_ada-trial-credit-balance.png` | Ada's credits / balances: $10 trial credit consumed to $0, ledger of draw-downs |
| 08 | `08_act2_ada-alerts-in-alarm.png` | Ada's alerts / notifications: "Trial credit almost used" and "Trial credit exhausted" in alarm |
| 09 | `09_act2_ada-draft-invoice.png` | Ada's draft invoice: usage per hardware, credit applied, remainder past the credit |
| 10 | `10_act3_lumen-contract-pro-support.png` | Lumen Labs contract: Pro Support subscription $500/mo |
| 11 | `11_act3_lumen-invoices-pro-support.png` | Lumen invoices: Pro Support line (scheduled/advance) + usage draft with one line per hardware |
| 12 | `12_act3_product-enterprise-support-composite.png` | Product "Enterprise Support (% of compute)": type Composite, applies to tag `compute` |
| 13 | `13_act3_northwind-invoice-support-10pct.png` | Northwind draft usage invoice: discounted compute lines + Enterprise Support 10% line |
| 14 | `14_act4_northwind-contract-commit-discount.png` | Northwind contract: $100k prepaid commit, 3 yearly access segments, 15% override (0.85) |
| 15 | `15_act4_northwind-commit-balance-ledger.png` | Northwind commit balance remaining + ledger (draw-downs) |
| 16 | `16_act4_northwind-customer-dashboard.png` | Embeddable "commits_and_credits" dashboard (URL printed by `06_dashboard_links.py`, saved in `Z Misc/state.json` under `dashboards`): what Northwind sees |
| 17 | `17_act4_northwind-commit-alert.png` | Northwind alerts: "Commit balance under $25,000" (state OK) + Lumen's "Monthly spend over $2,500" if visible |

### Phase C: after R runs `05_add_machine_type.py --sample-usage`
| NN | File | What to show |
|---|---|---|
| 04 | `04_act1_rate-card-h100-added.png` | Same rate card, now with the 8th row `gpu-h100` |
| 05 | `05_act1_lumen-invoice-h100-line.png` | Lumen's draft invoice now showing an H100 line, with no other change |

## Documentation template (one section per screen in `04 presentation/screens/README.md`)

```
## NN · Title
- File: NN_actX_purpose.png
- Purpose: why this screen is in the demo (pain it answers)
- Areas of focus: the 2-3 things on screen to point at
- Actions, in order: 1. … 2. … (navigation path, scroll, expand, hover, click tab)
- Talk track (1-2 sentences): what to say while on it
```
