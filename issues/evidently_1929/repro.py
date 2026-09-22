"""evidently #1929: chi_stat_test and g_test return nan when a categorical column has one category.

Identical constant columns mean no drift, so a p-value of 1.0 is expected (z_stat_test says so).
A nan is not a p-value and poisons anything that averages or counts drift scores.
An open pull request for this is evidently #1932.
"""
import math
import warnings

import pandas as pd

warnings.filterwarnings("ignore")
from evidently.legacy.calculations.stattests import chi_stat_test, g_test, z_stat_test  # noqa: E402
from evidently.legacy.core import ColumnType  # noqa: E402

same = pd.Series(["a"] * 50)
nan_from = []
for name, test in [("chi_stat_test", chi_stat_test), ("g_test", g_test), ("z_stat_test", z_stat_test)]:
    r = test(reference_data=same, current_data=same, feature_type=ColumnType.Categorical, threshold=0.05)
    score = float(r.drift_score)
    print(f"{name:14} drift_score={score}  drifted={bool(r.drifted)}")
    if math.isnan(score):
        nan_from.append(name)
print("STATUS:", "Reproduced" if nan_from else "Fixed")
