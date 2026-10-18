"""
Shared plumbing for the Replicate × Metronome demo setup scripts.

WHY THIS FILE
-------------
Every script in this folder performs the WRITE actions the strategist is not
allowed to perform in the sandbox. They all need the same client, the same
Replicate hardware catalog, and the same idempotency helpers, so they import
from here. State (created IDs) is persisted to `state.json` so scripts can be
re-run safely and so later scripts can reference what earlier ones created.

RUN ORDER
---------
  01_metric_and_products.py   -> billable metric + hardware/support products
  02_rate_card.py             -> "Replicate — Public Pay-per-second" rate card + all rates
  03_trial_flow.py            -> trial package + trial customer + trial alerts
  04_enterprise_commit.py     -> enterprise customer + $100k/3yr commit + alerts
  05_send_usage.py            -> realistic GPU-seconds events for both customers

PREREQUISITES
-------------
  pip install --pre metronome-sdk        # official Metronome Python SDK
  export METRONOME_API_TOKEN=<sandbox token>   # Developer -> API tokens -> + Add (Writer role is enough)
"""

from __future__ import annotations

import json
import os
import pathlib
import sys

from metronome import Metronome

HERE = pathlib.Path(__file__).resolve().parent
STATE_FILE = HERE / "state.json"


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

def get_client() -> Metronome:
    token = os.environ.get("METRONOME_API_TOKEN")
    if not token:
        sys.exit("Set METRONOME_API_TOKEN (Developer -> API tokens in the Metronome app).")
    base = os.environ.get("METRONOME_API_BASE")  # optional, staging only
    return Metronome(bearer_token=token, base_url=base) if base else Metronome(bearer_token=token)


# ---------------------------------------------------------------------------
# State persistence (makes every script idempotent / re-runnable)
# ---------------------------------------------------------------------------

def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2, sort_keys=True))


# ---------------------------------------------------------------------------
# USD credit type lookup
# ---------------------------------------------------------------------------

def usd_credit_type_id(client: Metronome) -> str:
    """Look up the USD pricing unit / credit type ID dynamically.

    Credits, commits, alerts and rate-card currencies all reference a credit
    type. We never hardcode the ID — we resolve it from the environment so the
    scripts work against any Metronome environment.
    """
    for unit in client.v1.pricing_units.list():
        if getattr(unit, "name", "").upper() == "USD" or getattr(unit, "id", "") == "USD":
            return unit.id
    # Fallback: some environments expose it under a different display name.
    for unit in client.v1.pricing_units.list():
        if "US" in getattr(unit, "name", "").upper():
            return unit.id
    sys.exit("Could not resolve the USD credit type from pricing_units.list()")


# ---------------------------------------------------------------------------
# Replicate hardware catalog (source: https://replicate.com/pricing)
# ---------------------------------------------------------------------------
# (slug used in events as properties.hardware, display name, USD per second)
REPLICATE_HARDWARE = [
    ("cpu",        "CPU",                    0.000100),
    ("t4",         "Nvidia T4 GPU",          0.000225),
    ("a40",        "Nvidia A40 GPU",         0.000575),
    ("a40-large",  "Nvidia A40 (Large) GPU", 0.000725),
    ("a100-40gb",  "Nvidia A100 (40GB) GPU", 0.001150),
    ("a100-80gb",  "Nvidia A100 (80GB) GPU", 0.001400),
    ("a40-large-8x", "8x Nvidia A40 (Large) GPU", 0.005800),
    # The "new machine type" Replicate wants to launch — the Pain #1 payoff.
    # With Metronome this is one rate row, not two engineering teams and weeks.
    ("h100",       "Nvidia H100 GPU  ★ NEW", 0.001525),
]

EVENT_TYPE = "gpu_inference"          # one event per prediction, billed by the second
METRIC_NAME = "Replicate GPU Seconds"
RATE_CARD_NAME = "Replicate — Public Pay-per-second"
RATE_CARD_ALIAS = "replicate-paygo"
GPU_PRODUCT_NAME = "GPU Compute (per second)"
GPU_TAG = "gpu-compute"               # product tag: target of commit discounts & credit scoping

# Support-tier products (Pain #3: fixed and percent-based fees)
PRIORITY_SUPPORT_NAME = "Priority Support"          # subscription, $500/mo flat
PRIORITY_SUPPORT_PRICE = 500.0
PREMIUM_SUPPORT_NAME = "Premium Support (% of usage)"  # composite, 10% of GPU spend
PREMIUM_SUPPORT_PCT = 0.10
ONBOARDING_NAME = "Onboarding & Solutions Engineering"  # fixed, one-time scheduled charge

# Fixed products that carry credits/commits (Metronome pattern: fixed products
# back credits, commits and scheduled charges so they show up as invoice lines)
TRIAL_CREDIT_PRODUCT = "Free Trial Credit"
COMMIT_PRODUCT = "Enterprise Committed Spend"

# Customers
TRIAL_CUSTOMER = {"name": "Ada Lovelace", "alias": "trial_ada_lovelace"}
TRIAL_CREDIT_USD = 25.00       # try-before-card allowance
TRIAL_DAYS = 14

ENT_CUSTOMER = {"name": "Acme Robotics, Inc.", "alias": "acme_robotics"}
ENT_COMMIT_TOTAL = 100_000.00  # $100k over 3 years, per the customer's example
ENT_DISCOUNT = 0.10            # 10% off list on GPU compute in exchange for the commit
ENT_ONBOARDING_FEE = 5_000.00  # one-time professional-services fee, invoiced in month 3
