"""Compare every live batch with the training reference (Evidently) and write the results.

Reads : out/data/reference.parquet, out/data/plan.json, out/data/batches/*.parquet, out/model.pkl,
        out/freshness.json, out/train_report.json, and Feast (each batch's features come back from the offline store).
Writes: out/summary.json   the dashboard and alerts.py read it
"""
import json
import math
import sys
from datetime import timedelta
from importlib.metadata import version
from pathlib import Path

import pandas as pd
from evidently import DataDefinition, Dataset, Report
from evidently.metrics import DriftedColumnsCount, ValueDrift
from evidently.tests import lt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # lets `import config` work when run as a script
import config  # noqa: E402
import model  # noqa: E402
import workarounds  # noqa: E402
from store import open_store  # noqa: E402

DEFINITION = DataDefinition(numerical_columns=config.NUMERIC + ["prediction"], categorical_columns=config.CATEGORICAL)
GATE = "Drift share under limit"
LABELS = {"ks": "K-S test", "chisquare": "Chi-square test"}  # both report a p-value
LIMIT = -math.log10(config.DRIFT_P)


def method_of(col):
    return config.CAT_TEST if col in config.CATEGORICAL else config.NUM_TEST


def level(p):
    """Drift strength for the chart: -log10(p), so bigger means stronger evidence. None if p is not a number."""
    if p is None or not math.isfinite(p):
        return None
    return round(max(0.0, -math.log10(min(max(p, 1e-12), 1.0))), 3)  # max(0.0, ...) turns -0.0 into 0.0


def compare(ref, cur):
    """One Evidently run: a p-value and a drifted flag for every monitored column, plus the share."""
    metrics = [DriftedColumnsCount(
        columns=config.MONITORED, num_method=config.NUM_TEST, cat_method=config.CAT_TEST,
        num_threshold=config.DRIFT_P, cat_threshold=config.DRIFT_P,
        share_tests=[lt(config.SHARE_ALERT, alias=GATE)],
    )]
    metrics += [ValueDrift(column=c, method=method_of(c), threshold=config.DRIFT_P) for c in config.MONITORED]
    data = [Dataset.from_pandas(d[config.MONITORED], data_definition=DEFINITION) for d in (cur, ref)]
    out = Report(metrics, include_tests=True).run(*data).dict()

    p, share = {}, 0.0
    for m in out["metrics"]:
        if m["config"]["type"].endswith("ValueDrift"):
            p[m["config"]["column"]] = m["value"]
        else:
            share = m["value"]["share"]
    flags = {t["metric_config"]["params"]["column"]: t["status"] == "FAIL" for t in out["tests"] if t["id"] == "drift"}
    gate = next(t for t in out["tests"] if t["id"] == "lt")
    return {
        "share": round(share, 3),
        "gate": {"label": workarounds.with_alias(gate["description"], GATE), "status": str(getattr(gate["status"], "value", gate["status"]))},
        "columns": {c: {"p": p[c], "level": level(p[c]), "drifted": flags[c]} for c in config.MONITORED},
    }


def one_batch(store, clf, ref, b):
    keys = pd.read_parquet(config.BATCHES / f"batch_{b['index']:02d}.parquet")
    entry = {"index": b["index"], "timestamp": b["timestamp"], "rows": len(keys), "drift_step": b["drift"]}
    if len(keys) < config.MIN_ROWS:  # evidently #1900: tiny and empty batches are not sent to the tests
        return {**entry, "status": "empty" if keys.empty else "too_small"}
    cur = workarounds.pull_features(store, keys)
    cur["prediction"] = model.predict(clf, cur)
    return {**entry, "status": "ok", **compare(ref, cur)}


def detection(batches):
    """Precision and recall of the drift flag, against the drift we planted (synthetic data only)."""
    tested = [b for b in batches if b["status"] == "ok"]
    flagged = [b["index"] for b in tested if b["share"] >= config.SHARE_WARN]
    truth = [b["index"] for b in tested if b["drift_step"] > 0]
    hits = set(flagged) & set(truth)
    return {
        "precision": round(len(hits) / len(flagged), 3) if flagged else None,
        "recall": round(len(hits) / len(truth), 3) if truth else None,
        "false_alarms": sorted(set(flagged) - set(truth)),
        "missed": sorted(set(truth) - set(flagged)),
    }


def freshness(now):
    out = []
    for f in json.loads(config.FRESHNESS.read_text()):
        oldest, ttl = pd.Timestamp(f["oldest"]), timedelta(hours=f["ttl_hours"])
        out.append({**f, "age_hours": round((now - oldest).total_seconds() / 3600, 1),
                    "stale": bool(workarounds.is_stale(oldest, ttl, now))})
    return out


def main():
    workarounds.patch_evidently()
    store, clf = open_store(), model.load()
    ref = pd.read_parquet(config.REFERENCE)
    plan = json.loads(config.PLAN.read_text())
    batches = [one_batch(store, clf, ref, b) for b in plan["batches"]]
    now = pd.Timestamp.now(tz="UTC")
    summary = {
        "generated_at": now.isoformat(),
        "versions": {"feast": version("feast"), "evidently": version("evidently")},
        "reference_rows": len(ref),
        "model": json.loads(config.TRAIN_REPORT.read_text()),
        "columns": [{"name": c, "method": LABELS[method_of(c)], "threshold": config.DRIFT_P, "limit": round(LIMIT, 3),
                     "constant": bool(ref[c].nunique() == 1)} for c in config.MONITORED],
        "batches": batches,
        "detection": detection(batches),
        "freshness": freshness(now),
    }
    config.SUMMARY.write_text(json.dumps(summary, indent=2, allow_nan=False))
    for b in batches:
        note = f"share {b['share']:.2f}  gate {b['gate']['status']}" if b["status"] == "ok" else b["status"]
        print(f"batch {b['index']:>2}  rows {b['rows']:>3}  {note}")
    print(f"detection: {summary['detection']}")
    print(f"wrote    : {config.SUMMARY}")


if __name__ == "__main__":
    main()
