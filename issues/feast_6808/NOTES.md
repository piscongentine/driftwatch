# feast #6808: feast init accepts project names that break the local SQLite template

[Issue](https://github.com/feast-dev/feast/issues/6808) | Upstream: Has PR ([#6809](https://github.com/feast-dev/feast/pull/6809), open) | Lab, 20 Sep 2026: **Reproduced** on feast 0.66.0

**What breaks.** `feast init feast-smoke` succeeds and writes a repo whose `feature_store.yaml` says `project: feast-smoke`. Loading that repo then fails:
"Project names for SQLite online stores cannot contain hyphens because they are used in table names". The repro calls `init_repo`, the function the CLI uses.
The issue says it supersedes #6807, which was closed after being filed from the wrong account.

**Where it hits DriftWatch.** First-run experience: a new member who names their own project with a hyphen. Ours is `driftwatch`, on purpose.

**Our workaround.** None in code. The README tells newcomers to use underscores or plain names.

**How to know it is fixed.** The repro prints `STATUS: Fixed` (init rejects the name, or the local template copes with it).

**Sprint task (Starter).** Review PR #6809.
