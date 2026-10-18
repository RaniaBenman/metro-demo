"""
02 — Replicate's entire public pricing as ONE rate card (including the new H100).

GOAL
----
Create the "Replicate — Public Pay-per-second" rate card (alias
`replicate-paygo`) and load every price from https://replicate.com/pricing
onto it:
  - 8 dimensional FLAT rates for "GPU Compute (per second)", one per machine
    type, keyed by the `hardware` pricing group — CPU through 8xA40, PLUS the
    brand-new H100 SKU.
  - 1 FLAT MONTHLY subscription rate for "Priority Support" ($500/mo,
    entitled=false by default — sales enables it per contract).
  - 1 PERCENTAGE rate (0.10) for "Premium Support (% of usage)" — the
    percent-of-spend support tier Replicate's homegrown billing cannot model.

POSITION IN THE DEMO NARRATIVE
------------------------------
Act 1 payoff (Pain #1): the rate card screen IS Replicate's pricing page, but
as configuration. Adding machine type #9 (H100) was one rate row — the same
motion a billing-ops person uses to add #10 next quarter. No PR, no deploy,
no two-week two-team project.
Act 3 setup (Pain #3): the Priority/Premium support rates live on the same
rate card, ready to be entitled on any contract.

BUSINESS MOTIVE
---------------
Pricing velocity. Replicate's competitors (modal, runpod, together) reprice
constantly; Metronome customers like OpenAI shipped 10+ pricing changes in a
year without touching billing code. This rate card is what that feels like.

NOTE: only CREATE calls. Idempotent via state.json — safe to re-run.
"""

import replicate_common as rc

EPOCH = "2020-01-01T00:00:00.000Z"  # rates effective since epoch => active now


def main() -> None:
    client = rc.get_client()
    state = rc.load_state()
    if "gpu_product_id" not in state:
        raise SystemExit("Run 01_metric_and_products.py first.")

    usd = rc.usd_credit_type_id(client)
    state["usd_credit_type_id"] = usd

    # --- Rate card -----------------------------------------------------------
    if "rate_card_id" not in state:
        card = client.v1.contracts.rate_cards.create(
            name=rc.RATE_CARD_NAME,
            description="Replicate public pay-per-second pricing, mirrored from replicate.com/pricing",
            fiat_credit_type_id=usd,
            aliases=[{"name": rc.RATE_CARD_ALIAS, "starting_at": EPOCH}],
        )
        state["rate_card_id"] = card.id
        rc.save_state(state)
        print(f"created rate card        {card.id}  ({rc.RATE_CARD_NAME})")
    else:
        print(f"reusing rate card        {state['rate_card_id']}")

    card_id = state["rate_card_id"]

    # --- GPU dimensional rates: one row per machine type --------------------
    # NOTE ON UNITS: for the USD credit type, all `price`/`amount` values are
    # in CENTS (verified against the sandbox's existing rate card). Our
    # catalog is in USD/sec, so convert: $0.000100/sec -> 0.01 cents/sec.
    if "gpu_rates_added" not in state:
        rates = [
            {
                "product_id": state["gpu_product_id"],
                "starting_at": EPOCH,
                "entitled": True,
                "rate_type": "FLAT",
                "price": round(price_usd_per_sec * 100, 6),  # cents per second
                "pricing_group_values": {"hardware": slug},
            }
            for slug, _label, price_usd_per_sec in rc.REPLICATE_HARDWARE
        ]
        client.v1.contracts.rate_cards.rates.add_many(rate_card_id=card_id, rates=rates)
        state["gpu_rates_added"] = True
        rc.save_state(state)
        print(f"added {len(rates)} dimensional GPU rates (cpu … h100)")

    # --- Support tier rates (Pain #3) ---------------------------------------
    if "support_rates_added" not in state:
        client.v1.contracts.rate_cards.rates.add_many(
            rate_card_id=card_id,
            rates=[
                {  # fixed recurring support fee — entitled per contract, not by default
                    "product_id": state["priority_support_id"],
                    "starting_at": EPOCH,
                    "entitled": False,
                    "rate_type": "FLAT",
                    "price": rc.PRIORITY_SUPPORT_PRICE * 100,  # $500 -> cents
                    "billing_frequency": "MONTHLY",
                },
                {  # percent-of-spend support fee: 10% of all GPU-compute spend
                    "product_id": state["premium_support_id"],
                    "starting_at": EPOCH,
                    "entitled": False,
                    "rate_type": "PERCENTAGE",
                    "price": rc.PREMIUM_SUPPORT_PCT,
                },
            ],
        )
        state["support_rates_added"] = True
        rc.save_state(state)
        print("added support rates      Priority $500/mo (FLAT) + Premium 10% (PERCENTAGE)")

    print("\nDone. Next: python3 03_trial_flow.py")


if __name__ == "__main__":
    main()
