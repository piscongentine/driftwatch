# Issue Lab

One folder per real upstream bug that DriftWatch hits or watches. Each folder holds the smallest program that shows the
bug (`repro.py`) and a page that explains it (`NOTES.md`). The lab is how the club finds work for the pull-request sprint.

## Run it

```bash
make issues                              # all 20, four at a time, prints a table and writes out/issues.json
python issues/check_all.py feast_6787    # only some
python issues/feast_6787/repro.py        # one, with its own output
```

Two repros need internet (`evidently_1905`, `evidently_1898`): they read upstream files. Without it they end in **Error**.
Two Feast repros (`feast_6790`, `feast_6815`) define on-demand views, and end in **Error** on Python 3.14 because Feast's `dill` fails there. Use Python 3.13 or older.

## Read the table

| Lab result | Meaning |
|---|---|
| **Reproduced** | The bug is still there with the installed versions of Feast and Evidently |
| **Fixed** | The bug is not seen any more. That means fixed upstream, or never present in this release. The NOTES page says which we know |
| **Error** | The repro itself broke: no internet, or an API it uses changed |

The **upstream** column is a different question: is there a pull request? It comes from [`sprint/ISSUES.md`](../sprint/ISSUES.md).
A merged fix stays "Reproduced" here until a release contains it. That is expected: see `feast_6842`.

## Test an upstream fix

```bash
pip install -U feast evidently           # or install a pull-request branch into a fresh virtualenv
make issues
```

When a row flips to **Fixed**: delete its workaround from `src/workarounds.py` (each is tagged with the issue number), run `make test`,
flip the row in the tracker, and celebrate in the pull request.

## Add a folder

1. Make `issues/<repo>_<number>/` with `repro.py` and `NOTES.md`.
2. `repro.py` is tiny, needs no cloud account, cleans up after itself, and ends with one line: `STATUS: Reproduced` or `STATUS: Fixed`
   (Feast repros can use `lab.make_store()` and `lab.verdict()`). Do not swallow unexpected errors: a crash means **Error**, on purpose.
3. `NOTES.md` says what breaks, where it hits DriftWatch, what our workaround is, how to know it is fixed, and **what you could not verify**.
   Do not guess at upstream behaviour. Link the issue.
4. Add a row to `sprint/ISSUES.md`. Security problems do **not** go here: see `sprint/SPRINT.md`.
