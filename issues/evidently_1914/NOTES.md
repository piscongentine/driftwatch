# evidently #1914: G-test raises ValueError when reference and current have different sample sizes

[Issue](https://github.com/evidentlyai/evidently/issues/1914) | Upstream: Has PR ([#1913](https://github.com/evidentlyai/evidently/pull/1913), [#1928](https://github.com/evidentlyai/evidently/pull/1928), both open) | Lab, 20 Sep 2026: **Reproduced** on evidently 0.7.23

**What breaks.** `g_test` builds expected counts from the reference and passes them to scipy unchanged. When the two
samples differ in size, scipy refuses: the observed and expected sums must agree. Evidently's `chisquare` test
already scales the expected counts by the size ratio (`chisquare_stattest.py`), so it does not fail.

**Where it hits DriftWatch.** Every live batch (40 rows) is far smaller than the reference (4,001 rows). With
`CAT_TEST = "g_test"` the whole Evidently report aborts on the first batch (we saw this).

**Our workaround.** No code. `config.CAT_TEST = "chisquare"`. That is listed in the docstring of `src/workarounds.py`.
Setting it to `g_test` brings the crash back, which is a quick way to see the bug.

**How to know it is fixed.** The repro prints `STATUS: Fixed`. You may then switch `CAT_TEST` back to `g_test`.

**Not verified.** We did not run the two open PRs. Two PRs fix the same thing differently: compare them.
