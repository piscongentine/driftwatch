# About DriftWatch

DriftWatch is a small, open-source, end-to-end example of machine-learning monitoring that runs on a laptop.
It belongs to **PiscongentinexMan** and the contributors who help build it. The same story is on the dashboard's About page (`web/about.html`).

## What it is

Feast keeps the sensor features of a fleet of machines. A small model learns from that history. New batches of readings
arrive, and some of them slowly drift. Evidently compares every batch with the training data, and a dashboard and alerts show what changed.

- A **feature store** is one shared place for the numbers a model uses, so training and serving read the same values.
- **Drift** means the data a model sees today no longer looks like the data it learned from, so its answers quietly get worse.

## What it can do

- **Keep features in Feast:** a file offline store for history, a SQLite online store for the latest values, a point-in-time correct training set.
- **Train and score a model:** the older 60% of history trains it, the next 15% picks its decision threshold, the newest 25% scores it (accuracy, precision, recall, F1, AUC).
- **Watch live batches:** each batch is read back from Feast and tested against the training reference. Empty and tiny batches are handled, not hidden.
- **Raise alerts:** the drifted share passes a limit, a column keeps drifting, a feature view goes stale, or a batch could not be tested.
- **Check itself:** we plant the drift, so the detector's own precision and recall are measured and tested.
- **Feed a PR sprint:** the Issue Lab holds one tiny reproduction per real upstream bug; a four-week plan turns them into reviews and pull requests.

## Why it is needed

Models fail quietly when their inputs move, and most students meet drift only in slides. Feast and Evidently are usually taught apart, but the hard
questions live where they meet: what is the reference, where do live batches come from, what happens with an empty batch or a constant column?
New contributors also need a safe way into open source: small, current, reproducible tasks with a clear expected result.

## How it compares (honestly)

DriftWatch does **not** replace production tools. Feast now ships its own feature monitoring, Evidently has a monitoring UI and a hosted product,
and managed platforms do much more.

**Where DriftWatch fits better**
- Small enough to read in twenty minutes: one job per file, about 150 lines at most.
- No cloud account, no paid keys, no web framework, no npm build.
- It shows the join itself: Feast as the source of truth, Evidently as the checker, with the edge cases left in on purpose.
- It has a built-in path to contribute: the Issue Lab and the sprint.

**Where to use something else**
- Real production monitoring, scheduling, authentication and many users.
- Real data. Ours is synthetic, and the model's marks say nothing about real fleets.
- Anything at scale. DriftWatch runs on one machine, on local files.

## What the reproduced bugs mean

The Issue Lab runs one small program for each of 20 real upstream bugs. **Reproduced** means we still see the bug in the installed version.
For each one, in short: why it happens, what it means, the trouble it can cause, and how it can be fixed. The [README](README.md#what-each-lab-result-means-and-how-it-can-be-fixed) has the full table, with the pull requests.

**Evidently**

- **[Evidently #1929](https://github.com/evidentlyai/evidently/issues/1929), nan on a constant column.** Why: one category leaves nothing to compare. Means: the score is not a number. Trouble: nan breaks totals and JSON. Fix: return p = 1.0.
- **[Evidently #1914](https://github.com/evidentlyai/evidently/issues/1914), G-test fails when sample sizes differ.** Why: expected counts are not rescaled. Means: it only works on equal-size samples. Trouble: the whole report aborts. Fix: rescale the counts, or use chi-square.
- **[Evidently #1900](https://github.com/evidentlyai/evidently/issues/1900), divergence tests on empty data.** Why: nothing checks for an empty series. Means: a crash or a silent nan. Trouble: monitoring stops, or goes on with a bad number, when data goes missing. Fix: raise a clear ValueError.
- **[Evidently #1907](https://github.com/evidentlyai/evidently/issues/1907), alias= is dropped.** Why: seven helpers do not pass it on. Means: the name you give a test is ignored. Trouble: reports and alerts show the wrong label. Fix: pass alias through.
- **[Evidently #1927](https://github.com/evidentlyai/evidently/issues/1927), no sequential drift metric.** Why: a missing feature; batches are tested one by one. Means: slow drift stays hidden. Trouble: it is noticed late. Fix: add a CUSUM metric (ask the maintainers first).
- **[Evidently #1902](https://github.com/evidentlyai/evidently/issues/1902), no calibration metric.** Why: a missing feature. Means: you cannot check that confidence matches accuracy. Trouble: an over-confident model goes unnoticed. Fix: add ECE and a reliability diagram.
- **[Evidently #1905](https://github.com/evidentlyai/evidently/issues/1905), dead link in the docs.** Why: the linked folder is not on main. Means: a docs error, not a code bug. Trouble: newcomers land on a 404. Fix: correct the link.
- **[Evidently #1898](https://github.com/evidentlyai/evidently/issues/1898), quickstart lacks openai.** Why: the install line leaves it out. Means: the guide fails as written. Trouble: a new user gets stuck. Fix: add openai to the docs.
- **[Evidently #1910](https://github.com/evidentlyai/evidently/issues/1910), litestar 3 import path.** Why: an import path that litestar 3 removed. Means: a future break; fine today. Trouble: evidently ui may fail on litestar 3. Fix: import from litestar.plugins.pydantic.

**Feast**

- **[Feast #6787](https://github.com/feast-dev/feast/issues/6787), rows silently dropped.** Why: rows with the same key and time collapse into one. Means: fewer rows than you asked for, and no error. Trouble: lost rows and labels in training data. Fix: give each row a unique id.
- **[Feast #6817](https://github.com/feast-dev/feast/issues/6817), empty entity frame (not seen on 0.66.0).** Why: per the issue, a row-wise step fails on empty input. Means: a crash instead of an empty result. Trouble: a job with zero rows can crash. Fix: handle the empty case.
- **[Feast #6819](https://github.com/feast-dev/feast/issues/6819), empty online request.** Why: nothing checks for zero rows. Means: an error instead of an empty answer. Trouble: an HTTP 500 looks like an outage. Fix: return an empty result.
- **[Feast #6796](https://github.com/feast-dev/feast/issues/6796), empty Arrow table.** Why: it reads the first batch of a table that has none. Means: an internal helper crashes. Trouble: an empty push can stop a pipeline. Fix: return early.
- **[Feast #6805](https://github.com/feast-dev/feast/issues/6805), precomputed retrieval loses order.** Why: results are filled by position after sorting. Means: answers do not match questions. Trouble: silently wrong values. Fix: map results back to the request rows.
- **[Feast #6821](https://github.com/feast-dev/feast/issues/6821), ttl not enforced online.** Why: online reads skip the age check. Means: old values look fresh. Trouble: predictions from stale data. Fix: enforce ttl online.
- **[Feast #6808](https://github.com/feast-dev/feast/issues/6808), hyphenated project name.** Why: init skips the SQLite naming rule. Means: init succeeds, then loading fails. Trouble: a broken first project. Fix: reject the name.
- **[Feast #6790](https://github.com/feast-dev/feast/issues/6790), join key dropped.** Why: a shared name is treated as request data only. Means: valid input is rejected. Trouble: a misleading error when serving. Fix: also count it as a join key.
- **[Feast #6845](https://github.com/feast-dev/feast/issues/6845), UI cannot create a feature view.** Why: the handler builds the source from a name only. Means: creating a view fails. Trouble: an internal error in the UI. Fix: resolve the source from the registry.
- **[Feast #6842](https://github.com/feast-dev/feast/issues/6842), version not in the UI (merged, not released).** Why: the fix is on master but not in 0.66.0. Means: wait for a release. Trouble: little; harder support. Fix: upgrade when it is released.
- **[Feast #6815](https://github.com/feast-dev/feast/issues/6815), on-demand function loses globals.** Why: it is rebuilt from source text alone. Means: it works where defined, not where served. Trouble: NameError when serving. Fix: change the serialization; keep functions self-contained.

## Open source

Apache-2.0, the same license as both projects it builds on. Contributions are welcome: see [CONTRIBUTING.md](CONTRIBUTING.md).

## Inspired by

- **[Feast](https://github.com/feast-dev/feast)** (feast-dev): the open-source feature store.
- **[Evidently](https://github.com/evidentlyai/evidently)** (Evidently AI): the open-source library to evaluate, test and monitor ML and LLM systems.

DriftWatch is an independent club project. It is not affiliated with, endorsed by, or sponsored by Feast, its maintainers, or Evidently AI.
Their names belong to their owners. All data in this repository is synthetic.
