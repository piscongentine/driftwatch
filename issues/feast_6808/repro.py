"""feast #6808: `feast init` accepts a project name that the local SQLite template then rejects.

`feast init feast-smoke` succeeds, but loading the repository it just wrote fails, because
SQLite online store table names cannot contain hyphens. Uses the same function the CLI calls.
"""
import os
import sys
import tempfile
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
os.environ.setdefault("FEAST_USAGE", "False")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lab  # noqa: E402
from feast import FeatureStore  # noqa: E402
from feast.repo_config import FeastConfigError  # noqa: E402
from feast.repo_operations import init_repo  # noqa: E402

work = Path(tempfile.mkdtemp(prefix="dw_lab_"))
here = os.getcwd()
os.chdir(work)
try:
    init_repo("feast-smoke", "local")
    print("feast init feast-smoke: accepted, wrote", sorted(p.name for p in (work / "feast-smoke").iterdir()))
    try:
        FeatureStore(repo_path=str(work / "feast-smoke" / "feature_repo"))
        print("loading the new repo: worked")
        bug = False
    except FeastConfigError as e:
        print("loading the new repo failed:", str(e).replace("\n", " ")[:190])
        bug = "hyphen" in str(e).lower()
finally:
    os.chdir(here)
    lab.clean(work)
lab.verdict(bug)
