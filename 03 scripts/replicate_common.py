"""
Shared helpers and pricing constants for the Replicate x Metronome demo scripts.

Every script uses the official Metronome Python SDK (`metronome-sdk`,
`from metronome import Metronome`).

Auth: the SDK reads METRONOME_BEARER_TOKEN by default; we also fall back to
METRONOME_API_TOKEN. Create the token in the Metronome app, in the Sandbox
environment, under Developer -> API tokens.
  https://docs.metronome.com/api-reference/authentication

Money: for USD, every monetary amount in the Metronome API is in cents
("1000 = $10.00"), percentages are decimal fractions ("0.1 for 10%").
  https://docs.metronome.com/guides/pricing-packaging/apply-credits-and-commits/create-a-pre-paid-commit
  https://docs.metronome.com/api-reference/rate-cards/add-a-rate
"""

import datetime as dt
import json
import os
import sys
import uuid # used by optional script 08

from metronome import Metronome

HERE = os.path.dirname(os.path.abspath(__file__))  # .../Metronome/05 Strategy/03 scripts

# Pipeline state shared by all step scripts (single JSON file, kept in "Z Misc").
STATE_PATH = os.environ.get(
    "METRONOME_STATE_PATH",
    os.path.join(HERE, "..", "Z Misc", "state.json"),
)

APP_URL = "https://app.metronome.com/sandbox"  # links printed for the demo prep


def client() -> Metronome:
    """SDK client. Token: METRONOME_BEARER_TOKEN, else METRONOME_API_TOKEN."""
    token = os.environ.get("METRONOME_BEARER_TOKEN") or os.environ.get("METRONOME_API_TOKEN")
    if not token:
        sys.exit(
            "ERROR: set METRONOME_BEARER_TOKEN in your environment.\n"
            "Create a token in the Metronome app (Sandbox) under Developer -> API tokens."
        )
    return Metronome(bearer_token=token)


def find_by_name(items, name, name_field="name"):
    """Match an SDK list item by name (SDK models expose attributes; some
    list responses nest the current value under `current`)."""
    for item in items:
        current_name = getattr(item, name_field, None)
        if current_name is None:
            current = getattr(item, "current", None)
            if current is not None:
                current_name = getattr(current, name_field, None)
        if current_name == name:
            return item
    return None


def get_id(item):
    """id from an SDK model or a plain dict."""
    if isinstance(item, dict):
        return item["id"]
    return item.id


def load_state():
    """IDs written by earlier scripts, or {} if none saved yet."""
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH) as f:
            return json.load(f)
    return {}


def save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)
    print(f"state saved -> {os.path.abspath(STATE_PATH)}")


def require(state, key, script):
    """Stop with a clear message when an earlier step has not been run."""
    if not state.get(key):
        raise SystemExit(f"Missing '{key}' in {os.path.abspath(STATE_PATH)}. Run {script} first.")
    return state[key]


# ---------------------------------------------------------------------------
# Time helpers. Contract, credit and commit boundaries must be hour-aligned:
# "... is required to be on an hour boundary (e.g. 1:00, not 1:30)".
#   https://docs.metronome.com/guides/pricing-packaging/billing-model-guides/free-trials/overview
# ---------------------------------------------------------------------------

def iso(d):
    """datetime -> Metronome's millisecond ISO format (UTC)."""
    return d.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def now_utc():
    return dt.datetime.now(dt.timezone.utc)


def first_of_month_utc(d=None):
    d = d or now_utc()
    return d.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def floor_hour(d):
    return d.replace(minute=0, second=0, microsecond=0)


def add_years(d, years):
    try:
        return d.replace(year=d.year + years)
    except ValueError:  # Feb 29 -> Feb 28
        return d.replace(year=d.year + years, day=28)


def parse_iso(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def cents(dollars):
    """USD -> USD cents, Metronome's unit for USD amounts."""
    return int(round(dollars * 100))


# ---------------------------------------------------------------------------
# Replicate's pricing (all list prices from the brief / replicate.com/pricing)
# ---------------------------------------------------------------------------

# ONE event type for all hardware time. `hardware` selects the price; `workload`
# (prediction | deployment | training) and `model` are only used for breakdowns
# (usage API, dashboards).
EVENT_TYPE = "compute_usage"
WORKLOADS = ("prediction", "deployment", "training") # used by optional script 08

#used by optional script 08 :
def compute_usage_event(transaction_seed, customer_ref, timestamp, seconds, hardware, workload, model, event_ref):
    """One `compute_usage` event, in the shape the billable metric counts: it only
    matches events carrying all four properties (seconds, hardware, workload, model).

    transaction_seed: text that identifies the event; hashed into transaction_id,
                      Metronome's idempotency key (duplicates are ignored for 34 days).
    customer_ref:     Replicate's own account id, registered as the customer's ingest alias.
    timestamp:        timezone-aware datetime of the usage.
    """
    return {
        "transaction_id": str(uuid.uuid5(uuid.NAMESPACE_URL, transaction_seed)),
        "customer_id": customer_ref,
        "event_type": EVENT_TYPE,
        "timestamp": iso(timestamp),
        "properties": {
            "seconds": str(seconds),  # strings: Metronome uses exact decimals
            "hardware": hardware,
            "workload": workload,
            "model": model,
            "id": event_ref,
        },
    }

# Today's price list, as given in the brief: sku -> (display name, $/second, $/hour).
# $/hour is exactly $/second x 3600, so pricing per hour is pricing per second.
HARDWARE = {
    "cpu":              ("CPU",                       0.000100,  0.36), # we dont send/use the descriptions to/in metronome
    "gpu-t4":           ("Nvidia T4 GPU",             0.000225,  0.81),
    "gpu-a40-small":    ("Nvidia A40 GPU",            0.000575,  2.07),
    "gpu-a40-large":    ("Nvidia A40 (Large) GPU",    0.000725,  2.61),
    "gpu-a100-small":   ("Nvidia A100 (40GB) GPU",    0.001150,  4.14),
    "gpu-a100-large":   ("Nvidia A100 (80GB) GPU",    0.001400,  5.04),
    "gpu-a40-large-8x": ("8x Nvidia A40 (Large) GPU", 0.005800, 20.88),
}

# Hardware Replicate is adding next (list prices published today on
# replicate.com/pricing). NOT on the rate card at setup:
#   gpu-l40s  -> launched by 05_launch_gpu.py (before/after screenshots)
#   gpu-h100  -> launched live in the Metronome UI during the demo
# 04_send_usage.py already sends usage for both, as the platform would on day 0.
ROADMAP_HARDWARE = {
    "gpu-h100":    ("Nvidia H100 GPU",     0.001525,  5.49),
    "gpu-l40s":    ("Nvidia L40S GPU",     0.000975,  3.51),
    "gpu-h200":    ("Nvidia H200 GPU",     0.001525,  5.49),
    "gpu-h100-8x": ("8x Nvidia H100 GPU",  0.012200, 43.92),
}

SECONDS_PER_HOUR = 3600  # quantity conversion: meter seconds, price hours

# Catalog names (what shows on invoices and in the Metronome UI)
BM_COMPUTE = "Compute seconds"
PROD_COMPUTE = "Compute hours"
PROD_PRO_SUPPORT = "Pro Support"
PROD_ENT_SUPPORT = "Enterprise Support (10% of compute)"
PROD_TRIAL_CREDIT = "Free trial credit"
PROD_PREPAID_COMMIT = "Committed spend (prepaid)"
PROD_POSTPAID_COMMIT = "Committed spend (postpaid true-up)"

TAG_COMPUTE = "compute"  # commits, credits, discounts and % support all target this tag
TAG_SUPPORT = "support"

RATE_CARD_NAME = "Replicate list prices"
RATE_CARD_ALIAS = "replicate-list-prices"
PRICE_LIST_START = "2026-01-01T00:00:00.000Z"  # list prices effective since Jan 1st

# Self-serve sign-up: plain pay-as-you-go that starts with the free trial credit
PKG_SELF_SERVE_NAME = "Pay-as-you-go ($10 free trial, 30 days)"
PKG_SELF_SERVE_ALIAS = "replicate-free-trial"
# Upsell: pay-as-you-go + the fixed-fee support tier
PKG_PRO_SUPPORT_NAME = "Pay-as-you-go + Pro Support ($500/mo)"
PKG_PRO_SUPPORT_ALIAS = "replicate-paygo-pro-support"

# Commercial terms (illustrative values agreed for the demo)
TRIAL_CREDIT_USD = 10.00
TRIAL_DAYS = 30
PRO_SUPPORT_MONTHLY_USD = 500.00
ENT_SUPPORT_PERCENT = 0.10           # 10% of compute spend
COMMIT_TOTAL_USD = 100_000.00        # "$100,000 over 3 years"
COMMIT_YEARS = 3
COMMIT_DISCOUNT_MULTIPLIER = 0.85    # 15% off list in exchange for the commit

# Custom field keys (entity, key). They tag trial credits so that ONE
# account-wide alert covers every trial, and tag contracts for reporting.
#   https://docs.metronome.com/guides/pricing-packaging/billing-model-guides/free-trials/overview
CUSTOM_FIELD_KEYS = [
    ("customer", "trial_started_at"),
    ("customer", "trial_source"),
    ("contract", "contract_type"),
    ("contract", "commit_model"),
    ("contract", "sfdc_opportunity_id"),
    ("contract_credit", "trial"),
    ("contract_credit", "trial_model"),
    ("package_credit", "trial"),
    ("package_credit", "trial_model"),
]
TRIAL_CREDIT_FIELDS = {"trial": "true", "trial_model": "expiring_credit"}

# The four demo personas, one per Replicate go-to-market motion.
# ingest_alias = the identifier Replicate's platform already puts on events.
CUSTOMERS = {
    "self_serve": {    # signs up on the self-serve package (pay-as-you-go, $10 free trial)
        "name": "Ada Okafor (free trial)",
        "alias": "adaokafor",
    },
    "pro_support": {   # signs up on the Pro Support package
        "name": "Brightframe AI (pay-as-you-go + Pro Support)",
        "alias": "brightframe-ai",
    },
    "prepaid": {
        "name": "Northwind Media (enterprise, prepaid commit)",
        "alias": "northwind-media",
    },
    "postpaid": {
        "name": "Kepler Games (enterprise, postpaid commit)",
        "alias": "kepler-games",
    },
}

SFDC_OP_ID = "006R00000AcmeCommit"

def customer_url(customer_id):
    return f"{APP_URL}/customers/{customer_id}"
