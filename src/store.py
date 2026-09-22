"""Open the Feast store that every script uses. It applies the repo definitions first; repeating is safe.

Reads : feature_repo/ (feature_store.yaml, entities.py, views.py); Feast checks that out/data/*.parquet exist.
Writes: out/feast/registry.db and out/feast/online.db (Feast's own files).
"""
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # lets `import config` work when run as a script
import config  # noqa: E402

warnings.filterwarnings("ignore", category=DeprecationWarning)  # Feast is chatty about upcoming renames


def open_store():
    """Return a FeatureStore with our entity and feature views registered."""
    from feast import FeatureStore

    sys.path.insert(0, str(config.REPO))  # the repo files import each other by name, like `feast apply` does
    import entities
    import views

    (config.OUT / "feast").mkdir(parents=True, exist_ok=True)
    store = FeatureStore(repo_path=str(config.REPO))
    store.apply([entities.machine, views.stats_view, views.service_view])
    return store
