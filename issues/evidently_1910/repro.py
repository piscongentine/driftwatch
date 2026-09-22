"""evidently #1910: litestar.contrib.pydantic was removed in litestar 3.0, and evidently still imports it.

Nothing crashes today: the installed litestar is older than 3.0, so the old path still exists.
So this checks the cause instead of waiting for the crash: does the installed evidently still
import from litestar.contrib.pydantic? Reproduced means yes, and it will break on litestar 3.
Open pull requests for this are evidently #1912 and #1919.
"""
import importlib.util
from importlib.metadata import version
from pathlib import Path

spec = importlib.util.find_spec("evidently.utils.schema")
source = Path(spec.origin).read_text(encoding="utf-8")
old = "litestar.contrib.pydantic" in source
new = "litestar.plugins.pydantic" in source
print("installed litestar:", version("litestar"), "| evidently:", version("evidently"))
print("evidently/utils/schema.py imports litestar.contrib.pydantic:", old)
print("evidently/utils/schema.py imports litestar.plugins.pydantic:", new)
print("old path importable in this environment:", importlib.util.find_spec("litestar.contrib.pydantic") is not None)
print("STATUS:", "Reproduced" if old else "Fixed")
