# PR Sprint

Four weeks, one goal: turn the Issue Lab into pull requests that upstream maintainers are glad to receive.
The tracker is [ISSUES.md](ISSUES.md). Run `python sprint/count.py` for the live numbers.

## The situation on 20 Sep 2026

We opened every issue before writing the plan. **Nearly all of them already have a pull request** (17 of 20), one more is merged, one is claimed,
one is open. So the honest plan is: **review and test first, write new code only where nobody has**. A competing pull request
wastes a maintainer's time and ours.

## Rules

1. **Pick one row** in `ISSUES.md` and put your name in **Owner** through a pull request to this repo that edits the table.
2. **Read the upstream issue and every comment.** If a pull request exists, do not start another. Review it, run it, test it, and comment what you found.
3. **Say you want it.** Comment on the upstream issue with what you plan to change, then wait for a maintainer or a short pause before you code.
   Evidently asks for an issue first and, for UI changes, a chat on its Discord before you start. Feast uses lazy consensus, and asks for a draft PR or an issue.
4. **Reproduce first** with the matching `issues/<name>/repro.py`. A code pull request needs a test that fails before your fix and passes after.
5. **Follow the upstream repo, not our habits:**
   - *Evidently* (default branch `main`): fork, branch, `pip install -e ".[dev,llm]"`, run **ruff** (`ruff check`, `ruff format`), **mypy** and `pytest -v tests`; `pre-commit install` runs the checks. Python 3.10 is the oldest supported.
     (An earlier brief said flake8. Evidently's own CONTRIBUTING says ruff, so use ruff.)
   - *Feast* (default branch `master`): fork, never a branch on the main repo. **Sign off every commit** (`git commit -s`). Rebase, do not merge (`git pull -r`, then `--force-with-lease`).
     PR title in conventional-commit form with a capital letter after the colon and at most 100 characters: `fix: Preserve duplicate entity rows`. Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert.
     Fill in the PR template; ask for a `kind/...` label. Install pre-commit (`make install-precommit`), run `make format-python`, `make lint-python`, `make test-python-unit`.
     A maintainer must mark a public PR `ok-to-test` before CI runs. Read `.commitlintrc.yaml` and `docs/project/development-guide.md` before you push.
6. **One issue, one fix, one small pull request.** Link the issue. Write the description yourself, in plain words. If a tool helped write code, you are still the author: read it, run it, own it.
7. **Be patient and kind.** Never ping repeatedly. Follow each project's code of conduct.
8. **After upstream merges:** delete the entry in `src/workarounds.py`, flip the Issue Lab status, update the tracker, celebrate.

## Security reports are not part of the sprint

Security issues (for example Feast #6785 and #6784) are **not** in the tracker on purpose. Never open a public issue or pull request for a vulnerability, and never post exploit details.
Feast asks for a private report through GitHub's advisory form and its `SECURITY.md`; do the same for any project.

## Schedule

| Week | Focus |
|---|---|
| 1 | Setup and reading. Run `make all` and `make issues`. Read both upstream CONTRIBUTING guides. Claim **review** tasks on the Starter rows (docs fixes, zero-row guards, the `feast init` name check). Comment on issues |
| 2 | Medium rows: test the open pull requests for G-test sample sizes, duplicate rows and `alias=`. Only if a row is truly free (#6821 is claimed; ask first), write code with a failing test first |
| 3 | Review week. Everyone reviews someone else's work, upstream or here. Stretch volunteers: sequential drift (#1927), calibration (#1902): comment first, code later |
| 4 | Demo day and retrospective. Re-run `make issues`, retire workarounds that no longer apply, update the roadmap and the counts |

## Definition of done for a row

The upstream pull request is merged, or you left a useful review on it; the matching Issue Lab entry flipped or was explained in `NOTES.md`;
the workaround was deleted if it was safe to; the tracker row is up to date.
