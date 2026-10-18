"""
03 — The friction-free trial, made real-time (Pain #2).

GOAL
----
Replicate wants sign-up to stay friction-free — "try before you enter a credit
card" — but their systems measure credit usage once a day, so users blow past
the free allowance before anyone asks for a card. This script builds the
Metronome version:

  1. Register the trial custom-field keys (so trial objects are distinguishable
     in alerts, webhooks and reports).
  2. Create trial customer "Ada Lovelace".
  3. Create her trial contract on the public pay-per-second rate card with a
     $25 credit that expires in 14 days, scoped to GPU compute, burned first
     (priority 1). When the credit expires or is exhausted, the same contract
     keeps billing at list prices — the customer lands on pay-as-you-go with
     zero engineering action.
  4. Create three real-time threshold alerts (per Metronome's free-trial
     guide), evaluated the moment usage is ingested — not once a day:
       - 25% of trial credit remaining  -> "nudge" moment
       - 3 days left on the trial       -> time-based nudge
       - balance hits $0                -> the "ask for the card NOW" signal

POSITION IN THE DEMO NARRATIVE
------------------------------
Act 2. Screens: trial customer's Overview + Commits & credits tab (balance
moving in real time), Developer -> Notifications (the webhook events that
carry these signals to Replicate's app), and the draft invoice showing credit
drawdown vs. overage. This is the direct replacement for Replicate's daily
batch job.

BUSINESS MOTIVE
---------------
Every hour of delay between "credit exhausted" and "card on file" is pure
margin loss on GPU cost — and every over-generous silent overrun trains users
to expect free compute. Real-time balance + webhooks closes the leak at the
exact moment it happens, without adding friction at signup.

NOTE: only CREATE calls. Idempotent via state.json + uniqueness keys.
"""

import datetime as dt

import replicate_common as rc

NOW = dt.datetime.now(dt.timezone.utc).replace(minute=0, second=0, microsecond=0)
TRIAL_START = NOW - dt.timedelta(days=9)   # trial started 9 days ago...
TRIAL_END = TRIAL_START + dt.timedelta(days=rc.TRIAL_DAYS)  # ...so 5 days remain


def iso(t: dt.datetime) -> str:
    return t.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def main() -> None:
    client = rc.get_client()
    state = rc.load_state()
    if "rate_card_id" not in state:
        raise SystemExit("Run 02_rate_card.py first.")
    usd = state.get("usd_credit_type_id") or rc.usd_credit_type_id(client)

    # --- 1. Custom-field keys (idempotent-ish: duplicate addKey errors are OK)
    for entity, key in (("customer", "trial_started_at"),
                        ("contract", "contract_type"),
                        ("contract_credit", "trial")):
        try:
            client.v1.custom_fields.add_key(entity=entity, key=key, enforce_uniqueness=False)
            print(f"registered custom field {entity}.{key}")
        except Exception as e:  # already registered
            print(f"custom field {entity}.{key}: {type(e).__name__} (already exists — fine)")

    # --- 2. Trial customer ---------------------------------------------------
    if "trial_customer_id" not in state:
        cust = client.v1.customers.create(
            name=rc.TRIAL_CUSTOMER["name"],
            ingest_aliases=[rc.TRIAL_CUSTOMER["alias"]],
            custom_fields={"trial_started_at": iso(TRIAL_START), "trial_source": "self_serve"},
        )
        state["trial_customer_id"] = cust.id
        rc.save_state(state)
        print(f"created customer         {cust.id}  ({rc.TRIAL_CUSTOMER['name']})")

    # --- 3. Trial contract with expiring $25 credit --------------------------
    if "trial_contract_id" not in state:
        contract = client.v1.contracts.create(
            customer_id=state["trial_customer_id"],
            name="Free Trial ($25 / 14 days)",
            starting_at=iso(TRIAL_START),
            rate_card_id=state["rate_card_id"],
            uniqueness_key="replicate-trial-ada",
            custom_fields={"contract_type": "trial"},
            credits=[{
                "name": "Trial credit",
                "product_id": state["trial_credit_product_id"],
                "priority": 1,  # burn trial credit before any other balance
                "applicable_product_tags": [rc.GPU_TAG],
                "custom_fields": {"trial": "true", "trial_model": "expiring_credit"},
                "access_schedule": {
                    "credit_type_id": usd,
                    "schedule_items": [{
                        "amount": rc.TRIAL_CREDIT_USD * 100,  # $25 -> cents
                        "starting_at": iso(TRIAL_START),
                        "ending_before": iso(TRIAL_END),
                    }],
                },
            }],
        )
        state["trial_contract_id"] = contract.id
        rc.save_state(state)
        print(f"created trial contract   {contract.id}  ($25 credit, {iso(TRIAL_START)[:10]} → {iso(TRIAL_END)[:10]})")

    # --- 4. Real-time threshold alerts (evaluated on ingest, not nightly) ----
    if "trial_alerts" not in state:
        alerts = [
            # Nudge #1: 25% of the trial credit remains -> in-product "add a card soon"
            dict(name="Trial credit 25% remaining",
                 alert_type="low_remaining_contract_credit_percentage_reached",
                 threshold=25, uniqueness_key="replicate-trial-pct-25"),
            # Nudge #2: 3 days before the trial window closes
            dict(name="Trial ends in 3 days",
                 alert_type="low_remaining_days_for_contract_credit_segment_reached",
                 threshold=3, uniqueness_key="replicate-trial-days-3"),
            # Backstop: balance actually exhausted by usage -> gate further runs
            dict(name="Trial balance exhausted",
                 alert_type="low_remaining_contract_credit_and_commit_balance_reached",
                 threshold=0, uniqueness_key="replicate-trial-zero",
                 alert_specifiers=[{"custom_field_filters": [
                     {"entity": "ContractCredit", "key": "trial", "value": "true"}]}]),
        ]
        created = []
        for a in alerts:
            alert = client.v1.alerts.create(
                credit_type_id=usd, evaluate_on_create=False, **a)
            created.append({"name": a["name"], "id": alert.id})
            print(f"created alert            {alert.id}  ({a['name']})")
        state["trial_alerts"] = created
        rc.save_state(state)

    print("\nDone. Next: python3 04_enterprise_commit.py")


if __name__ == "__main__":
    main()
