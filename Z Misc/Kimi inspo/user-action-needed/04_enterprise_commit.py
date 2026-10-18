"""
04 — The enterprise commit Replicate can't see into today (Pain #4) + support tiers (Pain #3).

GOAL
----
Replicate's large customers commit to spend (their own example: $100,000 over
3 years) in exchange for a discount — but today nobody can tell the customer
where they stand against the commitment without an engineer pulling data from
the database. This script builds that exact deal in Metronome:

  1. Enterprise customer "Acme Robotics, Inc." with a Salesforce account id
     wired into its configuration (the CRM join key for quote-to-cash).
  2. A 3-year contract on the SAME public rate card, containing:
       - PREPAID commit $100,000 with a ramped access schedule
         (Y1 $25k / Y2 $35k / Y3 $40k — adoption ramps),
       - invoiced in two installments ($50k at signature, $50k at year 2),
       - 25% rollover into a renewal (a clause enterprise buyers ask for),
       - a MULTIPLIER override: 10% off list on all `gpu-compute` products —
         the discount they earned for committing,
       - "Priority Support" subscription ENABLED on this contract ($500/mo) and
         "Premium Support" at 10% of GPU spend — Pain #3, both fee shapes,
       - one $5,000 scheduled charge in month 3 (solutions engineering),
       - NetSuite as the revenue system / Stripe-style billing provider hooks.
  3. A commit-balance alert at 80% consumed — the account team's renewal
     trigger, fired in real time.

POSITION IN THE DEMO NARRATIVE
------------------------------
Act 3 (support tiers entitled on the contract — Pain #3) and Act 4 (the
commit: contract page shows access schedule + invoice schedule + override;
Commits & credits tab shows Consumed / Remaining in real time — Pain #4).
The kicker: this visibility is also available to Replicate's OWN customers via
the embeddable dashboard / customerBalances API — no engineer required.

BUSINESS MOTIVE
---------------
Commit visibility is a revenue function, not a reporting nicety: it drives
on-time renewals, upsell timing, and eliminates a recurring engineering
interrupt. It also removes the "discount but can't track" blocker that keeps
Replicate from closing bigger committed deals.

NOTE: only CREATE calls. Idempotent via state.json + uniqueness key.
"""

import datetime as dt

import replicate_common as rc

NOW = dt.datetime.now(dt.timezone.utc).replace(minute=0, second=0, microsecond=0)
DEAL_START = NOW - dt.timedelta(days=45)          # deal started ~1.5 months ago
Y1_END = DEAL_START + dt.timedelta(days=365)
Y2_END = DEAL_START + dt.timedelta(days=730)
Y3_END = DEAL_START + dt.timedelta(days=1095)
ONBOARDING_AT = DEAL_START + dt.timedelta(days=75)  # month 3 of the contract


def iso(t: dt.datetime) -> str:
    return t.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def main() -> None:
    client = rc.get_client()
    state = rc.load_state()
    if "rate_card_id" not in state:
        raise SystemExit("Run 02_rate_card.py first.")
    usd = state.get("usd_credit_type_id") or rc.usd_credit_type_id(client)

    # --- 1. Enterprise customer, joined to Salesforce -------------------------
    if "ent_customer_id" not in state:
        cust = client.v1.customers.create(
            name=rc.ENT_CUSTOMER["name"],
            ingest_aliases=[rc.ENT_CUSTOMER["alias"]],
            custom_fields={"salesforce_account_id": "001R000003AcmeAI",
                           "segment": "enterprise"},
        )
        state["ent_customer_id"] = cust.id
        rc.save_state(state)
        print(f"created customer         {cust.id}  ({rc.ENT_CUSTOMER['name']})")

    # --- 2. The $100k / 3-year committed-spend contract -----------------------
    if "ent_contract_id" not in state:
        contract = client.v1.contracts.create(
            customer_id=state["ent_customer_id"],
            name="Enterprise — $100k / 3yr commit (10% off GPU)",
            starting_at=iso(DEAL_START),
            ending_before=iso(Y3_END),
            rate_card_id=state["rate_card_id"],
            uniqueness_key="replicate-ent-acme-3yr",
            net_payment_terms_days=30,
            commits=[{
                "type": "PREPAID",
                "name": "Committed spend — $100k / 3yr",
                "product_id": state["commit_product_id"],
                "priority": 1,
                "applicable_product_tags": [rc.GPU_TAG],
                # Ramped drawdown schedule: what Acme may consume each year
                "access_schedule": {
                    "credit_type_id": usd,
                    "schedule_items": [
                        {"amount": 2_500_000, "starting_at": iso(DEAL_START), "ending_before": iso(Y1_END)},  # $25k Y1
                        {"amount": 3_500_000, "starting_at": iso(Y1_END),     "ending_before": iso(Y2_END)},  # $35k Y2
                        {"amount": 4_000_000, "starting_at": iso(Y2_END),     "ending_before": iso(Y3_END)},  # $40k Y3
                    ],
                },
                # Cash schedule: $50k up front, $50k at the start of year 2
                "invoice_schedule": {
                    "credit_type_id": usd,
                    "schedule_items": [
                        {"amount": 5_000_000, "timestamp": iso(DEAL_START)},
                        {"amount": 5_000_000, "timestamp": iso(Y1_END)},
                    ],
                },
                "rollover_fraction": 0.25,  # up to 25% rolls into a renewal
            }],
            # Pain #3 — both support fee shapes, entitled on THIS contract only.
            # The rates live on the shared rate card as entitled=false; an
            # entitlement override flips them on for Acme (the documented
            # per-contract enablement pattern).
            overrides=[
                {
                    # The discount they bought with the commitment:
                    # 10% off list on every GPU-compute product, whole term.
                    "starting_at": iso(DEAL_START),
                    "ending_before": iso(Y3_END),
                    "type": "MULTIPLIER",
                    "multiplier": 1 - rc.ENT_DISCOUNT,
                    "applicable_product_tags": [rc.GPU_TAG],
                },
                # Priority Support: $500/mo flat subscription -> ON for Acme
                *([{"starting_at": iso(DEAL_START), "product_id": state["priority_support_id"],
                    "entitled": True}] if "priority_support_id" in state else []),
                # Premium Support: 10% of GPU spend (composite) -> ON for Acme
                *([{"starting_at": iso(DEAL_START), "product_id": state["premium_support_id"],
                    "entitled": True}] if "premium_support_id" in state else []),
            ],
            scheduled_charges=[{
                "product_id": state["onboarding_product_id"],
                "name": "Onboarding & solutions engineering (one-time)",
                "schedule": {
                    "credit_type_id": usd,
                    "schedule_items": [{
                        "amount": rc.ENT_ONBOARDING_FEE * 100,  # $5k -> cents
                        "timestamp": iso(ONBOARDING_AT),
                    }],
                },
            }] if "onboarding_product_id" in state else [],
            custom_fields={"sfdc_opportunity_id": "006R00000AcmeCommit",
                           "contract_type": "enterprise_commit"},
        )
        state["ent_contract_id"] = contract.id
        rc.save_state(state)
        print(f"created contract         {contract.id}  ($100k commit, 10% off, $5k onboarding)")

    # --- 3. Renewal-trigger alert: 80% of the commit consumed ----------------
    if "ent_alert_id" not in state:
        alert = client.v1.alerts.create(
            name="Acme commit 80% consumed",
            alert_type="low_remaining_commit_percentage_reached",
            threshold=20,               # fires when 20% remains == 80% consumed
            credit_type_id=usd,
            customer_id=state["ent_customer_id"],
            evaluate_on_create=False,
            uniqueness_key="replicate-ent-80pct",
        )
        state["ent_alert_id"] = alert.id
        rc.save_state(state)
        print(f"created alert            {alert.id}  (commit 80% consumed)")

    print("\nDone. Next: python3 05_send_usage.py")


if __name__ == "__main__":
    main()
