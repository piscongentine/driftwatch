# feast #6787: get_historical_features on the file store drops entity rows that share a join key and timestamp

[Issue](https://github.com/feast-dev/feast/issues/6787) | Upstream: Has PR ([#6786](https://github.com/feast-dev/feast/pull/6786), open) | Lab, 20 Sep 2026: **Reproduced** on feast 0.66.0 (3 rows in, 2 out)

**What breaks.** On the Dask/file offline store, entity rows with the same join key and event timestamp are collapsed into one,
and the columns the caller attached (labels, order ids) of the dropped row are lost. Per the issue, DuckDB and the SQL stores carry a
per-row unique id and are not affected.

**Where it hits DriftWatch.** Edge case 4: machine 1 reports twice at one timestamp, so `labels.parquet` has two entity rows with
the same key. The training set silently loses a row.

**Our workaround.** `workarounds.pull_features()` asks Feast for the unique (key, timestamp) rows, then merges the answer back
onto the full entity frame. `make train` prints `rows lost: 0`.

**How to know it is fixed.** The repro prints `STATUS: Fixed`. Then replace `pull_features` with a plain `get_historical_features` call;
`tests/test_workarounds.py::test_duplicate_entity_rows_are_kept` must still pass.

**Sprint task (Medium).** PR #6786 is open. Review and test it. Feast needs signed-off commits (`git commit -s`) and a conventional PR title.
