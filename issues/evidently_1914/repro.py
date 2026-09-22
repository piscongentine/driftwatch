"""evidently #1914: g_test raises ValueError when reference and current have different sample sizes.

Same 50/50 split of two categories, 1000 rows against 100 rows. Expected: p close to 1, no drift.
Live batches are always smaller than the training reference, so this is our everyday case.
Open pull requests for this are evidently #1913 and #1928.
"""
import warnings

import pandas as pd

warnings.filterwarnings("ignore")
from evidently.legacy.calculations.stattests import g_test  # noqa: E402
from evidently.legacy.core import ColumnType  # noqa: E402

reference = pd.Series(["a"] * 500 + ["b"] * 500)
current = pd.Series(["a"] * 50 + ["b"] * 50)
try:
    r = g_test(reference_data=reference, current_data=current, feature_type=ColumnType.Categorical, threshold=0.05)
    print(f"drift_score={float(r.drift_score):.3f}  drifted={bool(r.drifted)}")
    bug = False
except ValueError as e:
    print("ValueError:", str(e).splitlines()[0][:110])
    bug = True
print("STATUS:", "Reproduced" if bug else "Fixed")
