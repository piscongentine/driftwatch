# feast #6821: feature view ttl is not applied on the standard online retrieval path

[Issue](https://github.com/feast-dev/feast/issues/6821) | Upstream: **Claimed** (obielin, 7 Sep; no PR found) | Lab, 20 Sep 2026: **Reproduced** on feast 0.66.0

**What breaks.** A feature view with `ttl` of one minute still serves a value that is one hour old, marked `PRESENT`.
Historical retrieval honours `ttl`; online retrieval does not compare the event timestamp with it. The proto already has an
`OUTSIDE_MAX_AGE` status that is not used here.

**Where it hits DriftWatch.** The freshness card. `machine_service` holds an inspection value 30 days old with a 7-day ttl (edge case 5).
Feast serves it as if it were fresh.

**Our workaround.** `workarounds.is_stale()` compares the event timestamp Feast returns with the ttl. `live.py` records the oldest and
newest timestamp per view, `check_drift.py` turns them into age and a stale flag, and `alerts.py` warns.

**How to know it is fixed.** The repro prints `STATUS: Fixed` when the value is missing or marked `OUTSIDE_MAX_AGE`.
Then the stale flag can come from Feast's own status.

**Sprint task (Medium).** Nobody has a PR. obielin asked to work on it on 7 Sep: comment on the issue and ask before starting.

**Also seen.** In 0.66.0, `to_df(include_event_timestamps=True)` returns event timestamps as integer epoch seconds (`live.py` handles both that and real datetimes).
