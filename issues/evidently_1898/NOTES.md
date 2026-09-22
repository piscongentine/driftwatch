# evidently #1898: LLM quickstart is missing the OpenAI dependency for DeclineLLMEval

[Issue](https://github.com/evidentlyai/evidently/issues/1898) | Upstream: Has PR ([evidentlyai/docs#2](https://github.com/evidentlyai/docs/pull/2), open; docs#3 closed unmerged) | Lab, 20 Sep 2026: **Reproduced**

**What breaks.** The quickstart at `quickstart_llm.mdx` installs with `pip install evidently` only, then uses
`DeclineLLMEval`, which defaults to the OpenAI provider. A fresh install has no `openai` package (we checked: not installed here).

**Important.** The docs live in a **separate repo**, `evidentlyai/docs`, not in `evidentlyai/evidently`. Open the pull request there.

**Where it hits DriftWatch.** It does not: we use no LLM features.

**How to know it is fixed.** The repro reads the raw quickstart source and prints `STATUS: Fixed` once an install line mentions openai (needs internet).

**Not verified.** We did not read the docs repo's own contribution rules: its README and CONTRIBUTING returned 404 on `main`.
Read whatever that repo shows before you push. We also did not run the quickstart with a key, so we did not see the exact ImportError.
