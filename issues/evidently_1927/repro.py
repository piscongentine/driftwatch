"""evidently #1927: feature request, a sequential drift metric (for example CUSUM) for time-ordered batches.

There is nothing to crash, so this looks for the feature: any metric or preset whose name says
sequential, CUSUM or change point. Reproduced means the gap is still there. No pull request yet;
Evidently's CONTRIBUTING asks you to open or comment on an issue first.
"""
import warnings

warnings.filterwarnings("ignore")
import evidently.metrics as metrics  # noqa: E402
import evidently.presets as presets  # noqa: E402

WORDS = ("sequential", "cusum", "changepoint", "change_point")
found = [f"{mod.__name__}.{n}" for mod in (metrics, presets) for n in dir(mod) if any(w in n.lower() for w in WORDS)]
print("metrics and presets checked:", len(dir(metrics)) + len(dir(presets)))
print("names that look like sequential drift:", found or "none")
print("STATUS:", "Fixed" if found else "Reproduced")
