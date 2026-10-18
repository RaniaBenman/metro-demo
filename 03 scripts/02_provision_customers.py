#!/usr/bin/env python3
"""
Step 2 - Provision Replicate's four demo customers, one per go-to-market motion,
using the official Metronome Python SDK (metronome-sdk).

  self_serve   "Ada Okafor (free trial)"
               sign-up flow: customer + contract from package alias `replicate-free-trial`,
               the self-serve package "Pay-as-you-go ($10 free trial, 30 days)"
               ($10 credit for 30 days, tagged trial=true, then list prices) -> pain #2 (trial leakage)
  pro_support  "Brightframe AI (pay-as-you-go + Pro Support)"
               customer + contract from package alias `replicate-paygo-pro-support`,
               the upsell package "Pay-as-you-go + Pro Support ($500/mo)"
               (list prices + $500/mo Pro Support subscription)     -> pain #3 (fixed-fee tier)
  prepaid      "Northwind Media (enterprise, prepaid commit)"
               3-year contract: $100,000 prepaid commit invoiced in 3 yearly installments,
               15% off list on all compute, Enterprise Support at 10% of compute
                                                                    -> pain #3 (% tier) + pain #4
  postpaid     "Kepler Games (enterprise, postpaid commit)"
               3-year contract: $100,000 minimum spend, usage billed monthly in arrears,
               true-up invoice at term end if spend falls short, same discount and % support
                                                                    -> pain #4, the other commit model

Self-serve customers are provisioned from PACKAGES (Replicate's sign-up flow only
needs the alias); enterprise customers get bespoke contracts (sales-led).

Re-running is safe: customers are reused by ingest alias, and a customer that
already has a contract is left as is.

API-SDK mapping (raw path -> SDK call):
  GET  /v1/customers?ingest_alias=                -> client.v1.customers.list(ingest_alias=...)
  POST /v1/customers                              -> client.v1.customers.create(...)
  POST /v2/contracts/list                         -> client.v2.contracts.list(customer_id=...)
  POST /v1/contracts/create                       -> client.v1.contracts.create(...)
  POST /v1/contracts/customerBalances/list        -> client.v1.contracts.list_balances(...)
  POST /v1/customFields/setValues                 -> client.v1.custom_fields.set_values(...)

Docs:
  "Free trials" / "Implement a free trial"
      https://docs.metronome.com/guides/pricing-packaging/billing-model-guides/free-trials/overview
      https://docs.metronome.com/guides/pricing-packaging/billing-model-guides/free-trials/implement-a-trial
  "Create packages"     https://docs.metronome.com/guides/implement-metronome/core-concepts/packages-overview
  "Launch an enterprise commit model"
      https://docs.metronome.com/guides/pricing-packaging/billing-model-guides/enterprise-commit
  "Apply credits and commits to contracts" (prepaid vs postpaid)
      https://docs.metronome.com/guides/pricing-packaging/apply-credits-and-commits/create-a-pre-paid-commit
  "Contract edits and overrides"
      https://docs.metronome.com/guides/pricing-packaging/make-pricing-changes/edit-or-override-a-contract

Usage (METRONOME_BEARER_TOKEN set; run 01_setup_catalog.py first):
  ./run_single.sh 02_provision_customers.py                     # all four customers, in the order below
  ./run_single.sh 02_provision_customers.py --only self_serve   # one customer

  --only   optional; provision only the customer on one offering. Expects one of:
             self_serve    Ada Okafor: self-serve package (pay-as-you-go, $10 free trial)
             pro_support   Brightframe AI: Pro Support package
             prepaid       Northwind Media: enterprise contract, prepaid commit
             postpaid      Kepler Games: enterprise contract, postpaid commit
           Default (flag omitted): all four.


--------UPGRADE------ A plain pay-as-you-go user upgrades to Pro on Oct 15
https://docs.metronome.com/guides/pricing-packaging/subscription/manage-subscription-lifecycle#upgrade-or-downgrade-a-subscription%E2%80%8B
Facilitate a contract transition by using the CREATE contract endpoint to
create a new contract from replicate-paygo-pro-support, starting Oct 15 on a whole hour, 
and specifying : {"type": "RENEWAL", "from_contract_id": <their self-serve contract>}. 


What happens:
- Oct 1–15 usage stays on the old contract. The transition "end-dates the trial contract at the paid contract's starting_at", so that usage is billed on the old contract's last usage invoice. I couldn't confirm from the docs exactly when that final invoice is issued.
- Usage from Oct 15 is priced on the new contract, which uses the same rate card and therefore the same prices. Its first usage invoice covers Oct 15 → Nov 1.
- Unused trial credit is lost: the transition "expires any unused balance".
- Nothing changes on Replicate's side: it's the same customer with the same identifier on events.

Note :
an alternative that keeps one contract: edit the existing contract to add the Pro Support subscription 
from Oct 15 (client.v2.contracts.edit(add_subscriptions=…), plus the entitlement override.
That needs contract editing to be enabled on the account. On the transition type: the SDK only lists RENEWAL, noting that values "may vary based on your client's configuration".

"""

import argparse
import datetime as dt

from metronome import APIStatusError

from replicate_common import (
    COMMIT_DISCOUNT_MULTIPLIER, COMMIT_TOTAL_USD, COMMIT_YEARS, CUSTOMERS,
    PROD_ENT_SUPPORT, PROD_POSTPAID_COMMIT, PROD_PREPAID_COMMIT, RATE_CARD_ALIAS,
    TAG_COMPUTE, TRIAL_CREDIT_FIELDS, SFDC_OP_ID,
    add_years, cents, client, customer_url, first_of_month_utc, floor_hour, iso,
    load_state, now_utc, require, save_state,
)

# Illustrative CRM ids: the contract keeps a pointer to the Salesforce opportunity.
SALESFORCE_OPPORTUNITY_IDS = {"prepaid": "006DEMO00000NWM001", "postpaid": "006DEMO00000KPL001"}


# --------------------------------------------------------------------------
# Customers and contracts
# --------------------------------------------------------------------------

def get_or_create_customer(c, persona, custom_fields=None):
    existing = list(c.v1.customers.list(ingest_alias=persona["alias"]))
    if existing:
        print(f"  reuse customer '{persona['name']}': {existing[0].id}")
        return existing[0].id
    payload = {"name": persona["name"], "ingest_aliases": [persona["alias"]]}
    if custom_fields:
        payload["custom_fields"] = custom_fields 
    # No billing provider configuration in this sandbox. In production:
    # Stripe for self-serve (charge_automatically), NetSuite for enterprise.
    customer = c.v1.customers.create(**payload).data
    print(f"  created customer '{persona['name']}': {customer.id}")
    return customer.id


def existing_contract(c, customer_id):
    contracts = list(c.v2.contracts.list(customer_id=customer_id).data)
    return contracts[0] if contracts else None


def create_contract(c, customer_id, label, payload):
    """contracts.create unless the customer already has a contract (safe re-runs).
    Returns (contract_id, starting_at ISO string)."""
    found = existing_contract(c, customer_id)
    if found:
        print(f"  reuse contract '{getattr(found, 'name', None) or label}': {found.id}")
        return found.id, iso(found.starting_at)
    try:
        contract = c.v1.contracts.create(customer_id=customer_id, **payload).data
    except APIStatusError as e:
        # The CRM pointer is optional: retry without it if this environment rejects it.
        if "salesforce_opportunity_id" in payload and "salesforce" in str(e.message).lower():
            print("  (salesforce_opportunity_id rejected in this environment; retrying without it)")
            payload = {k: v for k, v in payload.items() if k != "salesforce_opportunity_id"}
            contract = c.v1.contracts.create(customer_id=customer_id, **payload).data
        else:
            raise
    shown = payload.get("name") or f"from package alias '{payload.get('package_alias')}'"
    print(f"  created contract {shown}: {contract.id}")
    return contract.id, payload["starting_at"]

# just for hygiene
def ensure_trial_credit_tagged(c, customer_id):
    """Package credits pass their custom fields down to the contract credit. Check it,
    and set them if needed, because the account-wide trial alerts filter on them."""
    for balance in c.v1.contracts.list_balances(customer_id=customer_id, include_contract_balances=True):
        if getattr(balance, "type", None) != "CREDIT":
            continue
        fields = getattr(balance, "custom_fields", None) or {}
        if all(fields.get(k) == v for k, v in TRIAL_CREDIT_FIELDS.items()):
            print(f"    trial credit {balance.id} tagged {fields}")
        else:
            c.v1.custom_fields.set_values(entity="contract_credit", entity_id=balance.id,
                                          custom_fields=TRIAL_CREDIT_FIELDS)
            print(f"    tagged trial credit {balance.id} with {TRIAL_CREDIT_FIELDS}")
        return balance.id
    print("    WARNING: no credit found on the trial contract yet; re-run this script in a minute")
    return None


# --------------------------------------------------------------------------
# One builder per motion. Each returns (customer custom fields, contract payload, starting_at)
# --------------------------------------------------------------------------

def self_serve(state):
    # Ada signed up 3 days ago (hour-aligned, as Metronome requires), so the
    # usage in 04_send_usage.py has a window to fall in.
    start = floor_hour(now_utc() - dt.timedelta(days=3))
    customer_fields = {"trial_started_at": iso(start), "trial_source": "self_serve"}
    # Exactly what Replicate's sign-up flow would send: the package alias, nothing else.
    contract = {"package_alias": state["package_aliases"]["self_serve"], "starting_at": iso(start)}
    return customer_fields, contract, start


def pro_support(state):
    start = first_of_month_utc()
    contract = {"package_alias": state["package_aliases"]["pro_support"], "starting_at": iso(start)}
    return None, contract, start

#--------------------------------
def _enterprise_base(state, start, end, commit_model):
    products = state["products"]
    return {
        "rate_card_alias": RATE_CARD_ALIAS,
        "starting_at": iso(start),
        "ending_before": iso(end),
        "usage_statement_schedule": {"frequency": "MONTHLY", "day": "FIRST_OF_MONTH"},
        "custom_fields": {"contract_type": "enterprise", "commit_model": commit_model, "sfdc_opportunity_id": SFDC_OP_ID}, #declared in ustom_fields.add_key
        "overrides": [
            # negotiated discount: 15% off list on everything tagged 'compute' (future GPUs included)
            {
                "starting_at": iso(start), # *** TODO why not ending_before too ?
                "type": "MULTIPLIER",
                "multiplier": COMMIT_DISCOUNT_MULTIPLIER,
                "applicable_product_tags": [TAG_COMPUTE],
            },
            # switch on the percent-based support tier (not entitled on the rate card). or prefix with *([{...}])
            {
                "starting_at": iso(start),
                "product_id": products[PROD_ENT_SUPPORT], #Or another override block for the other support tier
                "entitled": True,
            },
        ],
    }
    '''
    # we could also include the code below v to the base payload ^
    # schedule professional services support during onboarding (if product added as shownin comment in 01)
        scheduled_charges=[{
            "product_id": state["onboarding_product_id"],
            "name": "Onboarding & solutions engineering (one-time)",
            "schedule": {
                "credit_type_id": usd,
                "schedule_items": [{
                    "amount": rc.ENT_ONBOARDING_FEE * 100,  # $5k -> cents
                    "timestamp": iso(ONBOARDING_AT),
                }],
            },
        }] if "onboarding_product_id" in state else [],
    '''


def prepaid(state): # ***TODO : name, uniqueness_key, net_payment_terms_days = 30
    start = first_of_month_utc() #*** TODO why 1st of month?
    end = add_years(start, COMMIT_YEARS)
    total = cents(COMMIT_TOTAL_USD)
    installment = total // COMMIT_YEARS
    installments = [installment] * (COMMIT_YEARS - 1) + [total - installment * (COMMIT_YEARS - 1)]
    custom_fields = None # or : {"salesforce_account_id": "001R000003AcmeAI", "segment": "enterprise"}
    contract = _enterprise_base(state, start, end, "prepaid")
    contract.update({
        "name": "Enterprise: $100k over 3 years (prepaid)",
        "salesforce_opportunity_id": SALESFORCE_OPPORTUNITY_IDS["prepaid"], #only works if Salesforce is connected to Metronome
        "commits": [{
            "type": "PREPAID",
            "name": "Committed spend: $100k over 3 years (prepaid)",
            "product_id": state["products"][PROD_PREPAID_COMMIT],
            "priority": 1,
            "applicable_product_tags": [TAG_COMPUTE],  # burns down on compute, future GPUs included
            "access_schedule": {
                "schedule_items": [
                    # $100,000 usable at any time over the 3 years, paid upfront in 3 yearly installments
                    {"amount": total, "starting_at": iso(start), "ending_before": iso(end)},
                ]
            },
            "invoice_schedule": {
                "schedule_items": [
                    # paid upfront in 3 yearly installments
                    {"timestamp": iso(add_years(start, year)), "amount": amount} for year, amount in enumerate(installments)
                ]
            },
            "rollover_fraction": 0.25,  # up to 25% rolls into a renewal
        }],
        # *** CHECKPOIMT
    })

    '''
    # in the prepaid payload above ^, we could instead have the schedule below v for a
    # multi-year schedule / Ramped drawdown schedule (what the company may consume each year)
                "schedule_items": [
                    {"amount": 2_500_000, "starting_at": iso(DEAL_START), "ending_before": iso(Y1_END)},  # $25k Y1
                    {"amount": 3_500_000, "starting_at": iso(Y1_END),     "ending_before": iso(Y2_END)},  # $35k Y2
                    {"amount": 4_000_000, "starting_at": iso(Y2_END),     "ending_before": iso(Y3_END)},  # $40k Y3
                ]
    '''
    return custom_fields, contract, start


def postpaid(state):
    start = first_of_month_utc()
    end = add_years(start, COMMIT_YEARS)
    total = cents(COMMIT_TOTAL_USD)
    custom_fields = None # or : {"salesforce_account_id": "001R000003AcmeAI", "segment": "enterprise"}
    contract = _enterprise_base(state, start, end, "postpaid")
    contract.update({
        "name": "Enterprise: $100k over 3 years (postpaid minimum)",
        "salesforce_opportunity_id": SALESFORCE_OPPORTUNITY_IDS["postpaid"], #only works if Salesforce is connected to Metronome
        "commits": [{
            "type": "POSTPAID",
            "name": "Minimum spend: $100k over 3 years (postpaid)",
            "product_id": state["products"][PROD_POSTPAID_COMMIT],
            "priority": 1,
            "applicable_product_tags": [TAG_COMPUTE],
            "access_schedule": {
                "schedule_items": [
                    # same as prepaid
                    {"amount": total, "starting_at": iso(start), "ending_before": iso(end)},
                ]
            },
            # usage is invoiced monthly in ARREARS (see base commit definition) and counts toward 
            # the $100k : a true-up invoice for any shortfall is issued at the end of the term :
            "invoice_schedule": {
                "schedule_items": [
                    {"timestamp": iso(end), "amount": total}
                ]
            },
        }],
    })
    return custom_fields, contract, start


BUILDERS = {"self_serve": self_serve, "pro_support": pro_support, "prepaid": prepaid, "postpaid": postpaid}


def build_parser():
    parser = argparse.ArgumentParser(description="Provision Replicate's demo customers")
    parser.add_argument("--only", choices=list(BUILDERS), default=None,
                        help="Provision only the customer on this offering (default: all four)")
    return parser


def main():
    args = build_parser().parse_args()
    state = load_state()
    require(state, "products", "01_setup_catalog.py")
    require(state, "package_aliases", "01_setup_catalog.py")

    c = client()
    offerings = [args.only] if args.only else list(BUILDERS)
    state.setdefault("customers", {})

    for i, offering in enumerate(offerings, 1):
        persona = CUSTOMERS[offering]
        print(f"== {i}/{len(offerings)} {persona['name']}")
        customer_fields, contract_payload, _start = BUILDERS[offering](state)
        try:
            customer_id = get_or_create_customer(c, persona, customer_fields)
            contract_id, starting_at = create_contract(c, customer_id, offering, contract_payload)

            # just a hygiene check
            if offering == "self_serve":   # the only package with a trial credit. we can add pro package if includes trial credit to check for hygiene
                ensure_trial_credit_tagged(c, customer_id)

        except APIStatusError as e:
            raise SystemExit(f"{offering}: HTTP {e.response.status_code}: {e.message}")
        state["customers"][offering] = {
            "name": persona["name"],
            "customer_id": customer_id,
            "ingest_alias": persona["alias"],
            "contract_id": contract_id,
            "starting_at": starting_at,
        }
        print(f"    {customer_url(customer_id)}")

    save_state(state)
    print("\nDone. Next: 03_create_alerts.py")


if __name__ == "__main__":
    main()
