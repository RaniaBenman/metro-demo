"""
01 — Model Replicate's metered product: one metric, one product, every machine type.

GOAL
----
Create the billing foundation for Replicate's pay-per-second model:
  1. ONE streaming billable metric "Replicate GPU Seconds" that SUMs the
     `billed_seconds` property of every `gpu_inference` event, grouped by the
     `hardware` property.
  2. ONE usage product "GPU Compute (per second)" wired to that metric with
     `hardware` as a PRICING group key — so every current and future machine
     type is priced as a dimensional rate on the same product.
  3. The three support-tier products Replicate's homegrown billing cannot
     model today (Pain #3):
       - "Priority Support"             SUBSCRIPTION -> fixed $/mo recurring fee
       - "Premium Support (% of usage)" COMPOSITE    -> percent of GPU spend
       - "Onboarding & Solutions Eng."  FIXED        -> one-time scheduled charge
  4. Two FIXED products that carry trial credits and enterprise commits.

POSITION IN THE DEMO NARRATIVE
------------------------------
Act 1 ("Pricing is config, not code"). This is the answer to Replicate's
Pain #1: "to add another machine type, we have to involve two different
engineering teams, which can take weeks." On Metronome, launching the H100 SKU
is one dimensional rate row on one product — no event schema change, no
deploy, no billing code. (Script 02 adds the rate rows, including H100.)

BUSINESS MOTIVE
---------------
Replicate ships new hardware (H100, H200, L40S…) faster than their billing
system can absorb it. Every week a SKU is not billable is stranded revenue and
eng time. Collapsing "new SKU" to a config change removes the billing
bottleneck from the hardware launch path entirely.

NOTE: only CREATE calls. Idempotent by name via state.json — safe to re-run.
"""

import replicate_common as rc


def main() -> None:
    client = rc.get_client()
    state = rc.load_state()

    # --- 1. Billable metric: SUM(billed_seconds) grouped by hardware --------
    if "metric_id" not in state:
        metric = client.v1.billable_metrics.create(
            name=rc.METRIC_NAME,
            event_type_filter={"in_values": [rc.EVENT_TYPE]},
            property_filters=[
                {"name": "billed_seconds", "exists": True},
                {"name": "hardware", "exists": True},
                {"name": "model", "exists": True},
                {"name": "kind", "exists": True},
            ],
            aggregation_type="SUM",
            aggregation_key="billed_seconds",
            # group key = the hardware dimension; enables dimensional rates and
            # per-SKU invoice line items (cf. "tier: lite" lines on an invoice)
            group_keys=[["hardware"], ["model"], ["kind"]],
        )
        state["metric_id"] = metric.id
        rc.save_state(state)
        print(f"created billable metric  {metric.id}  ({rc.METRIC_NAME})")
    else:
        print(f"reusing billable metric  {state['metric_id']}")

    # --- 2. Usage product: GPU Compute (per second), priced by hardware -----
    if "gpu_product_id" not in state:
        product = client.v1.contracts.products.create(
            name=rc.GPU_PRODUCT_NAME,
            type="USAGE",
            billable_metric_id=state["metric_id"],
            pricing_group_key=["hardware"],
            presentation_group_key=["hardware"],
            tags=[rc.GPU_TAG],  # one tag -> commit discounts & credit scoping
        )
        state["gpu_product_id"] = product.id
        rc.save_state(state)
        print(f"created usage product    {product.id}  ({rc.GPU_PRODUCT_NAME})")
    else:
        print(f"reusing usage product    {state['gpu_product_id']}")

    # --- 3a. Pain #3: subscription support tier (fixed recurring fee) -------
    if "priority_support_id" not in state:
        p = client.v1.contracts.products.create(name=rc.PRIORITY_SUPPORT_NAME, type="SUBSCRIPTION")
        state["priority_support_id"] = p.id
        rc.save_state(state)
        print(f"created subscription     {p.id}  ({rc.PRIORITY_SUPPORT_NAME})")

    # --- 3b. Pain #3: composite support tier (percent of GPU spend) ---------
    if "premium_support_id" not in state:
        p = client.v1.contracts.products.create(
            name=rc.PREMIUM_SUPPORT_NAME,
            type="COMPOSITE",
            composite_tags=[rc.GPU_TAG],  # 10% is computed on all GPU-compute spend
        )
        state["premium_support_id"] = p.id
        rc.save_state(state)
        print(f"created composite        {p.id}  ({rc.PREMIUM_SUPPORT_NAME})")

    # --- 3c. Pain #3: fixed one-time charge product (professional services) -
    if "onboarding_product_id" not in state:
        p = client.v1.contracts.products.create(name=rc.ONBOARDING_NAME, type="FIXED")
        state["onboarding_product_id"] = p.id
        rc.save_state(state)
        print(f"created fixed product    {p.id}  ({rc.ONBOARDING_NAME})")

    # --- 4. Fixed products carrying credits and commits ---------------------
    for key, name in (("trial_credit_product_id", rc.TRIAL_CREDIT_PRODUCT),
                      ("commit_product_id", rc.COMMIT_PRODUCT)):
        if key not in state:
            p = client.v1.contracts.products.create(name=name, type="FIXED")
            state[key] = p.id
            rc.save_state(state)
            print(f"created fixed product    {p.id}  ({name})")

    print("\nDone. Next: python3 02_rate_card.py")


if __name__ == "__main__":
    main()
