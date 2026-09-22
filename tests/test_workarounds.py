"""Each workaround does its one job. Pure helpers are tested with a small fake store, so no Feast is needed.

Reads : src/workarounds.py.  Writes: nothing.
Each test names the upstream issue. When the issue is fixed and the workaround is deleted, delete its test with it.
"""
from datetime import timedelta

import pandas as pd

import config
import workarounds as w

T = pd.Timestamp("2026-09-20 10:00", tz="UTC")


class FakeStore:
    """Answers get_historical_features like the file store does with feast #6787: unique rows only."""

    def __init__(self):
        self.calls = 0

    def get_historical_features(self, entity_df, features):
        self.calls += 1
        out = entity_df.drop_duplicates(w.KEYS).assign(**{f.split(":")[1]: 1.5 for f in features})
        return type("Job", (), {"to_df": lambda self: out})()


def test_duplicate_entity_rows_are_kept():  # feast #6787
    labels = pd.DataFrame({"machine_id": [1, 1, 2], "event_timestamp": [T, T, T], "failure": [0, 1, 0]})
    got = w.pull_features(FakeStore(), labels, ["machine_stats:temperature"])
    assert len(got) == 3 and list(got["failure"]) == [0, 1, 0] and got["temperature"].notna().all()


def test_zero_row_entity_frame_never_reaches_feast():  # feast #6817
    store = FakeStore()
    got = w.pull_features(store, pd.DataFrame({"machine_id": [], "event_timestamp": []}), ["machine_stats:temperature"])
    assert got.empty and "temperature" in got.columns and store.calls == 0


def test_empty_batch_is_not_pushed():  # feast #6796
    assert w.push_batch(object(), pd.DataFrame(columns=config.FEATURE_COLS)) == 0   # a real store would fail: it has no push()


def test_zero_machine_online_read_returns_an_empty_frame():  # feast #6819
    assert w.online_rows(object(), []).empty


def test_stale_means_older_than_the_ttl():  # feast #6821
    ttl = timedelta(hours=6)
    assert w.is_stale(T - timedelta(hours=7), ttl, T) and not w.is_stale(T - timedelta(hours=5), ttl, T)


def test_alias_replaces_the_metric_name_and_is_not_added_twice():  # evidently #1907
    assert w.with_alias("Share of Drifted Columns: Actual value 0.8 >= 0.4", "Gate") == "Gate: Actual value 0.8 >= 0.4"
    assert w.with_alias("Gate: Actual value 0.8", "Gate") == "Gate: Actual value 0.8"


def test_constant_column_gives_p_one_and_a_real_difference_still_drifts():  # evidently #1929
    from evidently.legacy.calculations.stattests import chi_stat_test
    from evidently.legacy.core import ColumnType

    w.patch_evidently()
    w.patch_evidently()  # safe to call twice
    same = pd.Series(["a"] * 50)
    r = chi_stat_test(reference_data=same, current_data=same, feature_type=ColumnType.Categorical, threshold=0.05)
    assert r.drift_score == 1.0 and not r.drifted
    ref = pd.Series(["a"] * 500 + ["b"] * 500)
    cur = pd.Series(["a"] * 5 + ["b"] * 95)
    r = chi_stat_test(reference_data=ref, current_data=cur, feature_type=ColumnType.Categorical, threshold=0.05)
    assert r.drifted
