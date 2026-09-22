# feast #6842: expose the running Feast version in the UI

[Issue](https://github.com/feast-dev/feast/issues/6842) (closed) | Upstream: **Merged** ([#6843](https://github.com/feast-dev/feast/pull/6843), 17 Sep 2026) | Lab, 20 Sep 2026: **Reproduced** on feast 0.66.0, meaning the release does not have it yet

**Read this first.** The brief that started this project said "PR #6843 exists, review and test only". By 20 Sep it was already merged, and the issue closed.
The merge is on master; the installed 0.66.0 has no `/version` route (404), so the lab still says Reproduced. It flips to Fixed when a release contains the change.

**What was added.** A router in `feast/api/registry/rest/system.py` serving `GET /version`. The merged code answers `{"version": "..."}`. The issue text
says `/api/v1/version` with a `feast_version` key; we followed the merged code, and the repro accepts either path. The UI sidebar label was not tested (needs the Node build).

**Where it hits DriftWatch.** It does not. It would help us show the Feast version on the dashboard from a running server.

**Our workaround.** None. `summary.json` reads the version with `importlib.metadata` instead.

**Sprint task (Review).** Nothing to write. When the next Feast release ships, upgrade, run `make issues`, and confirm this flips to Fixed.
