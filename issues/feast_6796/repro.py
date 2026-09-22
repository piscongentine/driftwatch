"""feast #6796: the Arrow-to-proto write helpers fail on a valid zero-row Table.

A zero-row pyarrow Table has no record batches, and the helper reads `table.to_batches()[0]`.
Expected: an empty write payload ([]). This calls the private helper the issue names.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lab  # noqa: E402
import pandas as pd  # noqa: E402
import pyarrow as pa  # noqa: E402
from feast.utils import _convert_arrow_fv_to_proto  # noqa: E402
from feast.value_type import ValueType  # noqa: E402

store, view, driver, folder = lab.make_store(online=False)
rows = pd.DataFrame({
    "driver_id": [1001],
    "event_timestamp": pd.to_datetime([lab.NOW], utc=True),
    "conv_rate": [0.1],
})
join_keys = {"driver_id": ValueType.INT64}
print("one row  :", len(_convert_arrow_fv_to_proto(pa.Table.from_pandas(rows), view, join_keys)), "item(s)")
empty = pa.Table.from_pandas(rows.iloc[0:0])
print("zero rows: table has", empty.num_rows, "rows and", len(empty.to_batches()), "record batches")
try:
    print("zero rows: payload", _convert_arrow_fv_to_proto(empty, view, join_keys))
    bug = False
except IndexError as e:
    print("zero rows: IndexError:", e)
    bug = True
lab.clean(folder)
lab.verdict(bug)
