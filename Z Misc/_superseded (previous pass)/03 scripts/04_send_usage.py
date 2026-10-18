#!/usr/bin/env python3
"""
Step 4 - Send realistic per-second compute usage for the three demo customers,
via the official Metronome Python SDK (metronome-sdk).

One event type ('compute_seconds') for everything Replicate meters. Each event carries:
  seconds   billable duration (Replicate bills by the second)
  hardware  pricing dimension -> which rate applies (gpu-t4, gpu-a100-large, ...)
  kind      prediction | deployment | training   (breakdowns only)
  model     e.g. black-forest-labs/flux-schnell  (breakdowns only)

Scenarios (list prices, before discounts / credits):
  trial       ~$12.59 of usage against a $10 trial credit
              -> Metronome flags the exhausted credit within minutes
                 (Replicate's daily batch let users run past it)
  paygo       ~$2,320 of usage + $500 Pro Support
  enterprise  ~$4,370 list -> ~$3,710 after 15% discount, drawn from the
              $33,333 year-1 commit segment, + 10% Enterprise Support

Events are spread between each contract start and now; transaction_id is
deterministic, so re-running is safe (Metronome dedupes on it).

API-SDK mapping (raw path -> SDK call):
  POST /v1/ingest -> client.v1.usage.ingest(usage=[...])   (max 100 events / request)

Usage:
  ./run_single.sh 04_send_usage.py                 # all three customers
  ./run_single.sh 04_send_usage.py --only trial    # one customer
  ./run_single.sh 04_send_usage.py --print-only    # show expected totals, send nothing
"""

import argparse
import datetime as dt
import uuid

from replicate_common import EVENT_TYPE, HARDWARE, client, load_state, now_utc, parse_iso

# (hardware, kind, model, events, seconds per event)
SCENARIOS = {
    "trial": [
        ("gpu-t4",         "prediction", "stability-ai/sdxl",               60,   20),
        ("gpu-a40-large",  "prediction", "black-forest-labs/flux-schnell", 120,   45),
        ("gpu-a100-large", "prediction", "meta/meta-llama-3-70b-instruct",  40,  150),
    ],
    "paygo": [
        # private deployments: one event per instance-hour
        ("gpu-a40-large",  "deployment", "lumen-labs/product-shots",       400, 3600),
        ("gpu-a100-large", "deployment", "lumen-labs/brand-llm",           250, 3600),
        # public model predictions
        ("gpu-t4",         "prediction", "stability-ai/sdxl",              300,   30),
        ("gpu-a40-small",  "prediction", "black-forest-labs/flux-schnell", 300,   60),
    ],
    "enterprise": [
        ("gpu-a100-large",   "deployment", "northwind/video-captioner",     600, 3600),
        ("gpu-a40-large-8x", "training",   "northwind/house-style-lora",     60, 3600),
        ("gpu-a40-large",    "prediction", "black-forest-labs/flux-dev",    500,  240),
        ("cpu",              "prediction", "northwind/thumbnail-resizer",   500,   60),
    ],
}

BATCH = 100  # Metronome ingest limit per request


def expected_cost_usd(key):
    rows, total = [], 0.0
    for hw, kind, model, n, secs in SCENARIOS[key]:
        subtotal = n * secs * HARDWARE[hw][1]
        rows.append((hw, kind, n, n * secs, subtotal))
        total += subtotal
    return rows, total


def build_events(key, customer_ref, start_iso):
    start = parse_iso(start_iso)
    end = now_utc() - dt.timedelta(minutes=5)  # never in the future
    span = max((end - start).total_seconds(), 60)
    total = sum(n for _, _, _, n, _ in SCENARIOS[key])

    events, index = [], 0
    for hw, kind, model, n, secs in SCENARIOS[key]:
        for _ in range(n):
            ts = start + dt.timedelta(seconds=span * (index + 1) / (total + 1))
            events.append({
                # deterministic transaction id -> idempotent re-runs
                "transaction_id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"replicate-demo-{key}-{customer_ref}-{index}")),
                "customer_id": customer_ref,  # ingest alias, no Metronome id needed
                "event_type": EVENT_TYPE,
                "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                "properties": {
                    "seconds": str(secs),
                    "hardware": hw,
                    "kind": kind,
                    "model": model,
                    "prediction_id": f"{key[:3]}-{index:05d}",  # optional dummy info
                },
            })
            index += 1
    # chronological order: balances burn down in the order usage happened
    events.sort(key=lambda e: e["timestamp"])
    return events


def print_expectations(key, name):
    rows, total = expected_cost_usd(key)
    print(f"  Expected rating for {name} (list prices, USD):")
    print(f"    {'hardware':<18}{'kind':<12}{'events':>7}{'seconds':>12}{'subtotal':>12}")
    for hw, kind, n, secs, subtotal in rows:
        print(f"    {hw:<18}{kind:<12}{n:>7}{secs:>12,}{subtotal:>12,.2f}")
    print(f"    {'TOTAL':<18}{'':<12}{'':>7}{'':>12}{total:>12,.2f}")


def main():
    parser = argparse.ArgumentParser(description="Send Replicate demo usage")
    parser.add_argument("--only", choices=sorted(SCENARIOS), default=None)
    parser.add_argument("--print-only", action="store_true", help="show expected totals, send nothing")
    args = parser.parse_args()

    state = load_state()
    customers = state.get("customers", {})
    keys = [args.only] if args.only else list(SCENARIOS)
    c = None if args.print_only else client()

    for i, key in enumerate(keys, 1):
        customer = customers.get(key)
        if not customer:
            raise SystemExit(f"No '{key}' customer in state. Run 02_provision_customers.py first.")
        print(f"== {i}/{len(keys)} {customer['name']}")
        print_expectations(key, customer["name"])
        if args.print_only:
            continue
        events = build_events(key, customer["ingest_alias"], customer["starting_at"])
        for b in range(0, len(events), BATCH):
            c.v1.usage.ingest(usage=events[b:b + BATCH])
        print(f"  sent {len(events)} events in {(len(events) + BATCH - 1) // BATCH} request(s) (dedup key: transaction_id)")

    print("\nNext: 05_add_machine_type.py (live in the demo) and 06_dashboard_links.py")


if __name__ == "__main__":
    main()
