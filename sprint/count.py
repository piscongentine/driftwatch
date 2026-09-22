"""Count the sprint: how many tracker rows are claimed, have a pull request, or are merged.

Reads : sprint/ISSUES.md
Writes: nothing (prints numbers). Paste them into the README when they change.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # lets `import config` work when run as a script
import config  # noqa: E402


PR_LINK = re.compile(r"\[[^\]]*#\d+\]")  # [#1932] or [evidentlyai/docs#2]


def rows():
    out = []
    for line in config.TRACKER.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) > 8 and re.search(r"\[#\d+\]", cells[1]):
            out.append(cells)
    return out


def main():
    table = rows()
    status = [r[4] for r in table]
    print(f"issues tracked        : {len(table)}")
    for s in ("Open", "Claimed", "Has PR", "Merged"):
        print(f"  upstream {s:<8}    : {status.count(s)}")
    print(f"rows owned by a member: {sum(bool(r[5]) for r in table)}")
    print(f"club pull requests    : {sum(bool(r[6]) for r in table)}")
    print(f"upstream PRs listed   : {sum(len(PR_LINK.findall(r[7])) for r in table)}")


if __name__ == "__main__":
    main()
