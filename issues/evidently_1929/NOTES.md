# evidently #1929: chi_stat_test and g_test return nan on a constant categorical column

[Issue](https://github.com/evidentlyai/evidently/issues/1929) | Upstream: Has PR ([#1932](https://github.com/evidentlyai/evidently/pull/1932), open) | Lab, 20 Sep 2026: **Reproduced** on evidently 0.7.23

**What breaks.** When a categorical column has one category on both sides, `chi_stat_test` and `g_test` return `nan`.
`z_stat_test` returns 1.0 for the same input, which is right: identical data means no drift.
A `nan` is not a p-value, and it also makes our `summary.json` invalid JSON, so the dashboard cannot read it.

**Where it hits DriftWatch.** `fw_ok` never changes (edge case 1 in `src/make_data.py`), and `config.CAT_TEST` is
`chisquare`. In `make drift`, before the workaround, the `fw_ok` score came back as `nan` (we saw this).

**Our workaround.** `workarounds.patch_evidently()` replaces the chi-square implementation in Evidently's stat-test
registry (public `register_stattest`). One category across both series returns `(1.0, False)`. Everything else calls the original.

**How to know it is fixed.** `python issues/evidently_1929/repro.py` prints `STATUS: Fixed`. Then delete `patch_evidently`
and its call in `src/check_drift.py`; `tests/test_workarounds.py::test_constant_column_is_not_nan` must still pass.

**Not verified.** The issue says the drifted *share* also turns `nan`. In our run the share stayed a number while the
column's own score was `nan`. We did not find out why the two differ.

**Sprint task.** Review and test PR #1932 with `make issues` and `make drift` against its branch.
