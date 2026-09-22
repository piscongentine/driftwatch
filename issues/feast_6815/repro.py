"""feast #6815: an on-demand view's UDF loses its module-level names when rebuilt from the registry.

Process A defines the view in a script (a helper and a constant live at module level) and
applies it. Process B only has the registry, like a feature server does, and asks for the
feature. Expected: it works. The issue reports NameError.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lab  # noqa: E402

LAB_DIR = str(Path(__file__).resolve().parents[1])
DEFINE = f'''
import sys
sys.path.insert(0, {LAB_DIR!r})
import lab
import pandas as pd
from feast import Field
from feast.on_demand_feature_view import on_demand_feature_view
from feast.types import Float64

store, view, driver, folder = lab.make_store()
SCALE = 100.0


def scaled(x):
    return x * SCALE


@on_demand_feature_view(sources=[view], schema=[Field(name="conv_rate_scaled", dtype=Float64)], mode="pandas")
def scaled_rate(inputs: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame()
    out["conv_rate_scaled"] = scaled(inputs["conv_rate"])
    return out


store.apply([scaled_rate])
print(folder)
'''
READ = '''
import sys
from feast import FeatureStore
store = FeatureStore(repo_path=sys.argv[1] + "/repo")
try:
    print(store.get_online_features(features=["scaled_rate:conv_rate_scaled"], entity_rows=[{"driver_id": 1001}]).to_dict())
except NameError as e:
    print("NameError:", e)
    sys.exit(3)
'''

work = Path(tempfile.mkdtemp(prefix="dw_lab_"))
(work / "define.py").write_text(DEFINE)
(work / "read.py").write_text(READ)
made = subprocess.run([sys.executable, str(work / "define.py")], capture_output=True, text=True, check=True)
folder = made.stdout.strip().splitlines()[-1]
read = subprocess.run([sys.executable, str(work / "read.py"), folder], capture_output=True, text=True)
print("process B said:", (read.stdout.strip().splitlines() or ["(nothing)"])[-1])
if read.returncode not in (0, 3):
    print(read.stderr[-400:])
    raise SystemExit("process B failed in an unexpected way")
lab.clean(work)
lab.clean(folder)
lab.verdict(read.returncode == 3)
