"""feast #6821: a feature view's ttl is not applied on the standard online retrieval path.

The value is one hour old and the ttl is one minute. Expected: not served, or marked
OUTSIDE_MAX_AGE. Reality in the issue: served and marked PRESENT, whatever the ttl.
"""
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lab  # noqa: E402
from feast.protos.feast.serving.ServingService_pb2 import FieldStatus  # noqa: E402

store, view, driver, folder = lab.make_store(ttl=timedelta(minutes=1), age=timedelta(hours=1))
resp = store.get_online_features(features=["driver_stats:conv_rate"], entity_rows=[{"driver_id": 1001}])
value = resp.to_dict()["conv_rate"][0]
status = resp.proto.results[0].statuses[0]
print(f"ttl 1 minute, value 1 hour old -> value {value}, status {FieldStatus.Name(status)}")
lab.clean(folder)
lab.verdict(value is not None and status != FieldStatus.OUTSIDE_MAX_AGE)
