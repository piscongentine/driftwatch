# feast #6790: join key value dropped when it shares a name with an OnDemandFeatureView RequestSource field

[Issue](https://github.com/feast-dev/feast/issues/6790) | Upstream: Has PR ([#6794](https://github.com/feast-dev/feast/pull/6794), open) | Lab, 20 Sep 2026: **Reproduced** on feast 0.66.0

**What breaks.** A FeatureService mixes a regular view (join key `driver_id`) and an on-demand view whose `RequestSource` also has a field
`driver_id`. `get_online_features` classifies the name as request data only, so the regular view never receives its join key and raises
`Missing join key values for keys: ['driver_id']`, although the value was provided. `get_historical_features` handles the same input.

**Where it hits DriftWatch.** Not yet. We have no on-demand view. Adding one with a request field called `machine_id` would hit it.

**Our workaround.** None. Name request fields differently from join keys.

**How to know it is fixed.** The repro prints `STATUS: Fixed`.

**Python 3.14.** On Python 3.14 this repro ends in **Error**, not Reproduced: `TypeError: _Pickler._batch_setitems() missing 1 required positional argument: 'obj'`.
Feast serialises an on-demand view with `dill` (0.3.9 here), and per the error text its pickler does not match Python 3.14's. Use Python 3.13 or older for this one.
(Seen on 21 Sep 2026 with feast 0.66.0, on Windows and on Debian.) We did not report this upstream.

**Sprint task (Medium).** Review PR #6794.
