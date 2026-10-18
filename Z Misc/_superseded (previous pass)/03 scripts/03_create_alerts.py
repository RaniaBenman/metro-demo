#!/usr/bin/env python3
"""
Step 3 - Create the threshold notifications (alerts) that replace Replicate's
once-a-day credit check, using the official Metronome Python SDK (metronome-sdk).

Run this BEFORE 04_send_usage.py: alerts then flip to IN_ALARM as usage lands,
which is exactly the story told in the demo.

  trial       "Trial credit almost used"  ($2 left)   -> prompt for a credit card
              "Trial credit exhausted"    ($0 left)   -> gate further runs
  paygo       "Monthly spend over $2,500"             -> expansion signal for sales
  enterprise  "Commit balance under $25,000"          -> renewal / upsell signal

Metronome evaluates threshold notifications at least every 3 minutes and fires
"within 5 minutes of the usage triggering the breach of the threshold being
ingested"; delivery is a signed webhook (retried for up to 48h).

Thresholds are in the credit type's unit, USD cents here (the docs' example
"$100 spend threshold reached" uses threshold 10000).

Scoping: alerts are created per demo customer to keep the sandbox clean.
In production Replicate would create ONE account-wide trial alert (no
customer_id) scoped to trial credits, which then covers every new sign-up.

API-SDK mapping (raw path -> SDK call):
  POST /v1/alerts/create -> client.v1.alerts.create(...)

Docs:
  "Create and manage notifications"
      https://docs.metronome.com/guides/customers-billing/set-up-notifications/create-and-manage-notifications
  "Create an alert"  https://docs.metronome.com/api-reference/alerts/create-an-alert
  "Webhooks"         https://docs.metronome.com/guides/platform-configuration/setup-webhooks
"""

from metronome import ConflictError

from replicate_common import cents, client, load_state, save_state

# persona -> [(alert_type, name, threshold in cents)]
ALERTS = {
    "trial": [
        ("low_remaining_contract_credit_balance_reached", "Trial credit almost used ($2 left)", cents(2)),
        ("low_remaining_contract_credit_balance_reached", "Trial credit exhausted ($0 left)", cents(0)),
    ],
    "paygo": [
        ("monthly_invoice_total_spend_threshold_reached", "Monthly spend over $2,500", cents(2_500)),
    ],
    "enterprise": [
        ("low_remaining_commit_balance_reached", "Commit balance under $25,000", cents(25_000)),
    ],
}


def main():
    state = load_state()
    customers = state.get("customers")
    if not customers:
        raise SystemExit("Run 02_provision_customers.py first.")

    c = client()
    created = state.setdefault("alerts", {})
    steps = [(k, a) for k in ALERTS for a in ALERTS[k] if k in customers]
    for i, (key, (alert_type, name, threshold)) in enumerate(steps, 1):
        customer_id = customers[key]["customer_id"]
        print(f"== {i}/{len(steps)} {customers[key]['name']}: {name}")
        try:
            resp = c.v1.alerts.create(
                alert_type=alert_type,
                name=name,
                threshold=threshold,
                customer_id=customer_id,
                evaluate_on_create=True,
                uniqueness_key=f"replicate-demo-{key}-{alert_type}-{int(threshold)}",
            )
            created[name] = resp.data.id
            print(f"    created: {resp.data.id}")
        except ConflictError:
            print("    already exists (uniqueness_key), skipping")

    save_state(state)
    print("\nNext: 04_send_usage.py")


if __name__ == "__main__":
    main()
