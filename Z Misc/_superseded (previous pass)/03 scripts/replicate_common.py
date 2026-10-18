"""
Shared helpers + pricing constants for the Replicate / Metronome demo scripts.

Uses the official Metronome Python SDK (`metronome-sdk`,
`from metronome import Metronome`).

Auth: the SDK reads METRONOME_BEARER_TOKEN by default; we also fall back to
METRONOME_API_TOKEN. Create a token in the Metronome dashboard under
Developer -> API tokens.
  https://docs.metronome.com/api-reference/authentication
"""

import datetime as dt
import json
import os
import sys

from metronome import Metronome

HERE = os.path.dirname(os.path.abspath(__file__))  # .../Metronome Strategy/03 scripts

# Pipeline state shared by all step scripts (single JSON file, kept in "Z Misc").
STATE_PATH = os.environ.get(
    "METRONOME_STATE_PATH",
    os.path.join(HERE, "..", "Z Misc", "state.json"),
)


def client() -> Metronome:
    """SDK client. Token: METRONOME_BEARER_TOKEN, else METRONOME_API_TOKEN."""
    token = os.environ.get("METRONOME_BEARER_TOKEN") or os.environ.get("METRONOME_API_TOKEN")
    if not token:
        sys.exit(
            "ERROR: set METRONOME_BEARER_TOKEN in your environment.\n"
            "Create a token in the Metronome dashboard under Developer -> API tokens."
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


# ---------------------------------------------------------------------------
# Time helpers (Metronome wants hour-aligned contract / credit boundaries)
# ---------------------------------------------------------------------------

def iso(d):
    """datetime -> Metronome's millisecond ISO format."""
    return d.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def now_utc():
    return dt.datetime.now(dt.timezone.utc)


def first_of_current_month_utc():
    return now_utc().replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def floor_hour(d):
    return d.replace(minute=0, second=0, microsecond=0)


def parse_iso(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def cents(dollars):
    """USD -> USD cents (Metronome's default credit type). Keeps decimals:
    per-second GPU prices are fractions of a cent."""
    return round(dollars * 100, 6)


# ---------------------------------------------------------------------------
# Replicate pricing constants (all monetary API values are in USD cents)
# ---------------------------------------------------------------------------

# ONE event type for all compute. `hardware` selects the price,
# `kind` / `model` are kept for breakdowns only.
EVENT_TYPE = "compute_seconds"

# Replicate's public price list (from the prompt, replicate.com/pricing):
# hardware SKU -> (display name, $ per second). Billed by the second.
HARDWARE = {
    "cpu":              ("CPU",                       0.000100),
    "gpu-t4":           ("Nvidia T4 GPU",             0.000225),
    "gpu-a40-small":    ("Nvidia A40 GPU",            0.000575),
    "gpu-a40-large":    ("Nvidia A40 (Large) GPU",    0.000725),
    "gpu-a100":         ("Nvidia A100 (40GB) GPU",    0.001150),
    "gpu-a100-large":   ("Nvidia A100 (80GB) GPU",    0.001400),
    "gpu-a40-large-8x": ("8x Nvidia A40 (Large) GPU", 0.005800),
}

# The machine type 05_add_machine_type.py adds live during the demo
# (current replicate.com/pricing list price: $0.001525/sec, $5.49/hr).
NEW_HARDWARE_DEFAULT = ("gpu-h100", "Nvidia H100 GPU", 0.001525)

# Catalog names (what shows on invoices and in the Metronome UI)
BM_COMPUTE = "Compute Seconds"
PROD_COMPUTE = "Compute (per second)"
PROD_PRO_SUPPORT = "Pro Support"
PROD_ENT_SUPPORT = "Enterprise Support (% of compute)"
PROD_TRIAL_CREDIT = "Free Trial Credit"
PROD_COMMIT = "Committed Spend"

RATE_CARD_NAME = "Replicate Public Pricing"
RATE_CARD_ALIAS = "replicate_public_pricing"
TAG_COMPUTE = "compute"  # commits, credits, discounts and % support all target this tag

PRO_SUPPORT_MONTHLY_USD = 500.00      # fixed fee support tier
ENT_SUPPORT_PERCENT = 0.10            # 10% of compute spend
TRIAL_CREDIT_USD = 10.00              # try-before-credit-card allowance
TRIAL_DAYS = 30

COMMIT_TOTAL_USD = 100_000.00         # "$100,000 over 3 years"
COMMIT_YEARS = 3
COMMIT_DISCOUNT_MULTIPLIER = 0.85     # 15% off list in exchange for the commit

LIST_START = "2020-01-01T00:00:00.000Z"  # rates effective "since forever" (sandbox data)

# The three demo personas, one per Replicate motion.
CUSTOMERS = {
    "trial": {
        "name": "Ada Okafor (free trial)",
        "alias": "ada.okafor@pixelforge.dev",
    },
    "paygo": {
        "name": "Lumen Labs (pay-as-you-go + Pro Support)",
        "alias": "lumen-labs",
    },
    "enterprise": {
        "name": "Northwind Media (enterprise commit)",
        "alias": "northwind-media",
    },
}
