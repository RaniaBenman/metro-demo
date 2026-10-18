#!/usr/bin/env python3
"""
Step 4 - Send realistic compute usage for the four demo customers,
via the official Metronome Python SDK (metronome-sdk).

One event type ('compute_usage') for everything Replicate meters. Each event:
  seconds   billable duration (Replicate bills by the second)
  hardware  pricing dimension -> which rate applies (gpu-t4, gpu-a100-large, ...)
  workload  prediction | deployment | training   (breakdowns only)
  model     e.g. stability-ai/sdxl                (breakdowns only)
  id        Replicate's prediction / instance-hour id (traceability only)

Predictions send their active seconds; private deployments send one event per
instance-hour (3600 s), as an hourly summary.

Scenarios (list prices, before discounts / credits):
  self_serve   ~$12.59 of usage against a $10 trial credit -> the credit runs out,
               the trial alerts fire within minutes (Replicate's daily batch let users run on)
  pro_support  ~$1,803 of usage (+ $500 Pro Support)       -> the $1,500 budget alert fires
  prepaid      ~$5,375 at list -> ~$4,569 after 15% off, drawn from the $100k prepaid commit,
               + 10% Enterprise Support
  postpaid     ~$1,343 at list -> ~$1,141 after 15% off, counted toward the $100k minimum

Roadmap hardware: H100 (pro_support + prepaid) and L40S (pro_support) usage is ALSO sent, as
Replicate's platform would on day 0 of a hardware rollout. Neither has a rate on
the rate card yet, so it is not billed until the GPU is launched: H100 with
05_launch_gpu.py, L40S live in the Metronome UI during the demo.
Use --without-roadmap to leave it out.

Events are spread between each contract start and now; transaction_id is
deterministic, so re-running is safe (Metronome dedupes on it for 34 days).

API-SDK mapping (raw path -> SDK call):
  POST /v1/ingest -> client.v1.usage.ingest(usage=[...])   (max 100 events / request)

Docs:
  "Send usage events to /ingest"  https://docs.metronome.com/guides/events/send-usage-events
  "Usage events at scale"         https://docs.metronome.com/guides/events/high-volume-ingestion

Usage:
  ./run_single.sh 04_send_usage.py                  # all four customers
  ./run_single.sh 04_send_usage.py --only self_serve  # one customer
  ./run_single.sh 04_send_usage.py --print-only     # show expected totals, send nothing
"""

import argparse
import datetime as dt
import uuid

from metronome import APIStatusError

from replicate_common import (
    EVENT_TYPE, HARDWARE, ROADMAP_HARDWARE, client, load_state, now_utc, parse_iso,
)

# (hardware, workload, model, events, seconds per event)
SCENARIOS = {
    # Ada, free trial: $12.59 at list; the $10 trial credit pays the first $10, the ~$2.59 overage lands on her invoice at list (trips the 20%-left and exhausted alerts)
    "self_serve": [
        ("gpu-t4",           "prediction", "stability-ai/sdxl",               60,   20),
        ("gpu-a40-large",    "prediction", "black-forest-labs/flux-schnell", 120,   45),
        ("gpu-a100-large",   "prediction", "meta/meta-llama-3-70b-instruct",  40,  150),
    ],
    # Brightframe, pay-as-you-go at list: $1,803.38 of compute (trips the $1,500 spend alert) + $500/mo Pro Support billed in advance; H100 +$54.90 and L40S +$42.12 once launched
    "pro_support": [
        # private deployments: one event per instance-hour
        ("gpu-a40-large",    "deployment", "brightframe/product-shots",      300, 3600),
        ("gpu-a100-large",   "deployment", "brightframe/brand-llm",          200, 3600),
        # public model predictions
        ("gpu-t4",           "prediction", "stability-ai/sdxl",              300,   30),
        ("gpu-a40-small",    "prediction", "black-forest-labs/flux-schnell", 300,   60),
        # roadmap hardware, already running in beta
        ("gpu-h100",         "deployment", "brightframe/brand-llm-h100",      10, 3600),
        ("gpu-l40s",         "deployment", "brightframe/product-shots-l40s",  12, 3600),
    ],
    # Northwind, $100k prepaid commit: $5,374.80 at list = $4,568.58 at 15% off, drawn from the commit (~95% left, no overage); ~$457 Enterprise Support (10%) invoiced on top; L40S adds $149.18 and H100 $466.65 net once launched
    "prepaid": [
        ("gpu-a100-large",   "deployment", "northwind/video-captioner",      800, 3600),
        ("gpu-a40-large-8x", "training",   "northwind/house-style-lora",      60, 3600),
        ("gpu-a40-large",    "prediction", "black-forest-labs/flux-dev",     500,  240),
        ("cpu",              "prediction", "northwind/thumbnail-resizer",    500,   60),
        # roadmap hardware, already running in beta
        ("gpu-h100",         "deployment", "northwind/video-captioner-h100", 100, 3600),
        ("gpu-l40s",         "deployment", "northwind/video-captioner-l40s",  50, 3600),  # keep new rows last: earlier rows keep their transaction ids
    ],
    # Kepler, $100k postpaid minimum: $1,342.50 at list = ~$1,141 at 15% off, invoiced monthly and counted toward the minimum; ~$114 Enterprise Support (10%); shortfall trued up at term end
    "postpaid": [
        ("gpu-a100-small",   "deployment", "kepler/asset-gen-3d",            300, 3600),
        ("gpu-a40-large",    "prediction", "stability-ai/sdxl",             1000,  120),
        ("gpu-t4",           "prediction", "kepler/texture-upscaler",       2000,   30),
    ],
}

BATCH = 100  # Metronome ingest limit per request


def hourly_price(hw):
    return (HARDWARE.get(hw) or ROADMAP_HARDWARE[hw])[2]


def scenario(offering, with_roadmap):
    # e.g : self_serve -> [row1, row2, row3]
    # accumulate scenario row if its hardware key is supported/existing ... or if key doesnt exist but we've indicated that we're open to new/future hardware keys (with_roadmap)
    return [row for row in SCENARIOS[offering] if with_roadmap or row[0] in HARDWARE] 


def print_expectations(offering, name, with_roadmap):
    print(f"  Expected rating for {name} (list prices, USD):")
    print(f"    {'hardware':<18}{'workload':<12}{'events':>7}{'hours':>10}{'$/hour':>8}{'subtotal':>11}")
    priced = 0.0
    for hw, workload, _model, n, secs in scenario(offering, with_roadmap):
        hours = n * secs / 3600
        subtotal = hours * hourly_price(hw)
        note = "  <- billed once launched" if hw not in HARDWARE else ""
        if hw in HARDWARE:
            priced += subtotal
        print(f"    {hw:<18}{workload:<12}{n:>7}{hours:>10,.2f}{hourly_price(hw):>8.2f}{subtotal:>11,.2f}{note}")
    print(f"    {'TOTAL priced today':<45}{priced:>14,.2f}")

# offering can be "self_serve" or "pro_support", etc (see SCENARIOS)"
def build_events(offering, customer_ref, start_iso, with_roadmap):
    start = parse_iso(start_iso)
    end = now_utc() - dt.timedelta(minutes=5)  # never in the future
    span = max((end - start).total_seconds(), 60)
    scenario_rows = scenario(offering, with_roadmap)
    scenario_event_count = sum(n for _, _, _, n, _ in scenario_rows)

    events, index = [], 0
    for hw, workload, model, n, secs in scenario_rows:
        for _ in range(n):
            ts = start + dt.timedelta(seconds=span * (index + 1) / (scenario_event_count + 1))
            events.append({
                # deterministic transaction id -> idempotent re-runs
                "transaction_id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"replicate-demo-{offering}-{customer_ref}-{hw}-{index}")),
                "customer_id": customer_ref,  # ingest alias: Replicate's own account id, no Metronome id needed
                "event_type": EVENT_TYPE,
                "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                "properties": {
                    "seconds": str(secs),   # strings: Metronome uses exact decimals
                    "hardware": hw,
                    "workload": workload,
                    "model": model,
                    "id": f"{offering[:3]}-{index:06d}",
                },
            })
            index += 1
    # chronological order: balances burn down in the order usage happened
    events.sort(key=lambda e: e["timestamp"])
    return events


def main():
    parser = argparse.ArgumentParser(description="Send Replicate demo usage")
    parser.add_argument("--only", choices=list(SCENARIOS), default=None)
    parser.add_argument("--print-only", action="store_true", help="show expected totals, send nothing")
    parser.add_argument("--without-roadmap", action="store_true",
                        help="do not send H100 / L40S usage (hardware not on the rate card yet)")
    args = parser.parse_args()
    with_roadmap = not args.without_roadmap

    state = load_state()
    customers = state.get("customers", {})
    offerings = [args.only] if args.only else list(SCENARIOS)
    c = None if args.print_only else client()

    # offering can be "self_serve" or "pro_support", etc (see SCENARIOS)"
    for i, offering in enumerate(offerings, 1):
        customer = customers.get(offering)
        name = customer["name"] if customer else offering
        print(f"== {i}/{len(offerings)} {name}")
        print_expectations(offering, name, with_roadmap)
        if args.print_only:
            continue
        if not customer:
            raise SystemExit(f"No '{offering}' customer in state. Run 02_provision_customers.py first.")
        events = build_events(offering, customer["ingest_alias"], customer["starting_at"], with_roadmap)
        try:
            for b in range(0, len(events), BATCH):
                c.v1.usage.ingest(usage=events[b:b + BATCH])
        except APIStatusError as e:
            raise SystemExit(f"{offering}: HTTP {e.response.status_code}: {e.message}")
        print(f"  sent {len(events)} events in {(len(events) + BATCH - 1) // BATCH} request(s) (dedup key: transaction_id)")

    print("\nNext: wait ~5 minutes, then 07_check_state.py and 06_dashboard_links.py")


if __name__ == "__main__":
    main()
