# evidently #1907: generic test helpers drop alias= for metric-level tests

[Issue](https://github.com/evidentlyai/evidently/issues/1907) | Upstream: Has PR ([#1908](https://github.com/evidentlyai/evidently/pull/1908), open) | Lab, 20 Sep 2026: **Reproduced** on evidently 0.7.23

**What breaks.** `gte()` passes `alias=` to the metric-level test; `gt`, `lt`, `lte`, `eq`, `not_eq`, `is_in` and
`not_in` accept it but only pass it to the descriptor test. The repro runs all eight on a `MeanValue` metric:
seven lose the alias, so the test description starts with the metric's own name.

**Where it hits DriftWatch.** `src/check_drift.py` gates each batch with `share_tests=[lt(SHARE_ALERT, alias="Drift share under limit")]`.
Without a fix the gate label reads "Share of Drifted Columns: Actual value ...".

**Our workaround.** `workarounds.with_alias()` swaps the leading metric name for our alias when Evidently left it out.

**How to know it is fixed.** The repro prints `STATUS: Fixed`. Then remove `with_alias` and use the description as it comes.

**Not verified.** The `@overload` signatures for metric tests do not declare `alias`, so a type checker may complain. We did not run mypy on it.
