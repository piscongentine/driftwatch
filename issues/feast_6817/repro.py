"""feast #6817: get_historical_features raises TypeError on a zero-row entity_df (file/Dask store).

The issue builds the empty frame the way batch code often does: an empty list for the
key column (dtype object) and an empty UTC timestamp column. We do the same.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lab  # noqa: E402
import pandas as pd  # noqa: E402

store, view, driver, folder = lab.make_store()
features = ["driver_stats:conv_rate"]


def frame(n):
    return pd.DataFrame({"driver_id": [1001] * n, "event_timestamp": pd.to_datetime([lab.NOW] * n, utc=True)})


print("one row :", store.get_historical_features(entity_df=frame(1), features=features).to_df().shape)
try:
    print("zero rows:", store.get_historical_features(entity_df=frame(0), features=features).to_df().shape)
    bug = False
except TypeError as e:
    print("zero rows: TypeError:", str(e)[:100])
    bug = True
lab.clean(folder)
lab.verdict(bug)
