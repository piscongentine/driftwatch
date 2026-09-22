# evidently #1902: Expected Calibration Error (ECE) and reliability diagrams

[Issue](https://github.com/evidentlyai/evidently/issues/1902) | Upstream: Has PR, related ([#1896](https://github.com/evidentlyai/evidently/pull/1896), open, not linked to this issue) | Lab, 20 Sep 2026: **Reproduced** (feature still missing) on evidently 0.7.23

**What is asked.** An `ExpectedCalibrationError` metric (with `n_bins`, uniform or quantile bins, and a maximum
calibration error) and a reliability diagram that plots confidence against accuracy per bin.

**Related work.** PR #1896 adds `BrierScore` and `ECE` metrics and says it closes #1895. Its description does not mention a
reliability diagram. Whether it covers one is not verified: read the PR before claiming this issue.

**Why it matters here.** The dashboard has no model-quality panel yet. The roadmap lists a calibration panel.

**How to know it is done.** The repro needs both a calibration-error metric and a reliability diagram by name; it prints `STATUS: Fixed` only then.

**Sprint task (Stretch).** Comment on the issue and on PR #1896 first. Evidently's CONTRIBUTING asks for an issue before a PR.
