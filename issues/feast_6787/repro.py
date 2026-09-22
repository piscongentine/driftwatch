"""feast #6787: get_historical_features drops entity_df rows that share a join key and a timestamp (file/Dask store).

Two entity rows for driver 1001 at the same timestamp are two different requests
(think two orders in the same second). Expected: one output row per input row.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lab  # noqa: E402
import pandas as pd  # noqa: E402

store, view, driver, folder = lab.make_store()
entity_df = pd.DataFrame({
    "driver_id": [1001, 1001, 1002],
    "event_timestamp": pd.to_datetime([lab.NOW] * 3, utc=True),
    "order_id": ["a", "b", "c"],
})
got = store.get_historical_features(entity_df=entity_df, features=["driver_stats:conv_rate"]).to_df()
print(f"entity rows in: {len(entity_df)}, rows out: {len(got)}")
print(f"order ids that came back: {sorted(got['order_id'])}")
lab.clean(folder)
lab.verdict(len(got) < len(entity_df))
