# feast #6815: on-demand feature view UDFs lose module globals when rebuilt from the registry

[Issue](https://github.com/feast-dev/feast/issues/6815) | Upstream: Has PR ([#6816](https://github.com/feast-dev/feast/pull/6816), open) | Lab, 20 Sep 2026: **Reproduced** on feast 0.66.0

**What breaks.** An on-demand view whose function calls a module-level helper or reads a module-level constant works in the process that defined it,
and fails with `NameError: name 'scaled' is not defined` in a process that only has the registry (a feature server). Per the issue, Feast rebuilds the
function from its source text alone and never falls back to the serialized body.

**How we reproduce it.** Two processes: A defines and applies the view from a script, B opens the registry and asks for the feature. B prints the NameError.

**Where it hits DriftWatch.** Not yet: no on-demand views. It would bite the day we serve one.

**Our workaround.** None. Keep on-demand functions self-contained (everything inside the function body).

**How to know it is fixed.** The repro prints `STATUS: Fixed`.

**Python 3.14.** On Python 3.14 this repro ends in **Error**: applying the on-demand view already fails with `TypeError: _Pickler._batch_setitems() missing 1 required positional argument: 'obj'`,
raised while Feast serialises it with `dill` (0.3.9 here). Use Python 3.13 or older. (Seen on 21 Sep 2026 with feast 0.66.0, on Windows and on Debian.) We did not report this upstream.

**Sprint task (Stretch).** Deeper change in Feast's serialization. Review PR #6816; read the comments before you comment.
