# evidently #1927: new metric, sequential drift detection on time-ordered batch data

[Issue](https://github.com/evidentlyai/evidently/issues/1927) | Upstream: Open (no comments, no PR) | Lab, 20 Sep 2026: **Reproduced** (feature still missing) on evidently 0.7.23

**What is asked.** A metric that takes the reference data for baseline parameters, then processes the current data in
time order with a sequential detector (CUSUM as a first version) and reports whether drift was detected, the change point
and the control limit.

**Why it matters here.** DriftWatch batches arrive in time order, and today each batch is tested on its own. A sequential
detector would notice a slow shift that no single batch shows.

**Our workaround.** None; nothing breaks. The roadmap lists it.

**How to know it is done.** The repro looks for any metric or preset named sequential, CUSUM or change point. It prints `STATUS: Fixed` once one exists.

**Sprint task (Stretch).** This is a feature. Evidently's CONTRIBUTING asks you to open or comment on an issue first, so
comment with your plan and wait for a maintainer before you write code.

**Not verified.** The repro only checks names. A metric with a different name would be missed.
