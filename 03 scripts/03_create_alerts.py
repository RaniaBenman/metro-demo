#!/usr/bin/env python3
"""
Step 3 - Create the threshold notifications that replace Replicate's once-a-day
credit check, using the official Metronome Python SDK (metronome-sdk).

Run this BEFORE 04_send_usage.py: the notifications then move to IN_ALARM as
usage lands, which is exactly the story told in the demo.

Account-wide (no customer_id = applies to every customer, existing and future):
  "Trial credit: 20% left"        low_remaining_contract_credit_percentage_reached
                                  -> nudge: prompt for a credit card
  "Trial credit: exhausted"       low_remaining_contract_credit_and_commit_balance_reached ($0)
                                  -> gate: stop free GPU time
  "Trial ends in 3 days"          low_remaining_days_for_contract_credit_segment_reached
  The two balance alerts only look at credits tagged trial=true (custom field set
  by the self-serve package's trial credit), so ONE configuration covers every new sign-up.
  "Commit: 25% remaining"         low_remaining_commit_percentage_reached
                                  -> renewal / expansion signal for the account team

Timing (docs): "The threshold is evaluated at least once every three minutes.
Notifications will fire within 5 minutes of the usage triggering the breach of
the threshold being ingested." Delivery is a signed webhook, retried up to 48h.

Thresholds: USD amounts in cents (`10000` = $100.00); percentage alerts take the
percentage REMAINING (25 fires when 25% is left); days alerts take days.

API-SDK mapping (raw path -> SDK call):
  POST /v1/alerts/create -> client.v1.alerts.create(...)

Docs:
  "Threshold notifications"  https://docs.metronome.com/guides/customers-billing/set-up-notifications/threshold-notifications
  "Manage your customer lifecycle with Metronome notifications"
      https://docs.metronome.com/guides/customers-billing/set-up-notifications/create-and-manage-notifications
  "Create alert specifiers"  https://docs.metronome.com/guides/customers-billing/set-up-notifications/create-alert-specifiers
  "Implement a free trial"   https://docs.metronome.com/guides/pricing-packaging/billing-model-guides/free-trials/implement-a-trial
"""

from metronome import APIStatusError, ConflictError

from replicate_common import TRIAL_CREDIT_FIELDS, cents, client, load_state, require, save_state

# the tag the self-serve package's trial credit carries (TRIAL_CREDIT_FIELDS)
TRIAL_FILTER = {"entity": "ContractCredit", "key": "trial", "value": TRIAL_CREDIT_FIELDS["trial"]}

# USD (cents), required on the balance, percentage and spend alerts; fixed ID from the "List pricing units" API reference
USD_CREDIT_TYPE_ID = "2714e483-4ff1-48e4-9e25-ac732e8f24f2" #Predefined by Metronome

#TODO : check alert types doc
def alerts(customers):
    """(state key, create kwargs) for every notification of the demo."""
    out = [
        ("trial_days_3", {
            "name": "Trial ends in 3 days",
            "alert_type": "low_remaining_days_for_contract_credit_segment_reached",
            "threshold": 3,
            "uniqueness_key": "replicate-demo-trial-days-3",
        }),
        ("trial_pct_20", {
            "name": "Trial credit: 20% left (nudge for a credit card)",
            "alert_type": "low_remaining_contract_credit_percentage_reached",
            "threshold": 20,
            "credit_type_id": USD_CREDIT_TYPE_ID,
            "custom_field_filters": [TRIAL_FILTER],
            "uniqueness_key": "replicate-demo-trial-credit-pct-20",
        }),
        ("trial_zero", {
            "name": "Trial credit: exhausted (gate free usage)",
            "alert_type": "low_remaining_contract_credit_and_commit_balance_reached",
            "threshold": 0,
            "credit_type_id": USD_CREDIT_TYPE_ID,
            "alert_specifiers": [{"custom_field_filters": [TRIAL_FILTER]}],
            "uniqueness_key": "replicate-demo-trial-credit-zero",
        }),
        ("commit_pct_25", {
            "name": "Commit: 25% remaining (renewal / expansion signal)",
            "alert_type": "low_remaining_commit_percentage_reached",
            "threshold": 25,
            "credit_type_id": USD_CREDIT_TYPE_ID,
            "uniqueness_key": "replicate-demo-commit-pct-25",
        }),
    ]
    '''
    Customer-specific: Brightframe AI sets a budget in Replicate's UI
    when a monthly spend over $1,500 --> spend_threshold_reached triggered
    '''
    if "pro_support" in customers:
        out.append(("pro_support_spend_1500", {
            "name": "Brightframe AI: monthly spend over $1,500",
            "alert_type": "spend_threshold_reached",
            "threshold": cents(1_500),
            "credit_type_id": USD_CREDIT_TYPE_ID,
            "customer_id": customers["pro_support"]["customer_id"],
            "uniqueness_key": "replicate-demo-pro-support-spend-1500",
        }))
    return out


def main():
    state = load_state()
    customers = require(state, "customers", "02_provision_customers.py")

    c = client()
    created = state.setdefault("alerts", {})
    steps = alerts(customers)
    for i, (alert_key, kwargs) in enumerate(steps, 1):
        scope = "one customer" if "customer_id" in kwargs else "all customers"
        print(f"== {i}/{len(steps)} {kwargs['name']} ({scope})")
        try:
            # evaluate_on_create: customers already past the threshold alarm immediately
            resp = c.v1.alerts.create(evaluate_on_create=True, **kwargs)
            created[alert_key] = resp.data.id
            print(f"    created: {resp.data.id}")
        except ConflictError:
            print("    already exists (uniqueness_key), skipping")
        except APIStatusError as e:
            raise SystemExit(f"{alert_key}: HTTP {e.response.status_code}: {e.message}")

    save_state(state)
    print("\nNext: 04_send_usage.py")


if __name__ == "__main__":
    main()
