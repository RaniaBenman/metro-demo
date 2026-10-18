#!/usr/bin/env python3
"""
Step 1 - Build Replicate's pricing catalog in Metronome,
using the official Metronome Python SDK (metronome-sdk).

Creates:
  - ONE billable metric  "Compute Seconds"  (SUM of event seconds, grouped by hardware)
  - ONE usage product    "Compute (per second)" priced per `hardware` (pricing group key)
  - support products:    "Pro Support" (fixed monthly fee, SUBSCRIPTION)
                         "Enterprise Support (% of compute)" (COMPOSITE, percentage)
  - fixed products:      "Free Trial Credit", "Committed Spend" (back credits / commits)
  - ONE rate card        "Replicate Public Pricing": 7 hardware rates + support rates

Re-running reuses existing resources (matched by name).

Key design point (pain #1, "adding a machine type takes weeks"):
  hardware is a *pricing dimension*, not a product. A new machine type is one
  new rate on the rate card (see 05_add_machine_type.py), no new metric,
  product, contract or code change.

API-SDK mapping (raw path -> SDK call):
  GET  /v1/billable-metrics                      -> client.v1.billable_metrics.list()
  POST /v1/billable-metrics/create               -> client.v1.billable_metrics.create(...)
  POST /v1/contract-pricing/products/list        -> client.v1.contracts.products.list()
  POST /v1/contract-pricing/products/create      -> client.v1.contracts.products.create(...)
  POST /v1/contract-pricing/rate-cards/list      -> client.v1.contracts.rate_cards.list()
  POST /v1/contract-pricing/rate-cards/create    -> client.v1.contracts.rate_cards.create(...)
  POST /v1/contract-pricing/rate-cards/addRates  -> client.v1.contracts.rate_cards.rates.add_many(...)

Docs:
  "Create products"   https://docs.metronome.com/pricing-packaging/create-products-contracts/
  "How Metronome works" https://docs.metronome.com/guides/get-started/how-metronome-works
"""

from replicate_common import (
    BM_COMPUTE, ENT_SUPPORT_PERCENT, EVENT_TYPE, HARDWARE, LIST_START,
    PROD_COMMIT, PROD_COMPUTE, PROD_ENT_SUPPORT, PROD_PRO_SUPPORT, PROD_TRIAL_CREDIT,
    PRO_SUPPORT_MONTHLY_USD, RATE_CARD_ALIAS, RATE_CARD_NAME, TAG_COMPUTE,
    cents, client, find_by_name, get_id, load_state, save_state,
)


def get_or_create_billable_metric(c):
    metrics = c.v1.billable_metrics.list(limit=100)
    existing = find_by_name(metrics, BM_COMPUTE)
    if existing:
        print(f"  reuse billable metric '{BM_COMPUTE}': {get_id(existing)}")
        return get_id(existing)
    resp = c.v1.billable_metrics.create(
        name=BM_COMPUTE,
        event_type_filter={"in_values": [EVENT_TYPE]},
        property_filters=[
            {"name": "seconds", "exists": True},
            {"name": "hardware", "exists": True},
        ],
        aggregation_type="SUM",
        aggregation_key="seconds",
        # - 'hardware' is the pricing dimension (one rate per machine type)
        # - 'kind' (prediction | deployment | training) and 'model' are kept
        #   for invoice/usage breakdowns, they never change the price
        group_keys=[["hardware"], ["kind"], ["model"]],
    )
    print(f"  created billable metric '{BM_COMPUTE}': {resp.data.id}")
    return resp.data.id


def get_or_create_product(c, name, payload):
    products = c.v1.contracts.products.list()
    existing = find_by_name(products, name)
    if existing:
        print(f"  reuse product '{name}': {get_id(existing)}")
        return get_id(existing)
    resp = c.v1.contracts.products.create(name=name, **payload)
    print(f"  created product '{name}': {resp.data.id}")
    return resp.data.id


def get_or_create_rate_card(c):
    # body={}: this endpoint 400s ('Unknown error parsing request body') when
    # the POST carries no JSON body at all, so send an explicit empty object.
    cards = c.v1.contracts.rate_cards.list(body={})
    existing = find_by_name(cards, RATE_CARD_NAME)
    if existing:
        print(f"  reuse rate card '{RATE_CARD_NAME}': {get_id(existing)}")
        return get_id(existing), False
    resp = c.v1.contracts.rate_cards.create(
        name=RATE_CARD_NAME,
        description="Replicate list prices: per-second compute by hardware + support tiers.",
        aliases=[{"name": RATE_CARD_ALIAS}],
    )
    print(f"  created rate card '{RATE_CARD_NAME}': {resp.data.id}")
    return resp.data.id, True


def add_rates(c, rate_card_id, products):
    rates = []
    # one FLAT rate per hardware SKU, on the single compute product
    for sku, (_display, usd_per_sec) in HARDWARE.items():
        rates.append({
            "product_id": products[PROD_COMPUTE],
            "starting_at": LIST_START,
            "entitled": True,
            "rate_type": "FLAT",
            "price": cents(usd_per_sec),
            "pricing_group_values": {"hardware": sku},
        })
    # fixed-fee support tier: $500 / month, only billed on contracts that subscribe to it
    rates.append({
        "product_id": products[PROD_PRO_SUPPORT],
        "starting_at": LIST_START,
        "entitled": True,
        "rate_type": "FLAT",
        "price": cents(PRO_SUPPORT_MONTHLY_USD),
        "billing_frequency": "MONTHLY",
    })
    # percent-based support tier: 10% of compute spend.
    # entitled=False on the rate card: nobody pays it by default, enterprise
    # contracts switch it on with an `entitled` override (02_provision_customers.py)
    rates.append({
        "product_id": products[PROD_ENT_SUPPORT],
        "starting_at": LIST_START,
        "entitled": False,
        "rate_type": "PERCENTAGE",
        "price": ENT_SUPPORT_PERCENT,  # decimal fraction: 0.1 = 10%
    })
    c.v1.contracts.rate_cards.rates.add_many(rate_card_id=rate_card_id, rates=rates)
    print(f"  added {len(rates)} rates ({len(HARDWARE)} hardware SKUs + Pro Support + Enterprise Support %)")


def main():
    c = client()
    state = load_state()

    print("== 1/3 Billable metric")
    bm_compute = get_or_create_billable_metric(c)

    print("== 2/3 Products")
    products = {}
    products[PROD_COMPUTE] = get_or_create_product(c, PROD_COMPUTE, {
        "type": "USAGE",
        "billable_metric_id": bm_compute,
        "pricing_group_key": ["hardware"],
        "presentation_group_key": ["hardware"],  # one invoice line per machine type
        "tags": [TAG_COMPUTE],
    })
    products[PROD_PRO_SUPPORT] = get_or_create_product(c, PROD_PRO_SUPPORT, {
        "type": "SUBSCRIPTION",
        "tags": ["support"],
    })
    products[PROD_ENT_SUPPORT] = get_or_create_product(c, PROD_ENT_SUPPORT, {
        "type": "COMPOSITE",
        "composite_tags": [TAG_COMPUTE],  # % applies to everything tagged 'compute' (future SKUs included)
        "tags": ["support"],
    })
    products[PROD_TRIAL_CREDIT] = get_or_create_product(c, PROD_TRIAL_CREDIT, {
        "type": "FIXED",
    })
    products[PROD_COMMIT] = get_or_create_product(c, PROD_COMMIT, {
        "type": "FIXED",
    })

    print("== 3/3 Rate card")
    rate_card_id, created = get_or_create_rate_card(c)
    if created:
        add_rates(c, rate_card_id, products)
    else:
        print("  rates already added on a previous run; skipping addRates")

    #to easily locate/reuse objects we just created here, in the other scripts :
    state.update({
        "billable_metrics": {"compute": bm_compute},
        "products": products,
        "rate_card_id": rate_card_id,
        "rate_card_alias": RATE_CARD_ALIAS,
    })
    print("== Success!")
    save_state(state)
    print("\nCatalog ready. Next: 02_provision_customers.py")


if __name__ == "__main__":
    main()
