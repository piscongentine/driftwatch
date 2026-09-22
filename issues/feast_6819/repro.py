"""feast #6819: an online request with zero entity rows fails instead of returning an empty result.

Two places show it. The SDK call raises an IndexError. The feature server answers HTTP 500 for an empty
key list and for no entities at all; both are asked here with FastAPI's test client, no real server needed.
An open pull request for this is feast #6820.
"""
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lab  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from feast.feature_server import get_app  # noqa: E402

logging.disable(logging.CRITICAL)  # the server logs a traceback for every 500; the status codes are what we read
store, view, driver, folder = lab.make_store()
features = ["driver_stats:conv_rate"]
print("SDK, one row  :", store.get_online_features(features=features, entity_rows=[{"driver_id": 1001}]).to_dict())
try:
    print("SDK, zero rows:", store.get_online_features(features=features, entity_rows=[]).to_dict())
    sdk_bug = False
except IndexError as e:
    print("SDK, zero rows: IndexError:", e)
    sdk_bug = True

client = TestClient(get_app(store), raise_server_exceptions=False)
http_bug = False
for name, entities in {"one row": {"driver_id": [1001]}, "empty key list": {"driver_id": []}, "no entities": {}}.items():
    code = client.post("/get-online-features", json={"features": features, "entities": entities}).status_code
    print(f"HTTP, {name:14}: {code}")
    http_bug = http_bug or code >= 500
lab.clean(folder)
lab.verdict(sdk_bug or http_bug)
