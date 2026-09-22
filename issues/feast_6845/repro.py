"""feast #6845: an internal error when creating a feature view through the Feast UI.

The UI form posts to the registry REST API. The handler builds the batch source from the
name alone instead of looking it up in the registry. This posts the same kind of request
the form sends (existing entity, existing data source by name). Expected: 201 Created.
Reproduced means the server refuses it with "Could not identify the source type": the source
was never looked up. The UI shows that as an internal error. No browser needed.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lab  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from feast.api.registry.rest.rest_registry_server import RestRegistryServer  # noqa: E402

store, view, driver, folder = lab.make_store()
client = TestClient(RestRegistryServer(store).app, raise_server_exceptions=False)
body = {
    "name": "made_in_the_ui", "project": "lab", "entities": ["driver"],
    "features": [{"name": "trips", "value_type": 5}], "batch_source": "stats_source", "ttl_seconds": 3600,
}
r = client.post("/feature_views", json=body)
print("POST /feature_views ->", r.status_code, r.text[:160])
lab.clean(folder)
refused = r.status_code >= 400 and "source type" in r.text
if r.status_code != 201 and not refused:
    raise SystemExit(f"unexpected answer {r.status_code}: the repro may be out of date")
lab.verdict(refused)
