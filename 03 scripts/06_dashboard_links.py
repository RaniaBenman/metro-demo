#!/usr/bin/env python3
"""
Step 6 - Get the customer-facing embeddable dashboards for the demo,
using the official Metronome Python SDK (metronome-sdk). READ-ONLY.

Answers pain #4 ("we cannot tell committed customers where they are without an
engineer pulling data from the database"): Metronome returns "a secure,
time-limited URL that can be embedded in an iframe", "a white-labeled billing
experience without building custom UI". Replicate drops it into its account page.

Prints (and saves to Z Misc/state.json under "dashboards"):
  prepaid      commits_and_credits   remaining commit, grant/deduction history, schedule
  prepaid      usage                 usage per hardware over the last 30/60/90 days
  postpaid     commits_and_credits   progress toward the $100k minimum
  self_serve   commits_and_credits   what's left of the trial credit
  pro_support  invoices              current draft + Pro Support invoice

The URLs are TIME-LIMITED: re-run this script just before taking screenshots and
again just before the demo.

API-SDK mapping (raw path -> SDK call):
  POST /v1/dashboards/getEmbeddableUrl -> client.v1.dashboards.get_embeddable_url(...)

Docs:
  "Build API-powered customer dashboards" (Embeddable dashboards)
      https://docs.metronome.com/guides/customers-billing/optimize-customer-experience/customer-dashboards-and-reporting
  "Get an embeddable customer dashboard"
      https://docs.metronome.com/api-reference/customers/get-an-embeddable-customer-dashboard
"""

from metronome import APIStatusError

from replicate_common import client, load_state, require, save_state

LINKS = [
    ("prepaid", "commits_and_credits"),
    ("prepaid", "usage"),
    ("self_serve", "commits_and_credits"),
    ("pro_support", "invoices"),
    ("postpaid", "commits_and_credits"),
]


def main():
    state = load_state()
    customers = require(state, "customers", "02_provision_customers.py")

    c = client()
    out = state.setdefault("dashboards", {})
    for i, (offering, dashboard) in enumerate(LINKS, 1):
        if offering not in customers:
            continue
        try:
            resp = c.v1.dashboards.get_embeddable_url(
                customer_id=customers[offering]["customer_id"],
                dashboard=dashboard,
            )
        except APIStatusError as e:
            raise SystemExit(f"{offering}/{dashboard}: HTTP {e.response.status_code}: {e.message}")
        url = resp.data.url
        out[f"{offering}:{dashboard}"] = url
        print(f"== {i}/{len(LINKS)} {customers[offering]['name']} / {dashboard}\n    {url}")

    save_state(state)
    print("\nOpen these in Chrome next to the Metronome app: this is what Replicate's customers would see.")


if __name__ == "__main__":
    main()
