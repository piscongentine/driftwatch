"""The synthetic data: edge cases are really in it, and drift really moves the sensors.

Reads : src/make_data.py.  Writes: nothing.
"""
import numpy as np
import pandas as pd

import config
import make_data as md

ANCHOR = pd.Timestamp("2026-09-20 12:00", tz="UTC")


def test_history_has_one_duplicate_reading_and_a_constant_flag():
    df = md.history(ANCHOR, np.random.default_rng(1))
    assert len(df) == config.N_MACHINES * config.HISTORY_HOURS + 1
    assert df.duplicated(["machine_id", "event_timestamp"]).sum() == 1   # feast #6787
    assert df["fw_ok"].nunique() == 1                                    # evidently #1929


def test_history_ends_before_the_first_live_batch():
    df = md.history(ANCHOR, np.random.default_rng(1))
    assert df["event_timestamp"].max() < md.batch_time(ANCHOR, 0)
    assert md.batch_time(ANCHOR, config.N_BATCHES - 1) == ANCHOR


def test_plan_has_an_empty_batch_a_tiny_one_and_a_gradual_drift():
    batches = md.plan(ANCHOR)["batches"]
    sizes = [b["size"] for b in batches]
    assert sizes[config.EMPTY_BATCH] == 0 and sizes[config.TINY_BATCH] == config.TINY_SIZE
    assert config.BATCH_SIZE < config.N_MACHINES * config.HISTORY_HOURS   # batches are small next to the reference
    drift = [b["drift"] for b in batches]
    assert drift[: config.DRIFT_START] == [0] * config.DRIFT_START
    assert drift == sorted(drift) and drift[-1] > 0


def test_an_empty_batch_is_an_empty_frame_with_the_right_columns():
    df = md.make_rows([ANCHOR], [], 0, np.random.default_rng(1))
    assert df.empty and set(config.FEATURE_COLS + ["failure"]) <= set(df.columns)
    assert str(df["event_timestamp"].dtype).startswith("datetime64")


def test_drift_moves_the_sensors_but_not_the_failure_rate():
    rng = np.random.default_rng(3)
    healthy = md.make_rows(pd.date_range(ANCHOR, periods=200, freq="h"), md.MACHINES, 0, rng)
    worn = md.make_rows(pd.date_range(ANCHOR, periods=200, freq="h"), md.MACHINES, 8, rng)
    assert worn["temperature"].mean() > healthy["temperature"].mean() + 5
    assert worn["vibration"].mean() > healthy["vibration"].mean()
    assert abs(worn["failure"].mean() - healthy["failure"].mean()) < 0.02   # only the sensors drifted


def test_service_data_is_old_on_purpose():
    df = md.service(ANCHOR, np.random.default_rng(1))
    age = ANCHOR - df["event_timestamp"].max()
    assert age.days == config.STALE_DAYS and config.STALE_DAYS > config.TTL_SERVICE_DAYS
