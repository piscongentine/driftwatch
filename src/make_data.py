"""Build the synthetic machine-sensor world, with the edge cases in on purpose.

Reads : config.py
Writes: out/data/history.parquet   sensor readings, the Feast offline source
        out/data/service.parquet   last inspection per machine, STALE_DAYS old
        out/data/labels.parquet    entity rows plus failure label; training starts here
        out/data/plan.json         schedule for `make live`: size and drift of each batch

Edge cases (what breaks and how we cope: issues/<name>/NOTES.md):
  1. fw_ok never changes                     evidently #1929
  2. live batches far smaller than history   evidently #1914, #1900
  3. one live batch has zero rows            feast #6817, #6819, #6796
  4. two readings share machine id + time    feast #6787
  5. one feature has an old timestamp        feast #6821
"""
import json
import sys
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # lets `import config` work when run as a script
import config  # noqa: E402

MACHINES = list(range(1, config.N_MACHINES + 1))


def failure_prob(df):
    """Hidden truth: hotter, shakier, damper machines in high mode fail more often. Strong on purpose:
    a clean signal keeps the demo model's marks high. Real fleets are noisier."""
    z = (2.45 * (df["temperature"] - 70) / 4 + 3.5 * (df["vibration"] - 2.0) / 0.5
         + 1.05 * (df["humidity"] - 45) / 8 + 2.45 * (df["mode"] == "high") - 7.4)
    return 1 / (1 + np.exp(-z))


def make_rows(times, machines, drift, rng):
    """One reading per machine per timestamp. `drift` counts steps of sensor wear (0 = healthy).

    The failure label comes from the true machine state. Drift only changes what the sensors
    report, so the model gets fooled while the real failure rate stays put.
    """
    n = len(times) * len(machines)
    df = pd.DataFrame({
        "machine_id": np.tile(np.array(machines, dtype="int64"), len(times)),
        "event_timestamp": pd.DatetimeIndex(times).repeat(len(machines)),
        "temperature": rng.normal(70, 4, n),
        "vibration": np.clip(rng.normal(2.0, 0.5, n), 0.1, None),
        "humidity": np.clip(rng.normal(45, 8, n), 5, 95),
        "mode": rng.choice(config.MODES, n, p=[0.2, 0.6, 0.2]),
        "fw_ok": True,                               # edge case 1: a constant flag
    })
    df["failure"] = rng.random(n) < failure_prob(df)

    shift = drift * config.DRIFT_STEP                # in standard deviations
    w = config.DRIFT_WEIGHTS
    df["temperature"] += 4 * shift * w["temperature"]
    df["vibration"] += 0.5 * shift * w["vibration"]
    df["humidity"] = (df["humidity"] + 8 * shift * w["humidity"]).clip(5, 95)
    df.loc[rng.random(n) < min(0.15 * shift, 0.5), "mode"] = "high"  # firmware starts reporting "high" more often
    return df


def batch_time(anchor, k):
    """Batch k lands on the hour; the last batch lands on `anchor`."""
    return anchor - timedelta(hours=config.N_BATCHES - 1 - k)  # stdlib timedelta: pd.Timedelta warns on numpy 2.5


def history(anchor, rng):
    """Training window: ends one hour before batch 0."""
    end = batch_time(anchor, 0) - timedelta(hours=1)
    times = pd.date_range(end=end, periods=config.HISTORY_HOURS, freq="h")
    df = make_rows(times, MACHINES, 0, rng)
    twin = make_rows(times[10:11], MACHINES[:1], 0, rng)  # edge case 4: machine 1 reports twice at one timestamp
    return pd.concat([df, twin], ignore_index=True)


def service(anchor, rng):
    """Last inspection per machine, recorded STALE_DAYS ago (edge case 5)."""
    stamp = anchor - timedelta(days=config.STALE_DAYS)
    wear = rng.uniform(5, 40, len(MACHINES))
    return pd.DataFrame({"machine_id": MACHINES, "event_timestamp": stamp, "wear_pct": wear})


def plan(anchor):
    """Edge cases 2 and 3: batches are small next to history, and one is empty."""
    odd = {config.EMPTY_BATCH: 0, config.TINY_BATCH: config.TINY_SIZE}
    batches = [
        {
            "index": k,
            "timestamp": batch_time(anchor, k).isoformat(),
            "size": odd.get(k, config.BATCH_SIZE),
            "drift": max(0, k - config.DRIFT_START + 1),
        }
        for k in range(config.N_BATCHES)
    ]
    return {"anchor": anchor.isoformat(), "batches": batches}


def main():
    rng = np.random.default_rng(config.SEED)
    anchor = pd.Timestamp.now(tz="UTC").floor("h")
    config.DATA.mkdir(parents=True, exist_ok=True)

    hist = history(anchor, rng)
    hist[config.FEATURE_COLS].to_parquet(config.HISTORY, index=False)
    hist[config.LABEL_COLS].to_parquet(config.LABELS, index=False)
    service(anchor, rng).to_parquet(config.SERVICE, index=False)
    config.PLAN.write_text(json.dumps(plan(anchor), indent=2))

    sizes = [b["size"] for b in plan(anchor)["batches"]]
    print(f"history : {len(hist)} rows, {config.N_MACHINES} machines x {config.HISTORY_HOURS} hours, plus 1 duplicate reading")
    print(f"service : {config.N_MACHINES} rows, inspection {config.STALE_DAYS} days old")
    print(f"plan    : {config.N_BATCHES} live batches, sizes {sizes}, drift starts at batch {config.DRIFT_START}")
    print(f"wrote   : {config.DATA}")


if __name__ == "__main__":
    main()
