"""evidently #1900: divergence stat tests crash badly, or answer nan, on an empty series.

A clear ValueError is a fine outcome ("this series is empty"). What the issue reports is an
opaque ZeroDivisionError from deep inside get_binned_data, and silent nan results.
Open pull requests for this are evidently #1901 and #1924.
"""
import math
import warnings

import pandas as pd

warnings.filterwarnings("ignore")
from evidently.legacy.calculations.stattests import (  # noqa: E402
    hellinger_stat_test,
    jensenshannon_stat_test,
    kl_div_stat_test,
    psi_stat_test,
)
from evidently.legacy.core import ColumnType  # noqa: E402

empty = pd.Series([], dtype=float)
some = pd.Series([1.0, 2.0, 3.0])
bad = []
for name, test in [("psi", psi_stat_test), ("kl_div", kl_div_stat_test), ("jensenshannon", jensenshannon_stat_test), ("hellinger", hellinger_stat_test)]:
    for label, ref, cur in [("current empty", some, empty), ("reference empty", empty, some)]:
        try:
            score = float(test(reference_data=ref, current_data=cur, feature_type=ColumnType.Numerical, threshold=0.1).drift_score)
            outcome = "nan (silent)" if math.isnan(score) else f"score {score:.3f}"
            if math.isnan(score):
                bad.append((name, label))
        except ValueError as e:
            outcome = "ValueError: " + str(e).splitlines()[0][:50] + "  (clear enough)"
        except Exception as e:  # noqa: BLE001
            outcome = type(e).__name__ + " (opaque)"
            bad.append((name, label))
        print(f"{name:14} {label:16} {outcome}")
print("STATUS:", "Reproduced" if bad else "Fixed")
