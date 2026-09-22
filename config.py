"""Every DriftWatch setting, as plain constants. Change a number, re-run the step.

Reads : nothing (every other file imports this one).
Writes: nothing.
"""
from pathlib import Path

# --- paths: scripts read and write only under out/ ---
ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
DATA = OUT / "data"
REPO = ROOT / "feature_repo"            # the Feast repo (feature_store.yaml lives here)
HISTORY = DATA / "history.parquet"      # Feast offline source: sensor readings
SERVICE = DATA / "service.parquet"      # Feast offline source: last inspection, old on purpose
LABELS = DATA / "labels.parquet"        # entity rows plus failure label; the training set starts here
PLAN = DATA / "plan.json"               # schedule for the live run: size and drift of each batch
BATCHES = DATA / "batches"              # one file per live batch: keys plus label
REFERENCE = DATA / "reference.parquet"  # training features as Feast returned them
MODEL = OUT / "model.pkl"
TRAIN_REPORT = OUT / "train_report.json"
LIVE_LOG = OUT / "live_log.json"
FRESHNESS = OUT / "freshness.json"
SUMMARY = OUT / "summary.json"          # read by the dashboard
ALERTS = OUT / "alerts.json"            # read by the dashboard
ISSUES_STATUS = OUT / "issues.json"     # written by `make issues`, read by the dashboard

# --- synthetic fleet ---
SEED = 7                    # same seed, same numbers: runs are repeatable
N_MACHINES = 40
HISTORY_HOURS = 100         # one reading per machine per hour: 4,000 training rows
N_BATCHES = 12              # live batches, one per hour
BATCH_SIZE = 40             # one reading per machine: far smaller than the reference
EMPTY_BATCH = 7             # this batch arrives with zero rows (a dead uplink)
TINY_BATCH = 3              # this batch has only TINY_SIZE rows
TINY_SIZE = 4
STALE_DAYS = 30             # age of the inspection feature, on purpose

# --- drift simulation: sensors wear out slowly after DRIFT_START ---
DRIFT_START = 4             # first batch that drifts
DRIFT_STEP = 0.35           # standard deviations of shift added per batch
DRIFT_WEIGHTS = {"temperature": 1.0, "vibration": 0.8, "humidity": 0.4}   # sensors drift; real failures do not change

# --- columns ---
NUMERIC = ["temperature", "vibration", "humidity"]
MODES = ["idle", "normal", "high"]
CATEGORICAL = ["mode", "fw_ok"]          # fw_ok never changes: a constant flag on purpose
MONITORED = NUMERIC + CATEGORICAL + ["prediction"]
FEATURE_COLS = ["machine_id", "event_timestamp"] + NUMERIC + CATEGORICAL   # Feast writes columns in exactly this order
LABEL_COLS = ["machine_id", "event_timestamp", "failure"]

# --- Feast ---
PUSH_SOURCE = "machine_push"
STATS_VIEW = "machine_stats"
SERVICE_VIEW = "machine_service"
FEATURES = [f"{STATS_VIEW}:{c}" for c in NUMERIC + CATEGORICAL]
TTL_STATS_HOURS = 6
TTL_SERVICE_DAYS = 7

# --- model: split by time, oldest to newest ---
VAL_SIZE = 0.15             # picks the decision threshold
TEST_SIZE = 0.25            # newest rows: scores the model, never used for any choice

# --- drift tests (Evidently) ---
NUM_TEST = "ks"             # p-value test for numeric columns
CAT_TEST = "chisquare"      # not g_test on purpose: see src/workarounds.py, evidently #1914
DRIFT_P = 0.05              # p-value below this means drift
MIN_ROWS = 5                # smaller batches are not tested at all

# --- alerts ---
SHARE_WARN = 0.20           # share of monitored columns drifted in one batch
SHARE_ALERT = 0.40
STREAK_ALERT = 3            # one column drifting this many batches in a row

# --- Issue Lab ---
ISSUES_DIR = ROOT / "issues"
TRACKER = ROOT / "sprint" / "ISSUES.md"   # titles, levels and upstream status come from here
ISSUE_WORKERS = 4                         # repros run this many at a time
ISSUE_TIMEOUT = 240                       # seconds before a repro counts as an Error
