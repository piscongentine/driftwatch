# evidently #1910: litestar.contrib.pydantic was removed in litestar 3.0

[Issue](https://github.com/evidentlyai/evidently/issues/1910) | Upstream: Has PR ([#1919](https://github.com/evidentlyai/evidently/pull/1919), open; [#1912](https://github.com/evidentlyai/evidently/pull/1912), draft) | Lab, 20 Sep 2026: **Reproduced** (the cause, not a crash)

**What breaks.** `evidently/utils/schema.py` imports `PydanticSchemaPlugin` from `litestar.contrib.pydantic`, a path the
issue says was removed in litestar 3.0. The issue's follow-up says `litestar.plugins.pydantic` exists since litestar 2.19.0,
Evidently's own floor, so a plain import swap is enough.

**Nothing crashes today.** Our environment resolved litestar 2.24.0, where the old path still works. The repro therefore checks
the cause: the installed evidently still contains the old import. It prints the litestar version so you can see the gap.

**Where it hits DriftWatch.** Our dashboard is static and does not use `evidently ui`. If you run `evidently ui` on
litestar 3, expect a crash on import.

**Our workaround.** `requirements.txt` pins evidently. If `evidently ui` fails after an upgrade, check the litestar version first.

**Checked on 21 Sep 2026:** PyPI lists litestar up to **2.24.0**, and nothing newer even with pre-releases included (`pip index versions litestar --pre`).
There is no litestar 3 to install, so the crash cannot be triggered by any installable version yet. Only the cause (the old import) can be seen.
**Not verified:** what the crash looks like on litestar 3, because it does not exist on PyPI.
