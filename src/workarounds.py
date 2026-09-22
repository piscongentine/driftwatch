"""Temporary fixes for upstream bugs. Each is tagged with its issue number; delete it when the fix ships.

Reads : nothing.
Writes: nothing (small helpers, plus one patch of Evidently's stat-test registry).

Retiring one: run `make issues`. When it says Fixed, delete the helper here, call the
plain library function instead, and flip the row in sprint/ISSUES.md.

Fixes that are not code:
  evidently #1914  config.CAT_TEST is chisquare, because g_test fails when batch and reference sizes differ
  evidently #1900  config.MIN_ROWS keeps tiny and empty batches away from the divergence tests
  evidently #1910  requirements.txt pins versions; if `evidently ui` fails, look at the litestar version first
  feast #6805      none needed: the standard online path keeps order and duplicates (tests/test_workarounds.py)
  Everything else in the Issue Lab is not hit by DriftWatch itself.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # lets `import config` work when run as a script
import config  # noqa: E402

KEYS = ["machine_id", "event_timestamp"]
STATS_COLS = config.NUMERIC + ["mode", "fw_ok"]


def pull_features(store, entity_df, features=config.FEATURES):
    """Point-in-time join through Feast, returning entity_df plus one column per feature.

    feast #6787: the file store drops entity rows that share (key, timestamp),
                 so ask for the unique rows and merge the answer back.
    feast #6817: a zero-row entity frame can raise TypeError, so answer it ourselves.
    """
    names = [f.split(":")[1] for f in features]
    if entity_df.empty:
        return pd.DataFrame(columns=list(entity_df.columns) + names)
    got = store.get_historical_features(entity_df=entity_df[KEYS].drop_duplicates(), features=features).to_df()
    return entity_df.merge(got, on=KEYS, how="left")


def push_batch(store, df):
    """Write a batch to the online and offline stores; returns the rows pushed.

    feast #6796: Feast's Arrow conversion breaks on zero rows, and an empty batch has nothing to push.
    """
    if df.empty:
        return 0
    from feast.data_source import PushMode

    store.push(config.PUSH_SOURCE, df[config.FEATURE_COLS], to=PushMode.ONLINE_AND_OFFLINE)
    return len(df)


def online_rows(store, ids):
    """Latest features for these machines, in the order asked (duplicates included).

    feast #6819: an online request with zero entity rows raises IndexError, so only ask when there is something to ask.
    """
    cols = ["machine_id"] + STATS_COLS
    if not ids:
        return pd.DataFrame(columns=cols)
    rows = [{"machine_id": i} for i in ids]
    return store.get_online_features(features=config.FEATURES, entity_rows=rows).to_df()[cols]


def is_stale(event_ts, ttl, now):
    """True where the newest value is older than the view's ttl.

    feast #6821: online reads ignore ttl and serve old values as if they were fresh,
                 so compare the event timestamp with the ttl ourselves.
    """
    return (now - event_ts) > ttl


_patched = False


def patch_evidently():
    """chisquare returns nan for a column with one category; identical single values mean no drift.

    evidently #1929: nan is not a p-value, and one nan poisons the drift share and the dashboard JSON.
    Replaces the built-in implementation in Evidently's registry, using its public register function.
    """
    global _patched
    if _patched:
        return
    from evidently.legacy.calculations.stattests import chi_stat_test, register_stattest

    original = chi_stat_test.func

    def fixed(reference, current, feature_type, threshold):
        if pd.concat([reference, current]).nunique() < 2:
            return 1.0, False
        return original(reference, current, feature_type, threshold)

    register_stattest(chi_stat_test, default_impl=fixed)
    _patched = True


def with_alias(description, alias):
    """Swap the leading metric name of a test description for our alias, if Evidently dropped it.

    evidently #1907: gt/lt/eq/... forward `alias=` only for some helpers. Without it the description
    starts with the metric's own name ("Share of Drifted Columns: Actual value ..."), not our alias.
    """
    if description.startswith(alias):
        return description
    return f"{alias}: {description.split(': ', 1)[-1]}"
