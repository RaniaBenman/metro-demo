"""
05 — Realistic GPU-seconds usage for both demo customers.

GOAL
----
Send `gpu_inference` usage events so the demo screens are alive:
  - Trial customer (Ada Lovelace): 9 days of hobbyist-to-heavy usage that
    burns through ~all of her $25 trial credit and tips slightly into
    overage — the exact moment Replicate's daily batch would have missed,
    and the state that fires the real-time "Trial balance exhausted" alert
    from script 03.
  - Enterprise customer (Acme Robotics): 45 days of production-scale
    multi-SKU usage (A100-80GB, 8xA40, H100, A100-40GB) that draws down
    ~a quarter of their Year-1 commit — a believable ramp, and the data
    behind the "Consumed / Remaining" bars on the Commits & credits tab.

POSITION IN THE DEMO NARRATIVE
------------------------------
Act 2: Ada's real-time balance + the draft invoice showing credit drawdown
vs. overage (Pain #2). Act 4: Acme's commit drawdown bars (Pain #4).
Act 1 kicker: some of Acme's events run on the NEW H100 SKU — proving the
rate row from script 02 rates real events immediately, no deploy.

BUSINESS MOTIVE
---------------
The events are the proof that metering → rating → credits/commits → invoice
is one real-time pipeline, not Replicate's nightly batch + SQL archaeology.

NOTE: deterministic transaction_ids (uuid5) => Metronome deduplicates on
re-run; sending the same events twice is safe.
"""

import datetime as dt
import uuid

import replicate_common as rc

NOW = dt.datetime.now(dt.timezone.utc)
NS = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")  # uuid namespace (DNS)


def iso(t: dt.datetime) -> str:
    return t.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def tx(customer_alias: str, n: int) -> str:
    return str(uuid.uuid5(NS, f"replicate-demo/{customer_alias}/{n}"))


def build_events() -> list[dict]:
    events: list[dict] = []

    def emit(alias: str, days_ago: float, hardware: str, seconds: int, n: int,
             model: str) -> None:
        events.append({
            "customer_id": alias,               # ingest alias, not Metronome ID
            "event_type": rc.EVENT_TYPE,
            "timestamp": iso(NOW - dt.timedelta(days=days_ago)),
            "transaction_id": tx(alias, n),
            "properties": {
                "hardware": hardware,
                "billed_seconds": seconds,
                "model": model,
                "prediction_id": f"p_{tx(alias, n)[:12]}",
            },
        })

    # --- Ada (trial): ~$26 of mixed usage over the last 9 days ---------------
    ada = rc.TRIAL_CUSTOMER["alias"]
    n = 0
    for i in range(20):   # Stable-Diffusion-class tinkering on T4: $8.10
        n += 1; emit(ada, 8.8 - i * 0.35, "t4", 1800, n, "stability-ai/sdxl")
    for i in range(15):   # heavier image runs on A40: $10.35
        n += 1; emit(ada, 6.5 - i * 0.3, "a40", 1200, n, "black-forest-labs/flux-schnell")
    for i in range(10):   # CPU glue jobs: $2.40
        n += 1; emit(ada, 5.0 - i * 0.4, "cpu", 2400, n, "replicate/hello-world")
    for i in range(5):    # first serious LLM fine-tune inference on A100-40: $5.18
        n += 1; emit(ada, 1.5 - i * 0.2, "a100-40gb", 900, n, "meta/llama-3-70b-instruct")
    # total ≈ $26.03 vs $25 credit => exhausted + ~$1 overage. Perfect.

    # --- Acme (enterprise): 45 days of production usage, ~$6.6k gross --------
    acme = rc.ENT_CUSTOMER["alias"]
    n = 0
    for i in range(50):   # batch video pipeline on A100-80GB: $2,800
        n += 1; emit(acme, 44 - i * 0.85, "a100-80gb", 40000, n, "custom/video-gen-prod")
    for i in range(20):   # training-scale 8xA40 jobs: $2,320
        n += 1; emit(acme, 40 - i * 1.9, "a40-large-8x", 20000, n, "custom/robotics-sim")
    for i in range(20):   # NEW H100 SKU, in production the week it launched: $915
        n += 1; emit(acme, 12 - i * 0.5, "h100", 30000, n, "custom/video-gen-prod")
    for i in range(10):   # A100-40 inference fleet: $575
        n += 1; emit(acme, 30 - i * 2.5, "a100-40gb", 50000, n, "meta/llama-3-70b-instruct")

    return events


def main() -> None:
    client = rc.get_client()
    state = rc.load_state()
    if "trial_contract_id" not in state or "ent_contract_id" not in state:
        raise SystemExit("Run 03_trial_flow.py and 04_enterprise_commit.py first.")

    events = build_events()
    # /v1/ingest accepts at most 100 events per call
    for i in range(0, len(events), 100):
        batch = events[i:i + 100]
        client.v1.usage.ingest(usage=batch)
        print(f"ingested events {i + 1}–{i + len(batch)} of {len(events)}")

    print("\nDone. In the app:")
    print("  - Customers -> Ada Lovelace -> Commits and credits: trial credit ~exhausted")
    print("  - Customers -> Ada Lovelace -> Invoices: draft usage invoice, credit drawdown + overage")
    print("  - Customers -> Acme Robotics -> Commits and credits: commit drawdown in real time")
    print("  - Usage events: filter event_type = gpu_inference, group by hardware")


if __name__ == "__main__":
    main()
