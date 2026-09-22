# feast #6845: internal error when creating a feature view through the Feast UI

[Issue](https://github.com/feast-dev/feast/issues/6845) | Upstream: Has PR ([#6849](https://github.com/feast-dev/feast/pull/6849), open; patelchaitany claimed it on 18 Sep) | Lab, 20 Sep 2026: **Reproduced** on feast 0.66.0

**What breaks.** The UI's create form posts to the registry REST API (`POST /feature_views`). The handler builds the batch source from the name only,
so the registry answers `Could not identify the source type being added` (HTTP 422 in our run). PR #6849's title says it resolves the batch source name against the registry.
The reporter saw "an internal error" in the UI on Windows with 0.66.0.

**How we reproduce it.** In-process, with FastAPI's test client against `RestRegistryServer`. No browser, no Node. It needs the `feast[grpcio]` extra, which `requirements.txt` includes.

**Not verified.** We did not open the UI, so we did not see the message the reporter saw, and we do not know whether the Windows detail matters. The issue text is short and gives only
`feast init`, `feast apply`, `feast ui`.

**Where it hits DriftWatch.** Only if a student uses `feast ui` to add a view.

**How to know it is fixed.** The repro prints `STATUS: Fixed` when the POST answers 201.

**Sprint task (Medium).** Review and test PR #6849. Feast UI changes have their own guide (`ui/CONTRIBUTING.md` upstream).
