"""evidently #1902: feature request, Expected Calibration Error and reliability diagrams.

There is nothing to crash, so this looks for both parts: a calibration-error metric and a
reliability diagram. Fixed only when both exist. Related open pull request evidently #1896
adds ECE and Brier score metrics but is not linked to this issue: check it before you start.
"""
import warnings

warnings.filterwarnings("ignore")
import evidently.metrics as metrics  # noqa: E402
import evidently.presets as presets  # noqa: E402

names = [n for mod in (metrics, presets) for n in dir(mod)]
ece = [n for n in names if n.lower() in ("ece", "expectedcalibrationerror") or "calibrationerror" in n.lower()]
diagram = [n for n in names if "reliability" in n.lower() or "calibrationcurve" in n.lower()]
print("calibration error metric :", ece or "missing")
print("reliability diagram      :", diagram or "missing")
print("STATUS:", "Fixed" if ece and diagram else "Reproduced")
