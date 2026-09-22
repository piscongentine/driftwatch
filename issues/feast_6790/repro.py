"""feast #6790: a join key value is dropped when it shares a name with an on-demand view's RequestSource field.

The ODFV asks for `driver_id` as request data, and the regular view needs `driver_id` as its
join key. One value in entity_rows should serve both. Expected: the request works.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lab  # noqa: E402
from feast import FeatureService, Field, RequestSource  # noqa: E402
from feast.on_demand_feature_view import on_demand_feature_view  # noqa: E402
from feast.types import Float64, Int64  # noqa: E402

store, view, driver, folder = lab.make_store()
request = RequestSource(name="ask", schema=[Field(name="driver_id", dtype=Int64), Field(name="bonus", dtype=Float64)])


@on_demand_feature_view(sources=[view, request], schema=[Field(name="boosted", dtype=Float64)], mode="pandas")
def boosted(inputs: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame()
    out["boosted"] = inputs["conv_rate"] + inputs["bonus"]
    return out


service = FeatureService(name="mixed", features=[view, boosted])
store.apply([boosted, service])
try:
    got = store.get_online_features(features=service, entity_rows=[{"driver_id": 1001, "bonus": 1.0}]).to_dict()
    print("worked:", got)
    bug = False
except Exception as e:  # noqa: BLE001 - we only care about the message
    print(type(e).__name__ + ":", str(e).replace("\n", " ")[:200])
    bug = "join key" in str(e).lower()
lab.clean(folder)
lab.verdict(bug)
