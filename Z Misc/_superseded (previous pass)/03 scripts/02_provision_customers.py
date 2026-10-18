#!/usr/bin/env python3
"""
Step 2 - Provision Replicate's three demo customers, one per go-to-market motion,
using the official Metronome Python SDK (metronome-sdk).

  trial       "Ada Okafor (free trial)"
              trial contract + $10 Free Trial Credit valid 30 days, no credit card
              -> pain #2: know *when* the trial credit runs out
  paygo       "Lumen Labs (pay-as-you-go + Pro Support)"
              list prices + $500/mo Pro Support subscription (fixed fee)
              -> pain #3: support tiers as fixed fees
  enterprise  "Northwind Media (enterprise commit)"
              3-year contract: $100,000 prepaid commit (one $33,333 segment / year),
              15% off list on all compute, Enterprise Support at 10% of compute
              -> pain #3 (percent-based fee) + pain #4: commit visibility

Re-running reuses customers (matched by ingest alias) and contracts
(uniqueness_key -> 409 on retry, we then read the existing contract back).

API-SDK mapping (raw path -> SDK call):
  POST /v1/customers                 -> client.v1.customers.create(...)
  GET  /v1/customers?ingest_alias=   -> client.v1.customers.list(ingest_alias=...)
  POST /v1/contracts/create          -> client.v1.contracts.create(...)
  POST /v2/contracts/list            -> client.v2.contracts.list(...)

Docs:
  "Create a free trial"            https://docs.metronome.com/manage-product-access/create-trial
  "Launch an enterprise commit model"
      https://docs.metronome.com/guides/pricing-packaging/billing-model-guides/enterprise-commit
  "Apply credits and commits"      https://docs.metronome.com/pricing-packaging/apply-credits-commits/
"""

import argparse
import datetime as dt

from metronome import APIStatusError, ConflictError

from replicate_common import (
    COMMIT_DISCOUNT_MULTIPLIER, COMMIT_TOTAL_USD, COMMIT_YEARS, CUSTOMERS,
    PROD_COMMIT, PROD_ENT_SUPPORT, PROD_PRO_SUPPORT, PROD_TRIAL_CREDIT,
    RATE_CARD_ALIAS, TAG_COMPUTE, TRIAL_CREDIT_USD, TRIAL_DAYS,
    cents, client, first_of_current_month_utc, floor_hour, iso, load_state,
    now_utc, save_state,
)


def get_or_create_customer(c, name, alias):
    existing = list(c.v1.customers.list(ingest_alias=alias))
    if existing:
        print(f"  reuse customer '{name}': {existing[0].id}")
        return existing[0].id
    customer = c.v1.customers.create(
        name=name,
        ingest_aliases=[alias],
        # No billing provider conf (sandboxed work).
        # In prod: Stripe config for paygo, NetSuite config for enterprise.
    ).data
    print(f"  created customer '{name}': {customer.id}")
    return customer.id


def create_contract(c, customer_id, label, **payload):
    """contracts.create with a uniqueness_key; on 409 return the existing contract."""
    key = f"replicate-demo-{label}-{customer_id}"
    try:
        contract = c.v1.contracts.create(customer_id=customer_id, uniqueness_key=key, **payload).data
        print(f"  created contract '{payload.get('name')}': {contract.id}")
        return contract.id
    except ConflictError:
        contracts = c.v2.contracts.list(customer_id=customer_id).data
        match = next((k for k in contracts if getattr(k, "name", None) == payload.get("name")), None)
        if match is None and contracts:
            match = contracts[0]
        print(f"  reuse contract '{payload.get('name')}': {match.id if match else '?'}")
        return match.id if match else None


# --------------------------------------------------------------------------
# One builder per motion
# --------------------------------------------------------------------------

def trial_contract(products):
    # trial started 3 days ago (so 04_send_usage.py has a window to fill),
    # hour-aligned as Metronome requires for contract / credit boundaries
    start = floor_hour(now_utc() - dt.timedelta(days=3))
    end = start + dt.timedelta(days=TRIAL_DAYS)
    return {
        "name": "Free trial",
        "rate_card_alias": RATE_CARD_ALIAS,
        "starting_at": iso(start),
        "ending_before": iso(end),
        # The allowance AND the time window live on one credit:
        # "a credit with an access schedule bounds both at once"
        "credits": [{
            "name": f"Free Trial Credit (${TRIAL_CREDIT_USD:.0f})",
            "product_id": products[PROD_TRIAL_CREDIT],
            "applicable_product_tags": [TAG_COMPUTE],
            "priority": 1,
            "access_schedule": {"schedule_items": [{
                "amount": cents(TRIAL_CREDIT_USD),
                "starting_at": iso(start),
                "ending_before": iso(end),
            }]},
        }],
    }


def paygo_contract(products):
    start = first_of_current_month_utc()
    return {
        "name": "Pay-as-you-go + Pro Support",
        "rate_card_alias": RATE_CARD_ALIAS,
        "starting_at": iso(start),
        "usage_statement_schedule": {"frequency": "MONTHLY", "day": "FIRST_OF_MONTH"},
        # Fixed-fee support tier: a $500/mo subscription, billed in advance.
        "subscriptions": [{
            "name": "Pro Support",
            "collection_schedule": "ADVANCE",
            "initial_quantity": 1,
            "proration": {"invoice_behavior": "BILL_IMMEDIATELY", "is_prorated": False},
            "subscription_rate": {
                "billing_frequency": "MONTHLY",
                "product_id": products[PROD_PRO_SUPPORT],
            },
        }],
    }


def enterprise_contract(products):
    start = first_of_current_month_utc()
    end = start.replace(year=start.year + COMMIT_YEARS)

    # $100,000 over 3 years = one access segment per contract year,
    # each invoiced (prepaid) at the start of its year.
    segment = round(COMMIT_TOTAL_USD / COMMIT_YEARS, 2)
    amounts = [segment] * (COMMIT_YEARS - 1) + [round(COMMIT_TOTAL_USD - segment * (COMMIT_YEARS - 1), 2)]
    access_items, invoice_items = [], []
    for year, amount in enumerate(amounts):
        seg_start = start.replace(year=start.year + year)
        seg_end = start.replace(year=start.year + year + 1)
        access_items.append({"amount": cents(amount), "starting_at": iso(seg_start), "ending_before": iso(seg_end)})
        invoice_items.append({"timestamp": iso(seg_start), "amount": cents(amount)})

    return {
        "name": "Enterprise - $100k / 3 years",
        "rate_card_alias": RATE_CARD_ALIAS,
        "starting_at": iso(start),
        "ending_before": iso(end),
        "usage_statement_schedule": {"frequency": "MONTHLY", "day": "FIRST_OF_MONTH"},
        "commits": [{
            "name": "Committed Spend ($100k / 3 yrs)",
            "type": "PREPAID",
            "product_id": products[PROD_COMMIT],
            "applicable_product_tags": [TAG_COMPUTE],  # burns down on compute, incl. future SKUs
            "priority": 1,
            "access_schedule": {"schedule_items": access_items},
            "invoice_schedule": {"schedule_items": invoice_items},
        }],
        "overrides": [
            # negotiated discount: 15% off list on everything tagged 'compute'
            {
                "starting_at": iso(start),
                "applicable_product_tags": [TAG_COMPUTE],
                "type": "MULTIPLIER",
                "multiplier": COMMIT_DISCOUNT_MULTIPLIER,
            },
            # switch on the percent-based support tier (not entitled on the rate card)
            {
                "starting_at": iso(start),
                "product_id": products[PROD_ENT_SUPPORT],
                "entitled": True,
            },
        ],
    }


BUILDERS = {
    "trial": trial_contract,
    "paygo": paygo_contract,
    "enterprise": enterprise_contract,
}


def build_parser():
    parser = argparse.ArgumentParser(description="Provision Replicate's demo customers")
    parser.add_argument("--only", choices=sorted(BUILDERS), default=None,
                        help="Provision a single persona (default: all three)")
    return parser


def main():
    args = build_parser().parse_args()
    state = load_state()
    products = state.get("products")
    if not products:
        raise SystemExit("Run 01_setup_catalog.py first.")

    c = client()
    personas = [args.only] if args.only else list(BUILDERS)
    state.setdefault("customers", {})

    for i, key in enumerate(personas, 1):
        persona = CUSTOMERS[key]
        print(f"== {i}/{len(personas)} {persona['name']}")
        try:
            customer_id = get_or_create_customer(c, persona["name"], persona["alias"])
            payload = BUILDERS[key](products)
            contract_id = create_contract(c, customer_id, key, **payload)
        except APIStatusError as e:
            raise SystemExit(f"{key}: HTTP {e.response.status_code}: {e.message}")
        state["customers"][key] = {
            "name": persona["name"],
            "customer_id": customer_id,
            "ingest_alias": persona["alias"],
            "contract_id": contract_id,
            "starting_at": payload["starting_at"],
        }
        print(f"    https://app.metronome.com/customers/{customer_id}")

    save_state(state)
    print("\nDone. Next: 03_create_alerts.py")


if __name__ == "__main__":
    main()
