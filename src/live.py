"""Simulate live traffic: create every batch in the plan (some drifted) and push it into Feast.

Reads : out/data/plan.json, out/data/service.parquet, and Feast.
Writes: Feast online store (out/feast/online.db) and offline store (new rows in out/data/history.parquet),
        out/data/batches/batch_XX.parquet   keys plus label of each batch; the features stay in Feast
        out/live_log.json                   what happened to each batch
        out/freshness.json                  oldest and newest value per feature view, with its ttl
Running it twice is safe: rows from an earlier live run are removed first.
"""
import json
import sys
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # lets `import config` work when run as a script
import config  # noqa: E402
import workarounds  # noqa: E402
from make_data import MACHINES, make_rows  # noqa: E402
from store import open_store  # noqa: E402


def drop_old_live_rows(first_ts):
    """Remove rows an earlier `make live` pushed, so repeating it never piles up duplicates."""
    hist = pd.read_parquet(config.HISTORY)
    hist[hist["event_timestamp"] < first_ts].to_parquet(config.HISTORY, index=False)


def as_utc(series):
    """Feast 0.66 gives online event timestamps as epoch seconds; accept real datetimes too."""
    unit = "s" if pd.api.types.is_numeric_dtype(series) else None
    return pd.to_datetime(series, unit=unit, utc=True)


def newest_values(store):
    """Oldest and newest event timestamp Feast serves online, per feature view."""
    views = [
        (config.STATS_VIEW, "temperature", timedelta(hours=config.TTL_STATS_HOURS)),
        (config.SERVICE_VIEW, "wear_pct", timedelta(days=config.TTL_SERVICE_DAYS)),
    ]
    rows = [{"machine_id": m} for m in MACHINES]
    out = []
    for view, col, ttl in views:
        df = store.get_online_features(features=[f"{view}:{col}"], entity_rows=rows).to_df(include_event_timestamps=True)
        ts = as_utc(df[f"{col}__ts"])
        out.append({
            "view": view,
            "oldest": ts.min().isoformat(),
            "newest": ts.max().isoformat(),
            "ttl_hours": ttl.total_seconds() / 3600,
            "machines": len(ts),
        })
    return out


def main():
    plan = json.loads(config.PLAN.read_text())
    drop_old_live_rows(pd.Timestamp(plan["batches"][0]["timestamp"]))
    store = open_store()
    store.write_to_online_store(config.SERVICE_VIEW, pd.read_parquet(config.SERVICE))  # the old inspection values

    rng = np.random.default_rng(config.SEED + 1)
    config.BATCHES.mkdir(parents=True, exist_ok=True)
    log = []
    for b in plan["batches"]:
        df = make_rows([pd.Timestamp(b["timestamp"])], MACHINES[: b["size"]], b["drift"], rng)
        pushed = workarounds.push_batch(store, df)
        back = workarounds.online_rows(store, list(df["machine_id"]))  # what a model would be served right now
        same_order = list(back["machine_id"]) == list(df["machine_id"])
        df[config.LABEL_COLS].to_parquet(config.BATCHES / f"batch_{b['index']:02d}.parquet", index=False)
        log.append({**b, "rows": len(df), "pushed": pushed, "online_same_order": same_order})
        print(f"batch {b['index']:>2}  rows {len(df):>3}  drift {b['drift']}  pushed {pushed:>3}  online order {'ok' if same_order else 'BROKEN'}")

    config.LIVE_LOG.write_text(json.dumps(log, indent=2))
    config.FRESHNESS.write_text(json.dumps(newest_values(store), indent=2))
    print(f"wrote    : {config.LIVE_LOG.name}, {config.FRESHNESS.name}, {len(log)} batch files")


if __name__ == "__main__":
    main()
