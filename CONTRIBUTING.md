# Contributing to DriftWatch

Welcome. This repo is small on purpose, so a change is easy to read and easy to review. For the upstream work (pull requests to Feast and Evidently)
read [sprint/SPRINT.md](sprint/SPRINT.md) first: upstream rules beat ours.

## Set up

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
make setup                                              # pip install -r requirements.txt
make all && make test                                   # data, train, live, drift, then the tests (about 30 s)
```

No `make`? Every recipe in the [Makefile](Makefile) is one Python command; run them by hand, or on Windows `winget install ezwinports.make`.
Python 3.10 or newer. No cloud account and no paid key is ever needed.

## Branches and commits

- Fork, then branch from `main`: `feat/short-name`, `fix/short-name`, `docs/short-name`, or `sprint/feast-6821-ttl` for sprint work.
- Commit messages: `type: Subject`, imperative, capital after the colon, 72 characters or fewer. Types: feat, fix, docs, test, refactor, chore, ci.
  Example: `fix: Keep duplicate readings in the training set`.
- One idea per commit and per pull request. Feast upstream also needs `git commit -s` (sign-off); it does no harm here.

## Code style (the tests check most of this)

- Python 3.10+, and only `feast`, `evidently`, `pandas`, `scikit-learn`, `pytest`. No web framework. The dashboard is plain HTML, CSS and JavaScript with no build step.
- One job per file, **about 150 lines at most**. Short clear names (`ref`, `cur`, `df`, `score`), short functions, comments that say *why*.
- Every file starts with a header that says **what it does, what it reads, what it writes**.
- Every setting is a constant in `config.py`. Every step reads and writes files under `out/`. No hidden state.
- A workaround for an upstream bug goes in `src/workarounds.py`, tagged with the issue number, with a test that names the issue.
- No emoji anywhere, in code, docs or the UI.

## Review checklist

- [ ] `make test` passes, and CI is green
- [ ] New behaviour has a test that fails without the change
- [ ] Nothing over about 150 lines; headers present; only the allowed libraries
- [ ] `config.py` holds any new number; `README.md` table updated if you added a constant
- [ ] Dashboard changes checked in light and dark, on a phone width, and with reduced motion
- [ ] Anything you could not verify is written down in the pull request
- [ ] You can explain every line, including any a tool wrote for you

## Add a test

Tests live in `tests/`. Small pure logic goes in a plain test with a fake object (see `test_workarounds.py`). Anything that needs Feast
or Evidently end to end uses the `project` fixture in `conftest.py`: it runs the real pipeline once in a temporary copy of the repo, so tests never touch `out/`.

## Add a drift feature (a new monitored column)

1. Generate it in `src/make_data.py` (`make_rows`) and add it to `config.NUMERIC` or `config.CATEGORICAL`, and to the Feast schema in `feature_repo/views.py`.
2. `make all`. The column appears in `summary.json` and on the dashboard by itself.
3. Add a test in `tests/test_make_data.py`, and check `test_pipeline.py` still holds.

## Add an Issue Lab folder

Follow [issues/README.md](issues/README.md): `repro.py` (tiny, ends with `STATUS:`), `NOTES.md`, and a row in `sprint/ISSUES.md`.

## Security

Never open a public issue or pull request about a vulnerability, in this repo or upstream, and never post exploit details. Report it privately to the
project's maintainers (Feast: GitHub advisory form and `SECURITY.md`).

## Be kind

Be patient with maintainers and with each other. Never ping repeatedly. Follow each project's code of conduct.
