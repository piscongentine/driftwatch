"""feast #6842: expose the running Feast version through the registry REST API (and the UI).

Merged upstream on 2026-09-17 (PR #6843). The merged code adds GET /version. This asks the
installed release for it. Reproduced here means: your installed Feast does not have it yet.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lab  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from feast.api.registry.rest.rest_registry_server import RestRegistryServer  # noqa: E402
from feast.version import get_version  # noqa: E402

store, view, driver, folder = lab.make_store()
client = TestClient(RestRegistryServer(store).app, raise_server_exceptions=False)
print("installed feast:", get_version())
found = None
for path in ("/version", "/api/v1/version"):
    r = client.get(path)
    print(f"GET {path:16} -> {r.status_code} {r.text[:60]}")
    if r.status_code == 200:
        found = path
lab.clean(folder)
lab.verdict(found is None)
