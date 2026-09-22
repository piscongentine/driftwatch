"""evidently #1907: the generic test helpers drop alias= when used as a metric-level test.

gte() forwards the alias; the issue says the other helpers only forward it to descriptor tests.
We run every helper on a Report metric and look for the alias in the test's description.
An open pull request for this is evidently #1908.
"""
import warnings

import pandas as pd

warnings.filterwarnings("ignore")
from evidently import Report  # noqa: E402
from evidently.metrics import MeanValue  # noqa: E402
from evidently.tests import eq, gt, gte, is_in, lt, lte, not_eq, not_in  # noqa: E402

ALIAS = "quality gate"
data = pd.DataFrame({"score": [0.0, 1.0]})
cases = {
    "gte": gte(1, alias=ALIAS), "gt": gt(1, alias=ALIAS), "lt": lt(1, alias=ALIAS), "lte": lte(1, alias=ALIAS),
    "eq": eq(1, alias=ALIAS), "not_eq": not_eq(1, alias=ALIAS), "is_in": is_in([1], alias=ALIAS), "not_in": not_in([1], alias=ALIAS),
}
dropped = []
for name, test in cases.items():
    text = Report([MeanValue(column="score", tests=[test])]).run(data).tests_results[0].description
    kept = text.startswith(ALIAS)
    print(f"{name:7} alias {'kept   ' if kept else 'DROPPED'} -> {text[:60]}")
    if not kept:
        dropped.append(name)
print("STATUS:", "Reproduced" if dropped else "Fixed")
