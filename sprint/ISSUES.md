# Issue tracker

The live table for the PR sprint. **One row per upstream issue we carry.** Owners claim a row with a
club-repo pull request that edits this file. `make issues` reads it, so keep the format: one row per
line, the issue link as `[#1234](url)`, no `|` characters inside a cell.

Statuses last checked: **20 Sep 2026**, by opening every issue and reading its body, its comments and
its linked pull requests (GitHub issue pages, the public REST API and the search API). Re-check
before you start. Things move fast: two days before this table was written, PR #6843 was merged.

| Upstream status | Meaning |
|---|---|
| Open | No pull request found and nobody has claimed it |
| Claimed | Someone said in the issue that they are working on it; no pull request yet |
| Has PR | At least one pull request is open. Do not start a competing one: review and test it |
| Merged | The fix is on the upstream main branch. It may not be in a release yet |

Level: **Starter** (small, local), **Medium** (needs some reading of upstream code), **Stretch**
(bigger, or a feature: ask the maintainers first), **Review** (only review and test).
"Lab result" (Reproduced, Fixed) is not in this table: `make issues` prints it and the dashboard shows it.

## Evidently (default branch `main`)

| Repo | Issue link | Title | Level | Upstream status | Owner | Club PR | Upstream PR | Notes |
|---|---|---|---|---|---|---|---|---|
| Evidently | [#1929](https://github.com/evidentlyai/evidently/issues/1929) | chi_stat_test and g_test return nan on a constant categorical column | Starter | Has PR | | | [#1932](https://github.com/evidentlyai/evidently/pull/1932) | Filed 18 Sep by warter666, who also opened the PR. Review it against our constant fw_ok column |
| Evidently | [#1914](https://github.com/evidentlyai/evidently/issues/1914) | G-test raises ValueError when reference and current have different sample sizes | Medium | Has PR | | | [#1913](https://github.com/evidentlyai/evidently/pull/1913), [#1928](https://github.com/evidentlyai/evidently/pull/1928) | Two PRs already compete. Compare them, test both, comment |
| Evidently | [#1900](https://github.com/evidentlyai/evidently/issues/1900) | Divergence stat tests crash or return wrong results on edge-case input | Medium | Has PR | | | [#1901](https://github.com/evidentlyai/evidently/pull/1901), [#1924](https://github.com/evidentlyai/evidently/pull/1924) | ArjunPakhan claimed it on 20 Jul. Two PRs open; #1924 raises a clear ValueError |
| Evidently | [#1907](https://github.com/evidentlyai/evidently/issues/1907) | Generic test helpers drop alias= for metric-level tests | Medium | Has PR | | | [#1908](https://github.com/evidentlyai/evidently/pull/1908) | Our drift gate test uses lt(alias=...) and loses it |
| Evidently | [#1927](https://github.com/evidentlyai/evidently/issues/1927) | New metric: sequential drift detection on time-ordered batches | Stretch | Open | | | | Feature. No comments, no PR. Ask the maintainers before coding |
| Evidently | [#1902](https://github.com/evidentlyai/evidently/issues/1902) | Add Expected Calibration Error and reliability diagrams | Stretch | Has PR | | | [#1896](https://github.com/evidentlyai/evidently/pull/1896) | #1896 (Brier score and ECE, closes #1895) is not linked to this issue. Check whether it covers the reliability diagram |
| Evidently | [#1905](https://github.com/evidentlyai/evidently/issues/1905) | Examples README links to examples/tutorials/, which does not exist | Starter | Has PR | | | [#1906](https://github.com/evidentlyai/evidently/pull/1906) | Docs fix, PR open since 27 Jul |
| Evidently | [#1898](https://github.com/evidentlyai/evidently/issues/1898) | LLM quickstart is missing the OpenAI dependency for DeclineLLMEval | Starter | Has PR | | | [evidentlyai/docs#2](https://github.com/evidentlyai/docs/pull/2) | The docs live in the separate evidentlyai/docs repo. docs#3 was closed without merging |
| Evidently | [#1910](https://github.com/evidentlyai/evidently/issues/1910) | litestar.contrib.pydantic removed in litestar 3.0 | Medium | Has PR | | | [#1919](https://github.com/evidentlyai/evidently/pull/1919), [#1912](https://github.com/evidentlyai/evidently/pull/1912) | #1912 is a draft. Nothing breaks today: the installed litestar is 2.x |

## Feast (default branch `master`)

| Repo | Issue link | Title | Level | Upstream status | Owner | Club PR | Upstream PR | Notes |
|---|---|---|---|---|---|---|---|---|
| Feast | [#6787](https://github.com/feast-dev/feast/issues/6787) | get_historical_features on the file store silently drops entity rows sharing join key and timestamp | Medium | Has PR | | | [#6786](https://github.com/feast-dev/feast/pull/6786) | Labels: kind/bug, priority/p2. Our duplicate machine reading is exactly this |
| Feast | [#6817](https://github.com/feast-dev/feast/issues/6817) | get_historical_features raises TypeError on a zero-row entity_df | Starter | Has PR | | | [#6818](https://github.com/feast-dev/feast/pull/6818) | Not reproduced on feast 0.66.0 (Lab: Fixed). The reporter used master. Test the PR against master |
| Feast | [#6819](https://github.com/feast-dev/feast/issues/6819) | Online request with zero entity rows returns HTTP 500 instead of an empty result or a 400 | Starter | Has PR | | | [#6820](https://github.com/feast-dev/feast/pull/6820) | Reproduced on 0.66.0: the SDK call (IndexError) and both HTTP shapes (500) |
| Feast | [#6796](https://github.com/feast-dev/feast/issues/6796) | Return an empty write payload when Arrow conversion gets a zero-row table | Starter | Has PR | | | [#6797](https://github.com/feast-dev/feast/pull/6797) | PR updated 20 Sep |
| Feast | [#6805](https://github.com/feast-dev/feast/issues/6805) | Precomputed online retrieval does not keep entity input order or duplicates | Medium | Has PR | | | [#6806](https://github.com/feast-dev/feast/pull/6806) | Only the precomputed path. The standard path keeps order (checked in live.py) |
| Feast | [#6821](https://github.com/feast-dev/feast/issues/6821) | Feature view ttl is not applied on the standard online retrieval path | Medium | Claimed | | | | obielin claimed it on 7 Sep and described a plan. No PR found. Ask before starting |
| Feast | [#6808](https://github.com/feast-dev/feast/issues/6808) | feast init accepts project names that break the local SQLite template | Starter | Has PR | | | [#6809](https://github.com/feast-dev/feast/pull/6809) | Supersedes closed #6807. Our project name has no hyphen on purpose |
| Feast | [#6790](https://github.com/feast-dev/feast/issues/6790) | Join key value silently dropped when it shares a name with an OnDemandFeatureView RequestSource field | Medium | Has PR | | | [#6794](https://github.com/feast-dev/feast/pull/6794) | Watch for this when we add on-demand features |
| Feast | [#6845](https://github.com/feast-dev/feast/issues/6845) | Internal error when creating a feature view through the Feast UI | Medium | Has PR | | | [#6849](https://github.com/feast-dev/feast/pull/6849) | patelchaitany claimed it on 18 Sep. Reported on Windows with 0.66.0 |
| Feast | [#6842](https://github.com/feast-dev/feast/issues/6842) | Expose running Feast version in the UI | Review | Merged | | | [#6843](https://github.com/feast-dev/feast/pull/6843) | Merged 17 Sep, issue closed. Not in the 0.66.0 release yet: Lab shows Reproduced until a release has it |
| Feast | [#6815](https://github.com/feast-dev/feast/issues/6815) | On-demand feature view UDFs lose module globals when rebuilt from registry (NameError) | Stretch | Has PR | | | [#6816](https://github.com/feast-dev/feast/pull/6816) | Deeper change. Review the PR |

## How we counted

- 20 issues: **17 Has PR** (one of them, #1902, only through a related pull request), **1 Merged**, **1 Claimed**, **1 Open**.
- Because nearly everything already has a PR, weeks 1 and 2 of the sprint are mostly **review and test** work, not new code. See [SPRINT.md](SPRINT.md).
- Security reports (for example feast #6785 and #6784) are **not** in this table on purpose. See SPRINT.md.
