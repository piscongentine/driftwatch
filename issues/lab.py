"""Shared setup for the Feast repros: a tiny local Feast repo in a temp folder.

Reads : nothing.
Writes: a temp folder (parquet file, SQLite online store, registry), removed when the repro ends.
Each repro stays short because the setup lives here. A repro prints what it saw and ends
with one line: `STATUS: Reproduced` (the bug is still there) or `STATUS: Fixed`.
"""
import os
import shutil
import tempfile
import warnings
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore")
os.environ.setdefault("FEAST_USAGE", "False")  # no usage pings from a repro
NOW = datetime.now(timezone.utc).replace(microsecond=0)
YAML = (
    "project: lab\nregistry: data/registry.db\nprovider: local\n"
    "online_store:\n  type: sqlite\n  path: data/online.db\n"
    "offline_store:\n  type: file\nentity_key_serialization_version: 3\n"
)


def make_store(ttl=timedelta(days=1), age=timedelta(hours=1), online=True):
    """One feature view `driver_stats` (feature conv_rate) for drivers 1001..1003.

    `age` is how old the feature rows are. Returns (store, feature_view, entity, folder).
    """
    from feast import Entity, FeatureStore, FeatureView, Field, FileSource
    from feast.types import Float64
    from feast.value_type import ValueType

    folder = Path(tempfile.mkdtemp(prefix="dw_lab_"))
    (folder / "repo").mkdir()
    (folder / "repo" / "feature_store.yaml").write_text(YAML)
    df = pd.DataFrame({
        "driver_id": [1001, 1002, 1003],
        "event_timestamp": pd.to_datetime([NOW - age] * 3, utc=True),
        "conv_rate": [0.1, 0.2, 0.3],
    })
    df.to_parquet(folder / "stats.parquet")
    driver = Entity(name="driver", join_keys=["driver_id"], value_type=ValueType.INT64)
    source = FileSource(name="stats_source", path=str(folder / "stats.parquet"), timestamp_field="event_timestamp")
    view = FeatureView(name="driver_stats", entities=[driver], ttl=ttl,
                       schema=[Field(name="conv_rate", dtype=Float64)], source=source)
    store = FeatureStore(repo_path=str(folder / "repo"))
    store.apply([driver, view])
    if online:
        store.write_to_online_store("driver_stats", df)
    return store, view, driver, folder


def clean(folder):
    shutil.rmtree(folder, ignore_errors=True)


def verdict(bug_present):
    """The one line check_all.py looks for."""
    print("STATUS:", "Reproduced" if bug_present else "Fixed")
