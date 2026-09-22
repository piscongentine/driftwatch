# feast #6819: online requests with zero entity rows return HTTP 500 instead of an empty result or a 400

[Issue](https://github.com/feast-dev/feast/issues/6819) | Upstream: Has PR ([#6820](https://github.com/feast-dev/feast/pull/6820), open) | Lab, 20 Sep 2026: **Reproduced** on feast 0.66.0

**What breaks.** `store.get_online_features(features=[...], entity_rows=[])` raises `IndexError: list index out of range`.
The feature server also answers **HTTP 500** to a request with an empty key list (`{"driver_id": []}`) and to one with no entities at all (`{}`).
A request with one entity row answers 200.

**Verified on 21 Sep 2026, feast 0.66.0:** all three failing shapes reproduce, with the messages the issue quotes ("Missing join key values for keys: []" and 'pop from an empty set').
The HTTP checks use FastAPI's test client on `feast.feature_server.get_app`, not a real `feast serve` process.

**Where it hits DriftWatch.** The empty live batch (edge case 3): reading back "what the model is served right now" for zero machines.

**Our workaround.** `workarounds.online_rows()` returns an empty frame for an empty id list and only calls Feast when there is something to ask.

**How to know it is fixed.** The repro prints `STATUS: Fixed`. Then call `get_online_features` directly.

**Sprint task (Starter).** Review PR #6820, and test the two HTTP shapes with a feature server (`feast serve`).
