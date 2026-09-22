# evidently #1900: divergence stat tests crash or return wrong results on edge-case input

[Issue](https://github.com/evidentlyai/evidently/issues/1900) | Upstream: Has PR ([#1901](https://github.com/evidentlyai/evidently/pull/1901), [#1924](https://github.com/evidentlyai/evidently/pull/1924), both open) | Lab, 20 Sep 2026: **Reproduced** on evidently 0.7.23

**What breaks.** With an empty series, `psi`, `kl_div` and `jensenshannon` raise an opaque `ZeroDivisionError`, and
`hellinger` silently returns `nan` (we saw all of this, for both an empty reference and an empty current).
The issue also lists two more cases that our repro does not test: both series empty (a `min()` error) and
values completely outside the reference range (all counted in the last bin).

**Where it hits DriftWatch.** Empty and tiny live batches (`EMPTY_BATCH`, `TINY_BATCH` in `config.py`). DriftWatch uses
the K-S test and chi-square, not the divergence tests, so it would only hit this if you switch `NUM_TEST` to `psi` or similar.

**Our workaround.** `config.MIN_ROWS = 5`: batches below it are never sent to any test, and alerts.py reports them as untested.

**How to know it is fixed.** The repro prints `STATUS: Fixed`. A clear `ValueError` on an empty series counts as fixed
(PR #1924 does that); an opaque crash or a silent `nan` does not.

**Sprint task.** ArjunPakhan claimed this on 20 Jul; two PRs are open. Review and test, do not start a third.
