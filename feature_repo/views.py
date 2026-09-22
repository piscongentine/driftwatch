"""Feast feature views: live sensor stats, and the last service inspection.

Reads : out/data/history.parquet and out/data/service.parquet (Feast offline sources).
Writes: nothing (Feast registers the views when the store is applied).

The stats view has a push source, so `make live` can write new batches straight
into the online and offline stores. The service view is old on purpose: it is our
staleness demo (feast #6821).
"""
import os
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # so `import config` works for `feast apply` too
import config  # noqa: E402
from entities import machine  # noqa: E402
from feast import FeatureView, Field, FileSource, PushSource  # noqa: E402
from feast.types import Bool, Float64, String  # noqa: E402


def rel(path):
    """Feast wants source paths relative to this folder."""
    return Path(os.path.relpath(path, config.REPO)).as_posix()


history_source = FileSource(
    name="machine_history", path=rel(config.HISTORY), timestamp_field="event_timestamp"
)
service_source = FileSource(
    name="machine_service_source", path=rel(config.SERVICE), timestamp_field="event_timestamp"
)
push_source = PushSource(name=config.PUSH_SOURCE, batch_source=history_source)

stats_view = FeatureView(
    name=config.STATS_VIEW,
    entities=[machine],
    ttl=timedelta(hours=config.TTL_STATS_HOURS),
    schema=[
        Field(name="temperature", dtype=Float64),
        Field(name="vibration", dtype=Float64),
        Field(name="humidity", dtype=Float64),
        Field(name="mode", dtype=String),
        Field(name="fw_ok", dtype=Bool),
    ],
    source=push_source,
)

service_view = FeatureView(
    name=config.SERVICE_VIEW,
    entities=[machine],
    ttl=timedelta(days=config.TTL_SERVICE_DAYS),
    schema=[Field(name="wear_pct", dtype=Float64)],
    source=service_source,
)
