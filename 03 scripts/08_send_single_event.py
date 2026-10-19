#!/usr/bin/env python3
"""
Step 8 (on demand) - Send ONE compute usage event for an existing demo customer,
via the official Metronome Python SDK (metronome-sdk).

Defaults: one hour of `gpu-999` deployment time for Kepler Games (the postpaid
commit customer), at 12:00 UTC on Oct 11, 2026.

What to expect with `gpu-999`: the event is ingested and counted by the billable
metric "Compute seconds", but the rate card has no rate for that hardware, so it is
metered and NOT billed: no invoice line, nothing counted toward Kepler's $100k
minimum. It shows in Usage events and in Kepler's usage. Adding a rate for it later
(in the UI, or 05_launch_gpu.py --hardware gpu-999 --price-per-hour <price>) prices
it on the open invoice, like the H100 and L40S launches.

Re-running is safe: the transaction_id is derived from the event's content, and
Metronome ignores duplicates for 34 days.

Usage (METRONOME_BEARER_TOKEN set; run 02_provision_customers.py first):
  ./run_single.sh 08_send_single_event.py --print-only     # show the event, send nothing
  ./run_single.sh 08_send_single_event.py                  # send it
  ./run_single.sh 08_send_single_event.py --offering prepaid --hardware gpu-h100 \
      --timestamp 2026-10-12T09:00:00Z --seconds 1800 --workload prediction

Options (defaults in brackets):
  --offering    self_serve | pro_support | prepaid | postpaid   [postpaid = Kepler Games]
  --hardware    hardware id sent in the event                    [gpu-999]
  --timestamp   ISO 8601, at most 34 days in the past            [2026-10-11T12:00:00Z]
  --seconds     billable duration in seconds                     [3600]
  --workload    prediction | deployment | training               [deployment]
  --model       model name, for usage breakdowns                 [manual-test/single-event]
  --print-only  show the event and send nothing

API-SDK mapping (raw path -> SDK call):
  POST /v1/ingest -> client.v1.usage.ingest(usage=[...])

Docs:
  "Send usage events to /ingest"
      https://docs.metronome.com/guides/events/send-usage-events
  Ingest API reference: "Historical events can be backdated up to 34 days" and
  "Duplicate events are automatically detected and ignored".
"""

import argparse
import datetime as dt

from metronome import APIStatusError

from replicate_common import (
    CUSTOMERS, HARDWARE, WORKLOADS, client, compute_usage_event, iso, load_state, now_utc,
    parse_iso, require,
)

DEFAULT_OFFERING = "postpaid"              # Kepler Games, the postpaid commit customer
DEFAULT_HARDWARE = "gpu-999"
DEFAULT_TIMESTAMP = "2026-10-11T12:00:00Z"
DEFAULT_SECONDS = 3600
DEFAULT_WORKLOAD = "deployment"
DEFAULT_MODEL = "manual-test/single-event"
BACKFILL_LIMIT = dt.timedelta(days=34)     # ingest API reference: "backdated up to 34 days"


def build_parser():
    parser = argparse.ArgumentParser(description="Send one compute usage event for a demo customer")
    parser.add_argument("--offering", choices=list(CUSTOMERS), default=DEFAULT_OFFERING,
                        help="demo customer, by offering (default: postpaid = Kepler Games)")
    parser.add_argument("--hardware", default=DEFAULT_HARDWARE, help="hardware id sent in the event")
    parser.add_argument("--timestamp", default=DEFAULT_TIMESTAMP,
                        help="when the usage happened, ISO 8601, at most 34 days ago")
    parser.add_argument("--seconds", type=int, default=DEFAULT_SECONDS, help="billable duration in seconds")
    parser.add_argument("--workload", choices=WORKLOADS, default=DEFAULT_WORKLOAD)
    parser.add_argument("--model", default=DEFAULT_MODEL, help="model name, used only for usage breakdowns")
    parser.add_argument("--print-only", action="store_true", help="show the event, send nothing")
    return parser


def parse_event_time(timestamp_text):
    """ISO 8601 text -> timezone-aware datetime inside Metronome's backfill window."""
    event_time = parse_iso(timestamp_text)
    if event_time.tzinfo is None:  # no offset given: read it as UTC
        event_time = event_time.replace(tzinfo=dt.timezone.utc)
    now = now_utc()
    if event_time > now:
        raise SystemExit(f"--timestamp {timestamp_text} is in the future.")
    if now - event_time > BACKFILL_LIMIT:
        raise SystemExit(f"--timestamp {timestamp_text} is more than 34 days ago: Metronome only "
                         "accepts events backdated up to 34 days.")
    return event_time


def main():
    args = build_parser().parse_args()
    if args.seconds <= 0:
        raise SystemExit("--seconds must be a positive number of seconds.")
    event_time = parse_event_time(args.timestamp)

    state = load_state()
    customers = require(state, "customers", "02_provision_customers.py")
    if args.offering not in customers:
        raise SystemExit(f"No '{args.offering}' customer in state. Run 02_provision_customers.py first.")
    customer = customers[args.offering]

    event = compute_usage_event(
        # every field that defines the event goes into the seed: re-sending the same command is
        # ignored as a duplicate, while any different event gets its own transaction_id
        transaction_seed=(f"replicate-demo-single-event-{args.offering}-{customer['ingest_alias']}-"
                          f"{args.hardware}-{iso(event_time)}-{args.seconds}-{args.workload}-{args.model}"),
        customer_ref=customer["ingest_alias"],
        timestamp=event_time,
        seconds=args.seconds,
        hardware=args.hardware,
        workload=args.workload,
        model=args.model,
        event_ref=f"single-{args.hardware}-{event_time:%Y%m%dT%H%M%S}",
    )

    print(f"== One {args.seconds} s '{args.hardware}' {args.workload} event for {customer['name']} "
          f"at {event['timestamp']}")
    print(f"    {event}")
    launched_hardware = state.get("launched_hardware", {})
    if args.hardware not in HARDWARE and args.hardware not in launched_hardware:
        print(f"    note: no rate for '{args.hardware}' in the price list or in the launches recorded in "
              "state.json: the event will be metered but not billed until a rate exists.")
    if args.print_only:
        return

    try:
        client().v1.usage.ingest(usage=[event])
    except APIStatusError as error:
        raise SystemExit(f"HTTP {error.response.status_code}: {error.message}")
    print(f"    sent (transaction_id {event['transaction_id']}). Sending the same event again is "
          "ignored as a duplicate.")


if __name__ == "__main__":
    main()
