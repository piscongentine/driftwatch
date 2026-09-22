"""End to end: data -> train -> live -> drift -> alerts, run for real in a temp copy of the repo.

Reads : the `project` fixture (tests/conftest.py).  Writes: nothing outside pytest's temp folder.
Numbers here follow the seeded data in config.py. If you change SEED or the drift settings, expect to revisit them.
"""
import config


def test_model_marks_are_strong_and_beat_the_baseline(project):
    r = project.json("train_report.json")
    assert r["rows_in"] == r["rows_out"], "training rows were lost between labels and Feast (feast #6787)"
    assert r["auc"] >= 0.90
    assert r["accuracy"] > r["baseline_accuracy"]
    assert r["precision"] >= 0.60 and r["recall"] >= 0.55


def test_every_batch_reached_feast_in_order(project):
    log = project.json("live_log.json")
    sizes = [b["rows"] for b in log]
    assert len(log) == config.N_BATCHES
    assert sizes[config.EMPTY_BATCH] == 0 and sizes[config.TINY_BATCH] == config.TINY_SIZE
    assert set(sizes) >= {0, config.TINY_SIZE, config.BATCH_SIZE}
    assert all(b["pushed"] == b["rows"] for b in log)
    assert all(b["online_same_order"] for b in log), "the online path changed the order of the rows (feast #6805)"


def test_summary_covers_every_batch_and_skips_the_untestable(project):
    batches = project.json("summary.json")["batches"]
    assert [b["status"] for b in batches].count("empty") == 1
    assert [b["status"] for b in batches].count("too_small") == 1
    assert all("share" in b and set(b["columns"]) == set(config.MONITORED) for b in batches if b["status"] == "ok")


def test_constant_column_is_never_nan_and_never_drifts(project):
    s = project.json("summary.json")  # project.json refuses NaN, so a nan would fail here
    assert [c for c in s["columns"] if c["name"] == "fw_ok"][0]["constant"] is True
    tested = [b for b in s["batches"] if b["status"] == "ok"]
    assert all(b["columns"]["fw_ok"]["p"] == 1.0 and not b["columns"]["fw_ok"]["drifted"] for b in tested)


def test_detector_is_quiet_when_healthy_and_loud_when_drifting(project):
    s = project.json("summary.json")
    d = s["detection"]
    assert d["precision"] >= 0.9 and d["recall"] >= 0.8, d
    healthy = [b for b in s["batches"] if b["status"] == "ok" and b["drift_step"] == 0]
    assert all(b["share"] < config.SHARE_WARN for b in healthy)
    assert s["batches"][-1]["share"] >= config.SHARE_ALERT


def test_freshness_flags_only_the_old_view(project):
    fresh = {f["view"]: f["stale"] for f in project.json("summary.json")["freshness"]}
    assert fresh == {config.STATS_VIEW: False, config.SERVICE_VIEW: True}


def test_alerts_cover_drift_untested_batches_and_stale_data(project):
    a = project.json("alerts.json")
    rules = {x["rule"] for x in a["alerts"]}
    assert {"drift_share", "streak", "untested", "freshness"} <= rules
    assert a["counts"]["alert"] >= 1


def test_strict_mode_exits_nonzero_when_an_alert_fired(project):
    assert project.run("alerts", "--strict").returncode == 1


def test_gate_label_keeps_our_alias(project):
    gate = project.json("summary.json")["batches"][-1]["gate"]
    assert gate["label"].startswith("Drift share under limit"), gate  # evidently #1907
