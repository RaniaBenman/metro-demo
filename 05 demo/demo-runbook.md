# Demo runbook: Replicate's pricing in Metronome (30 min)

The demo lives in the **Production** environment of your Metronome account, not its Sandbox: your API token was a Production token. Production has no orange "Sandbox" banner, and the links below open there. Numbers come from `Z Misc/state_snapshot.json` (run of 17 Oct 2026) and from the app after the L40S launch (17 Oct, 05:02). Lines marked *expected* depend on the live H100.

| Customer | Offering | Link |
|---|---|---|
| Ada Okafor | Free trial ($10, 30 days) | https://app.metronome.com/customers/d44c4fc0-a5cf-4069-82d4-5a48daf4af7c |
| Brightframe AI | Pay-as-you-go + Pro Support | https://app.metronome.com/customers/10a372d9-6bd7-4984-886d-a24ac14994ca |
| Northwind Media | $100k prepaid commit, 3 years | https://app.metronome.com/customers/a162a702-1a41-43c1-92d9-f28d7f6615cf |
| Kepler Games | $100k postpaid minimum, 3 years | https://app.metronome.com/customers/27da32a3-451b-48fb-ba14-84f252556716 |

## Before the demo

1. **Present in October.** All usage sits on October's draft invoices, which close on Nov 1.
2. **L40S launched (done 17 Oct).** The rate card shows `gpu-l40s` at $3.51/h from Oct 1. On a fresh build, run `./run_single.sh 05_launch_gpu.py --hardware gpu-l40s` after `run.sh`.
3. **Within the hour before the demo:** `./run_single.sh 06_dashboard_links.py`. The customer dashboard links expire 1 hour after they're generated.
4. **Open the tabs in demo order:** 
	1. Usage events, 
	2. Offering → Billable metrics → Compute seconds, 
	3. Offering → Products → Compute hours, 
	4. Offering → Rate cards → Replicate list prices, 
	5. Offering → Packages, 
	6. Customer/Ada, 
	7. *Developer → Notifications,* 
	8. Customer/Brightframe, 
	9. Customer/Northwind, 
	10. Customer/Kepler, 
	11. the 5 dashboard links, 
	12. *Developer → Integrations.*
5. **Don't rehearse the H100 rate on this rate card.** Once added, its lines are on Brightframe's and Northwind's invoices for good.
6. **Mind the Raindrop leftovers.** Production also holds your Raindrop exercise: the *Raindrop Starter Rate Card*, 4 token products, and the *Raindrop Starter ($20/mo)* package with 4 customers on it. Open pages from the links in this runbook rather than from those lists, or say it's a shared demo account.

## Act 0: one event, every price (2 min)

- **Show** : 
	- `compute_usage` ==🟢**events** (LAST transaction)== ==🟡carrying `seconds`, `hardware`==, `workload` (prediction, deployment or training) and `model`. 
	- Then the ==🟢**billable metric** *Compute seconds*==: ==🟡sum of `seconds`, grouped by `hardware`==, `model` and `workload`.
  - Screens: 
	  - [act0_01_usage-events_stream_after-l40s](screens/act0_01_usage-events_stream_after-l40s.jpg),
	  - [act0_02_usage-events_one-event-payload](screens/act0_02_usage-events_one-event-payload.jpg),
	  - [act0_03_billable-metric_compute-seconds](screens/act0_03_billable-metric_compute-seconds.jpg).
- **Say:** 
	- one event type covers everything Replicate meters. 
	- `hardware` picks the price; 
	- `workload` and `model` are only for breakdowns.

## Act 1: a new GPU is a rate, not a project (7 min)

- **Their words:** "To add another machine type, we have to involve two different engineering teams, which can take weeks."
- **Show:** 
	- ==🟢ONE product "*Compute hours"*==:  with ==🟡seconds converted to hours==. 
	- ((==🟢rate card== *Replicate list prices*: )) so it can be ==🟡priced by the hour== (according to your pricing model) , and per `hardware` --> which becomes nothing but a pricing dimension 
	  --> and you know what that means ... :  that meeeeans that : a gpu launch.. blling-wise translates to a  ONE simple additional line in this card of rates (or as we call it rating card)... ZERO code change in your app (...and we'll even do this live in a few minutes)
	  for now, if you take a look you'll we see your 7 machine types + an  additional `gpu-l40s` at $3.51/h, added with one API call before the demo.
	- INJECT ////TODO
  - Screens:
	  - [act1_product_compute-hours](screens/act1_product_compute-hours.jpg), 
	  - [act1_rate-card_replicate-list-prices_after-l40s](screens/act1_rate-card_replicate-list-prices_after-l40s.jpg).
- **Show:** ((Customer invoices with prices that differ across)) and those are reflected in customer invoices, according to their terms
	- Here we have the current period's invoice for company ==🟢Brightframe== >>>
	  -/!\ ((Oct01-Nov01)) a ==🟡paygo customer== consuming at ==🟡list prices==.... 
	  -/!\ ((Oct1)) which also has (if u look closely), purchased a ==🟣((prod+rate+package))== support subscription... at the monthly fixed fee of 500USD, to sorta illustrate the type of ==🟡fixed-rate support tier== you can implement on Metronome) 
	  
	- Here we have the invoice draft for ==🟢Ada==, a ==🟡newly-signed-up== paygo customer, /!\ which as you can see had benefited from ==🟡free trial credit==, which they consumed.... and in this scenario,  the invoice even shows ==🟡overrage==  to illustrate the case where we allow them to continue consuming because perhaps they registered a card.
	  --> In another scenario ... we could have shut down the service for Ada, the minute we're notified of the free credit exhaustion>>>
	  but we'll get into the notification part in a few minutes
	  
	- Here, we have ==🟢Northwind=='s ..  : 
	  -/!\ ((Oct1)) NOT a paygo customer (like Ada and Brightframe), but one that signed a ==🟡COMMIT== of 100K.. prepaid upfront in ==🟡3 yearly installments==.
	  -/!\ ((Oct01-Nov01)) and since they signed a commit, we also modeled here a ==🟡discount of 15%==  on the list prices (which brings cpus price to 0.31/h down from of 0.36, and so on)
	  -We also  illustrate here how you could model a ==🟣((prod w composite_tags on compute+rate))== support tier billed>>>NOT with a flat rate as we saw earlier... but as a % of their consumption. (here 10%)
  - Screens: 
	  - [act1_brightframe_app_usage-invoice_after-l40s](screens/act1_brightframe_app_usage-invoice_after-l40s.jpg) ,
	  - [act1_northwind_app_invoice-l40s-from-commit_after-l40s](screens/act1_northwind_app_invoice-l40s-from-commit_after-l40s.jpg).
- **TRANSITION :** Now all these invoices are calculated based on usage events we'd receive from the Replicate app : every inference event would carry, as we saw earlier, the customer identifier, the number of seconds, the hardware so we can infer the price, etc.
  But the thing is.. among the events we sent to Metronome in this example, were events relating to a hypothetical newly launched hardware by Replicate, called GPU-h100, which we HAVEN'T priced in yet in the ==🟢rate card,== and which (consequently) ISN'T accounted for in these invoices.
  So what we'll do in this part of the demo, is launch together the billing of h100, to illustrate how your app and engineers can independently launch their hardware and start emitting events and basically INNOVATE-LEANLY-AND-FREELY  without being hurdled by billing mechanics which can handled separately.
- **Live:** Offering → Rate cards → Replicate list prices → **+ Add a rate** (top right):
  - product **Compute hours**;
  - `hardware` = **gpu-h100**;
  - **$5.49** per hour;
  - starting **Oct 1, 2026 (UTC)**;
  - entitled.
  
  Two invoices change: Brightframe's gains an H100 line, 10 h × $5.49 = **$54.90** at list. Northwind's gains 100 h at 15% off = **$466.65**, paid from the commit, and its Enterprise Support grows by **$46.67**.
- **Fallback:** `./run_single.sh 05_launch_gpu.py --hardware gpu-h100` adds the same rate by API.
- **Say:** no new metric, product, contract or code. The 15% discount and the 10% support fee target the `compute` tag, so every new GPU inherits them.
  - Screens: [act1_brightframe_app_contract-rates_before](screens/act1_brightframe_app_contract-rates_before.jpg) (Brightframe at list), [act1_northwind_app_contract-rates-15pct-off_before](screens/act1_northwind_app_contract-rates-15pct-off_before.jpg) (Northwind at 15% off, with Enterprise Support switched on).

## Act 2: a card-free trial that can't leak (6 min)

- **Their words:** "Our systems measure credit usage once a day, and often users use far beyond their free trial credit."
- **Show:** Offering → Packages: *Pay-as-you-go ($10 free trial, 30 days)* and *Pay-as-you-go + Pro Support ($500/mo)*.
  - Screens: [act2_packages](screens/act2_packages.jpg).
- **Show:** Ada's $10 credit, valid Oct 13 – Nov 12 (UTC), is fully used. Her draft invoice applies the credit to the first $10.00 of compute, then bills **$2.59** of overage at list.
  - Screens: [act2_ada_app_trial-credit-consumed](screens/act2_ada_app_trial-credit-consumed.jpg), [act2_ada_app_invoice-credit-and-overage](screens/act2_ada_app_invoice-credit-and-overage.jpg).
- **Show:** Ada's alerts: *Trial credit: 20% left* and *Trial credit: exhausted* are in alarm. *Trial ends in 3 days* is OK, with 27 days left.
  - Screens: [act2_ada_app_alerts-in-alarm](screens/act2_ada_app_alerts-in-alarm.jpg).
- **Show:** Developer → Notifications: the same three trial alerts cover every customer, because they filter on the credit's `trial` tag.
  - Screens: [act2_developer_notifications-account-wide](screens/act2_developer_notifications-account-wide.jpg).
- **Say:** Metronome evaluates thresholds at least every 3 minutes and fires within 5 minutes of the usage arriving (threshold notifications docs). The leak shrinks from up to a day of GPU time to minutes, and Replicate's app gates usage on the webhook.
- **Customer view:** Ada's credits dashboard: [act2_ada_dashboard_trial-credit-window](screens/act2_ada_dashboard_trial-credit-window.jpg), [act2_ada_dashboard_trial-credit-ledger](screens/act2_ada_dashboard_trial-credit-ledger.jpg).

## Act 3: support tiers you can sell (5 min)

- **Their words:** "We don't have support tiers because the current billing platform cannot model fixed or percent-based fees."
- **Show:** Brightframe's contract: *Pro Support* at $500/month, billed in advance. October's invoice is finalized; November's is a draft.
  - Screens: [act3_brightframe_app_customer-overview](screens/act3_brightframe_app_customer-overview.jpg), [act3_brightframe_app_contract-pro-support](screens/act3_brightframe_app_contract-pro-support.jpg), [act3_brightframe_dashboard_pro-support-invoice](screens/act3_brightframe_dashboard_pro-support-invoice.jpg) (customer view).
- **Show:** Brightframe's usage invoice: one line per machine type, **$1,900.40** once the H100 is live (*expected*). The *monthly spend over $1,500* alert is in alarm.
  - Screens: [act1_brightframe_app_usage-invoice_after-l40s](screens/act1_brightframe_app_usage-invoice_after-l40s.jpg) (before the H100; customer view before the L40S: [act3_brightframe_dashboard_usage-invoice_before](screens/act3_brightframe_dashboard_usage-invoice_before.jpg)), [act3_brightframe_app_alerts-spend-in-alarm](screens/act3_brightframe_app_alerts-spend-in-alarm.jpg).
- **Show:** Northwind's usage invoice. The commit pays the compute, and *Enterprise Support (10% of compute)* = **$518.44** is billed once the H100 is live (*expected*): 10% of the $5,184.41 discounted compute.
  - Screens: [act1_northwind_app_invoice-l40s-from-commit_after-l40s](screens/act1_northwind_app_invoice-l40s-from-commit_after-l40s.jpg) ($471.78 due before the H100; before the L40S: [act3_northwind_app_invoice-commit-and-support_before](screens/act3_northwind_app_invoice-commit-and-support_before.jpg)).
- **Say:** a fixed tier for growing teams, and a percentage tier that grows with enterprise usage, future GPUs included.

## Act 4: where am I on my commit? (7 min)

- **Their words:** "We cannot tell those customers where they are against their commitment without having an engineer pull data from the database."
- **Ask first:** are your commits paid up front, or a minimum billed as it's used? Up front → Northwind; minimum → Kepler.
- **Northwind, prepaid:**
  - The contract is $100k over 3 years, with a 15% discount on everything tagged `compute` and 25% rollover.
    - Screens: [act4_northwind_app_contract-commit_after-l40s](screens/act4_northwind_app_contract-commit_after-l40s.jpg) (before: [act4_northwind_app_contract-commit_before](screens/act4_northwind_app_contract-commit_before.jpg)).
  - The commit balance is **$94,815.60** of $100,000 ($5,184.41 used) once the H100 is live (*expected*).
    - Screens: [act4_northwind_app_customer-overview_before](screens/act4_northwind_app_customer-overview_before.jpg) (the commit bar, before the L40S launch).
  - Installments: $33,333.33 invoiced Oct 2026, with drafts for 2027 and 2028.
    - Screens: [act4_northwind_dashboard_commit-invoice-schedule](screens/act4_northwind_dashboard_commit-invoice-schedule.jpg).
  - Customer view: the commit and usage dashboards.
    - Screens: [act4_northwind_dashboard_commit-ledger_before](screens/act4_northwind_dashboard_commit-ledger_before.jpg), [act4_northwind_dashboard_usage_before](screens/act4_northwind_dashboard_usage_before.jpg); the same chart in the app after the L40S launch: [act4_northwind_app_usage_after-l40s](screens/act4_northwind_app_usage_after-l40s.jpg).
- **Kepler, postpaid:**
  - **$1,141.13** used toward the $100k minimum (list $1,342.50, less 15%).
    - Screens: [act4_kepler_app_customer-overview](screens/act4_kepler_app_customer-overview.jpg).
  - October's invoice is **$1,255.24**: $1,141.13 of compute plus $114.11 of support.
    - Screens: [act4_kepler_app_october-invoice-billed-monthly](screens/act4_kepler_app_october-invoice-billed-monthly.jpg).
  - A true-up invoice is scheduled for Oct 1, 2029 to cover whatever is left of the minimum ($98,858.88 today).
    - Screens: [act4_kepler_app_true-up-invoice-2029](screens/act4_kepler_app_true-up-invoice-2029.jpg).
  - Customer view: the commit dashboard.
    - Screens: [act4_kepler_dashboard_minimum-ledger](screens/act4_kepler_dashboard_minimum-ledger.jpg), [act4_kepler_dashboard_minimum-invoice-schedule](screens/act4_kepler_dashboard_minimum-invoice-schedule.jpg).
- **Show:** *Commit: 25% remaining* is OK for both today. It's the renewal and expansion signal.
  - Screens: the alert's policy is listed in [act2_developer_notifications-account-wide](screens/act2_developer_notifications-account-wide.jpg).

## Act 5: fits your quote-to-cash (3 min)

- **Show:** Developer → Integrations: Stripe and Salesforce, plus the AWS, Azure and GCP marketplaces. None is connected here, and NetSuite isn't listed in this account.
  - Screens: [act5_developer_integrations](screens/act5_developer_integrations.jpg).
- **Say:** Stripe collects self-serve payments, NetSuite invoices enterprise (Public Beta), and Salesforce gets a daily sync.
- **If asked:** the enterprise contracts store their opportunity ID in an `sfdc_opportunity_id` custom field. Metronome's own Salesforce field needs the integration connected.

## Numbers at a glance

| | Before the L40S launch | After the L40S launch (17 Oct) | After the live H100 (*expected*) |
|---|---|---|---|
| Brightframe usage invoice | $1,803.38 | $1,845.50 | $1,900.40 |
| Northwind compute, 15% off, from the commit | $4,568.58 | $4,717.75 | $5,184.41 |
| Northwind commit remaining | $95,431.42 | $95,282.25 | $94,815.60 |
| Northwind Enterprise Support (10%) | $456.86 | $471.78 | $518.44 |
| Kepler October invoice | $1,255.24 | unchanged | unchanged |
| Ada overage after the $10 credit | $2.59 | unchanged | unchanged |

## If something goes wrong

- **A dashboard link shows an error:** it's older than an hour. Re-run `06_dashboard_links.py`.
- **An invoice hasn't changed after a rate is added:** refresh after a minute.
- **An alert shows "evaluating":** wait. Alerts are re-evaluated at least every 3 minutes.
- **Someone asks about the usage chart's shape:** the usage is synthetic, and each workload type was sent as one block of time.
- **A total is a cent off from this runbook:** half-cent amounts round differently between views. Kepler's $1,141.125 shows as $1,141.12 or $1,141.13, and Northwind's $4,717.755 as $4,717.75.
- **The Usage events page shows 1,960 duplicates:** Northwind's usage was re-sent on 17 Oct to add its L40S hours, and Metronome dropped the events it already had (deduplication on `transaction_id`).
- **Hard questions:** see the deck's appendix slide "Straight answers to the hard questions".

## Screenshots (`screens/`)

38 screenshots taken on 17 Oct 2026, cited above under the step they illustrate, in the order you show them. Names read `act<N>_<subject>_<view>`: `app` is the Metronome app and `dashboard` the customer-facing embedded dashboard. `_after-l40s` is the state you'll present; `_before` is the same view before the L40S launch. Files without either suffix didn't change with it.

The customer dashboards weren't retaken after the L40S launch, because their links had expired. Run `06_dashboard_links.py` if you want them.
