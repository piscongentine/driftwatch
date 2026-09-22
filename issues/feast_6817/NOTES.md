# feast #6817: get_historical_features raises TypeError on a zero-row entity_df

[Issue](https://github.com/feast-dev/feast/issues/6817) | Upstream: Has PR ([#6818](https://github.com/feast-dev/feast/pull/6818), open) | Lab, 20 Sep 2026: **Fixed here, meaning not reproduced** on feast 0.66.0

**Read this first.** The reporter used **master at commit 5ad5592** (Python 3.11, dask 2026.8.0). We ran the issue's own construction
(an empty list for the key column, an empty UTC timestamp column) on the **released 0.66.0**, with dask 2026.8.0 and Python 3.13, and got
an empty frame `(0, 3)` instead of a `TypeError`. The suspect code, `_normalize_timestamp` with a row-wise `apply`, is the same in 0.66.0
and in the master we cloned, so we do not know why 0.66.0 does not fail. It may be a difference we did not find, or the bug may need master.
"Fixed" in this lab means "not seen with the installed versions"; it does not prove upstream fixed anything.

**Where it hits DriftWatch.** An empty live batch pulled back with `get_historical_features` (edge case 3).

**Our workaround.** `workarounds.pull_features()` returns an empty frame for an empty entity frame before calling Feast. It is harmless on 0.66.0.

**How to know it is fixed on master.** Install Feast from the PR branch or from master and run `python issues/feast_6817/repro.py`.
We could not do that here (untested).

**Sprint task (Starter).** Test PR #6818 against master: does the zero-row call fail before the PR and pass after?
