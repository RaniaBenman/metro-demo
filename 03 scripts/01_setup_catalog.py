#!/usr/bin/env python3
"""
Step 1 - Build Replicate's pricing catalog in Metronome,
using the official Metronome Python SDK (metronome-sdk).

Creates (re-running reuses what already exists, matched by name / key):
  - custom field keys   that tag trial credits and contracts (see replicate_common.CUSTOM_FIELD_KEYS)
  - ONE billable metric "Compute seconds"  SUM of `seconds` on `compute_usage` events,
                                           group keys: hardware | model | workload
  - ONE usage product   "Compute hours"    priced per `hardware` (pricing group key),
                                           seconds -> hours by quantity conversion
  - support products    "Pro Support"                          SUBSCRIPTION (fixed monthly fee)
                        "Enterprise Support (10% of compute)"  COMPOSITE (% of everything tagged `compute`)
  - fixed products      trial credit, prepaid commit, postpaid commit true-up
  - ONE rate card       "Replicate list prices": 7 hardware rates + Pro Support + Enterprise Support
  - TWO packages        "Pay-as-you-go ($10 free trial, 30 days)" alias replicate-free-trial
                            self-serve sign-up: trial credit first, then list prices
                        "Pay-as-you-go + Pro Support ($500/mo)"   alias replicate-paygo-pro-support
                            the support-tier upsell

Design points (pain #1, "adding a machine type takes two teams and weeks"):
  hardware is a pricing DIMENSION, not a product: a new machine type is one new
  rate on the rate card (05_launch_gpu.py or the UI). No new metric, product,
  contract or code change. Discounts, commits and the % support fee target the
  `compute` TAG, so they cover future hardware automatically.

API-SDK mapping (raw path -> SDK call):
  POST /v1/customFields/listKeys                 -> client.v1.custom_fields.list_keys(...)
  POST /v1/customFields/addKey                   -> client.v1.custom_fields.add_key(...)
  GET  /v1/billable-metrics                      -> client.v1.billable_metrics.list()
  POST /v1/billable-metrics/create               -> client.v1.billable_metrics.create(...)
  POST /v1/contract-pricing/products/list        -> client.v1.contracts.products.list()
  POST /v1/contract-pricing/products/create      -> client.v1.contracts.products.create(...)
  POST /v1/contract-pricing/rate-cards/list      -> client.v1.contracts.rate_cards.list()
  POST /v1/contract-pricing/rate-cards/create    -> client.v1.contracts.rate_cards.create(...)
  POST /v1/contract-pricing/rate-cards/getRates  -> client.v1.contracts.rate_cards.rates.list(...)
  POST /v1/contract-pricing/rate-cards/addRates  -> client.v1.contracts.rate_cards.rates.add_many(...)
  POST /v1/packages/list                         -> client.v1.packages.list()
  POST /v1/packages/create                       -> client.v1.packages.create(...)

Docs:
  "Create products"               https://docs.metronome.com/guides/implement-metronome/core-concepts/create-products-contracts
  "Create and manage rate cards"  https://docs.metronome.com/guides/implement-metronome/core-concepts/create-manage-rate-cards
  "Billing for provisioned throughput" (GPU-seconds priced per GPU-hour via quantity conversion)
      https://docs.metronome.com/guides/pricing-packaging/billing-model-guides/provisioned-throughput
  "Create packages"               https://docs.metronome.com/guides/implement-metronome/core-concepts/packages-overview


"""

from metronome import APIStatusError

from replicate_common import (
    BM_COMPUTE, CUSTOM_FIELD_KEYS, ENT_SUPPORT_PERCENT, EVENT_TYPE, HARDWARE,
    PKG_PRO_SUPPORT_ALIAS, PKG_PRO_SUPPORT_NAME, PKG_SELF_SERVE_ALIAS, PKG_SELF_SERVE_NAME, PRICE_LIST_START,
    PROD_COMPUTE, PROD_ENT_SUPPORT, PROD_POSTPAID_COMMIT, PROD_PREPAID_COMMIT,
    PROD_PRO_SUPPORT, PROD_TRIAL_CREDIT, PRO_SUPPORT_MONTHLY_USD, RATE_CARD_ALIAS,
    RATE_CARD_NAME, SECONDS_PER_HOUR, TAG_COMPUTE, TAG_SUPPORT, TRIAL_CREDIT_FIELDS,
    TRIAL_CREDIT_USD, TRIAL_DAYS,
    cents, client, find_by_name, get_id, load_state, now_utc, save_state,
)


def ensure_custom_field_keys(c):
    entities = sorted({entity for entity, _ in CUSTOM_FIELD_KEYS})
    existing = {(k.entity, k.key) for k in c.v1.custom_fields.list_keys(entities=entities)}
    for entity, key in CUSTOM_FIELD_KEYS:
        if (entity, key) in existing:
            print(f"  reuse custom field key {entity}.{key}")
            continue
        c.v1.custom_fields.add_key(entity=entity, key=key, enforce_uniqueness=False)
        print(f"  created custom field key {entity}.{key}")


#---------------------
def get_or_create_billable_metric(c):
    existing = find_by_name(c.v1.billable_metrics.list(limit=100), BM_COMPUTE)
    if existing:
        print(f"  reuse billable metric '{BM_COMPUTE}': {get_id(existing)}")
        return get_id(existing)
    resp = c.v1.billable_metrics.create(
        name=BM_COMPUTE,
        event_type_filter={"in_values": [EVENT_TYPE]},
        # a property must be filtered with `exists` to be usable as a group key
        property_filters=[
            {"name": "seconds", "exists": True},
            {"name": "hardware", "exists": True},
            {"name": "model", "exists": True},
            {"name": "workload", "exists": True},
        ],
        aggregation_type="SUM",
        aggregation_key="seconds",
        # - 'hardware' is the pricing dimension (one rate per machine type)
        # - 'model' and 'workload' (prediction | deployment | training) are kept for
        #   usage breakdowns; they never change the price
        group_keys=[["hardware"], ["model"], ["workload"]],
    )
    print(f"  created billable metric '{BM_COMPUTE}': {resp.data.id}")
    return resp.data.id


#---------------------
def get_or_create_product(c, name, payload):
    existing = find_by_name(c.v1.contracts.products.list(), name)
    if existing:
        print(f"  reuse product '{name}': {get_id(existing)}")
        return get_id(existing)
    resp = c.v1.contracts.products.create(name=name, **payload)
    print(f"  created product '{name}': {resp.data.id}")
    return resp.data.id


#---------------------
def get_or_create_rate_card(c):
    # body={}: this endpoint 400s ('Unknown error parsing request body') when
    # the POST carries no JSON body at all, so send an explicit empty object.
    existing = find_by_name(c.v1.contracts.rate_cards.list(body={}), RATE_CARD_NAME)
    if existing:
        print(f"  reuse rate card '{RATE_CARD_NAME}': {get_id(existing)}")
        return get_id(existing)
    resp = c.v1.contracts.rate_cards.create(
        name=RATE_CARD_NAME,
        description="Replicate list prices: compute per hardware-hour (metered per second) + support tiers.",
        aliases=[{"name": RATE_CARD_ALIAS}],
    )
    print(f"  created rate card '{RATE_CARD_NAME}': {resp.data.id}")
    return resp.data.id


def wanted_rates(products):
    rates = []
    # Pain 1 - Add machine = new dim,no code
    # one FLAT rate per machine type, on the single compute product (USD cents per hour)
    for sku, (_display, _usd_per_sec, usd_per_hour) in HARDWARE.items():
        rates.append({
            "product_id": products[PROD_COMPUTE],
            "starting_at": PRICE_LIST_START,
            "entitled": True,
            "rate_type": "FLAT",
            "price": cents(usd_per_hour),
            "pricing_group_values": {"hardware": sku},#**
        })
    # fixed-fee support tier: $500 / month, billed only on contracts that subscribe to it
    rates.append({
        "product_id": products[PROD_PRO_SUPPORT],
        "starting_at": PRICE_LIST_START,
        "entitled": False,
        "rate_type": "FLAT",
        "price": cents(PRO_SUPPORT_MONTHLY_USD),
        "billing_frequency": "MONTHLY",
    })
    # percent-based support tier: 10% of compute spend. Not entitled by default:
    # enterprise contracts switch it on with an `entitled` override (02_provision_customers.py)
    rates.append({
        "product_id": products[PROD_ENT_SUPPORT],
        "starting_at": PRICE_LIST_START,
        "entitled": False,
        "rate_type": "PERCENTAGE",
        "price": ENT_SUPPORT_PERCENT,  # decimal fraction: 0.1 = 10%
    })
    return rates


def rate_key(product_id, pricing_group_values):
    return product_id, tuple(sorted((pricing_group_values or {}).items()))

# checks what (prepared) rates havent been added yet, then submits those that havent
def ensure_rates(c, rate_card_id, products):
    """Add every wanted rate that is not on the card yet (safe to re-run; never
    touches rates added later, like a launched GPU)."""
    current = {
        rate_key(r.product_id, r.pricing_group_values)
        for r in c.v1.contracts.rate_cards.rates.list(rate_card_id=rate_card_id, at=now_utc())
    }
    missing = [r for r in wanted_rates(products)
               if rate_key(r["product_id"], r.get("pricing_group_values")) not in current]
    if not missing:
        print("  all rates already on the rate card")
        return
    c.v1.contracts.rate_cards.rates.add_many(rate_card_id=rate_card_id, rates=missing)
    print(f"  added {len(missing)} rate(s) to '{RATE_CARD_NAME}'")

#---------------------
def get_or_create_package(c, name, payload):
    existing = find_by_name(c.v1.packages.list(), name)
    if existing:
        print(f"  reuse package '{name}': {get_id(existing)}")
        return get_id(existing)
    resp = c.v1.packages.create(name=name, rate_card_alias=RATE_CARD_ALIAS, **payload)
    print(f"  created package '{name}': {resp.data.id}")
    return resp.data.id


def self_serve_package(products):
    # Self-serve sign-up = plain pay-as-you-go that starts with the free trial.
    # The allowance AND the time window live on one credit: "a credit with an
    # access schedule bounds both at once". No contract end date: when the credit
    # expires, usage is simply rated at list price (pay-as-you-go).
    return {
        "aliases": [{"name": PKG_SELF_SERVE_ALIAS}],
        "contract_name": "Pay-as-you-go",
        # each billing period running from the 1st of the calendar month instead of sign-up date (CONTRACT_START)
        # --> usage is billed in arrears
        "usage_statement_schedule": {"frequency": "MONTHLY", "day": "FIRST_OF_MONTH"}, # 
        "credits": [{
            "name": f"Free trial credit (${TRIAL_CREDIT_USD:.0f}, {TRIAL_DAYS} days)",
            "product_id": products[PROD_TRIAL_CREDIT],
            "priority": 1,                          # burned before anything else
            "applicable_product_tags": [TAG_COMPUTE],
            "custom_fields": TRIAL_CREDIT_FIELDS,   # lets ONE alert target every trial credit
            "access_schedule": {
                "schedule_items": [{
                    "amount": cents(TRIAL_CREDIT_USD),
                    "starting_at_offset": {"value": 0, "unit": "DAYS"},
                    "duration": {"value": TRIAL_DAYS, "unit": "DAYS"},
                }]
            },
        }],
    }


def pro_support_package(products):
    # The support-tier upsell: pay-as-you-go at list price + the fixed-fee support tier, billed in advance.
    return {
        "aliases": [{"name": PKG_PRO_SUPPORT_ALIAS}],
        "contract_name": "Pay-as-you-go + Pro Support",
        "net_payment_terms_days": 0,
        "usage_statement_schedule": {"frequency": "MONTHLY", "day": "FIRST_OF_MONTH"},
        "subscriptions": [{
            "name": "Pro Support",
            "collection_schedule": "ADVANCE",
            "initial_quantity": 1,
            "proration": {"invoice_behavior": "BILL_IMMEDIATELY", "is_prorated": True},
            "subscription_rate": {"billing_frequency": "MONTHLY", "product_id": products[PROD_PRO_SUPPORT]},
            "billing_cycle_config": {"invoice_placement": "ON_SCHEDULED_INVOICE"},
        }],
        # we could also add a "credits": [{}] object here to give free trial credit like we did in plain paygo
         # Pro Support is not entitled on the rate card : switch it ON for contracts from this package
        "overrides": [{
            "override_specifiers": [{"product_id": products[PROD_PRO_SUPPORT]}],  # WHAT: which product it applies to
            "starting_at_offset": {"unit": "DAYS", "value": 0},                   # WHEN: from the contract's first day
            "entitled": True,                                                     # CHANGE: switch it on
        }],
    }


#---------------------
def print_price_list():
    print("\n  Replicate list prices now on the rate card (compute):")
    print(f"    {'hardware':<18}{'name':<28}{'$/sec':>10}{'$/hour':>9}")
    for sku, (display, per_sec, per_hour) in HARDWARE.items():
        print(f"    {sku:<18}{display:<28}{per_sec:>10.6f}{per_hour:>9.2f}")


def main():
    c = client()
    state = load_state()

    try:
        print("== 1/5 Custom field keys")
        ensure_custom_field_keys(c)

        print("== 2/5 Billable metric")
        bm_compute = get_or_create_billable_metric(c)

        print("== 3/5 Products")
        products = {
            #A.
            PROD_COMPUTE: get_or_create_product(c, PROD_COMPUTE, {
                "type": "USAGE",
                "billable_metric_id": bm_compute,
                "pricing_group_key": ["hardware"],
                "presentation_group_key": ["hardware"],   # one invoice line per machine type
                # events carry seconds; price and invoice in hours (exact: $/hr = $/sec x 3600)
                "quantity_conversion": {"conversion_factor": SECONDS_PER_HOUR, "operation": "DIVIDE", "name": "hours"},
                "tags": [TAG_COMPUTE],
            }),

            # B. Pain 3 - Support tier
            #    (fixed recurring fee)
            PROD_PRO_SUPPORT: get_or_create_product(c, PROD_PRO_SUPPORT, {
                "type": "SUBSCRIPTION",
                "tags": [TAG_SUPPORT],
            }),
            #    (percent of GPU spend)
            PROD_ENT_SUPPORT: get_or_create_product(c, PROD_ENT_SUPPORT, {
                "type": "COMPOSITE",
                "composite_tags": [TAG_COMPUTE],   # % of everything tagged 'compute', future GPUs included
                "tags": [TAG_SUPPORT],
            }),
            #   OPTIONALLY : we can also have a (professional services / Onboarding & Solutions Engineering) tier, as a fixed one-time charge product --> TYPE : FIXED 

            # C.
            PROD_TRIAL_CREDIT: get_or_create_product(c, PROD_TRIAL_CREDIT, {"type": "FIXED"}),
            PROD_PREPAID_COMMIT: get_or_create_product(c, PROD_PREPAID_COMMIT, {"type": "FIXED"}),
            PROD_POSTPAID_COMMIT: get_or_create_product(c, PROD_POSTPAID_COMMIT, {"type": "FIXED"}),
        }

        print("== 4/5 Rate card")
        rate_card_id = get_or_create_rate_card(c)
        ensure_rates(c, rate_card_id, products)

        print("== 5/5 Packages (self-serve provisioning: sign-up = 1 customer + 1 contract from an alias)")
        packages = {
            "self_serve": get_or_create_package(c, PKG_SELF_SERVE_NAME, self_serve_package(products)),
            "pro_support": get_or_create_package(c, PKG_PRO_SUPPORT_NAME, pro_support_package(products)),
        }
    except APIStatusError as e:
        raise SystemExit(f"HTTP {e.response.status_code}: {e.message}")

    # to easily locate/reuse the objects created here, in the other scripts:
    state.update({
        "billable_metrics": {"compute": bm_compute},
        "products": products,
        "rate_card_id": rate_card_id,
        "rate_card_alias": RATE_CARD_ALIAS,
        "packages": packages,
        "package_aliases": {"self_serve": PKG_SELF_SERVE_ALIAS, "pro_support": PKG_PRO_SUPPORT_ALIAS},
    })
    print_price_list()
    print("\n== Success!")
    save_state(state)
    print("Catalog ready. Next: 02_provision_customers.py")


if __name__ == "__main__":
    main()
