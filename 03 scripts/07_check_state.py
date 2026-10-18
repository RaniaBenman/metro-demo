#!/usr/bin/env python3
"""
Step 7 - Check the demo state, using the official Metronome Python SDK
(metronome-sdk). READ-ONLY: changes nothing in Metronome.

For each demo customer, prints:
  - commits and credits with their remaining balance (real time)
  - invoices (draft + scheduled) with their line items
  - threshold notifications and their status (ok / in_alarm / evaluating)
and saves the same data to "Z Misc/state_snapshot.json" for the demo script.

API-SDK mapping (raw path -> SDK call):
  POST /v1/contracts/customerBalances/list   -> client.v1.contracts.list_balances(...)
  GET  /v1/customers/{id}/invoices           -> client.v1.customers.invoices.list(...)
  POST /v1/customer-alerts/list              -> client.v1.customers.alerts.list(...)

Docs:
  "Track the remaining balance of a credit or commit"
      https://docs.metronome.com/guides/customers-billing/optimize-customer-experience/get-remaining-balance
  "Threshold notifications"
      https://docs.metronome.com/guides/customers-billing/set-up-notifications/threshold-notifications
"""

import json
import os

from metronome import APIStatusError

from replicate_common import STATE_PATH, client, load_state, require


def usd(cents_value):
    return f"${(cents_value or 0) / 100:,.2f}"


def balances(c, customer_id):
    rows = []
    for b in c.v1.contracts.list_balances(customer_id=customer_id, include_contract_balances=True,
                                          include_balance=True):
        items = getattr(getattr(b, "access_schedule", None), "schedule_items", None) or []
        rows.append({
            "name": getattr(b, "name", None) or b.product.name,
            "type": b.type,
            "total": sum(i.amount for i in items),
            "balance": getattr(b, "balance", None),
            "custom_fields": getattr(b, "custom_fields", None) or {},
        })
    return rows


def invoices(c, customer_id):
    rows = []
    for inv in c.v1.customers.invoices.list(customer_id=customer_id):
        rows.append({
            "type": inv.type,
            "status": inv.status,
            "total": inv.total,
            "start": inv.start_timestamp.isoformat() if inv.start_timestamp else None,
            "issued_at": inv.issued_at.isoformat() if inv.issued_at else None,
            "line_items": [{
                "name": li.name,
                "group": (li.pricing_group_values or {}).get("hardware") or li.group_value,
                "quantity": li.quantity,
                "unit_price": getattr(li, "unit_price", None),
                "total": li.total,
                "commit_type": li.commit_type,
            } for li in inv.line_items],
        })
    return rows


def alerts(c, customer_id):
    return [{"name": a.alert.name, "status": a.customer_status}
            for a in c.v1.customers.alerts.list(customer_id=customer_id)]


def main():
    state = load_state()
    customers = require(state, "customers", "02_provision_customers.py")
    c = client()

    snapshot = {}
    for offering, customer in customers.items():
        cid = customer["customer_id"]
        print(f"\n=== {customer['name']}  ({cid})")
        try:
            snap = {"balances": balances(c, cid), "invoices": invoices(c, cid), "alerts": alerts(c, cid)}
        except APIStatusError as e:
            raise SystemExit(f"{offering}: HTTP {e.response.status_code}: {e.message}")
        snapshot[offering] = snap

        for b in snap["balances"]:
            print(f"  {b['type']:<8} {b['name']:<55} balance {usd(b['balance']):>13} / {usd(b['total'])}")
        for inv in snap["invoices"]:
            if inv["status"] not in ("DRAFT", "FINALIZED"):
                continue
            print(f"  invoice {inv['type']:<10} {inv['status']:<10} total {usd(inv['total']):>12}  (period start {inv['start']})")
            for li in inv["line_items"]:
                qty = f"{li['quantity']:,.2f}" if isinstance(li["quantity"], (int, float)) else "-"
                print(f"      - {li['name']:<45} {str(li['group'] or ''):<18} qty {qty:>10}  {usd(li['total']):>12}")
        for a in snap["alerts"]:
            print(f"  alert   {a['status'] or '-':<11} {a['name']}")

    path = os.path.join(os.path.dirname(STATE_PATH), "state_snapshot.json")  # next to state.json
    with open(path, "w") as f:
        json.dump(snapshot, f, indent=2, default=str)
    print(f"\nsnapshot saved -> {os.path.abspath(path)}")


if __name__ == "__main__":
    main()
