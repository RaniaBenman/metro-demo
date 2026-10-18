#!/usr/bin/env python3
"""
Step 5 - Launch a new machine type: ONE rate on the rate card,
using the official Metronome Python SDK (metronome-sdk).

This is the answer to pain #1 ("adding a machine type involves two engineering
teams and takes weeks"). Because `hardware` is a pricing dimension of the single
"Compute hours" product:
  - no new billable metric, no new product, no contract edit, no code change
  - every contract on the rate card picks the new price up immediately
  - the enterprise 15% discount, the commit drawdown and the 10% Enterprise
    Support fee apply automatically: they target the `compute` TAG, not a SKU list
  - usage the platform already sent for this hardware (04_send_usage.py) is rated
    on the open draft invoices as soon as the rate exists, because the rate starts
    on launch day (default: first day of the current month)

Defaults: hardware from Replicate's roadmap list (replicate_common.ROADMAP_HARDWARE).
  ./run_single.sh 05_launch_gpu.py --hardware gpu-l40s     # before/after screenshots
  ./run_single.sh 05_launch_gpu.py --hardware gpu-h100     # fallback for the live demo moment ****
  ./run_single.sh 05_launch_gpu.py --hardware gpu-h200 --starting-at 2026-11-01T00:00:00Z
                                                           # schedule a launch in advance

Options:
  --name, --price-per-hour   override the display name / list price ($/hour)
  --starting-at              launch date (ISO 8601, hour-aligned). Default: 1st of this month
  --send-usage               also send 10 fresh instance-hours for the pay-as-you-go customer
  --print-only               show the rate that would be added, change nothing

API-SDK mapping (raw path -> SDK call):
  POST /v1/contract-pricing/rate-cards/getRates -> client.v1.contracts.rate_cards.rates.list(...)
  POST /v1/contract-pricing/rate-cards/addRate  -> client.v1.contracts.rate_cards.rates.add(...)
  POST /v1/ingest                               -> client.v1.usage.ingest(...)

Docs:
  "Create and manage rate cards" (dimensional pricing, scheduled rate changes)
      https://docs.metronome.com/guides/implement-metronome/core-concepts/create-manage-rate-cards
  "Launch new pricing"   https://docs.metronome.com/guides/pricing-packaging/make-pricing-changes/make-a-pricing-change
  "How Metronome invoices work" (changes are reflected on open invoices)
      https://docs.metronome.com/guides/implement-metronome/core-concepts/how-invoicing-works
"""

import argparse
import datetime as dt
import uuid

from metronome import APIStatusError

from replicate_common import (
    EVENT_TYPE, HARDWARE, PROD_COMPUTE, RATE_CARD_NAME, ROADMAP_HARDWARE,
    cents, client, first_of_month_utc, iso, load_state, now_utc, parse_iso, require, save_state,
)


def build_parser():
    parser = argparse.ArgumentParser(description="Launch a machine type on Replicate's rate card")
    parser.add_argument("--hardware", default="gpu-l40s", help="hardware SKU as sent in events (default: gpu-l40s)")
    parser.add_argument("--name", default=None, help="display name (default: from the roadmap list)")
    parser.add_argument("--price-per-hour", type=float, default=None, help="list price in USD per hour")
    parser.add_argument("--starting-at", default=None, help="launch date, ISO 8601 (default: 1st of this month)")
    parser.add_argument("--send-usage", action="store_true", help="send 10 fresh hours for the Pro Support customer (Brightframe AI)")
    parser.add_argument("--print-only", action="store_true", help="show the call, change nothing")
    return parser


def resolve(args):
    known = ROADMAP_HARDWARE.get(args.hardware) or HARDWARE.get(args.hardware)
    name = args.name or (known[0] if known else args.hardware)
    price = args.price_per_hour if args.price_per_hour is not None else (known[2] if known else None)
    if price is None:
        raise SystemExit(f"Unknown hardware '{args.hardware}': pass --price-per-hour.")
    start = parse_iso(args.starting_at) if args.starting_at else first_of_month_utc()
    if start.minute or start.second or start.microsecond:
        raise SystemExit("--starting-at must be on an hour boundary (e.g. 2026-11-01T00:00:00Z).")
    return name, price, start


def rate_exists(c, rate_card_id, product_id, hardware, at):
    for r in c.v1.contracts.rate_cards.rates.list(rate_card_id=rate_card_id, at=at):
        if r.product_id == product_id and (r.pricing_group_values or {}).get("hardware") == hardware:
            return True
    return False


def send_fresh_usage(c, state, hardware):
    pro = state.get("customers", {}).get("pro_support")
    if not pro:
        raise SystemExit("No pro_support customer in state. Run 02_provision_customers.py first.")
    base = now_utc() - dt.timedelta(hours=11)
    events = [{
        "transaction_id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"replicate-demo-launch-{hardware}-{i}")),
        "customer_id": pro["ingest_alias"],
        "event_type": EVENT_TYPE,
        "timestamp": (base + dt.timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "properties": {"seconds": "3600", "hardware": hardware, "workload": "deployment",
                       "model": f"brightframe/launch-{hardware}", "id": f"launch-{i:03d}"},
    } for i in range(10)]
    c.v1.usage.ingest(usage=events)
    print(f"    sent 10 x 1h '{hardware}' deployment events for {pro['name']}")


def main():
    args = build_parser().parse_args()
    name, price, start = resolve(args)
    state = load_state()
    rate_card_id = require(state, "rate_card_id", "01_setup_catalog.py")
    product_id = require(state, "products", "01_setup_catalog.py")[PROD_COMPUTE]

    rate = {
        "rate_card_id": rate_card_id,
        "product_id": product_id,
        "starting_at": iso(start),
        "entitled": True,
        "rate_type": "FLAT",
        "price": cents(price),                         # USD cents per hour
        "pricing_group_values": {"hardware": args.hardware},
    }
    when = "today (backdated to launch day)" if start <= now_utc() else f"scheduled for {iso(start)}"
    print(f"== Launching '{name}' ({args.hardware}) at ${price:.2f}/hour "
          f"(${price / 3600:.6f}/sec) on '{RATE_CARD_NAME}', effective {when}")
    print(f"    {rate}")
    if args.print_only:
        return

    c = client()
    try:
        if rate_exists(c, rate_card_id, product_id, args.hardware, at=max(start, now_utc())):
            print("    a rate for this hardware is already on the rate card: nothing to do")
        else:
            c.v1.contracts.rate_cards.rates.add(**rate)
            print("    rate added: live for every contract on this rate card, discounts and commits included")
        state.setdefault("launched_hardware", {})[args.hardware] = {
            "name": name, "price_per_hour": price, "starting_at": iso(start)}
        if args.send_usage:
            send_fresh_usage(c, state, args.hardware)
    except APIStatusError as e:
        raise SystemExit(f"HTTP {e.response.status_code}: {e.message}")

    save_state(state)
    print("\nOpen the rate card and the customers' draft invoices: the new line is there.")


if __name__ == "__main__":
    main()
