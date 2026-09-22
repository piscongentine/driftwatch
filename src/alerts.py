"""Turn summary.json into alerts: print them and write alerts.json.

Reads : out/summary.json, and the limits in config.py
Writes: out/alerts.json   the dashboard reads it
Rules:
  1. drift share  a batch drifted on SHARE_WARN or SHARE_ALERT of the monitored columns
  2. streak       one column is drifting now, and has for STREAK_ALERT tested batches in a row
  3. freshness    a feature view holds a value older than its ttl
  4. untested     a batch was empty or too small to test
Use `--strict` to exit with 1 when any alert (not warning) fired, for CI.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # lets `import config` work when run as a script
import config  # noqa: E402

ORDER = {"alert": 0, "warn": 1}


def item(level, rule, title, detail, batch=None, when=None):
    return {"level": level, "rule": rule, "title": title, "detail": detail, "batch": batch, "time": when}


def drift_share(tested):
    out = []
    for b in tested:
        level = "alert" if b["share"] >= config.SHARE_ALERT else "warn" if b["share"] >= config.SHARE_WARN else None
        if level:
            hit = [c for c, v in b["columns"].items() if v["drifted"]]
            title = f"Batch {b['index']}: {len(hit)} of {len(b['columns'])} columns drifted"
            out.append(item(level, "drift_share", title, ", ".join(hit), b["index"], b["timestamp"]))
    return out


def streaks(tested):
    """Columns that are drifting now, and for how many tested batches in a row. One alert, not one per column."""
    runs = {}
    for col in config.MONITORED:
        run = 0
        for b in tested:  # untested batches are skipped, they do not break a streak
            run = run + 1 if b["columns"][col]["drifted"] else 0
        if run >= config.STREAK_ALERT:
            runs[col] = run
    if not runs:
        return []
    last = tested[-1]
    title = f"{len(runs)} column(s) drifting for {config.STREAK_ALERT}+ batches in a row"
    detail = ", ".join(f"{c} ({n})" for c, n in runs.items())
    return [item("alert", "streak", title, detail, last["index"], last["timestamp"])]


def stale(summary):
    return [
        item("warn", "freshness", f"{f['view']} is stale",
             f"oldest value is {f['age_hours']:.0f} h old, ttl is {f['ttl_hours']:.0f} h", None, summary["generated_at"])
        for f in summary["freshness"] if f["stale"]
    ]


def untested(summary):
    why = {"empty": "was empty", "too_small": f"had too few rows (under {config.MIN_ROWS})"}
    return [
        item("warn", "untested", f"Batch {b['index']} {why[b['status']]}", "drift was not checked", b["index"], b["timestamp"])
        for b in summary["batches"] if b["status"] != "ok"
    ]


def main():
    summary = json.loads(config.SUMMARY.read_text())
    tested = [b for b in summary["batches"] if b["status"] == "ok"]
    found = drift_share(tested) + streaks(tested) + stale(summary) + untested(summary)
    found.sort(key=lambda a: (ORDER[a["level"]], -(a["batch"] if a["batch"] is not None else -1)))
    counts = {lv: sum(a["level"] == lv for a in found) for lv in ORDER}
    limits = {"warn": config.SHARE_WARN, "alert": config.SHARE_ALERT, "streak": config.STREAK_ALERT}
    config.ALERTS.write_text(json.dumps({"generated_at": summary["generated_at"], "limits": limits, "counts": counts, "alerts": found}, indent=2))

    for a in found:
        print(f"{a['level'].upper():<5}  {a['title']}  ({a['detail']})")
    print(f"{counts['alert']} alert(s), {counts['warn']} warning(s); wrote {config.ALERTS}")
    if "--strict" in sys.argv and counts["alert"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
