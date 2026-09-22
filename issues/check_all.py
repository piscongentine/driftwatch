"""Run every Issue Lab repro and print a status table.

Reads : issues/*/repro.py, and sprint/ISSUES.md for each issue's title, level and upstream status.
Writes: out/issues.json   the dashboard reads it
Result per issue:
  Reproduced  the bug is still there in the installed versions
  Fixed       the bug is not seen any more (fixed upstream, or never in this release: read its NOTES.md)
  Error       the repro itself broke (no internet, an API changed, ...)
Run some only:  python issues/check_all.py feast_6787 evidently_1929
Add --strict to exit with 1 when any repro ends in Error.
"""
import json
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from importlib.metadata import version
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # lets `import config` work when run as a script
import config  # noqa: E402

ROW = re.compile(r"\[#(\d+)\]\((https://github\.com/[^)]+)\)")


def tracker():
    """{number: row} read from the tables in sprint/ISSUES.md."""
    rows = {}
    for line in config.TRACKER.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        m = ROW.search(cells[1]) if len(cells) > 4 else None
        if m:
            rows[int(m.group(1))] = {"repo": cells[0], "url": m.group(2), "title": cells[2], "level": cells[3], "upstream": cells[4]}
    return rows


def run(folder, rows):
    number = int(folder.name.split("_")[1])
    info = rows.get(number, {"repo": folder.name.split("_")[0].title(), "url": "", "title": "(not in the tracker)", "level": "", "upstream": ""})
    start = time.time()
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "FEAST_USAGE": "False"}
    try:
        p = subprocess.run([sys.executable, str(folder / "repro.py")], capture_output=True, text=True, timeout=config.ISSUE_TIMEOUT, env=env)
        found = re.findall(r"^STATUS: (Reproduced|Fixed)\s*$", p.stdout, re.M)
        status, detail = (found[-1], "") if found and p.returncode == 0 else ("Error", (p.stderr.strip().splitlines() or ["no STATUS line"])[-1][:200])
    except subprocess.TimeoutExpired:
        status, detail = "Error", f"timed out after {config.ISSUE_TIMEOUT} s"
    return {"key": folder.name, "number": number, **info, "status": status, "detail": detail, "seconds": round(time.time() - start, 1)}


def main():
    wanted = [a for a in sys.argv[1:] if not a.startswith("--")]
    folders = sorted(p for p in config.ISSUES_DIR.iterdir() if (p / "repro.py").exists() and (not wanted or p.name in wanted))
    rows = tracker()
    with ThreadPoolExecutor(config.ISSUE_WORKERS) as pool:
        results = list(pool.map(lambda f: run(f, rows), folders))

    print(f"Issue Lab: feast {version('feast')}, evidently {version('evidently')}, {len(results)} repro(s)\n")
    print(f"{'folder':<16} {'upstream':<9} {'lab result':<11} {'secs':>5}  title")
    for r in results:
        print(f"{r['key']:<16} {r['upstream']:<9} {r['status']:<11} {r['seconds']:>5}  {r['title'][:62]}")
        if r["detail"]:
            print(f"{'':<16} -> {r['detail']}")
    count = {s: sum(r["status"] == s for r in results) for s in ("Reproduced", "Fixed", "Error")}
    print("\n" + ", ".join(f"{n} {s}" for s, n in count.items()))

    if not wanted:  # a partial run would leave the dashboard with a partial table
        config.OUT.mkdir(exist_ok=True)
        payload = {"generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "results": results}
        config.ISSUES_STATUS.write_text(json.dumps(payload, indent=2))
    if "--strict" in sys.argv and count["Error"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
