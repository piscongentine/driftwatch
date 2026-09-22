# feast #6796: return an empty write payload when Arrow conversion gets a zero-row table

[Issue](https://github.com/feast-dev/feast/issues/6796) | Upstream: Has PR ([#6797](https://github.com/feast-dev/feast/pull/6797), open, updated 20 Sep) | Lab, 20 Sep 2026: **Reproduced** on feast 0.66.0

**What breaks.** `_convert_arrow_fv_to_proto` (and the ODFV twin) read `table.to_batches()[0]`. A zero-row pyarrow Table has no record
batches, so the helper raises `IndexError` instead of returning an empty payload `[]`. The repro calls that private helper directly, as the issue does.

**Public API.** The issue says the public write APIs reject empty frames. In our scratch test on 0.66.0, `store.push()` with an empty
DataFrame returned without an error. We did not investigate why the two differ.

**Where it hits DriftWatch.** The empty live batch (edge case 3) must not be pushed.

**Our workaround.** `workarounds.push_batch()` returns 0 for an empty frame and never calls Feast.

**How to know it is fixed.** The repro prints `STATUS: Fixed`. The repro uses a private function, so a rename makes it end in Error, not Fixed.

**Sprint task (Starter).** Review PR #6797 and its regression test.
