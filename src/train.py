"""Pull training history from Feast, fit a small failure model, save it.

Reads : out/data/labels.parquet, and the Feast offline store for the features.
Writes: out/model.pkl
        out/train_report.json         holdout accuracy, precision, recall, F1, AUC
        out/data/reference.parquet    the features Feast returned plus the prediction: Evidently's reference
Split by time: oldest 60% trains, next 15% picks the decision threshold, newest 25% scores the model.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # lets `import config` work when run as a script
import config  # noqa: E402
import model  # noqa: E402
import workarounds  # noqa: E402
from store import open_store  # noqa: E402


def best_threshold(y, p):
    """Decision threshold with the best F1 on the validation slice. F1 balances precision and recall."""
    grid = np.linspace(0.05, 0.95, 91)
    return float(grid[int(np.argmax([f1_score(y, p >= t, zero_division=0) for t in grid]))])


def main():
    store = open_store()
    labels = pd.read_parquet(config.LABELS)
    df = workarounds.pull_features(store, labels)
    df = df.sort_values("event_timestamp", kind="stable").reset_index(drop=True)

    a = int(len(df) * (1 - config.VAL_SIZE - config.TEST_SIZE))
    b = int(len(df) * (1 - config.TEST_SIZE))
    train, val, test = df.iloc[:a], df.iloc[a:b], df.iloc[b:]
    clf = model.build().fit(model.encode(train), train["failure"])
    threshold = best_threshold(val["failure"], model.predict(clf, val))
    model.save(clf)

    p = model.predict(clf, test)
    y, hit = test["failure"], p >= threshold
    report = {
        "model": "logistic regression on standardized sensors",
        "rows_in": len(labels), "rows_out": len(df),
        "train_rows": a, "val_rows": b - a, "test_rows": len(df) - b,
        "failure_rate": round(float(df["failure"].mean()), 4),
        "threshold": round(threshold, 2),
        "auc": round(float(roc_auc_score(y, p)), 3),
        "accuracy": round(float(accuracy_score(y, hit)), 3),
        "baseline_accuracy": round(float(1 - y.mean()), 3),  # what "never fails" would score
        "precision": round(float(precision_score(y, hit, zero_division=0)), 3),
        "recall": round(float(recall_score(y, hit)), 3),
        "f1": round(float(f1_score(y, hit)), 3),
        "trained_at": pd.Timestamp.now(tz="UTC").isoformat(),
    }
    config.TRAIN_REPORT.write_text(json.dumps(report, indent=2))

    df["prediction"] = model.predict(clf, df)
    df[["machine_id", "event_timestamp"] + config.MONITORED].to_parquet(config.REFERENCE, index=False)

    print(f"labels   : {len(labels)} rows")
    print(f"features : {len(df)} rows back from Feast (rows lost: {len(labels) - len(df)})")
    print(f"model    : {report['model']}, threshold {report['threshold']}")
    print(f"holdout  : accuracy {report['accuracy']} (never-fails baseline {report['baseline_accuracy']}), "
          f"precision {report['precision']}, recall {report['recall']}, F1 {report['f1']}, AUC {report['auc']}")
    print(f"reference: {config.REFERENCE}")


if __name__ == "__main__":
    main()
