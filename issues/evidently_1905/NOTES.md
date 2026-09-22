# evidently #1905: examples README links to examples/tutorials/, which does not exist

[Issue](https://github.com/evidentlyai/evidently/issues/1905) | Upstream: Has PR ([#1906](https://github.com/evidentlyai/evidently/pull/1906), open since 27 Jul) | Lab, 20 Sep 2026: **Reproduced**

**What breaks.** `examples/README.md` links `./tutorials/` (and mentions it again further down), but that folder is not
on the `main` branch. The repro downloads the README, then asks GitHub about the folder: `tutorials` answers 404 and `cookbook`
(the control) answers 200. The issue also lists `examples/cookbook/README.md`; we did not check that file.

**Where it hits DriftWatch.** It does not. It is a docs fix, a good first pull request.

**How to know it is fixed.** The repro prints `STATUS: Fixed` (needs internet).

**Sprint task (Starter).** A PR is already open, so review it. One more contributor asked on the issue on 2 Aug whether it was free.
