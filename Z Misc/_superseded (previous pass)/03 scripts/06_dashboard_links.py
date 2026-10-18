#!/usr/bin/env python3
"""
Step 6 - Get the customer-facing embeddable dashboards for the demo,
using the official Metronome Python SDK (metronome-sdk).

Answers pain #4 ("we cannot tell committed customers where they are
without an engineer pulling data from the database"): Metronome returns a
URL that Replicate drops into an iframe on its account page. No database
query, no engineer.

Prints (and saves to Z Misc/state.json):
  enterprise  commits_and_credits  remaining commit, burn-down ledger, segment dates
  enterprise  usage                usage per hardware over the last 30/60/90 days
  trial       credits              what's left of the trial allowance
  paygo       invoices             current draft + history (incl. Pro Support line)

This script only READS from Metronome (it creates no billing objects).

API-SDK mapping (raw path -> SDK call):
  POST /v1/dashboards/getEmbeddableUrl -> client.v1.dashboards.get_embeddable_url(...)

Docs:
  "Build API-powered customer dashboards"
      https://docs.metronome.com/guides/customers-billing/optimize-customer-experience/customer-dashboards-and-reporting
"""

from replicate_common import client, load_state, save_state

LINKS = [
    ("enterprise", "commits_and_credits"),
    ("enterprise", "usage"),
    ("trial", "credits"),
    ("paygo", "invoices"),
]


def main():
    state = load_state()
    customers = state.get("customers")
    if not customers:
        raise SystemExit("Run 02_provision_customers.py first.")

    c = client()
    out = state.setdefault("dashboards", {})
    for i, (key, dashboard) in enumerate(LINKS, 1):
        if key not in customers:
            continue
        resp = c.v1.dashboards.get_embeddable_url(
            customer_id=customers[key]["customer_id"],
            dashboard=dashboard,
        )
        url = resp.data.url
        out[f"{key}:{dashboard}"] = url
        print(f"== {i}/{len(LINKS)} {customers[key]['name']} / {dashboard}\n    {url}")

    save_state(state)
    print("\nOpen these in Chrome next to the Metronome app: they are what Replicate's customers would see.")


if __name__ == "__main__":
    main()
