#!/usr/bin/env python3
"""
Step 5 - Launch a new machine type: ONE rate on the rate card,
using the official Metronome Python SDK (metronome-sdk).

This is the answer to pain #1 ("adding a machine type involves two
engineering teams and takes weeks"). Because `hardware` is a pricing
dimension of the single "Compute (per second)" product:
  - no new billable metric, no new product, no contract edits
  - every existing contract picks the new price up from the rate card
  - the enterprise 15% discount and 10% support fee apply automatically
    (they target the 'compute' tag, not a list of SKUs)
  - usage for the new SKU can be sent the moment the rate exists

Default: Nvidia H100 at Replicate's current list price ($0.001525/sec, $5.49/hr).

Options:
  --sample-usage   also send 10 one-hour H100 deployment events for the
                   paygo customer, so the new line shows up on their draft invoice
  --print-only     show the rate that would be added, change nothing

API-SDK mapping (raw path -> SDK call):
  POST /v1/contract-pricing/rate-cards/addRate -> client.v1.contracts.rate_cards.rates.add(...)
  POST /v1/ingest                              -> client.v1.usage.ingest(...)

Docs:
  "Create products" (pricing group keys: "set different prices for the same product")
      https://docs.metronome.com/pricing-packaging/create-products-contracts/
"""

import argparse
import datetime as dt
import uuid

from replicate_common import (
    EVENT_TYPE, LIST_START, NEW_HARDWARE_DEFAULT, PROD_COMPUTE,
    cents, client, load_state, now_utc, save_state,
)


def main():
    sku, display, price = NEW_HARDWARE_DEFAULT
    parser = argparse.ArgumentParser(description="Add a machine type to Replicate's rate card")
    parser.add_argument("--hardware", default=sku, help=f"hardware SKU as sent in events (default: {sku})")
    parser.add_argument("--name", default=display, help=f"display name (default: {display})")
    parser.add_argument("--price-per-sec", type=float, default=price, help=f"USD per second (default: {price})")
    parser.add_argument("--sample-usage", action="store_true", help="send 10 sample hours for the paygo customer")
    parser.add_argument("--print-only", action="store_true", help="show the call, change nothing")
    args = parser.parse_args()

    state = load_state()
    if not state.get("rate_card_id"):
        raise SystemExit("Run 01_setup_catalog.py first.")

    rate = {
        "rate_card_id": state["rate_card_id"],
        "product_id": state["products"][PROD_COMPUTE],
        "starting_at": LIST_START,
        "entitled": True,
        "rate_type": "FLAT",
        "price": cents(args.price_per_sec),
        "pricing_group_values": {"hardware": args.hardware},
    }
    print(f"== 1/2 Adding '{args.name}' ({args.hardware}) at ${args.price_per_sec}/sec "
          f"(${args.price_per_sec * 3600:.2f}/hr)")
    print(f"    {rate}")
    if args.print_only:
        return

    c = client()
    c.v1.contracts.rate_cards.rates.add(**rate)
    print("    rate added: live for every contract on this rate card")
    state.setdefault("added_hardware", {})[args.hardware] = args.price_per_sec

    if args.sample_usage:
        paygo = state.get("customers", {}).get("paygo")
        if not paygo:
            raise SystemExit("No paygo customer in state. Run 02_provision_customers.py first.")
        print(f"== 2/2 Sending 10 x 1h {args.hardware} deployment events for {paygo['name']}")
        base = now_utc() - dt.timedelta(hours=11)
        events = [{
            "transaction_id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"replicate-demo-new-hw-{args.hardware}-{i}")),
            "customer_id": paygo["ingest_alias"],
            "event_type": EVENT_TYPE,
            "timestamp": (base + dt.timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "properties": {"seconds": "3600", "hardware": args.hardware,
                           "kind": "deployment", "model": "lumen-labs/brand-llm-h100"},
        } for i in range(10)]
        c.v1.usage.ingest(usage=events)
        print(f"    sent 10 events (~${10 * 3600 * args.price_per_sec:,.2f} at list)")
    else:
        print("== 2/2 skipped (pass --sample-usage to send usage on the new SKU)")

    save_state(state)


if __name__ == "__main__":
    main()
