"""feast #6805: precomputed online retrieval ignores the order of the entity rows, and duplicates.

A FeatureService with precompute_online=True is asked for drivers [1003, 1001, 1003, 1002].
Expected: one answer per requested row, in that order (conv_rate 0.3, 0.1, 0.3, 0.2).
The vectors are written with the online store's own write_precomputed_vector, the way
upstream's tests do: `store.precompute_feature_service` only scans entities on Redis.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lab  # noqa: E402
from feast import FeatureService, FeatureView, Field  # noqa: E402
from feast.protos.feast.core.PrecomputedFeatureVector_pb2 import PrecomputedFeatureVector  # noqa: E402
from feast.protos.feast.types.EntityKey_pb2 import EntityKey  # noqa: E402
from feast.protos.feast.types.Value_pb2 import Value  # noqa: E402
from feast.types import Bytes  # noqa: E402
from google.protobuf.timestamp_pb2 import Timestamp  # noqa: E402

store, view, driver, folder = lab.make_store()
service = FeatureService(name="precomputed", features=[view], precompute_online=True)
store.apply([service])

online = store._get_provider().online_store
table = FeatureView(name="__precomputed__precomputed", entities=[], schema=[Field(name="vector", dtype=Bytes)], source=None)
online.update(config=store.config, tables_to_delete=[], tables_to_keep=[table], entities_to_delete=[], entities_to_keep=[], partial=True)
scores = {1001: 0.1, 1002: 0.2, 1003: 0.3}
for driver_id, score in scores.items():
    stamp = Timestamp()
    stamp.GetCurrentTime()
    vector = PrecomputedFeatureVector(feature_names=["driver_stats__conv_rate"], values=[Value(double_val=score)], precomputed_at=stamp)
    key = EntityKey(join_keys=["driver_id"], entity_values=[Value(int64_val=driver_id)])
    online.write_precomputed_vector(store.config, "precomputed", store.project, key, vector.SerializeToString())

asked = [1003, 1001, 1003, 1002]
resp = store.get_online_features(features=service, entity_rows=[{"driver_id": i} for i in asked], full_feature_names=True).to_dict()
expected = [scores[i] for i in asked]
got = resp["driver_stats__conv_rate"]
print("asked   :", asked)
print("expected:", expected)
print("got     :", got)
lab.clean(folder)
lab.verdict(got != expected)
