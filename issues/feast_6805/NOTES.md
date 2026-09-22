# feast #6805: precomputed online retrieval does not keep entity input order or duplicates

[Issue](https://github.com/feast-dev/feast/issues/6805) | Upstream: Has PR ([#6806](https://github.com/feast-dev/feast/pull/6806), open) | Lab, 20 Sep 2026: **Reproduced** on feast 0.66.0

**What breaks.** With `precompute_online=True`, the read path de-duplicates and sorts the entity keys, reads their vectors, then fills
response rows by position. Asking for drivers `[1003, 1001, 1003, 1002]` returns `[0.1, 0.2, 0.3, None]` instead of `[0.3, 0.1, 0.3, 0.2]`:
the values are in sorted order and the fourth row is empty. This is a wrong-answer bug, not only an ordering nicety.

**How we reproduce it.** `store.precompute_feature_service()` only scans entities on Redis (we read the code), so the repro writes the vectors with the
online store's own `write_precomputed_vector`, as upstream's unit tests do, after creating the vector table with `update()`.

**Where it hits DriftWatch.** It does not. DriftWatch uses the standard online path. That path keeps order and duplicates,
and `make live` checks it for every batch (`online order ok` in the output; `tests/test_live.py`).

**Our workaround.** None needed. If you switch to a precomputed feature service, keep that check.

**How to know it is fixed.** The repro prints `STATUS: Fixed`.

**Sprint task (Medium).** Review PR #6806. Also test the async path: the issue says `get_online_features_async` has the same problem (untested here).
