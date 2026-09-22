"""The Issue Lab and the sprint tracker agree with each other.

Reads : issues/, sprint/ISSUES.md.  Writes: nothing.
"""
import subprocess
import sys

import pytest

import config

sys.path.insert(0, str(config.ISSUES_DIR))
import check_all  # noqa: E402

ROWS = check_all.tracker()
FOLDERS = sorted(p.name for p in config.ISSUES_DIR.iterdir() if p.is_dir() and (p / "repro.py").exists())


def test_twenty_issues_and_a_folder_for_every_row():
    assert len(ROWS) == 20
    expected = sorted(f"{r['repo'].lower()}_{n}" for n, r in ROWS.items())
    assert FOLDERS == expected


@pytest.mark.parametrize("folder", FOLDERS)
def test_folder_has_notes_and_a_repro_that_reports_a_status(folder):
    base = config.ISSUES_DIR / folder
    assert (base / "NOTES.md").read_text(encoding="utf-8").startswith("# ")
    assert "STATUS:" in (base / "repro.py").read_text(encoding="utf-8") or "verdict(" in (base / "repro.py").read_text(encoding="utf-8")


def test_tracker_uses_only_known_words():
    assert {r["upstream"] for r in ROWS.values()} <= {"Open", "Claimed", "Has PR", "Merged"}
    assert {r["level"] for r in ROWS.values()} <= {"Starter", "Medium", "Stretch", "Review"}


def test_check_all_runs_one_repro_and_reports_its_status():
    done = subprocess.run([sys.executable, str(config.ISSUES_DIR / "check_all.py"), "evidently_1929"], capture_output=True, text=True)
    assert done.returncode == 0 and "evidently_1929" in done.stdout
    assert "Error" not in done.stdout.split("lab result")[1].split("\n")[1]
